from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from arp_topology.laws import (
    EdgeLattice,
    ModelParams,
    apply_overrides,
    default_variants,
    initial_state,
    load_mapping,
    simulate,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run matched-present ablations from a common damaged snapshot.")
    parser.add_argument("--config", type=str, default=None, help="Optional JSON/YAML config file.")
    parser.add_argument("--outdir", type=str, default="outputs/matched_present", help="Output directory.")
    parser.add_argument("--nx", type=int, default=8)
    parser.add_argument("--ny", type=int, default=8)
    return parser.parse_args()


def recovery_time(time: np.ndarray, trace: np.ndarray, t0: float, target_value: float, sustain_steps: int = 8) -> float | None:
    post = np.where(time >= t0)[0]
    if len(post) == 0:
        return None
    mask = trace[post] >= target_value
    run = 0
    for offset, ok in enumerate(mask):
        run = run + 1 if ok else 0
        if run >= sustain_steps:
            idx = post[offset - sustain_steps + 1]
            return float(time[idx] - t0)
    return None


def write_table(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    keys = list(rows[0].keys())
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    config = load_mapping(args.config)
    model_cfg = config.get("model", config)
    params = apply_overrides(ModelParams(), model_cfg)

    lattice = EdgeLattice.square(nx=args.nx, ny=args.ny)
    variants = default_variants()
    full_variant = next(v for v in variants if v.name == "full_law")

    warmup = simulate(
        lattice=lattice,
        p=params,
        variant=full_variant,
        state=initial_state(lattice, params),
        steps=params.damage_step + 1,
        starting_step=0,
        apply_damage_event=True,
        snapshot_steps=[params.damage_step],
    )

    shared_state = warmup.final_state.copy()
    horizon_steps = params.steps - (params.damage_step + 1)
    t0 = (params.damage_step + 1) * params.dt

    pre_mask = (warmup.time >= (params.damage_step - 25) * params.dt) & (warmup.time < params.damage_step * params.dt)
    pre_total_ref = float(np.mean(warmup.total_current[pre_mask]))
    pre_boundary_ref = float(np.mean(warmup.boundary_fraction[pre_mask]))
    target_boundary = params.recovery_target_fraction * pre_boundary_ref

    branched_results = {}
    rows: list[dict[str, object]] = []

    for variant in variants:
        result = simulate(
            lattice=lattice,
            p=params,
            variant=variant,
            state=shared_state,
            steps=horizon_steps,
            starting_step=params.damage_step + 1,
            apply_damage_event=False,
            snapshot_steps=[params.steps - 1],
        )
        branched_results[variant.name] = result

        transfer_eff = result.total_current / max(pre_total_ref, 1e-9)
        t_recover = recovery_time(result.time, result.boundary_fraction, t0, target_boundary)
        rows.append(
            {
                "variant": variant.name,
                "recovery_time": t_recover,
                "final_boundary_fraction": float(result.boundary_fraction[-1]),
                "final_transfer_efficiency": float(transfer_eff[-1]),
                "final_edge_bulk_ratio": float(result.edge_bulk_ratio[-1]),
                "final_coherence": float(result.coherence[-1]),
            }
        )

    write_table(outdir / "matched_present_summary.csv", rows)
    (outdir / "matched_present_summary.json").write_text(json.dumps(rows, indent=2))

    full = branched_results["full_law"]
    principal = branched_results["principal_branch"]
    memory_gap = full.boundary_fraction - principal.boundary_fraction

    fig, axes = plt.subplots(1, 3, figsize=(14, 4.6))
    for name, result in branched_results.items():
        transfer_eff = result.total_current / max(pre_total_ref, 1e-9)
        axes[0].plot(result.time, result.boundary_fraction, linewidth=2.0, label=name)
        axes[1].plot(result.time, transfer_eff, linewidth=2.0, label=name)

    axes[2].plot(full.time, memory_gap, linewidth=2.2, label="full - principal_branch")

    for ax in axes:
        ax.axvline(t0, linestyle="--", linewidth=1.4)
        ax.grid(alpha=0.25)
        ax.set_xlabel("time")

    axes[0].set_title("Matched-present boundary fraction")
    axes[0].set_ylabel("fraction")
    axes[1].set_title("Matched-present transfer efficiency")
    axes[1].set_ylabel("normalized total current")
    axes[2].set_title("Memory gap after common damaged snapshot")
    axes[2].set_ylabel("boundary-fraction gap")
    for ax in axes:
        ax.legend(loc="best", fontsize=8)

    fig.tight_layout()
    fig.savefig(outdir / "matched_present_traces.png", dpi=180)
    plt.close(fig)

    print(f"[done] wrote matched-present artifacts to: {outdir}")


if __name__ == "__main__":
    main()
