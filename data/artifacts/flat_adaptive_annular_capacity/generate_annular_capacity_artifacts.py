from __future__ import annotations

import csv
import math
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
ROOT_OUT = REPO / "data" / "artifacts" / "flat_adaptive_annular_capacity"
DOCS_OUT = REPO / "docs" / "data" / "artifacts" / "flat_adaptive_annular_capacity"


def capacity(beta: float, a: float, b: float, lambda0: float = 1.0, r0: float = 1.0) -> float:
    if abs(beta) < 1e-12:
        return 2.0 * math.pi * lambda0 / math.log(b / a)
    return 2.0 * math.pi * lambda0 * (r0 ** (-beta)) * beta / (a ** (-beta) - b ** (-beta))


def profile(beta: float, r: float, a: float, b: float) -> float:
    if abs(beta) < 1e-12:
        return math.log(b / r) / math.log(b / a)
    return (r ** (-beta) - b ** (-beta)) / (a ** (-beta) - b ** (-beta))


def polyline(points: list[tuple[float, float]], color: str, width: float = 2.0) -> str:
    pts = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)
    return f"<polyline fill='none' stroke='{color}' stroke-width='{width}' points='{pts}' />"


def line(x1: float, y1: float, x2: float, y2: float, color: str = "#9aa7bd", width: float = 1.0, dash: str = "") -> str:
    dash_attr = f" stroke-dasharray='{dash}'" if dash else ""
    return f"<line x1='{x1:.2f}' y1='{y1:.2f}' x2='{x2:.2f}' y2='{y2:.2f}' stroke='{color}' stroke-width='{width}'{dash_attr} />"


def text(x: float, y: float, value: str, size: int = 16, weight: str = "400", fill: str = "#173052", anchor: str = "start") -> str:
    return (
        f"<text x='{x:.2f}' y='{y:.2f}' font-family='Georgia, Times New Roman, serif' "
        f"font-size='{size}' font-weight='{weight}' fill='{fill}' text-anchor='{anchor}'>{value}</text>"
    )


def build_svg(a: float = 1.0, b: float = 4.0) -> str:
    width = 1280
    height = 760
    left_x0, left_y0, left_w, left_h = 80, 170, 500, 430
    right_x0, right_y0, right_w, right_h = 690, 170, 500, 430

    beta_min, beta_max = -1.6, 2.6
    samples: list[tuple[float, float]] = []
    for idx in range(220):
        beta = beta_min + (beta_max - beta_min) * idx / 219
        if abs(beta) < 0.015:
            continue
        samples.append((beta, capacity(beta, a, b)))

    max_cap = max(y for _, y in samples) * 1.05
    min_cap = 0.0

    def map_left(beta: float, cap: float) -> tuple[float, float]:
        x = left_x0 + (beta - beta_min) / (beta_max - beta_min) * left_w
        y = left_y0 + left_h - (cap - min_cap) / (max_cap - min_cap) * left_h
        return x, y

    cap_points = [map_left(beta, cap) for beta, cap in samples]

    profiles = [
        (-1.0, "#b3541e", "beta = -1"),
        (0.0, "#2a6f97", "beta = 0"),
        (1.0, "#218380", "beta = 1"),
        (2.0, "#8f2d56", "beta = 2"),
    ]

    def map_right(r: float, val: float) -> tuple[float, float]:
        x = right_x0 + (r - a) / (b - a) * right_w
        y = right_y0 + right_h - val * right_h
        return x, y

    profile_polylines: list[str] = []
    legend_rows: list[str] = []
    for idx, (beta, color, label) in enumerate(profiles):
        pts = [map_right(a + (b - a) * k / 240, profile(beta, a + (b - a) * k / 240, a, b)) for k in range(241)]
        profile_polylines.append(polyline(pts, color, 3.0))
        ly = 620 + idx * 28
        legend_rows.append(line(720, ly - 6, 760, ly - 6, color, 4.0))
        legend_rows.append(text(775, ly, label, 18))

    grid: list[str] = []
    for beta_tick in [-1.0, 0.0, 1.0, 2.0]:
        x, _ = map_left(beta_tick, 0.0)
        grid.append(line(x, left_y0, x, left_y0 + left_h, "#d9e2f2", 1.0))
        grid.append(text(x, left_y0 + left_h + 28, f"{beta_tick:g}", 15, fill="#50627d", anchor="middle"))
    for frac in [0.0, 0.25, 0.5, 0.75, 1.0]:
        cap_tick = min_cap + frac * (max_cap - min_cap)
        _, y = map_left(beta_min, cap_tick)
        grid.append(line(left_x0, y, left_x0 + left_w, y, "#d9e2f2", 1.0))
        grid.append(text(left_x0 - 14, y + 5, f"{cap_tick:.2f}", 14, fill="#50627d", anchor="end"))

    zero_x, _ = map_left(0.0, 0.0)
    boundary_grid = [
        line(zero_x, left_y0, zero_x, left_y0 + left_h, "#c84b31", 2.0, "8 6"),
        text(zero_x, left_y0 - 16, "critical beta = 0", 16, "600", "#c84b31", "middle"),
    ]

    right_grid: list[str] = []
    for r_tick in [1.0, 2.0, 3.0, 4.0]:
        x, _ = map_right(r_tick, 0.0)
        right_grid.append(line(x, right_y0, x, right_y0 + right_h, "#d9e2f2", 1.0))
        right_grid.append(text(x, right_y0 + right_h + 28, f"{r_tick:g}", 15, fill="#50627d", anchor="middle"))
    for val_tick in [0.0, 0.25, 0.5, 0.75, 1.0]:
        _, y = map_right(a, val_tick)
        right_grid.append(line(right_x0, y, right_x0 + right_w, y, "#d9e2f2", 1.0))
        right_grid.append(text(right_x0 - 14, y + 5, f"{val_tick:.2f}", 14, fill="#50627d", anchor="end"))

    svg = f"""<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}' viewBox='0 0 {width} {height}'>
  <rect width='{width}' height='{height}' fill='#f5f1e8' />
  <rect x='24' y='24' width='{width - 48}' height='{height - 48}' rx='26' fill='#fffdf8' stroke='#e6dcc8' />
  {text(80, 80, 'Flat-Adaptive Annular Capacity Law', 34, '700', '#17263c')}
  {text(80, 112, 'Exact radial capacity and harmonic profile for the power-law flat branch', 20, '400', '#50627d')}

  <rect x='{left_x0 - 16}' y='{left_y0 - 36}' width='{left_w + 32}' height='{left_h + 64}' rx='22' fill='#fbf9f4' stroke='#d8cdb9' />
  {text(left_x0, left_y0 - 8, 'Capacity vs beta', 24, '700')}
  {''.join(grid)}
  {line(left_x0, left_y0 + left_h, left_x0 + left_w, left_y0 + left_h, '#8fa1bc', 1.5)}
  {line(left_x0, left_y0, left_x0, left_y0 + left_h, '#8fa1bc', 1.5)}
  {''.join(boundary_grid)}
  {polyline(cap_points, '#214e8a', 3.0)}
  {text(left_x0 + left_w / 2, left_y0 + left_h + 58, 'branch exponent beta', 18, '600', '#173052', 'middle')}
  {text(left_x0 - 58, left_y0 + left_h / 2, 'capacity', 18, '600', '#173052', 'middle')}

  <rect x='{right_x0 - 16}' y='{right_y0 - 36}' width='{right_w + 32}' height='{right_h + 64}' rx='22' fill='#fbf9f4' stroke='#d8cdb9' />
  {text(right_x0, right_y0 - 8, 'Exact harmonic profile on 1 < r < 4', 24, '700')}
  {''.join(right_grid)}
  {line(right_x0, right_y0 + right_h, right_x0 + right_w, right_y0 + right_h, '#8fa1bc', 1.5)}
  {line(right_x0, right_y0, right_x0, right_y0 + right_h, '#8fa1bc', 1.5)}
  {''.join(profile_polylines)}
  {text(right_x0 + right_w / 2, right_y0 + right_h + 58, 'radius r', 18, '600', '#173052', 'middle')}
  {text(right_x0 - 42, right_y0 + right_h / 2, 'u_beta(r)', 18, '600', '#173052', 'middle')}
  {''.join(legend_rows)}

  <rect x='80' y='642' width='560' height='78' rx='18' fill='#fff8e7' stroke='#e4c37a' />
  {text(98, 676, 'Exact law:', 20, '700', '#6c4d00')}
  {text(98, 704, 'C_f(a,b;beta) = 2*pi*lambda_0*r_0^(-beta)*beta / (a^(-beta)-b^(-beta)) with logarithmic beta->0 limit.', 16, '400', '#6c4d00')}

  <rect x='690' y='642' width='500' height='78' rx='18' fill='#edf6ff' stroke='#aac6ec' />
  {text(708, 676, 'Bridge:', 20, '700', '#1b4b80')}
  {text(708, 704, 'This turns d_eff = beta + 2 into an exact measurable annular transport observable.', 16, '400', '#1b4b80')}
</svg>
"""
    return svg


def main() -> None:
    ROOT_OUT.mkdir(parents=True, exist_ok=True)
    DOCS_OUT.mkdir(parents=True, exist_ok=True)

    csv_rows = []
    for idx in range(161):
        beta = -1.5 + 4.0 * idx / 160
        if abs(beta) < 1e-12:
            beta = 0.0
        csv_rows.append((beta, capacity(beta, 1.0, 4.0)))

    for out_dir in (ROOT_OUT, DOCS_OUT):
        svg_path = out_dir / "annular_capacity_profiles.svg"
        csv_path = out_dir / "annular_capacity_table.csv"
        svg_path.write_text(build_svg(), encoding="utf-8")
        with csv_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["beta", "capacity_a1_b4_lambda1_r01"])
            writer.writerows((f"{beta:.6f}", f"{cap:.12f}") for beta, cap in csv_rows)
        derivation_src = ROOT_OUT / "derivation_note.md"
        if derivation_src.exists() and out_dir is DOCS_OUT:
            (out_dir / "derivation_note.md").write_text(derivation_src.read_text(encoding="utf-8"), encoding="utf-8")

    print(f"wrote: {ROOT_OUT / 'annular_capacity_profiles.svg'}")
    print(f"wrote: {ROOT_OUT / 'annular_capacity_table.csv'}")
    print(f"mirrored: {DOCS_OUT}")


if __name__ == "__main__":
    main()