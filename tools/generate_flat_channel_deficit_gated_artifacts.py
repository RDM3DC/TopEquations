from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.gridspec import GridSpec


REPO = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO / "data" / "artifacts" / "flat_channel_loop_signature"
OUT_DIR = REPO / "data" / "artifacts" / "flat_channel_deficit_gated_self_healing"


def _load_metrics() -> dict:
    path = SOURCE_DIR / "flat_channel_loop_metrics.json"
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite metrics file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _load_timeseries() -> dict[str, np.ndarray]:
    path = SOURCE_DIR / "flat_channel_loop_timeseries.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite timeseries file: {path}")

    rows: dict[str, list[float]] = {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            for key, value in row.items():
                rows.setdefault(key, []).append(float(value))
    return {key: np.array(values, dtype=float) for key, values in rows.items()}


def _deficit(series: np.ndarray, reference: float) -> np.ndarray:
    return np.clip(1.0 - series / max(reference, 1e-12), 0.0, 1.0)


def _loop_segments(nx: int = 6, ny: int = 6) -> dict[str, list[tuple[tuple[float, float], tuple[float, float]]]]:
    boundary: list[tuple[tuple[float, float], tuple[float, float]]] = []
    top_strip: list[tuple[tuple[float, float], tuple[float, float]]] = []
    center: list[tuple[tuple[float, float], tuple[float, float]]] = []

    for x in range(nx - 1):
        boundary.append(((x, ny - 1), (x + 1, ny - 1)))
        boundary.append(((x, 0), (x + 1, 0)))
        top_strip.append(((x, ny - 1), (x + 1, ny - 1)))
        top_strip.append(((x + 1, ny - 2), (x, ny - 2)))
    for y in range(ny - 1):
        boundary.append(((0, y), (0, y + 1)))
        boundary.append(((nx - 1, y), (nx - 1, y + 1)))
    top_strip.append(((0, ny - 2), (0, ny - 1)))
    top_strip.append(((nx - 1, ny - 1), (nx - 1, ny - 2)))

    cx = (nx - 2) // 2
    cy = (ny - 2) // 2
    center.extend(
        [
            ((cx, cy), (cx + 1, cy)),
            ((cx + 1, cy), (cx + 1, cy + 1)),
            ((cx + 1, cy + 1), (cx, cy + 1)),
            ((cx, cy + 1), (cx, cy)),
        ]
    )
    return {"boundary": boundary, "top_strip": top_strip, "center": center}


def _draw_grid(ax, nx: int = 6, ny: int = 6) -> None:
    for x in range(nx):
        ax.plot([x, x], [0, ny - 1], color="#d1d5db", linewidth=0.6, zorder=0)
    for y in range(ny):
        ax.plot([0, nx - 1], [y, y], color="#d1d5db", linewidth=0.6, zorder=0)
    xx, yy = np.meshgrid(np.arange(nx), np.arange(ny))
    ax.scatter(xx.flatten(), yy.flatten(), s=18, color="#111827", alpha=0.75, zorder=1)
    ax.set_xlim(-0.5, nx - 0.5)
    ax.set_ylim(-0.5, ny - 0.5)
    ax.set_aspect("equal")
    ax.set_xticks(range(nx))
    ax.set_yticks(range(ny))
    ax.grid(alpha=0.08)


def _plot_segments(ax, segments, color: str, alpha: float, linewidth: float, label: str | None = None) -> None:
    first = True
    for (x0, y0), (x1, y1) in segments:
        kwargs = {"color": color, "alpha": alpha, "linewidth": linewidth, "zorder": 3}
        if label and first:
            kwargs["label"] = label
            first = False
        ax.plot([x0, x1], [y0, y1], **kwargs)


def _build_dashboard(path: Path, metrics: dict, series: dict[str, np.ndarray]) -> None:
    summary = metrics["summary"]
    time_values = series["t"]
    top_deficit = _deficit(series["top_strip_signature"], summary["top_strip_pre"])
    boundary_deficit = _deficit(series["boundary_signature"], summary["boundary_pre"])
    center_deficit = _deficit(series["center_signature"], summary["center_pre"])
    damage_time = summary["damage_time"]
    damage_index = int(summary["damage_index"])
    segments = _loop_segments()

    figure = plt.figure(figsize=(14, 10), constrained_layout=True)
    grid = GridSpec(2, 2, figure=figure)
    ax_map = figure.add_subplot(grid[0, 0])
    ax_sig = figure.add_subplot(grid[0, 1])
    ax_def = figure.add_subplot(grid[1, 0])
    ax_bar = figure.add_subplot(grid[1, 1])

    _draw_grid(ax_map)
    _plot_segments(ax_map, segments["boundary"], "#0f766e", 0.35, 2.0, label="Boundary loop")
    _plot_segments(ax_map, segments["top_strip"], "#b45309", 0.85, 3.0, label="Top-strip loop")
    _plot_segments(ax_map, segments["center"], "#4338ca", 0.85, 3.0, label="Central plaquette")
    ax_map.set_title("Monitored loops for the deficit gate")
    ax_map.legend(frameon=False, loc="lower left")

    ax_sig.plot(time_values, series["top_strip_signature"], color="#b45309", linewidth=2.4, label="Top-strip signature")
    ax_sig.plot(time_values, series["boundary_signature"], color="#0f766e", linewidth=2.0, label="Boundary signature")
    ax_sig.plot(time_values, series["center_signature"], color="#4338ca", linewidth=2.0, label="Center signature")
    ax_sig.axvline(damage_time, color="#991b1b", linestyle="--", linewidth=1.2)
    ax_sig.set_title("Observed flat-channel signatures")
    ax_sig.set_xlabel("time")
    ax_sig.set_ylabel("Sigma_Gamma^(pi_f)")
    ax_sig.grid(alpha=0.18)
    ax_sig.legend(frameon=False, loc="upper right")

    ax_def.plot(time_values, top_deficit, color="#b45309", linewidth=2.4, label="Top-strip deficit")
    ax_def.plot(time_values, boundary_deficit, color="#0f766e", linewidth=2.0, label="Boundary deficit")
    ax_def.plot(time_values, center_deficit, color="#4338ca", linewidth=2.0, label="Center deficit")
    ax_def.axvline(damage_time, color="#991b1b", linestyle="--", linewidth=1.2)
    ax_def.set_title("Deficit gate D_Gamma(t)")
    ax_def.set_xlabel("time")
    ax_def.set_ylabel("Deficit gate")
    ax_def.set_ylim(-0.02, 1.02)
    ax_def.grid(alpha=0.18)
    ax_def.legend(frameon=False, loc="lower right")

    labels = ["Top strip", "Boundary", "Center"]
    values = [top_deficit[damage_index], boundary_deficit[damage_index], center_deficit[damage_index]]
    colors = ["#b45309", "#0f766e", "#4338ca"]
    bars = ax_bar.bar(labels, values, color=colors)
    ax_bar.set_ylim(0.0, 1.05)
    ax_bar.set_title("Damage-step repair activation")
    ax_bar.set_ylabel("D_Gamma(t_damage)")
    ax_bar.grid(axis="y", alpha=0.18)
    for bar, value in zip(bars, values):
        ax_bar.text(bar.get_x() + bar.get_width() / 2.0, value + 0.02, f"{value:.3f}", ha="center", va="bottom")
    ax_bar.text(
        0.02,
        0.98,
        "Extra term vanishes when chi_Gamma = 0\nor D_Gamma = 0, so the law recovers\nthe base EGATL phase-coupled conductance update.",
        transform=ax_bar.transAxes,
        ha="left",
        va="top",
        fontsize=10,
        bbox={"facecolor": "white", "alpha": 0.82, "edgecolor": "none"},
    )

    figure.suptitle(
        "Flat-Channel Deficit-Gated Self-Healing Law\n"
        f"Damage-step deficits: top strip = {values[0]:.3f}, boundary = {values[1]:.3f}, center = {values[2]:.3f}",
        fontsize=14,
    )
    figure.savefig(path, dpi=180)
    plt.close(figure)


def _build_animation(path: Path, metrics: dict, series: dict[str, np.ndarray]) -> None:
    summary = metrics["summary"]
    time_values = series["t"]
    top_deficit = _deficit(series["top_strip_signature"], summary["top_strip_pre"])
    boundary_deficit = _deficit(series["boundary_signature"], summary["boundary_pre"])
    center_deficit = _deficit(series["center_signature"], summary["center_pre"])
    damage_time = summary["damage_time"]
    segments = _loop_segments()
    frame_indices = list(range(0, len(time_values), 2))
    if frame_indices[-1] != len(time_values) - 1:
        frame_indices.append(len(time_values) - 1)

    figure = plt.figure(figsize=(11, 5.5), constrained_layout=True)
    grid = GridSpec(1, 2, figure=figure, width_ratios=[1.0, 1.3])
    ax_map = figure.add_subplot(grid[0, 0])
    ax_def = figure.add_subplot(grid[0, 1])

    _draw_grid(ax_map)
    ax_map.set_title("Loop-health deficit activation")
    boundary_lines = [ax_map.plot([], [], color="#0f766e", linewidth=2.0, alpha=0.2)[0] for _ in segments["boundary"]]
    top_lines = [ax_map.plot([], [], color="#b45309", linewidth=3.2, alpha=0.2)[0] for _ in segments["top_strip"]]
    center_lines = [ax_map.plot([], [], color="#4338ca", linewidth=3.0, alpha=0.2)[0] for _ in segments["center"]]
    for line, segment in zip(boundary_lines, segments["boundary"]):
        (x0, y0), (x1, y1) = segment
        line.set_data([x0, x1], [y0, y1])
    for line, segment in zip(top_lines, segments["top_strip"]):
        (x0, y0), (x1, y1) = segment
        line.set_data([x0, x1], [y0, y1])
    for line, segment in zip(center_lines, segments["center"]):
        (x0, y0), (x1, y1) = segment
        line.set_data([x0, x1], [y0, y1])

    ax_def.plot(time_values, top_deficit, color="#b45309", linewidth=2.4, label="Top-strip deficit")
    ax_def.plot(time_values, boundary_deficit, color="#0f766e", linewidth=2.0, label="Boundary deficit")
    ax_def.plot(time_values, center_deficit, color="#4338ca", linewidth=2.0, label="Center deficit")
    ax_def.axvline(damage_time, color="#991b1b", linestyle="--", linewidth=1.2)
    cursor = ax_def.axvline(time_values[0], color="#111827", linewidth=1.2)
    info = ax_def.text(
        0.02,
        0.98,
        "",
        transform=ax_def.transAxes,
        ha="left",
        va="top",
        fontsize=10,
        bbox={"facecolor": "white", "alpha": 0.82, "edgecolor": "none"},
    )
    ax_def.set_ylim(-0.02, 1.02)
    ax_def.set_xlabel("time")
    ax_def.set_ylabel("Deficit gate")
    ax_def.set_title("Repair gate turns on when loop health collapses")
    ax_def.grid(alpha=0.18)
    ax_def.legend(frameon=False, loc="lower right")

    def _update(frame_number: int):
        index = frame_indices[frame_number]
        for line in boundary_lines:
            line.set_alpha(0.15 + 0.85 * boundary_deficit[index])
        for line in top_lines:
            line.set_alpha(0.15 + 0.85 * top_deficit[index])
        for line in center_lines:
            line.set_alpha(0.15 + 0.85 * center_deficit[index])
        time_value = float(time_values[index])
        cursor.set_xdata([time_value, time_value])
        info.set_text(
            "\n".join(
                [
                    f"t = {time_value:.1f}",
                    f"D_top = {top_deficit[index]:.3f}",
                    f"D_boundary = {boundary_deficit[index]:.3f}",
                    f"D_center = {center_deficit[index]:.3f}",
                ]
            )
        )
        return boundary_lines + top_lines + center_lines + [cursor, info]

    animation = FuncAnimation(figure, _update, frames=len(frame_indices), interval=120, blit=False)
    animation.save(path, writer=PillowWriter(fps=8))
    plt.close(figure)


def _write_timeseries(path: Path, series: dict[str, np.ndarray], metrics: dict) -> None:
    summary = metrics["summary"]
    top_deficit = _deficit(series["top_strip_signature"], summary["top_strip_pre"])
    boundary_deficit = _deficit(series["boundary_signature"], summary["boundary_pre"])
    center_deficit = _deficit(series["center_signature"], summary["center_pre"])
    fieldnames = [
        "t",
        "top_strip_signature",
        "boundary_signature",
        "center_signature",
        "top_strip_deficit",
        "boundary_deficit",
        "center_deficit",
        "transfer",
        "top_edge_fraction",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for idx, time_value in enumerate(series["t"]):
            writer.writerow(
                {
                    "t": float(time_value),
                    "top_strip_signature": float(series["top_strip_signature"][idx]),
                    "boundary_signature": float(series["boundary_signature"][idx]),
                    "center_signature": float(series["center_signature"][idx]),
                    "top_strip_deficit": float(top_deficit[idx]),
                    "boundary_deficit": float(boundary_deficit[idx]),
                    "center_deficit": float(center_deficit[idx]),
                    "transfer": float(series["transfer"][idx]),
                    "top_edge_fraction": float(series["top_edge_fraction"][idx]),
                }
            )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    metrics = _load_metrics()
    series = _load_timeseries()
    summary = metrics["summary"]
    top_deficit = _deficit(series["top_strip_signature"], summary["top_strip_pre"])
    boundary_deficit = _deficit(series["boundary_signature"], summary["boundary_pre"])
    center_deficit = _deficit(series["center_signature"], summary["center_pre"])
    damage_index = int(summary["damage_index"])

    out_metrics = {
        "equationId": "eq-flat-channel-deficit-gated-self-healing-law",
        "generator": "tools/generate_flat_channel_deficit_gated_artifacts.py",
        "sourceArtifact": "data/artifacts/flat_channel_loop_signature/flat_channel_loop_timeseries.csv",
        "summary": {
            "damage_time": float(summary["damage_time"]),
            "damage_index": damage_index,
            "top_strip_deficit_at_damage": float(top_deficit[damage_index]),
            "boundary_deficit_at_damage": float(boundary_deficit[damage_index]),
            "center_deficit_at_damage": float(center_deficit[damage_index]),
            "top_strip_signature_at_damage": float(series["top_strip_signature"][damage_index]),
            "boundary_signature_at_damage": float(series["boundary_signature"][damage_index]),
            "center_signature_at_damage": float(series["center_signature"][damage_index]),
            "transfer_pre": float(summary["transfer_pre"]),
            "transfer_post": float(summary["transfer_post"]),
            "exact_recovery_conditions": [
                "chi_Gamma = 0 removes the deficit-gated repair term exactly.",
                "D_Gamma(t) = 0 when the monitored loop stays at its reference signature, so the law reduces to the base EGATL phase-coupled conductance update.",
            ],
        },
    }

    dashboard_path = OUT_DIR / "flat_channel_deficit_gate_dashboard.png"
    animation_path = OUT_DIR / "flat_channel_deficit_gate_activation.gif"
    metrics_path = OUT_DIR / "flat_channel_deficit_gate_metrics.json"
    timeseries_path = OUT_DIR / "flat_channel_deficit_gate_timeseries.csv"

    _build_dashboard(dashboard_path, metrics, series)
    _build_animation(animation_path, metrics, series)
    _write_timeseries(timeseries_path, series, metrics)
    metrics_path.write_text(json.dumps(out_metrics, indent=2), encoding="utf-8")

    print(json.dumps(out_metrics, indent=2))
    print(f"dashboard={dashboard_path}")
    print(f"animation={animation_path}")
    print(f"metrics={metrics_path}")
    print(f"timeseries={timeseries_path}")


if __name__ == "__main__":
    main()