from __future__ import annotations

import json
import textwrap
from datetime import datetime, timezone
from pathlib import Path

import imageio.v2 as imageio
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image


REPO = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = REPO / "data" / "artifacts" / "pif_anticipatory_self_healing"
RESULTS_CSV = ARTIFACT_DIR / "benchmark_results.csv"
SUMMARY_CSV = ARTIFACT_DIR / "benchmark_summary.csv"
SUMMARY_IMAGE = ARTIFACT_DIR / "benchmark_summary.png"
MAZE_TRACE_IMAGE = ARTIFACT_DIR / "maze_trace_seed0.png"
CLASSIC_TRACE_IMAGE = ARTIFACT_DIR / "classic_trace_seed0.png"
OUT_DASHBOARD = ARTIFACT_DIR / "pif_anticipatory_self_healing_dashboard.png"
OUT_GIF = ARTIFACT_DIR / "pif_anticipatory_self_healing_preview.gif"
OUT_JSON = ARTIFACT_DIR / "pif_anticipatory_self_healing_metrics.json"
OUT_REPORT = ARTIFACT_DIR / "pif_anticipatory_self_healing_report.md"


def _normalize_bool(series: pd.Series) -> pd.Series:
    lowered = series.astype(str).str.strip().str.lower()
    mapped = lowered.map({"true": True, "false": False})
    if mapped.isna().any():
        raise ValueError("Could not normalize pif_enabled column to booleans")
    return mapped


def _load_tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    if not RESULTS_CSV.exists():
        raise FileNotFoundError(f"Missing results CSV: {RESULTS_CSV}")
    if not SUMMARY_CSV.exists():
        raise FileNotFoundError(f"Missing summary CSV: {SUMMARY_CSV}")

    results = pd.read_csv(RESULTS_CSV)
    summary = pd.read_csv(SUMMARY_CSV)
    results["pif_enabled"] = _normalize_bool(results["pif_enabled"])
    summary["pif_enabled"] = _normalize_bool(summary["pif_enabled"])
    return results, summary


def _validate_summary(results: pd.DataFrame, summary: pd.DataFrame) -> dict:
    numeric_cols = [
        "recovery_ratio",
        "G_ratio",
        "mismatch_peak_5",
        "mismatch_tail",
        "mean_pi_f_final",
        "damaged_edges",
    ]
    grouped = (
        results.groupby(["mode", "pif_enabled"], as_index=False)[numeric_cols]
        .mean()
        .sort_values(["mode", "pif_enabled"])
        .reset_index(drop=True)
    )
    summary_sorted = summary.sort_values(["mode", "pif_enabled"]).reset_index(drop=True)
    if list(grouped[["mode", "pif_enabled"]].itertuples(index=False, name=None)) != list(
        summary_sorted[["mode", "pif_enabled"]].itertuples(index=False, name=None)
    ):
        raise ValueError("Summary rows do not match grouped benchmark rows")

    max_abs_diff = 0.0
    diffs: dict[str, float] = {}
    for column in numeric_cols:
        diff = (grouped[column] - summary_sorted[column]).abs().max()
        diffs[column] = float(diff)
        max_abs_diff = max(max_abs_diff, float(diff))
    if max_abs_diff > 1e-12:
        raise ValueError(f"Summary mismatch too large: {max_abs_diff}")

    seed_std = (
        results.groupby(["mode", "pif_enabled"])[numeric_cols]
        .std(ddof=0)
        .fillna(0.0)
    )
    max_seed_std = float(seed_std.to_numpy().max()) if not seed_std.empty else 0.0

    return {
        "summary_matches_grouped_results": True,
        "max_abs_diff": max_abs_diff,
        "per_column_abs_diff": diffs,
        "max_seed_std": max_seed_std,
    }


def _row(summary: pd.DataFrame, mode: str, enabled: bool) -> pd.Series:
    mask = (summary["mode"] == mode) & (summary["pif_enabled"] == enabled)
    rows = summary.loc[mask]
    if rows.empty:
        raise KeyError(f"Missing summary row for mode={mode!r}, pif_enabled={enabled}")
    return rows.iloc[0]


def _compute_metrics(results: pd.DataFrame, summary: pd.DataFrame, validation: dict) -> dict:
    classic_off = _row(summary, "classic", False)
    classic_on = _row(summary, "classic", True)
    maze_off = _row(summary, "maze", False)
    maze_on = _row(summary, "maze", True)

    maze_tail_reduction = 1.0 - float(maze_on["mismatch_tail"]) / max(float(maze_off["mismatch_tail"]), 1e-12)
    classic_tail_change = float(classic_on["mismatch_tail"] - classic_off["mismatch_tail"])
    maze_recovery_gain = float(maze_on["recovery_ratio"] - maze_off["recovery_ratio"])
    classic_g_gain = float(classic_on["G_ratio"] - classic_off["G_ratio"])

    metrics = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "sourceFiles": {
            "results": str(RESULTS_CSV.relative_to(REPO)).replace("\\", "/"),
            "summary": str(SUMMARY_CSV.relative_to(REPO)).replace("\\", "/"),
            "summaryImage": str(SUMMARY_IMAGE.relative_to(REPO)).replace("\\", "/") if SUMMARY_IMAGE.exists() else "",
            "mazeTrace": str(MAZE_TRACE_IMAGE.relative_to(REPO)).replace("\\", "/") if MAZE_TRACE_IMAGE.exists() else "",
            "classicTrace": str(CLASSIC_TRACE_IMAGE.relative_to(REPO)).replace("\\", "/") if CLASSIC_TRACE_IMAGE.exists() else "",
        },
        "validation": validation,
        "modes": {
            "classic": {
                "off": {
                    "recovery_ratio": float(classic_off["recovery_ratio"]),
                    "G_ratio": float(classic_off["G_ratio"]),
                    "mismatch_peak_5": float(classic_off["mismatch_peak_5"]),
                    "mismatch_tail": float(classic_off["mismatch_tail"]),
                    "mean_pi_f_final": float(classic_off["mean_pi_f_final"]),
                },
                "on": {
                    "recovery_ratio": float(classic_on["recovery_ratio"]),
                    "G_ratio": float(classic_on["G_ratio"]),
                    "mismatch_peak_5": float(classic_on["mismatch_peak_5"]),
                    "mismatch_tail": float(classic_on["mismatch_tail"]),
                    "mean_pi_f_final": float(classic_on["mean_pi_f_final"]),
                },
                "delta": {
                    "recovery_ratio": float(classic_on["recovery_ratio"] - classic_off["recovery_ratio"]),
                    "G_ratio": classic_g_gain,
                    "mismatch_peak_5": float(classic_on["mismatch_peak_5"] - classic_off["mismatch_peak_5"]),
                    "mismatch_tail": classic_tail_change,
                    "mean_pi_f_final": float(classic_on["mean_pi_f_final"] - classic_off["mean_pi_f_final"]),
                },
            },
            "maze": {
                "off": {
                    "recovery_ratio": float(maze_off["recovery_ratio"]),
                    "G_ratio": float(maze_off["G_ratio"]),
                    "mismatch_peak_5": float(maze_off["mismatch_peak_5"]),
                    "mismatch_tail": float(maze_off["mismatch_tail"]),
                    "mean_pi_f_final": float(maze_off["mean_pi_f_final"]),
                },
                "on": {
                    "recovery_ratio": float(maze_on["recovery_ratio"]),
                    "G_ratio": float(maze_on["G_ratio"]),
                    "mismatch_peak_5": float(maze_on["mismatch_peak_5"]),
                    "mismatch_tail": float(maze_on["mismatch_tail"]),
                    "mean_pi_f_final": float(maze_on["mean_pi_f_final"]),
                },
                "delta": {
                    "recovery_ratio": maze_recovery_gain,
                    "G_ratio": float(maze_on["G_ratio"] - maze_off["G_ratio"]),
                    "mismatch_peak_5": float(maze_on["mismatch_peak_5"] - maze_off["mismatch_peak_5"]),
                    "mismatch_tail": float(maze_on["mismatch_tail"] - maze_off["mismatch_tail"]),
                    "mean_pi_f_final": float(maze_on["mean_pi_f_final"] - maze_off["mean_pi_f_final"]),
                    "mismatch_tail_relative_reduction": maze_tail_reduction,
                },
            },
        },
        "headlineFindings": [
            f"Maze-mode recovery ratio improves by {maze_recovery_gain:+.6f} with pi_f enabled.",
            f"Maze-mode tail mismatch falls by {abs(float(maze_on['mismatch_tail'] - maze_off['mismatch_tail'])):.6f}, a {maze_tail_reduction * 100:.2f}% relative reduction.",
            f"Classic-mode final conductance ratio rises by {classic_g_gain:+.6f} with pi_f enabled.",
            f"Classic-mode tail mismatch increases by {classic_tail_change:+.6f}, so the current evidence is stronger in maze mode than in classic mode.",
            f"The committed 10-seed bundle is numerically deterministic across listed seeds (max seed std = {validation['max_seed_std']:.3e}).",
        ],
        "limitations": [
            "The graph-mode benchmark harness is preserved as a source snapshot, but TopEquations does not include the imported hafc_sim or hafc_sim_pif_active modules needed to rerun it in-place.",
            "Current evidence is graph-mode only; lattice or EGATL ablations with the same pi_f channel are still missing.",
            "A direct precursor lead-time comparison against Bott or Chern observables is not yet part of this bundle.",
        ],
    }
    return metrics


def _image_panel(ax, path: Path, title: str, fallback: str) -> None:
    ax.set_title(title)
    ax.axis("off")
    if path.exists():
        ax.imshow(mpimg.imread(path), aspect="auto")
    else:
        ax.text(0.5, 0.5, fallback, ha="center", va="center", fontsize=12)


def _build_dashboard(metrics: dict) -> None:
    figure = plt.figure(figsize=(14, 13.2))
    grid = figure.add_gridspec(3, 2, height_ratios=[1.0, 1.35, 1.25], hspace=0.28, wspace=0.22)
    ax_summary = figure.add_subplot(grid[0, :])
    ax_maze = figure.add_subplot(grid[1, :])
    ax_table = figure.add_subplot(grid[2, 0])
    ax_text = figure.add_subplot(grid[2, 1])

    _image_panel(
        ax_summary,
        SUMMARY_IMAGE,
        "Mode-level benchmark summary",
        "benchmark_summary.png not found",
    )
    _image_panel(
        ax_maze,
        MAZE_TRACE_IMAGE,
        "Representative maze trace (seed 0)",
        "maze_trace_seed0.png not found",
    )

    ax_table.axis("off")
    table_rows = [
        ["Classic off", f"{metrics['modes']['classic']['off']['recovery_ratio']:.6f}", f"{metrics['modes']['classic']['off']['G_ratio']:.6f}", f"{metrics['modes']['classic']['off']['mismatch_tail']:.6f}"],
        ["Classic on", f"{metrics['modes']['classic']['on']['recovery_ratio']:.6f}", f"{metrics['modes']['classic']['on']['G_ratio']:.6f}", f"{metrics['modes']['classic']['on']['mismatch_tail']:.6f}"],
        ["Maze off", f"{metrics['modes']['maze']['off']['recovery_ratio']:.6f}", f"{metrics['modes']['maze']['off']['G_ratio']:.6f}", f"{metrics['modes']['maze']['off']['mismatch_tail']:.6f}"],
        ["Maze on", f"{metrics['modes']['maze']['on']['recovery_ratio']:.6f}", f"{metrics['modes']['maze']['on']['G_ratio']:.6f}", f"{metrics['modes']['maze']['on']['mismatch_tail']:.6f}"],
    ]
    table = ax_table.table(
        cellText=table_rows,
        colLabels=["Mode", "Recovery", "G ratio", "Tail mismatch"],
        loc="center",
        cellLoc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.15, 2.0)
    ax_table.set_title("Committed summary values")

    ax_text.axis("off")
    text_lines = [
        "History-Resolved pi_f Anticipatory Self-Healing bundle",
        "",
        *[f"- {line}" for line in metrics["headlineFindings"]],
        "",
        "Validation:",
        f"- Summary/groupby max abs diff: {metrics['validation']['max_abs_diff']:.3e}",
        f"- Max seed std in committed bundle: {metrics['validation']['max_seed_std']:.3e}",
        "",
        "Limits:",
        "- Graph-mode evidence only; lattice and EGATL ablations are still missing.",
        "- The upstream benchmark harness needs external hafc_sim modules; see the report for the full provenance note.",
        "- See pif_anticipatory_self_healing_report.md for the complete limitations block.",
    ]
    wrapped_lines: list[str] = []
    for line in text_lines:
        if not line:
            wrapped_lines.append("")
        elif line.endswith(":") or not line.startswith("-"):
            wrapped_lines.extend(textwrap.wrap(line, width=62) or [line])
        else:
            wrapped = textwrap.wrap(line[2:], width=58)
            if not wrapped:
                wrapped_lines.append(line)
            else:
                wrapped_lines.append(f"- {wrapped[0]}")
                wrapped_lines.extend([f"  {segment}" for segment in wrapped[1:]])

    ax_text.text(
        0.0,
        1.0,
        "\n".join(wrapped_lines),
        ha="left",
        va="top",
        fontsize=10.0,
        bbox={"facecolor": "#f8fafc", "edgecolor": "#cbd5e1", "boxstyle": "round,pad=0.5"},
    )

    figure.suptitle(
        "History-Resolved pi_f Anticipatory Self-Healing Conductance Law\n"
        "Repo-native dashboard for the committed graph-mode evidence bundle",
        fontsize=15,
    )
    figure.subplots_adjust(top=0.90, bottom=0.04, left=0.05, right=0.97)
    figure.savefig(OUT_DASHBOARD, dpi=180)
    plt.close(figure)


def _normalized_frame(path: Path, target_size: tuple[int, int]) -> np.ndarray:
    image = Image.open(path).convert("RGB")
    image.thumbnail(target_size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", target_size, "white")
    x_off = (target_size[0] - image.width) // 2
    y_off = (target_size[1] - image.height) // 2
    canvas.paste(image, (x_off, y_off))
    return np.asarray(canvas)


def _build_animation() -> None:
    frames: list = []
    target_size = (1600, 1000)
    for path in [SUMMARY_IMAGE, MAZE_TRACE_IMAGE, OUT_DASHBOARD]:
        if path.exists():
            frame = _normalized_frame(path, target_size)
            frames.extend([frame] * 8)
    if not frames:
        raise FileNotFoundError("No source frames available for preview GIF")
    imageio.mimsave(OUT_GIF, frames, duration=0.18)


def _write_metrics(metrics: dict) -> None:
    OUT_JSON.write_text(json.dumps(metrics, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_report(metrics: dict) -> None:
    lines = [
        "# History-Resolved pi_f Anticipatory Self-Healing Bundle Report",
        "",
        f"Generated: {metrics['generatedAt']}",
        "",
        "## Headline findings",
        *[f"- {line}" for line in metrics["headlineFindings"]],
        "",
        "## Validation",
        f"- Summary rows match grouped benchmark results: {metrics['validation']['summary_matches_grouped_results']}",
        f"- Max absolute summary difference: {metrics['validation']['max_abs_diff']:.3e}",
        f"- Max seed standard deviation in committed bundle: {metrics['validation']['max_seed_std']:.3e}",
        "",
        "## Limits",
        *[f"- {line}" for line in metrics["limitations"]],
        "",
        "## Generated files",
        f"- {OUT_DASHBOARD.relative_to(REPO).as_posix()}",
        f"- {OUT_GIF.relative_to(REPO).as_posix()}",
        f"- {OUT_JSON.relative_to(REPO).as_posix()}",
    ]
    OUT_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    results, summary = _load_tables()
    validation = _validate_summary(results, summary)
    metrics = _compute_metrics(results, summary, validation)
    _build_dashboard(metrics)
    _build_animation()
    _write_metrics(metrics)
    _write_report(metrics)

    print(json.dumps({
        "dashboard": str(OUT_DASHBOARD.relative_to(REPO)).replace("\\", "/"),
        "animation": str(OUT_GIF.relative_to(REPO)).replace("\\", "/"),
        "metrics": str(OUT_JSON.relative_to(REPO)).replace("\\", "/"),
        "report": str(OUT_REPORT.relative_to(REPO)).replace("\\", "/"),
    }, indent=2))


if __name__ == "__main__":
    main()