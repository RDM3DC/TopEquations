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
    parser = argparse.ArgumentParser(description="Run the Adaptive Chern self-healing recovery demo.")
    parser.add_argument("--config", type=str, default=None, help="Optional JSON/YAML config file.")
    parser.add_argument("--outdir", type=str, default="outputs/recovery_demo", help="Output directory.")
    parser.add_argument("--nx", type=int, default=8)
    parser.add_argument("--ny", type=int, default=8)
    return parser.parse_args()


def recovery_time(time: np.ndarray, trace: np.ndarray, damage_time: float, target_value: float, sustain_steps: int = 8) -> float | None:
    post = np.where(time >= damage_time)[0]
    if len(post) == 0:
        return None
    mask = trace[post] >= target_value
    run = 0
    for offset, ok in enumerate(mask):
        run = run + 1 if ok else 0
        if run >= sustain_steps:
            idx = post[offset - sustain_steps + 1]
            return float(time[idx] - damage_time)
    return None


def save_csv(path: Path, results: dict[str, dict[str, np.ndarray]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    variants = list(results.keys())
    time = results[variants[0]]["time"]
    with path.open("w", newline="") as f:
        writer = csv.writer(f)
        header = ["time"]
        for name in variants:
            header.extend([
                f"{name}_boundary_fraction",
                f"{name}_transfer_efficiency",
                f"{name}_edge_bulk_ratio",
                f"{name}_coherence",
            ])
        writer.writerow(header)
        for i, t in enumerate(time):
            row = [float(t)]
            for name in variants:
                row.extend([
                    float(results[name]["boundary_fraction"][i]),
                    float(results[name]["transfer_efficiency"][i]),
                    float(results[name]["edge_bulk_ratio"][i]),
                    float(results[name]["coherence"][i]),
                ])
            writer.writerow(row)


def plot_snapshot_panel(lattice: EdgeLattice, values: np.ndarray, title: str, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(5.2, 4.8))
    sc = ax.scatter(lattice.edge_midpoints[:, 0], lattice.edge_midpoints[:, 1], c=values, s=55, cmap="viridis")
    ax.set_title(title)
    ax.set_aspect("equal")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    fig.colorbar(sc, ax=ax, label="|g_e|")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def main() -> None:
    args = parse_args()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    config = load_mapping(args.config)
    model_cfg = config.get("model", config)
    params = apply_overrides(ModelParams(), model_cfg)

    lattice = EdgeLattice.square(nx=args.nx, ny=args.ny)
    variants = default_variants()
    snapshot_steps = [0, params.damage_step, params.steps - 1]
    raw_results = {}

    for variant in variants:
        result = simulate(
            lattice=lattice,
            p=params,
            variant=variant,
            state=initial_state(lattice, params),
            snapshot_steps=snapshot_steps,
        )
        raw_results[variant.name] = result

    full = raw_results["full_law"]
    pre_mask = (full.time >= (params.damage_step - 25) * params.dt) & (full.time < params.damage_step * params.dt)
    pre_total_ref = float(np.mean(full.total_current[pre_mask]))
    pre_boundary_ref = float(np.mean(full.boundary_fraction[pre_mask]))
    damage_time = params.damage_step * params.dt
    target_boundary = params.recovery_target_fraction * pre_boundary_ref

    results_for_export: dict[str, dict[str, np.ndarray]] = {}
    summary: dict[str, object] = {
        "damage_time": damage_time,
        "pre_total_ref": pre_total_ref,
        "pre_boundary_ref": pre_boundary_ref,
        "target_boundary_fraction": target_boundary,
        "variants": {},
    }

    for name, result in raw_results.items():
        transfer_efficiency = result.total_current / max(pre_total_ref, 1e-9)
        t_recover = recovery_time(result.time, result.boundary_fraction, damage_time, target_boundary)
        results_for_export[name] = {
            "time": result.time,
            "boundary_fraction": result.boundary_fraction,
            "transfer_efficiency": transfer_efficiency,
            "edge_bulk_ratio": result.edge_bulk_ratio,
            "coherence": result.coherence,
        }
        summary["variants"][name] = {
            "recovery_time": t_recover,
            "final_boundary_fraction": float(result.boundary_fraction[-1]),
            "final_transfer_efficiency": float(transfer_efficiency[-1]),
            "final_edge_bulk_ratio": float(result.edge_bulk_ratio[-1]),
            "final_coherence": float(result.coherence[-1]),
        }

    save_csv(outdir / "recovery_traces.csv", results_for_export)
    (outdir / "summary.json").write_text(json.dumps(summary, indent=2))

    fig, axes = plt.subplots(2, 2, figsize=(12, 8), sharex=True)
    for name, export in results_for_export.items():
        axes[0, 0].plot(export["time"], export["boundary_fraction"], label=name, linewidth=2.0)
        axes[0, 1].plot(export["time"], export["transfer_efficiency"], label=name, linewidth=2.0)
        axes[1, 0].plot(export["time"], export["edge_bulk_ratio"], label=name, linewidth=2.0)

    full_gap = results_for_export["full_law"]["boundary_fraction"] - results_for_export["principal_branch"]["boundary_fraction"]
    axes[1, 1].plot(results_for_export["full_law"]["time"], full_gap, linewidth=2.2, label="memory_gap = full_law - principal_branch")

    for ax in axes.flat:
        ax.axvline(damage_time, linestyle="--", linewidth=1.4)
        ax.grid(alpha=0.25)

    axes[0, 0].set_title("Boundary-current fraction")
    axes[0, 1].set_title("Transfer efficiency (normalized)")
    axes[1, 0].set_title("Edge / bulk conductance ratio")
    axes[1, 1].set_title("Full-law memory gap vs principal branch")
    axes[0, 0].set_ylabel("fraction")
    axes[0, 1].set_ylabel("normalized total current")
    axes[1, 0].set_ylabel("ratio")
    axes[1, 1].set_ylabel("boundary-fraction gap")
    axes[1, 0].set_xlabel("time")
    axes[1, 1].set_xlabel("time")
    for ax in axes.flat:
        ax.legend(loc="best", fontsize=8)

    fig.tight_layout()
    fig.savefig(outdir / "recovery_traces.png", dpi=180)
    plt.close(fig)

    for step in snapshot_steps:
        key = str(step)
        label = "healthy" if step == 0 else "damaged" if step == params.damage_step else "recovered"
        plot_snapshot_panel(
            lattice=lattice,
            values=full.snapshots_g_abs[key],
            title=f"full_law |g_e| snapshot: {label} (step={step})",
            path=outdir / f"snapshot_{label}.png",
        )

    print(f"[done] wrote recovery demo artifacts to: {outdir}")


if __name__ == "__main__":
    main()
