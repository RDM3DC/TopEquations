from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.collections import LineCollection
from matplotlib.gridspec import GridSpec


REPO = Path(__file__).resolve().parents[1]
WORKSPACE = REPO.parent
EGATL_PATH = WORKSPACE / "AdaptiveCAD-Manim" / "solver" / "egatl.py"
ARTIFACT_DIR = REPO / "data" / "artifacts" / "flat_channel_loop_signature"


def _load_egatl_module():
    spec = importlib.util.spec_from_file_location("flat_channel_egatl", EGATL_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load EGATL module from {EGATL_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _cell_id(x: int, y: int, nx: int) -> int:
    return x + y * nx


def _bond_index(lattice) -> dict[tuple[int, int], tuple[int, int]]:
    index: dict[tuple[int, int], tuple[int, int]] = {}
    for edge_index, bond in enumerate(lattice.bonds):
        index[(bond.u, bond.v)] = (edge_index, 1)
        index[(bond.v, bond.u)] = (edge_index, -1)
    return index


def _path_to_edges(path_cells: list[int], edge_lookup: dict[tuple[int, int], tuple[int, int]]) -> list[tuple[int, int]]:
    edges: list[tuple[int, int]] = []
    for source_cell, target_cell in zip(path_cells[:-1], path_cells[1:]):
        key = (source_cell, target_cell)
        if key not in edge_lookup:
            raise KeyError(f"Missing bond for path segment {key}")
        edges.append(edge_lookup[key])
    return edges


def _boundary_loop(lattice) -> list[tuple[int, int]]:
    nx = lattice.nx
    ny = lattice.ny
    edge_lookup = _bond_index(lattice)

    path_cells: list[int] = []
    path_cells.extend(_cell_id(x, ny - 1, nx) for x in range(nx))
    path_cells.extend(_cell_id(nx - 1, y, nx) for y in range(ny - 2, -1, -1))
    path_cells.extend(_cell_id(x, 0, nx) for x in range(nx - 2, -1, -1))
    path_cells.extend(_cell_id(0, y, nx) for y in range(1, ny))

    return _path_to_edges(path_cells, edge_lookup)


def _top_strip_loop(lattice) -> list[tuple[int, int]]:
    nx = lattice.nx
    ny = lattice.ny
    edge_lookup = _bond_index(lattice)

    top_y = ny - 1
    inner_y = ny - 2
    path_cells: list[int] = []
    path_cells.extend(_cell_id(x, top_y, nx) for x in range(nx))
    path_cells.append(_cell_id(nx - 1, inner_y, nx))
    path_cells.extend(_cell_id(x, inner_y, nx) for x in range(nx - 2, -1, -1))
    path_cells.append(_cell_id(0, top_y, nx))

    return _path_to_edges(path_cells, edge_lookup)


def _central_plaquette_loop(lattice) -> list[tuple[int, int]]:
    nx = lattice.nx
    ny = lattice.ny
    edge_lookup = _bond_index(lattice)

    left_x = (nx - 2) // 2
    bottom_y = (ny - 2) // 2
    path_cells = [
        _cell_id(left_x, bottom_y, nx),
        _cell_id(left_x + 1, bottom_y, nx),
        _cell_id(left_x + 1, bottom_y + 1, nx),
        _cell_id(left_x, bottom_y + 1, nx),
        _cell_id(left_x, bottom_y, nx),
    ]
    return _path_to_edges(path_cells, edge_lookup)


def _loop_signature(edge_values: np.ndarray, pi_a_value: float, loop_edges: list[tuple[int, int]]) -> tuple[float, float]:
    edge_indices = np.array([edge_index for edge_index, _ in loop_edges], dtype=int)
    signs = np.array([sign for _, sign in loop_edges], dtype=float)

    magnitudes = np.abs(edge_values[edge_indices])
    geometric_mean = float(np.exp(np.mean(np.log(np.maximum(magnitudes, 1e-12)))))
    holonomy = float(np.sum(signs * np.angle(edge_values[edge_indices])))
    coherence = 0.5 * (1.0 + math.cos(holonomy / max(pi_a_value, 1e-12)))
    return geometric_mean * coherence, holonomy


def _compute_series(egatl, lattice, out: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    boundary_loop = _boundary_loop(lattice)
    top_strip_loop = _top_strip_loop(lattice)
    center_loop = _central_plaquette_loop(lattice)

    time_values = out["t"]
    g_history = out["g"]
    pi_history = out["pi_a"]
    step_count = len(time_values)

    boundary_signature = np.zeros(step_count)
    top_strip_signature = np.zeros(step_count)
    center_signature = np.zeros(step_count)
    boundary_holonomy = np.zeros(step_count)
    top_strip_holonomy = np.zeros(step_count)
    center_holonomy = np.zeros(step_count)

    for step_index in range(step_count):
        boundary_signature[step_index], boundary_holonomy[step_index] = _loop_signature(
            g_history[step_index], pi_history[step_index], boundary_loop
        )
        top_strip_signature[step_index], top_strip_holonomy[step_index] = _loop_signature(
            g_history[step_index], pi_history[step_index], top_strip_loop
        )
        center_signature[step_index], center_holonomy[step_index] = _loop_signature(
            g_history[step_index], pi_history[step_index], center_loop
        )

    transfer = np.array([
        egatl.effective_transfer(out["phi"][step_index], lattice.source_cell, lattice.sink_cell)
        for step_index in range(step_count)
    ])
    boundary_fraction = np.array([
        egatl.boundary_current_fraction(out["I_norm"][step_index], lattice.bonds)
        for step_index in range(step_count)
    ])
    top_edge_fraction = np.array([
        egatl.top_edge_fraction(out["I_norm"][step_index], lattice)
        for step_index in range(step_count)
    ])
    slip_density = egatl.slip_density(out["dW_e"])
    proxy_chern = egatl.proxy_chern_series(out["g"], lattice, nk=17)

    return {
        "boundary_signature": boundary_signature,
        "top_strip_signature": top_strip_signature,
        "center_signature": center_signature,
        "boundary_holonomy": boundary_holonomy,
        "top_strip_holonomy": top_strip_holonomy,
        "center_holonomy": center_holonomy,
        "transfer": transfer,
        "boundary_fraction": boundary_fraction,
        "top_edge_fraction": top_edge_fraction,
        "slip_density": slip_density,
        "proxy_chern": proxy_chern,
    }


def _segment_geometry(lattice) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    segments = []
    midpoints = []
    for bond in lattice.bonds:
        ux, uy = lattice.cell_xy[bond.u]
        vx, vy = lattice.cell_xy[bond.v]
        segments.append([(ux, uy), (vx, vy)])
        midpoints.append(((ux + vx) / 2.0, (uy + vy) / 2.0))
    cell_points = np.array([lattice.cell_xy[cell] for cell in sorted(lattice.cell_xy)])
    return np.array(segments, dtype=float), np.array(midpoints, dtype=float), cell_points


def _draw_network(ax, lattice, segments: np.ndarray, midpoints: np.ndarray, cell_points: np.ndarray,
                  edge_values: np.ndarray, damaged_edges: list[int], title: str, norm, cmap) -> None:
    magnitudes = np.abs(edge_values)
    collection = LineCollection(
        segments,
        colors=cmap(norm(magnitudes)),
        linewidths=1.5 + 4.0 * norm(magnitudes),
        alpha=0.95,
    )
    ax.add_collection(collection)
    if damaged_edges:
        ax.scatter(
            midpoints[damaged_edges, 0],
            midpoints[damaged_edges, 1],
            s=70,
            marker="x",
            color="#b91c1c",
            linewidths=1.5,
            label="damaged bonds",
        )
    ax.scatter(cell_points[:, 0], cell_points[:, 1], s=18, color="#111827", alpha=0.8)
    source_x, source_y = lattice.cell_xy[lattice.source_cell]
    sink_x, sink_y = lattice.cell_xy[lattice.sink_cell]
    ax.scatter([source_x], [source_y], s=70, color="#0f766e", marker="o", zorder=5)
    ax.scatter([sink_x], [sink_y], s=70, color="#9333ea", marker="s", zorder=5)
    ax.set_title(title, fontsize=11)
    ax.set_aspect("equal")
    ax.set_xlim(-0.5, lattice.nx - 0.5)
    ax.set_ylim(-0.5, lattice.ny - 0.5)
    ax.set_xticks(range(lattice.nx))
    ax.set_yticks(range(lattice.ny))
    ax.grid(alpha=0.12, linewidth=0.5)


def _write_timeseries_csv(path: Path, time_values: np.ndarray, out: dict[str, np.ndarray], series: dict[str, np.ndarray]) -> None:
    fieldnames = [
        "t",
        "top_strip_signature",
        "boundary_signature",
        "center_signature",
        "top_strip_holonomy",
        "boundary_holonomy",
        "center_holonomy",
        "transfer",
        "boundary_fraction",
        "top_edge_fraction",
        "slip_density",
        "proxy_chern",
        "entropy",
        "pi_a",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for step_index, time_value in enumerate(time_values):
            writer.writerow({
                "t": float(time_value),
                "top_strip_signature": float(series["top_strip_signature"][step_index]),
                "boundary_signature": float(series["boundary_signature"][step_index]),
                "center_signature": float(series["center_signature"][step_index]),
                "top_strip_holonomy": float(series["top_strip_holonomy"][step_index]),
                "boundary_holonomy": float(series["boundary_holonomy"][step_index]),
                "center_holonomy": float(series["center_holonomy"][step_index]),
                "transfer": float(series["transfer"][step_index]),
                "boundary_fraction": float(series["boundary_fraction"][step_index]),
                "top_edge_fraction": float(series["top_edge_fraction"][step_index]),
                "slip_density": float(series["slip_density"][step_index]),
                "proxy_chern": float(series["proxy_chern"][step_index]),
                "entropy": float(out["S"][step_index]),
                "pi_a": float(out["pi_a"][step_index]),
            })


def _summary_stats(time_values: np.ndarray, series: dict[str, np.ndarray], damage_time: float) -> dict[str, float | dict[str, float]]:
    pre_mask = (time_values >= max(0.0, damage_time - 2.0)) & (time_values < damage_time)
    post_mask = time_values >= (damage_time + 4.0)
    if not np.any(pre_mask):
        pre_mask = time_values < damage_time
    if not np.any(post_mask):
        post_mask = time_values >= damage_time

    def _window_mean(values: np.ndarray, mask: np.ndarray) -> float:
        return float(np.mean(values[mask])) if np.any(mask) else float(np.mean(values))

    def _drop_ratio(values: np.ndarray) -> float:
        pre_mean = _window_mean(values, pre_mask)
        post_min = float(np.min(values[time_values >= damage_time]))
        return post_min / max(pre_mean, 1e-12)

    damage_index = int(np.searchsorted(time_values, damage_time))

    def _damage_ratio(values: np.ndarray) -> float:
        pre_mean = _window_mean(values, pre_mask)
        return float(values[damage_index]) / max(pre_mean, 1e-12)

    return {
        "damage_time": damage_time,
        "damage_index": damage_index,
        "top_strip_pre": _window_mean(series["top_strip_signature"], pre_mask),
        "top_strip_at_damage": float(series["top_strip_signature"][damage_index]),
        "top_strip_post": _window_mean(series["top_strip_signature"], post_mask),
        "top_strip_min_post": float(np.min(series["top_strip_signature"][time_values >= damage_time])),
        "boundary_pre": _window_mean(series["boundary_signature"], pre_mask),
        "boundary_at_damage": float(series["boundary_signature"][damage_index]),
        "boundary_post": _window_mean(series["boundary_signature"], post_mask),
        "center_pre": _window_mean(series["center_signature"], pre_mask),
        "center_at_damage": float(series["center_signature"][damage_index]),
        "center_post": _window_mean(series["center_signature"], post_mask),
        "transfer_pre": _window_mean(series["transfer"], pre_mask),
        "transfer_at_damage": float(series["transfer"][damage_index]),
        "transfer_post": _window_mean(series["transfer"], post_mask),
        "top_edge_fraction_pre": _window_mean(series["top_edge_fraction"], pre_mask),
        "top_edge_fraction_at_damage": float(series["top_edge_fraction"][damage_index]),
        "top_edge_fraction_post": _window_mean(series["top_edge_fraction"], post_mask),
        "proxy_chern_pre": _window_mean(series["proxy_chern"], pre_mask),
        "proxy_chern_post": _window_mean(series["proxy_chern"], post_mask),
        "slip_density_post_mean": _window_mean(series["slip_density"], post_mask),
        "drop_ratios": {
            "top_strip_min_over_pre": _drop_ratio(series["top_strip_signature"]),
            "boundary_min_over_pre": _drop_ratio(series["boundary_signature"]),
            "center_min_over_pre": _drop_ratio(series["center_signature"]),
        },
        "damage_step_ratios": {
            "top_strip_over_pre": _damage_ratio(series["top_strip_signature"]),
            "boundary_over_pre": _damage_ratio(series["boundary_signature"]),
            "center_over_pre": _damage_ratio(series["center_signature"]),
        },
    }


def _build_dashboard(path: Path, lattice, out: dict[str, np.ndarray], series: dict[str, np.ndarray], summary: dict[str, float | dict[str, float]], damage_time: float, damaged_edges: list[int]) -> None:
    segments, midpoints, cell_points = _segment_geometry(lattice)
    magnitude_history = np.abs(out["g"])
    norm = plt.Normalize(vmin=float(np.min(magnitude_history)), vmax=float(np.max(magnitude_history)))
    cmap = plt.get_cmap("viridis")

    pre_index = int(np.searchsorted(out["t"], max(0.0, damage_time - 0.2)))
    post_index = len(out["t"]) - 1

    figure = plt.figure(figsize=(14, 10), constrained_layout=True)
    grid = GridSpec(2, 2, figure=figure, height_ratios=[1.0, 1.2])
    ax_pre = figure.add_subplot(grid[0, 0])
    ax_post = figure.add_subplot(grid[0, 1])
    ax_sig = figure.add_subplot(grid[1, 0])
    ax_recovery = figure.add_subplot(grid[1, 1])

    _draw_network(ax_pre, lattice, segments, midpoints, cell_points, out["g"][pre_index], damaged_edges,
                  f"Pre-damage conductance field (t={out['t'][pre_index]:.1f})", norm, cmap)
    _draw_network(ax_post, lattice, segments, midpoints, cell_points, out["g"][post_index], damaged_edges,
                  f"Late recovery conductance field (t={out['t'][post_index]:.1f})", norm, cmap)

    ax_sig.plot(out["t"], series["top_strip_signature"], label="Top-strip loop signature", color="#b45309", linewidth=2.4)
    ax_sig.plot(out["t"], series["boundary_signature"], label="Boundary loop signature", color="#0f766e", linewidth=2.0)
    ax_sig.plot(out["t"], series["center_signature"], label="Central plaquette signature", color="#4338ca", linewidth=2.0)
    ax_sig.axvline(damage_time, color="#991b1b", linestyle="--", linewidth=1.3, label="damage")
    ax_sig.set_title("Flat-channel loop signatures")
    ax_sig.set_xlabel("time")
    ax_sig.set_ylabel(r"$\Sigma_\Gamma^{(\pi_f)}$")
    ax_sig.grid(alpha=0.18)
    ax_sig.legend(frameon=False, loc="upper right")

    ax_recovery.plot(out["t"], series["transfer"], label="Transfer efficiency", color="#1d4ed8", linewidth=2.0)
    ax_recovery.plot(out["t"], series["top_edge_fraction"], label="Top-edge fraction", color="#7c3aed", linewidth=2.0)
    ax_recovery.plot(out["t"], series["proxy_chern"], label="Proxy Chern", color="#059669", linewidth=2.0)
    ax_recovery.plot(out["t"], series["slip_density"], label="Slip density", color="#dc2626", linewidth=1.8)
    ax_recovery.axvline(damage_time, color="#991b1b", linestyle="--", linewidth=1.3)
    ax_recovery.set_title("Recovery and topology metrics")
    ax_recovery.set_xlabel("time")
    ax_recovery.grid(alpha=0.18)
    ax_recovery.legend(frameon=False, loc="upper right")

    drop_ratios = summary["drop_ratios"]
    damage_step_ratios = summary["damage_step_ratios"]
    figure.suptitle(
        "Flat-Channel Loop Signature (pi_f Health Observable)\n"
        f"Damage-step/pre: top-strip = {damage_step_ratios['top_strip_over_pre']:.3f}, "
        f"boundary = {damage_step_ratios['boundary_over_pre']:.3f}, "
        f"center = {damage_step_ratios['center_over_pre']:.3f}"
        f"  |  min/pre: {drop_ratios['top_strip_min_over_pre']:.2e}, {drop_ratios['boundary_min_over_pre']:.2e}, {drop_ratios['center_min_over_pre']:.2e}",
        fontsize=14,
    )
    figure.savefig(path, dpi=180)
    plt.close(figure)


def _build_animation(path: Path, lattice, out: dict[str, np.ndarray], series: dict[str, np.ndarray], damage_time: float, damaged_edges: list[int]) -> None:
    segments, midpoints, cell_points = _segment_geometry(lattice)
    magnitude_history = np.abs(out["g"])
    norm = plt.Normalize(vmin=float(np.min(magnitude_history)), vmax=float(np.max(magnitude_history)))
    cmap = plt.get_cmap("viridis")

    frame_indices = list(range(0, len(out["t"]), 4))
    if frame_indices[-1] != len(out["t"]) - 1:
        frame_indices.append(len(out["t"]) - 1)

    figure = plt.figure(figsize=(11, 5.5), constrained_layout=True)
    grid = GridSpec(1, 2, figure=figure, width_ratios=[1.0, 1.35])
    ax_net = figure.add_subplot(grid[0, 0])
    ax_sig = figure.add_subplot(grid[0, 1])

    collection = LineCollection(segments, linewidths=np.full(len(lattice.bonds), 2.0), alpha=0.95)
    ax_net.add_collection(collection)
    if damaged_edges:
        ax_net.scatter(
            midpoints[damaged_edges, 0],
            midpoints[damaged_edges, 1],
            s=70,
            marker="x",
            color="#b91c1c",
            linewidths=1.5,
        )
    ax_net.scatter(cell_points[:, 0], cell_points[:, 1], s=18, color="#111827", alpha=0.8)
    source_x, source_y = lattice.cell_xy[lattice.source_cell]
    sink_x, sink_y = lattice.cell_xy[lattice.sink_cell]
    ax_net.scatter([source_x], [source_y], s=70, color="#0f766e", marker="o", zorder=5)
    ax_net.scatter([sink_x], [sink_y], s=70, color="#9333ea", marker="s", zorder=5)
    ax_net.set_title("Conductance field")
    ax_net.set_aspect("equal")
    ax_net.set_xlim(-0.5, lattice.nx - 0.5)
    ax_net.set_ylim(-0.5, lattice.ny - 0.5)
    ax_net.set_xticks(range(lattice.nx))
    ax_net.set_yticks(range(lattice.ny))
    ax_net.grid(alpha=0.12, linewidth=0.5)

    ax_sig.plot(out["t"], series["top_strip_signature"], label="Top-strip", color="#b45309", linewidth=2.4)
    ax_sig.plot(out["t"], series["boundary_signature"], label="Boundary", color="#0f766e", linewidth=2.0)
    ax_sig.plot(out["t"], series["center_signature"], label="Center", color="#4338ca", linewidth=2.0)
    ax_sig.plot(out["t"], series["proxy_chern"], label="Proxy Chern", color="#059669", linewidth=1.9)
    ax_sig.axvline(damage_time, color="#991b1b", linestyle="--", linewidth=1.2)
    time_cursor = ax_sig.axvline(out["t"][0], color="#111827", linewidth=1.2)
    info_text = ax_sig.text(
        0.02,
        0.98,
        "",
        transform=ax_sig.transAxes,
        ha="left",
        va="top",
        fontsize=10,
        bbox={"facecolor": "white", "alpha": 0.82, "edgecolor": "none"},
    )
    ax_sig.set_title("Loop signature response")
    ax_sig.set_xlabel("time")
    ax_sig.grid(alpha=0.18)
    ax_sig.legend(frameon=False, loc="upper right")

    def _update(frame_number: int):
        step_index = frame_indices[frame_number]
        magnitudes = np.abs(out["g"][step_index])
        collection.set_colors(cmap(norm(magnitudes)))
        collection.set_linewidths(1.5 + 4.0 * norm(magnitudes))
        time_value = float(out["t"][step_index])
        time_cursor.set_xdata([time_value, time_value])
        info_text.set_text(
            "\n".join([
                f"t = {time_value:.1f}",
                f"top-strip = {series['top_strip_signature'][step_index]:.3f}",
                f"boundary = {series['boundary_signature'][step_index]:.3f}",
                f"center = {series['center_signature'][step_index]:.3f}",
                f"transfer = {series['transfer'][step_index]:.3f}",
                f"proxy Chern = {series['proxy_chern'][step_index]:.3f}",
            ])
        )
        return collection, time_cursor, info_text

    animation = FuncAnimation(figure, _update, frames=len(frame_indices), interval=120, blit=False)
    animation.save(path, writer=PillowWriter(fps=8))
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate artifacts for the flat-channel loop signature equation")
    parser.add_argument("--nx", type=int, default=6)
    parser.add_argument("--ny", type=int, default=6)
    parser.add_argument("--T", type=float, default=6.0)
    parser.add_argument("--dt", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--damage-time", type=float, default=2.0)
    parser.add_argument("--mass", type=float, default=-1.0)
    args = parser.parse_args()

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    egatl = _load_egatl_module()
    lattice, out = egatl.run_recovery_protocol(
        nx=args.nx,
        ny=args.ny,
        T=args.T,
        dt=args.dt,
        seed=args.seed,
        damage_time=args.damage_time,
        mass=args.mass,
    )
    damaged_edges = egatl.top_edge_damage_bonds(lattice)
    series = _compute_series(egatl, lattice, out)
    summary = _summary_stats(out["t"], series, args.damage_time)

    metrics_path = ARTIFACT_DIR / "flat_channel_loop_metrics.json"
    csv_path = ARTIFACT_DIR / "flat_channel_loop_timeseries.csv"
    dashboard_path = ARTIFACT_DIR / "flat_channel_loop_dashboard.png"
    animation_path = ARTIFACT_DIR / "flat_channel_loop_damage.gif"

    metrics_payload = {
        "equationId": "eq-flat-channel-loop-signature-pi-f-health-observable",
        "generator": "tools/generate_flat_channel_loop_artifacts.py",
        "parameters": {
            "nx": args.nx,
            "ny": args.ny,
            "T": args.T,
            "dt": args.dt,
            "seed": args.seed,
            "damage_time": args.damage_time,
            "mass": args.mass,
        },
        "summary": summary,
    }
    metrics_path.write_text(json.dumps(metrics_payload, indent=2), encoding="utf-8")
    _write_timeseries_csv(csv_path, out["t"], out, series)
    _build_dashboard(dashboard_path, lattice, out, series, summary, args.damage_time, damaged_edges)
    _build_animation(animation_path, lattice, out, series, args.damage_time, damaged_edges)

    print(json.dumps(metrics_payload, indent=2))
    print(f"dashboard={dashboard_path}")
    print(f"animation={animation_path}")
    print(f"metrics={metrics_path}")
    print(f"timeseries={csv_path}")


if __name__ == "__main__":
    main()