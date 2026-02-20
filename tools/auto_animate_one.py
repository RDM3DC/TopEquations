"""Auto-animate ONE equation and wire it into the TopEquations site.

Updated (2026-02-20): animations are now *educational* mini-explainers (~25–35s)
rendered in 16:9 for watching on GitHub Pages.

What it does:
- Finds the next equation in data/equations.json whose animation.path is empty.
- Renders a Manim explainer:
    title + equation + quick symbol legend + simple behavior demo + "prediction" line
- Writes video to docs/assets/animations/<id>.mp4
- Updates data/equations.json: animation.status="linked", animation.path="./assets/animations/<id>.mp4"
- Rebuilds docs HTML pages (python tools/build_site.py)

Usage:
  python tools/auto_animate_one.py

Notes:
- Includes a special renderer for the Phase-Coupled Stability Threshold Law.
- Requires manim available on PATH (python -m manim).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime


REPO = Path(__file__).resolve().parents[1]
DATA = REPO / "data" / "equations.json"
DOCS = REPO / "docs"
ANIM_DIR = DOCS / "assets" / "animations"
ANIM_DIR.mkdir(parents=True, exist_ok=True)


GENERIC_TEMPLATE = r"""
from manim import *

class AutoEquation(Scene):
    def construct(self):
        title = Text({title!r}, font_size=52)
        title.to_edge(UP)

        eq = MathTex({latex!r}).scale(1.25)
        eq.next_to(title, DOWN, buff=0.55)

        what = Text({what!r}, font_size=30, color=BLUE_A)
        what.next_to(eq, DOWN, buff=0.45)

        legend_title = Text("Symbols", font_size=28, color=GRAY_A)
        legend = VGroup(*[Text(s, font_size=26) for s in {legend!r}]).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        legend_box = VGroup(legend_title, legend).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        legend_box.to_corner(DL)

        pred_title = Text("Prediction", font_size=28, color=GRAY_A)
        pred = Text({pred!r}, font_size=28)
        pred_box = VGroup(pred_title, pred).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        pred_box.to_corner(DR)

        self.play(FadeIn(title, shift=DOWN), run_time=0.8)
        self.play(Write(eq), run_time=1.8)
        self.play(FadeIn(what, shift=DOWN), run_time=1.2)
        self.play(FadeIn(legend_box, shift=UP), FadeIn(pred_box, shift=UP), run_time=1.2)

        box = SurroundingRectangle(eq, color=GREEN, buff=0.18)
        self.play(Create(box), run_time=0.7)
        self.wait(1.3)
        self.play(FadeOut(box), run_time=0.4)

        # Simple demo: animate a generic "response" curve (illustrative)
        axes = Axes(x_range=[0, 10, 2], y_range=[0, 1.2, 0.2], tips=False).scale(0.75)
        axes.to_edge(DOWN)
        xlab = axes.get_x_axis_label(Text("input", font_size=24), edge=RIGHT, direction=RIGHT)
        ylab = axes.get_y_axis_label(Text("response", font_size=24), edge=UP, direction=UP)
        graph = axes.plot(lambda x: 1 - np.exp(-0.55*x), x_range=[0,10], color=YELLOW)
        dot = Dot(axes.c2p(0,0), radius=0.06, color=RED)
        tracker = ValueTracker(0)
        dot.add_updater(lambda m: m.move_to(axes.c2p(tracker.get_value(), 1 - np.exp(-0.55*tracker.get_value()))))

        self.play(FadeIn(axes), FadeIn(xlab), FadeIn(ylab), run_time=0.9)
        self.play(Create(graph), run_time=1.0)
        self.play(FadeIn(dot), run_time=0.4)
        self.play(tracker.animate.set_value(10), run_time=6.0, rate_func=smooth)
        self.wait(2.0)
"""


PHASE_COUPLED_TEMPLATE = r"""
from manim import *
import numpy as np

class AutoEquation(Scene):
    def construct(self):
        title = Text({title!r}, font_size=52)
        title.to_edge(UP)

        eq = MathTex({latex!r}).scale(1.18)
        eq.next_to(title, DOWN, buff=0.5)

        what = Text("Couples ARP growth to accumulated lifted phase.", font_size=30, color=BLUE_A)
        what.next_to(eq, DOWN, buff=0.35)

        legend_title = Text("Symbols", font_size=28, color=GRAY_A)
        legend_lines = [
            "α: reinforcement gain",
            "μ: decay rate",
            "λ: phase-suppression rate",
            "θ_R: lifted (unwrapped) phase",
            "π_a: local phase period",
        ]
        legend = VGroup(*[Text(s, font_size=26) for s in legend_lines]).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        legend_box = VGroup(legend_title, legend).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        legend_box.to_corner(DL)

        pred_title = Text("Prediction", font_size=28, color=GRAY_A)
        pred = Text("Suppression peaks near θ_R ≈ (2k+1)π_a → conductance collapses/limits.", font_size=28)
        pred_box = VGroup(pred_title, pred).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        pred_box.to_corner(DR)

        self.play(FadeIn(title, shift=DOWN), run_time=0.8)
        self.play(Write(eq), run_time=2.0)
        self.play(FadeIn(what, shift=DOWN), run_time=1.1)
        self.play(FadeIn(legend_box, shift=UP), FadeIn(pred_box, shift=UP), run_time=1.2)

        # Demo 1: sin^2 term over theta_R
        axes = Axes(
            x_range=[0, 4, 1],
            y_range=[0, 1.05, 0.25],
            tips=False,
        ).scale(0.78)
        axes.to_edge(DOWN)
        xlab = axes.get_x_axis_label(MathTex(r"\\theta_R/\\pi_a"), edge=RIGHT, direction=RIGHT).scale(0.8)
        ylab = axes.get_y_axis_label(MathTex(r"\\sin^2(\\theta_R/2\\pi_a)"), edge=UP, direction=UP).scale(0.8)

        f = lambda x: (np.sin(np.pi * x / 2.0) ** 2)
        graph = axes.plot(lambda x: f(x), x_range=[0,4], color=YELLOW)

        tracker = ValueTracker(0.0)
        dot = always_redraw(lambda: Dot(axes.c2p(tracker.get_value(), f(tracker.get_value())), radius=0.06, color=RED))
        vline = always_redraw(lambda: Line(
            axes.c2p(tracker.get_value(), 0),
            axes.c2p(tracker.get_value(), f(tracker.get_value())),
            color=RED,
            stroke_width=3,
        ))

        peak1 = axes.get_vertical_line(axes.c2p(1, f(1)), color=BLUE_B, stroke_width=3)
        peak3 = axes.get_vertical_line(axes.c2p(3, f(3)), color=BLUE_B, stroke_width=3)
        peak_lbl = Text("peaks at odd half-turns", font_size=24, color=BLUE_B).next_to(graph, UP, buff=0.25)

        self.play(FadeIn(axes), FadeIn(xlab), FadeIn(ylab), run_time=1.0)
        self.play(Create(graph), run_time=1.2)
        self.play(FadeIn(dot), FadeIn(vline), run_time=0.5)
        self.play(Create(peak1), Create(peak3), FadeIn(peak_lbl, shift=UP), run_time=0.9)

        self.play(tracker.animate.set_value(4.0), run_time=7.0, rate_func=smooth)
        self.wait(1.0)

        # Demo 2: qualitative G(t) under phase suppression
        axes2 = Axes(x_range=[0, 10, 2], y_range=[0, 1.3, 0.25], tips=False).scale(0.65)
        axes2.to_corner(UR)
        g1 = axes2.plot(lambda t: 1 - np.exp(-0.55*t), x_range=[0,10], color=GREEN)
        g2 = axes2.plot(lambda t: (1 - np.exp(-0.55*t)) * (0.55 + 0.45*np.cos(0.9*t)**2), x_range=[0,10], color=RED)
        lbl2 = VGroup(
            Text("G(t) no phase", font_size=20, color=GREEN),
            Text("G(t) w/ suppression", font_size=20, color=RED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12).next_to(axes2, LEFT, buff=0.35)

        self.play(FadeIn(axes2), Create(g1), Create(g2), FadeIn(lbl2), run_time=2.0)
        self.wait(6.0)
"""


def pick_entry(data: dict) -> dict | None:
    # Priority bump: animate this one first if it hasn't been animated yet.
    priority_ids = [
        "eq-arp-phase-critical-collapse",  # Phase-Coupled Stability Threshold Law
    ]

    entries = list(data.get("entries", []))

    for pid in priority_ids:
        for e in entries:
            if e.get("id") == pid:
                anim = e.get("animation") or {}
                path = (anim.get("path") or "").strip()
                if not path:
                    return e

    for e in entries:
        anim = e.get("animation") or {}
        path = (anim.get("path") or "").strip()
        if not path:
            return e

    return None


def clamp_desc(s: str, max_len: int = 120) -> str:
    s = (s or "").strip().replace("\n", " ")
    if len(s) <= max_len:
        return s
    return s[: max_len - 1].rstrip() + "…"


def main() -> int:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    entry = pick_entry(data)
    if not entry:
        print("No un-animated equations found (all have animation.path).")
        return 0

    eid = entry.get("id") or "eq"
    title = entry.get("name") or eid
    latex = (entry.get("equationLatex") or "").strip() or r"x=0"
    desc = clamp_desc(entry.get("description") or "")

    # Generic legend/prediction (fallback)
    legend = ["α: reinforcement", "μ: decay", "(see card for assumptions)"]
    what = desc if desc else "Derived equation"
    pred = "Simulate + look for a distinctive response curve." 

    # Choose template
    template = GENERIC_TEMPLATE
    if eid == "eq-arp-phase-critical-collapse":
        template = PHASE_COUPLED_TEMPLATE

    # Write manim file
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    script_path = REPO / "tools" / f"_auto_scene_{eid}_{stamp}.py"
    script_path.write_text(
        template.format(title=title, latex=latex, desc=desc, legend=legend, what=what, pred=pred),
        encoding="utf-8",
    )

    # Render (16:9)
    out_mp4 = ANIM_DIR / f"{eid}.mp4"
    cmd = [
        sys.executable,
        "-m",
        "manim",
        "-qk",
        "-r",
        "1920,1080",
        str(script_path),
        "AutoEquation",
    ]
    print("Running:", " ".join(cmd))
    subprocess.check_call(cmd, cwd=str(REPO))

    # Manim output location is under repo/media/videos/<scriptname>/<res>/AutoEquation.mp4
    media_dir = REPO / "media" / "videos"
    candidates = list(media_dir.rglob("AutoEquation.mp4"))
    if not candidates:
        raise RuntimeError("Could not find rendered AutoEquation.mp4 under media/videos")
    newest = max(candidates, key=lambda p: p.stat().st_mtime)
    out_mp4.write_bytes(newest.read_bytes())

    # Update data/equations.json
    entry.setdefault("animation", {})
    entry["animation"]["status"] = "linked"
    entry["animation"]["path"] = f"./assets/animations/{eid}.mp4"
    data["lastUpdated"] = datetime.now().strftime("%Y-%m-%d")
    DATA.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Rebuild site
    subprocess.check_call([sys.executable, str(REPO / "tools" / "build_site.py")], cwd=str(REPO))

    print(f"Animated: {eid} -> {out_mp4}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
