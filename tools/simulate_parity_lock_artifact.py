from __future__ import annotations

import csv
import math
from pathlib import Path


def wrapped_arg(y_re: float, y_im: float) -> float:
    return math.atan2(y_im, y_re)


def unwrap_angles(phases: list[float]) -> list[float]:
    if not phases:
        return []
    out = [phases[0]]
    shift = 0.0
    for i in range(1, len(phases)):
        d = phases[i] - phases[i - 1]
        if d > math.pi:
            shift -= 2.0 * math.pi
        elif d < -math.pi:
            shift += 2.0 * math.pi
        out.append(phases[i] + shift)
    return out


def edge_admittance(t: float, eps: float) -> tuple[float, float]:
    # A deformed loop around the origin that avoids singular crossing in tested eps range.
    y_re = 0.35 + math.cos(t) + eps * math.cos(2.0 * t)
    y_im = math.sin(t) + eps * math.sin(3.0 * t)
    return y_re, y_im


def winding_from_unwrap(unwrapped: list[float]) -> int:
    if len(unwrapped) < 2:
        return 0
    delta = unwrapped[-1] - unwrapped[0]
    return int(round(delta / (2.0 * math.pi)))


def slip_events_principal(phases: list[float]) -> int:
    events = 0
    for i in range(1, len(phases)):
        if abs(phases[i] - phases[i - 1]) > math.pi:
            events += 1
    return events


def slip_events_unwrapped(unwrapped: list[float]) -> int:
    # In lifted coordinates, branch-cut jumps should be removed.
    events = 0
    for i in range(1, len(unwrapped)):
        if abs(unwrapped[i] - unwrapped[i - 1]) > math.pi:
            events += 1
    return events


def visibility_from_slips(slip_events: int, penalty: float = 0.35) -> float:
    return math.exp(-penalty * float(slip_events))


def make_svg(rows: list[dict[str, float]], out_path: Path) -> None:
    width = 980
    height = 420
    margin = 50
    panel_w = (width - 3 * margin) // 2
    panel_h = height - 2 * margin

    eps_values = [r["epsilon"] for r in rows]
    x_min = min(eps_values)
    x_max = max(eps_values)

    def x_map(x: float, x0: float) -> float:
        if x_max == x_min:
            return x0
        return x0 + (x - x_min) / (x_max - x_min) * panel_w

    def y_map(y: float, y0: float, y_min: float, y_max: float) -> float:
        if y_max == y_min:
            return y0 + panel_h / 2.0
        return y0 + panel_h - (y - y_min) / (y_max - y_min) * panel_h

    def poly(points: list[tuple[float, float]], color: str) -> str:
        pts = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)
        return f"<polyline fill='none' stroke='{color}' stroke-width='3' points='{pts}' />"

    y0 = margin
    x0_left = margin
    x0_right = 2 * margin + panel_w

    slip_std = [r["slip_rate_standard"] for r in rows]
    slip_lft = [r["slip_rate_lifted"] for r in rows]
    vis_std = [r["visibility_standard"] for r in rows]
    vis_lft = [r["visibility_lifted"] for r in rows]

    slip_y_min = min(slip_std + slip_lft)
    slip_y_max = max(slip_std + slip_lft)
    vis_y_min = min(vis_std + vis_lft)
    vis_y_max = max(vis_std + vis_lft)

    left_std_pts = [
        (x_map(r["epsilon"], x0_left), y_map(r["slip_rate_standard"], y0, slip_y_min, slip_y_max))
        for r in rows
    ]
    left_lft_pts = [
        (x_map(r["epsilon"], x0_left), y_map(r["slip_rate_lifted"], y0, slip_y_min, slip_y_max))
        for r in rows
    ]
    right_std_pts = [
        (x_map(r["epsilon"], x0_right), y_map(r["visibility_standard"], y0, vis_y_min, vis_y_max))
        for r in rows
    ]
    right_lft_pts = [
        (x_map(r["epsilon"], x0_right), y_map(r["visibility_lifted"], y0, vis_y_min, vis_y_max))
        for r in rows
    ]

    svg = [
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}' viewBox='0 0 {width} {height}'>",
        "<rect x='0' y='0' width='100%' height='100%' fill='#0b1020' />",
        "<text x='24' y='28' fill='#e5e7eb' font-size='18' font-family='Segoe UI'>PL-AIN parity-lock deformation artifact</text>",
        f"<rect x='{x0_left}' y='{y0}' width='{panel_w}' height='{panel_h}' fill='none' stroke='#334155'/>",
        f"<rect x='{x0_right}' y='{y0}' width='{panel_w}' height='{panel_h}' fill='none' stroke='#334155'/>",
        f"<text x='{x0_left + 8}' y='{y0 + 20}' fill='#cbd5e1' font-size='13' font-family='Segoe UI'>Slip-rate per cycle</text>",
        f"<text x='{x0_right + 8}' y='{y0 + 20}' fill='#cbd5e1' font-size='13' font-family='Segoe UI'>Visibility V</text>",
        poly(left_std_pts, '#f97316'),
        poly(left_lft_pts, '#22c55e'),
        poly(right_std_pts, '#f97316'),
        poly(right_lft_pts, '#22c55e'),
        "<text x='70' y='390' fill='#f97316' font-size='12' font-family='Segoe UI'>standard</text>",
        "<text x='150' y='390' fill='#22c55e' font-size='12' font-family='Segoe UI'>lifted</text>",
        "<text x='560' y='390' fill='#f97316' font-size='12' font-family='Segoe UI'>standard</text>",
        "<text x='640' y='390' fill='#22c55e' font-size='12' font-family='Segoe UI'>lifted</text>",
        "</svg>",
    ]
    out_path.write_text("\n".join(svg), encoding="utf-8")


def main() -> None:
    repo = Path(__file__).resolve().parents[1]
    csv_path = repo / "data" / "artifacts" / "parity_lock_deformation.csv"
    md_path = repo / "data" / "artifacts" / "parity_lock_deformation_table.md"
    svg_path = repo / "docs" / "assets" / "figures" / "parity_lock_comparison.svg"

    eps_values = [0.00, 0.04, 0.08, 0.12, 0.16, 0.20]
    n = 1600
    dt = 2.0 * math.pi / n

    rows: list[dict[str, float]] = []
    for eps in eps_values:
        wrapped = []
        min_mod = float("inf")
        for k in range(n + 1):
            t = k * dt
            y_re, y_im = edge_admittance(t, eps)
            mod = math.hypot(y_re, y_im)
            min_mod = min(min_mod, mod)
            wrapped.append(wrapped_arg(y_re, y_im))

        lifted = unwrap_angles(wrapped)
        w = winding_from_unwrap(lifted)
        b = -1 if (w % 2) else 1

        slips_std = slip_events_principal(wrapped)
        slips_lft = slip_events_unwrapped(lifted)

        v_std = visibility_from_slips(slips_std)
        v_lft = visibility_from_slips(slips_lft)

        rows.append(
            {
                "epsilon": eps,
                "min_modulus": min_mod,
                "winding": float(w),
                "parity": float(b),
                "slip_rate_standard": float(slips_std),
                "slip_rate_lifted": float(slips_lft),
                "visibility_standard": v_std,
                "visibility_lifted": v_lft,
                "slip_delta": float(slips_std - slips_lft),
                "visibility_delta": float(v_lft - v_std),
            }
        )

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "epsilon",
                "min_modulus",
                "winding",
                "parity",
                "slip_rate_standard",
                "slip_rate_lifted",
                "visibility_standard",
                "visibility_lifted",
                "slip_delta",
                "visibility_delta",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    # Markdown table artifact for quick publishing in docs/PRs.
    lines = []
    lines.append("# Parity Lock Under Deformation (Artifact Table)")
    lines.append("")
    lines.append("Formal failure boundary (per edge): parity can change only when min_t |Y_ij(t,omega)| = 0.")
    lines.append("")
    lines.append("| epsilon | min|Y| | winding w | parity b | slip std | slip lifted | V std | V lifted | delta slip | delta V |")
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for r in rows:
        lines.append(
            f"| {r['epsilon']:.2f} | {r['min_modulus']:.4f} | {int(r['winding'])} | {int(r['parity'])} | {r['slip_rate_standard']:.0f} | {r['slip_rate_lifted']:.0f} | {r['visibility_standard']:.4f} | {r['visibility_lifted']:.4f} | {r['slip_delta']:.0f} | {r['visibility_delta']:.4f} |"
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    make_svg(rows, svg_path)

    print(f"wrote: {csv_path}")
    print(f"wrote: {md_path}")
    print(f"wrote: {svg_path}")


if __name__ == "__main__":
    main()
