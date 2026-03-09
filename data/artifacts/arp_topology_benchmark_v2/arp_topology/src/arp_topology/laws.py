from __future__ import annotations

import json
from dataclasses import dataclass, fields, replace
from pathlib import Path
from typing import Any

import numpy as np


Array = np.ndarray


@dataclass(slots=True)
class EdgeLattice:
    nx: int
    ny: int
    edge_pairs: Array
    edge_midpoints: Array
    boundary_mask: Array

    @property
    def n_edges(self) -> int:
        return int(self.edge_midpoints.shape[0])

    @classmethod
    def square(cls, nx: int = 8, ny: int = 8) -> "EdgeLattice":
        if nx < 3 or ny < 3:
            raise ValueError("nx and ny must both be >= 3")

        edges: list[list[list[float]]] = []
        midpoints: list[list[float]] = []
        boundary: list[bool] = []

        for j in range(ny):
            for i in range(nx - 1):
                p0 = [float(i), float(j)]
                p1 = [float(i + 1), float(j)]
                edges.append([p0, p1])
                midpoints.append([(p0[0] + p1[0]) / 2.0, (p0[1] + p1[1]) / 2.0])
                boundary.append(j == 0 or j == ny - 1)

        for i in range(nx):
            for j in range(ny - 1):
                p0 = [float(i), float(j)]
                p1 = [float(i), float(j + 1)]
                edges.append([p0, p1])
                midpoints.append([(p0[0] + p1[0]) / 2.0, (p0[1] + p1[1]) / 2.0])
                boundary.append(i == 0 or i == nx - 1)

        return cls(
            nx=nx,
            ny=ny,
            edge_pairs=np.asarray(edges, dtype=float),
            edge_midpoints=np.asarray(midpoints, dtype=float),
            boundary_mask=np.asarray(boundary, dtype=bool),
        )


@dataclass(slots=True)
class ModelParams:
    steps: int = 480
    dt: float = 0.03
    damage_step: int = 170
    damage_scale: float = 0.14
    drive: float = 1.0
    g0: float = 0.34
    g_max: float = 2.40
    alpha0: float = 0.66
    alpha_gain: float = 0.26
    mu0: float = 0.22
    mu_relief: float = 0.08
    lambda_s: float = 0.92
    chi: float = 0.95
    slip_penalty: float = 0.58
    memory_current_gain: float = 0.75
    pi_a_center: float = float(np.pi)
    pi_a_min: float = float(0.62 * np.pi)
    pi_a_max: float = float(1.25 * np.pi)
    pi_a_sensitivity: float = 0.42
    phase_advance: float = 0.34
    damage_phase_kick: float = 1.10
    boundary_drive_bias: float = 0.72
    coherence_gain: float = 0.60
    recovery_target_fraction: float = 0.78
    seed: int = 7


@dataclass(slots=True)
class VariantConfig:
    name: str
    use_phase_lift: bool = True
    use_topology_feedback: bool = True
    adaptive_ruler: bool = True
    lambda_scale: float = 1.0
    chi_scale: float = 1.0


@dataclass(slots=True)
class SimulationState:
    g: Array
    theta_R: Array
    damaged: bool = False

    def copy(self) -> "SimulationState":
        return SimulationState(g=self.g.copy(), theta_R=self.theta_R.copy(), damaged=bool(self.damaged))


@dataclass(slots=True)
class SimulationResult:
    variant: str
    time: Array
    total_current: Array
    boundary_current: Array
    boundary_fraction: Array
    edge_bulk_ratio: Array
    coherence: Array
    pi_a: Array
    state_scalar: Array
    snapshots_g_abs: dict[str, Array]
    snapshots_j_abs: dict[str, Array]
    final_state: SimulationState


def default_variants() -> list[VariantConfig]:
    return [
        VariantConfig(name="full_law"),
        VariantConfig(name="principal_branch", use_phase_lift=False, use_topology_feedback=False, lambda_scale=1.8, chi_scale=0.0),
        VariantConfig(name="no_topology_feedback", use_topology_feedback=False, chi_scale=0.0),
        VariantConfig(name="fixed_ruler", adaptive_ruler=False, lambda_scale=1.25, chi_scale=0.12),
    ]


def wrap_to_pi(x: Array | float) -> Array:
    return (np.asarray(x) + np.pi) % (2.0 * np.pi) - np.pi


def clip_magnitude(z: Array, r_min: float, r_max: float) -> Array:
    mag = np.abs(z)
    phase = np.angle(z + 1e-12)
    mag = np.clip(mag, r_min, r_max)
    return mag * np.exp(1j * phase)


def phase_lift_update(theta_prev: Array, theta_raw_wrapped: Array, pi_a: float) -> Array:
    delta = wrap_to_pi(theta_raw_wrapped - theta_prev)
    delta = np.clip(delta, -pi_a, pi_a)
    return theta_prev + delta


def alpha_G(state_scalar: float, p: ModelParams) -> float:
    return p.alpha0 * (1.0 + p.alpha_gain * np.tanh(1.4 * (state_scalar - 1.0)))


def mu_G(state_scalar: float, p: ModelParams) -> float:
    return p.mu0 * (1.0 - p.mu_relief * np.tanh(1.1 * (state_scalar - 1.0)))


def adaptive_pi(state_scalar: float, p: ModelParams, adaptive: bool) -> float:
    if not adaptive:
        return float(p.pi_a_center)
    value = p.pi_a_center * (1.0 + p.pi_a_sensitivity * np.tanh(state_scalar - 1.0))
    return float(np.clip(value, p.pi_a_min, p.pi_a_max))


def load_mapping(path: str | Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    if path.suffix.lower() == ".json":
        return json.loads(path.read_text())
    if path.suffix.lower() in {".yml", ".yaml"}:
        try:
            import yaml  # type: ignore
        except ImportError as exc:
            raise RuntimeError("YAML config requested but PyYAML is not installed. Either install it or use JSON.") from exc
        data = yaml.safe_load(path.read_text())
        return {} if data is None else dict(data)
    raise ValueError(f"Unsupported config format: {path.suffix}")


def apply_overrides(params: ModelParams, overrides: dict[str, Any]) -> ModelParams:
    if not overrides:
        return params
    allowed = {f.name for f in fields(ModelParams)}
    clean = {k: v for k, v in overrides.items() if k in allowed}
    return replace(params, **clean)


def initial_state(lattice: EdgeLattice, p: ModelParams) -> SimulationState:
    rng = np.random.default_rng(p.seed)
    mags = p.g0 * (1.0 + 0.06 * rng.normal(size=lattice.n_edges))
    mags = np.clip(mags, 0.08, None)
    phase0 = 0.12 * lattice.boundary_mask.astype(float) - 0.02 * (~lattice.boundary_mask).astype(float)
    g0 = mags * np.exp(1j * phase0)
    return SimulationState(g=g0.astype(np.complex128), theta_R=np.angle(g0), damaged=False)


def boundary_mean(values: Array, mask: Array) -> float:
    return float(np.mean(values[mask])) if np.any(mask) else 0.0


def bulk_mean(values: Array, mask: Array) -> float:
    bulk = ~mask
    return float(np.mean(values[bulk])) if np.any(bulk) else 0.0


def compute_local_chern_proxy(j_abs: Array, theta_used: Array, boundary_mask: Array, history_consistency: Array) -> Array:
    eps = 1e-9
    b_mean = boundary_mean(j_abs, boundary_mask)
    k_mean = bulk_mean(j_abs, boundary_mask)
    transport_gap = np.tanh((b_mean - k_mean) / (abs(k_mean) + eps))
    boundary_phase_ref = np.angle(np.mean(np.exp(1j * theta_used[boundary_mask]))) if np.any(boundary_mask) else 0.0
    phase_alignment = 0.5 * (1.0 + np.cos(theta_used - boundary_phase_ref))
    c_loc = boundary_mask.astype(float) * np.clip(0.45 * phase_alignment + 0.35 * max(transport_gap, 0.0) + 0.20 * history_consistency, 0.0, 1.0)
    return c_loc


def compute_currents(state: SimulationState, theta_used: Array, lattice: EdgeLattice, p: ModelParams) -> tuple[Array, float]:
    eps = 1e-9
    boundary_mask = lattice.boundary_mask
    g_abs = np.abs(state.g)
    boundary_coherence = float(np.abs(np.mean(np.exp(1j * theta_used[boundary_mask])))) if np.any(boundary_mask) else 0.0
    channel_bias = 1.0 + p.boundary_drive_bias * boundary_mask.astype(float)
    coherence_bias = 1.0 + p.coherence_gain * boundary_mask.astype(float) * boundary_coherence
    j_abs = p.drive * channel_bias * coherence_bias * np.maximum(g_abs, eps)
    return j_abs, boundary_coherence


def _step(state: SimulationState, lattice: EdgeLattice, p: ModelParams, variant: VariantConfig, global_step: int) -> dict[str, Any]:
    g_abs = np.abs(state.g)
    state_scalar = float(np.mean(g_abs) / max(p.g0, 1e-9))
    pi_a = adaptive_pi(state_scalar, p, adaptive=variant.adaptive_ruler)

    boundary_mask_float = lattice.boundary_mask.astype(float)
    phase_drive = p.phase_advance * (1.0 + 0.20 * boundary_mask_float)
    damage_kick = p.damage_phase_kick * boundary_mask_float * (1.0 if state.damaged else 0.0) / (g_abs + 0.25)

    theta_raw_continuous = state.theta_R + phase_drive + damage_kick
    theta_raw_wrapped = wrap_to_pi(theta_raw_continuous)

    wrapped_delta = np.abs(wrap_to_pi(theta_raw_wrapped - state.theta_R))
    if variant.use_phase_lift:
        theta_used = phase_lift_update(state.theta_R, theta_raw_wrapped, pi_a)
        history_consistency = np.clip(1.0 - wrapped_delta / max(pi_a, 1e-9), 0.0, 1.0)
    else:
        theta_used = theta_raw_wrapped
        history_consistency = np.clip(1.0 - wrapped_delta / np.pi, 0.0, 1.0)

    j_abs, coherence = compute_currents(state, theta_used, lattice, p)
    c_loc = compute_local_chern_proxy(j_abs, theta_used, lattice.boundary_mask, history_consistency) if variant.use_topology_feedback and variant.chi_scale != 0.0 else np.zeros_like(j_abs)
    memory_gain = 1.0 + p.memory_current_gain * boundary_mask_float * history_consistency * c_loc
    j_abs = j_abs * memory_gain

    alpha = alpha_G(state_scalar, p)
    mu = mu_G(state_scalar, p)
    suppression = (p.lambda_s * variant.lambda_scale) * state.g * np.sin(theta_used / (2.0 * pi_a)) ** 2
    slip_factor = (1.0 - history_consistency) * (1.0 + 1.8 * boundary_mask_float * (1.0 if state.damaged else 0.0))
    branch_slip_penalty = p.slip_penalty * slip_factor * state.g
    boundary_target = p.g0 * (1.0 + 1.8 * boundary_mask_float)
    healing = (p.chi * variant.chi_scale) * c_loc * np.maximum(boundary_target - np.abs(state.g), 0.0) * np.exp(1j * theta_used)
    dg_dt = alpha * j_abs * np.exp(1j * theta_used) - mu * state.g - suppression - branch_slip_penalty + healing

    state.g = clip_magnitude(state.g + p.dt * dg_dt, r_min=0.02, r_max=p.g_max)
    state.theta_R = theta_used

    boundary_current = float(np.sum(j_abs[lattice.boundary_mask]))
    total_current = float(np.sum(j_abs))
    boundary_fraction = boundary_current / max(total_current, 1e-9)
    b_mean = boundary_mean(np.abs(state.g), lattice.boundary_mask)
    k_mean = bulk_mean(np.abs(state.g), lattice.boundary_mask)
    edge_bulk_ratio = b_mean / max(k_mean, 1e-9)

    return {
        "total_current": total_current,
        "boundary_current": boundary_current,
        "boundary_fraction": boundary_fraction,
        "edge_bulk_ratio": edge_bulk_ratio,
        "coherence": coherence,
        "pi_a": pi_a,
        "state_scalar": state_scalar,
        "j_abs": j_abs.copy(),
    }


def simulate(
    lattice: EdgeLattice,
    p: ModelParams,
    variant: VariantConfig,
    state: SimulationState | None = None,
    *,
    steps: int | None = None,
    starting_step: int = 0,
    apply_damage_event: bool = True,
    snapshot_steps: list[int] | None = None,
) -> SimulationResult:
    if state is None:
        state = initial_state(lattice, p)
    else:
        state = state.copy()

    total_steps = p.steps if steps is None else int(steps)
    snapshot_steps = [] if snapshot_steps is None else list(snapshot_steps)

    time = np.zeros(total_steps, dtype=float)
    total_current = np.zeros(total_steps, dtype=float)
    boundary_current = np.zeros(total_steps, dtype=float)
    boundary_fraction = np.zeros(total_steps, dtype=float)
    edge_bulk_ratio = np.zeros(total_steps, dtype=float)
    coherence = np.zeros(total_steps, dtype=float)
    pi_a = np.zeros(total_steps, dtype=float)
    state_scalar = np.zeros(total_steps, dtype=float)

    snapshots_g_abs: dict[str, Array] = {}
    snapshots_j_abs: dict[str, Array] = {}

    for local_idx in range(total_steps):
        global_step = starting_step + local_idx
        if apply_damage_event and (global_step == p.damage_step) and (not state.damaged):
            state.g[lattice.boundary_mask] *= p.damage_scale
            state.damaged = True

        metrics = _step(state, lattice, p, variant, global_step)

        time[local_idx] = global_step * p.dt
        total_current[local_idx] = metrics["total_current"]
        boundary_current[local_idx] = metrics["boundary_current"]
        boundary_fraction[local_idx] = metrics["boundary_fraction"]
        edge_bulk_ratio[local_idx] = metrics["edge_bulk_ratio"]
        coherence[local_idx] = metrics["coherence"]
        pi_a[local_idx] = metrics["pi_a"]
        state_scalar[local_idx] = metrics["state_scalar"]

        if global_step in snapshot_steps:
            key = str(global_step)
            snapshots_g_abs[key] = np.abs(state.g).copy()
            snapshots_j_abs[key] = metrics["j_abs"].copy()

    return SimulationResult(
        variant=variant.name,
        time=time,
        total_current=total_current,
        boundary_current=boundary_current,
        boundary_fraction=boundary_fraction,
        edge_bulk_ratio=edge_bulk_ratio,
        coherence=coherence,
        pi_a=pi_a,
        state_scalar=state_scalar,
        snapshots_g_abs=snapshots_g_abs,
        snapshots_j_abs=snapshots_j_abs,
        final_state=state.copy(),
    )
