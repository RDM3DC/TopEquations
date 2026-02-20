"""Auto-animate ONE equation and wire it into the TopEquations site.

What it does:
- Finds the first equation in data/equations.json whose animation.path is empty.
- Renders a simple square Manim animation:
    title + equation (MathTex) + short description
- Writes video to docs/assets/animations/<id>.mp4
- Updates data/equations.json: animation.status="linked", animation.path="./assets/animations/<id>.mp4"
- Rebuilds docs HTML pages (python tools/build_site.py)

Usage:
  python tools/auto_animate_one.py

Notes:
- This is intentionally generic (works without equation-specific simulation).
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


SCENE_TEMPLATE = r"""
from manim import *

class AutoEquation(Scene):
    def construct(self):
        title = Text({title!r}, font_size=44)
        title.to_edge(UP)

        eq = MathTex({latex!r}).scale(1.15)
        eq.next_to(title, DOWN, buff=0.6)

        desc = Text({desc!r}, font_size=26)
        desc.set_color(BLUE_A)
        desc.next_to(eq, DOWN, buff=0.55)

        self.play(FadeIn(title, shift=DOWN), run_time=0.8)
        self.play(Write(eq), run_time=1.4)
        self.play(FadeIn(desc, shift=DOWN), run_time=1.0)

        box = SurroundingRectangle(eq, color=GREEN, buff=0.18)
        self.play(Create(box), run_time=0.6)
        self.wait(0.7)
        self.play(FadeOut(box), run_time=0.5)
        self.wait(1.0)
"""


def pick_entry(data: dict) -> dict | None:
    for e in data.get("entries", []):
        anim = e.get("animation") or {}
        path = (anim.get("path") or "").strip()
        if not path:
            return e
    return None


def clamp_desc(s: str, max_len: int = 90) -> str:
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

    # Write manim file
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    script_path = REPO / "tools" / f"_auto_scene_{eid}_{stamp}.py"
    script_path.write_text(
        SCENE_TEMPLATE.format(title=title, latex=latex, desc=desc), encoding="utf-8"
    )

    # Render (square)
    out_mp4 = ANIM_DIR / f"{eid}.mp4"
    cmd = [
        sys.executable,
        "-m",
        "manim",
        "-qk",
        "-r",
        "1080,1080",
        str(script_path),
        "AutoEquation",
    ]
    print("Running:", " ".join(cmd))
    subprocess.check_call(cmd, cwd=str(REPO))

    # Manim output location is under repo/media/videos/<scriptname>/<res>/AutoEquation.mp4
    # Find newest mp4 in repo/media/videos/**/AutoEquation.mp4
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
