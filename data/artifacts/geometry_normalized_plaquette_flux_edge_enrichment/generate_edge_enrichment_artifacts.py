from __future__ import annotations

from html import escape
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
OUT_DIR = REPO / "data" / "artifacts" / "geometry_normalized_plaquette_flux_edge_enrichment"
DOCS_OUT_DIR = REPO / "docs" / "data" / "artifacts" / "geometry_normalized_plaquette_flux_edge_enrichment"


def text(x: float, y: float, value: str, size: int = 16, weight: str = "400", fill: str = "#173052", anchor: str = "start") -> str:
    return (
        f"<text x='{x:.2f}' y='{y:.2f}' font-family='Georgia, Times New Roman, serif' "
        f"font-size='{size}' font-weight='{weight}' fill='{fill}' text-anchor='{anchor}'>{escape(value, quote=False)}</text>"
    )


def line(x1: float, y1: float, x2: float, y2: float, color: str = "#9aa7bd", width: float = 1.0, dash: str = "") -> str:
    dash_attr = f" stroke-dasharray='{dash}'" if dash else ""
    return f"<line x1='{x1:.2f}' y1='{y1:.2f}' x2='{x2:.2f}' y2='{y2:.2f}' stroke='{color}' stroke-width='{width}'{dash_attr} />"


def rect(x: float, y: float, w: float, h: float, fill: str, stroke: str, rx: float = 18.0) -> str:
    return f"<rect x='{x:.2f}' y='{y:.2f}' width='{w:.2f}' height='{h:.2f}' rx='{rx:.2f}' fill='{fill}' stroke='{stroke}' />"


def polyline(points: list[tuple[float, float]], color: str, width: float = 3.0, fill: str = "none") -> str:
    pts = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)
    return f"<polyline fill='{fill}' stroke='{color}' stroke-width='{width}' points='{pts}' />"


def build_svg() -> str:
    width = 1280
    height = 780

    chart_x0, chart_y0, chart_w, chart_h = 620, 170, 560, 360
    xs = [128, 160]
    ys = [0.9823, 0.9773]
    xmin, xmax = 120, 168
    ymin, ymax = 0.94, 1.04

    def map_chart(x: float, y: float) -> tuple[float, float]:
        px = chart_x0 + (x - xmin) / (xmax - xmin) * chart_w
        py = chart_y0 + chart_h - (y - ymin) / (ymax - ymin) * chart_h
        return px, py

    chart_grid: list[str] = []
    for ytick in [0.94, 0.96, 0.98, 1.00, 1.02, 1.04]:
        _, py = map_chart(xmin, ytick)
        chart_grid.append(line(chart_x0, py, chart_x0 + chart_w, py, "#d6e0eb", 1.0))
        chart_grid.append(text(chart_x0 - 16, py + 5, f"{ytick:.2f}", 14, fill="#4f6278", anchor="end"))
    for xtick in xs:
        px, _ = map_chart(xtick, ymin)
        chart_grid.append(line(px, chart_y0, px, chart_y0 + chart_h, "#d6e0eb", 1.0))
        chart_grid.append(text(px, chart_y0 + chart_h + 28, str(xtick), 15, fill="#4f6278", anchor="middle"))

    baseline_y = map_chart(xmin, 1.0)[1]
    chart_pts = [map_chart(x, y) for x, y in zip(xs, ys)]
    fill_pts = [(chart_pts[0][0], baseline_y)] + chart_pts + [(chart_pts[-1][0], baseline_y)]

    lattice_cells: list[str] = []
    cell = 26
    grid_origin_x = 95
    grid_origin_y = 210
    cols = 9
    rows = 9
    for r in range(rows):
        for c in range(cols):
            x = grid_origin_x + c * (cell + 4)
            y = grid_origin_y + r * (cell + 4)
            is_boundary = r in (0, rows - 1) or c in (0, cols - 1)
            fill = "#d7e3f2" if not is_boundary else "#f0d8a8"
            stroke = "#9cb0c8" if not is_boundary else "#ba7a22"
            lattice_cells.append(rect(x, y, cell, cell, fill, stroke, rx=5))

    damage_y = grid_origin_y + 4 * (cell + 4) - 2
    damage_x = grid_origin_x + 2 * (cell + 4)
    damage_w = 5 * (cell + 4) - 4
    lattice_cells.append(rect(damage_x, damage_y, damage_w, cell + 4, "rgba(200,75,49,0.10)", "#c84b31", rx=8))

    highlight_cells: list[str] = []
    edge_weights = {
        (0, 0): 0.72,
        (0, 1): 0.82,
        (0, 2): 0.86,
        (0, 3): 0.88,
        (0, 4): 0.90,
        (0, 5): 0.88,
        (0, 6): 0.85,
        (0, 7): 0.80,
        (0, 8): 0.72,
        (8, 0): 0.63,
        (8, 1): 0.69,
        (8, 2): 0.72,
        (8, 3): 0.75,
        (8, 4): 0.77,
        (8, 5): 0.75,
        (8, 6): 0.72,
        (8, 7): 0.68,
        (8, 8): 0.63,
        (1, 0): 0.60,
        (2, 0): 0.58,
        (3, 0): 0.56,
        (4, 0): 0.55,
        (5, 0): 0.56,
        (6, 0): 0.58,
        (7, 0): 0.60,
        (1, 8): 0.60,
        (2, 8): 0.58,
        (3, 8): 0.56,
        (4, 8): 0.55,
        (5, 8): 0.56,
        (6, 8): 0.58,
        (7, 8): 0.60,
    }
    for (r, c), weight in edge_weights.items():
        x = grid_origin_x + c * (cell + 4)
        y = grid_origin_y + r * (cell + 4)
        alpha = 0.28 + 0.58 * weight
        highlight_cells.append(
            f"<rect x='{x + 4:.2f}' y='{y + 4:.2f}' width='{cell - 8:.2f}' height='{cell - 8:.2f}' rx='4' fill='rgba(44,114,182,{alpha:.3f})' stroke='none' />"
        )

    interpretation = [
        ("Xi_edge > 1", "genuine edge concentration", "#b4432a"),
        ("Xi_edge = 1", "boundary-area scaling", "#1d6f86"),
        ("Xi_edge < 1", "flux pushed inward", "#5d6d7e"),
    ]

    interp_rows: list[str] = []
    y0 = 612
    for idx, (lhs, rhs, color) in enumerate(interpretation):
        yy = y0 + idx * 34
        interp_rows.append(line(92, yy - 6, 128, yy - 6, color, 5.0))
        interp_rows.append(text(144, yy, lhs, 18, "700", "#173052"))
        interp_rows.append(text(268, yy, rhs, 18, "400", "#50627d"))

    svg = f"""<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}' viewBox='0 0 {width} {height}'>
  <rect width='{width}' height='{height}' fill='#f4efe6' />
  <rect x='24' y='24' width='{width - 48}' height='{height - 48}' rx='26' fill='#fffdf8' stroke='#e5dbc7' />

  {text(80, 82, 'Geometry-Normalized Plaquette-Flux Edge Enrichment', 34, '700', '#16283f')}
  {text(80, 114, 'Xi_edge compares measured boundary plaquette-flux weight to the geometric boundary share.', 20, '400', '#50627d')}

  <rect x='64' y='154' width='500' height='392' rx='22' fill='#fbf8f2' stroke='#d9cfbb' />
  {text(86, 186, 'Conceptual plaquette-flux map after central-strip damage', 24, '700', '#173052')}
  {''.join(lattice_cells)}
  {''.join(highlight_cells)}
  {text(92, 536, 'Warm border cells mark the geometric boundary set partial Omega; blue inset intensity sketches |rho_p|.', 16, '400', '#50627d')}
  {text(damage_x + damage_w / 2, damage_y - 12, 'central-strip damage window', 16, '700', '#c84b31', 'middle')}

  <rect x='600' y='154' width='608' height='392' rx='22' fill='#fbf8f2' stroke='#d9cfbb' />
  {text(622, 186, 'Measured Xi_edge stays pinned near the boundary-area baseline', 24, '700', '#173052')}
  {''.join(chart_grid)}
  {line(chart_x0, baseline_y, chart_x0 + chart_w, baseline_y, '#c84b31', 2.5, '10 7')}
  {text(chart_x0 + chart_w - 8, baseline_y - 12, 'baseline = 1.00', 16, '700', '#c84b31', 'end')}
  {polyline(fill_pts, '#9ed0ef', 0.0, fill='rgba(123,188,228,0.30)')}
  {polyline(chart_pts, '#2c72b6', 4.0)}
  <circle cx='{chart_pts[0][0]:.2f}' cy='{chart_pts[0][1]:.2f}' r='7' fill='#2c72b6' stroke='#ffffff' stroke-width='2' />
  <circle cx='{chart_pts[1][0]:.2f}' cy='{chart_pts[1][1]:.2f}' r='7' fill='#2c72b6' stroke='#ffffff' stroke-width='2' />
  {text(chart_pts[0][0], chart_pts[0][1] - 16, '0.9823', 16, '700', '#2c72b6', 'middle')}
  {text(chart_pts[1][0], chart_pts[1][1] - 16, '0.9773', 16, '700', '#2c72b6', 'middle')}
  {text(chart_x0 + chart_w / 2, chart_y0 + chart_h + 58, 'lattice size', 18, '600', '#173052', 'middle')}
  {text(chart_x0 - 72, chart_y0 + chart_h / 2, 'Xi_edge', 18, '600', '#173052', 'middle')}

  <rect x='64' y='574' width='1144' height='164' rx='22' fill='#f8fbff' stroke='#cadced' />
  {text(86, 610, 'Interpretation', 24, '700', '#173052')}
  {''.join(interp_rows)}
  {text(86, 722, 'For the promoted HAFC-EGATL entry, central-strip runs at sizes 128 and 160 stay close to Xi_edge = 1, supporting stable boundary-area scaling rather than inward collapse.', 17, '400', '#50627d')}
  {text(86, 752, 'Equation: Xi_edge = f_edge^(rho) / (|partial Omega| / N_p), with f_edge^(rho) = sum_(p in partial Omega) |rho_p| / sum_p |rho_p|.', 16, '400', '#50627d')}
</svg>
"""
    return svg


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_OUT_DIR.mkdir(parents=True, exist_ok=True)

    svg = build_svg()
    note_src = OUT_DIR / "derivation_note.md"

    for out_dir in (OUT_DIR, DOCS_OUT_DIR):
        out_svg = out_dir / "edge_enrichment_dashboard.svg"
        out_svg.write_text(svg, encoding="utf-8")
        if note_src.exists() and out_dir is DOCS_OUT_DIR:
            (out_dir / "derivation_note.md").write_text(note_src.read_text(encoding="utf-8"), encoding="utf-8")

    print(f"wrote: {OUT_DIR / 'edge_enrichment_dashboard.svg'}")
    print(f"mirrored: {DOCS_OUT_DIR}")


if __name__ == "__main__":
    main()