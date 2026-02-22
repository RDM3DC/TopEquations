from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


def _display_artifact(entry: dict, key: str) -> str:
    payload = entry.get(key, {}) or {}
    path = (payload.get("path") or "").strip()
    status = (payload.get("status") or "planned").strip() or "planned"
    return path if path else status


def _safe(text: str) -> str:
    return str(text).replace("|", "\\|")


def _row(cols: list[str]) -> str:
    return "| " + " | ".join(_safe(c) for c in cols) + " |"


def generate(input_path: Path, output_path: Path) -> None:
    data = json.loads(input_path.read_text(encoding="utf-8"))
    entries_all = list(data.get("entries", []))
    entries_all.sort(key=lambda e: float(e.get("score", 0)), reverse=True)

    # Display cap: only show "leaderboard" entries with score >= 68.
    # Lower-scoring entries may still exist in the registry, but they won't appear
    # in the top tables.
    DISPLAY_THRESHOLD = 68
    entries = [e for e in entries_all if float(e.get("score", 0)) >= DISPLAY_THRESHOLD]

    today = datetime.now().strftime("%Y-%m-%d")
    this_month = datetime.now().strftime("%Y-%m")

    monthly = [e for e in entries if str(e.get("date", "")).startswith(this_month)]

    # Registry keeps everything, regardless of score (historical record).
    registry = [e for e in entries_all if str(e.get("firstSeen", "")).startswith(("2025", "2026", "2027", "2028", "2029"))]
    registry.sort(key=lambda e: str(e.get("firstSeen", "9999-99")))

    lines: list[str] = []
    lines.append("# Equation Leaderboard")
    lines.append(f"_Last updated: {today}_")
    lines.append("")
    lines.append("This is the canonical ranking board for existing and newly derived equations.")
    lines.append("")
    lines.append("Scoring model (0-100):")
    lines.append("- Tractability (0-20)")
    lines.append("- Physical plausibility (0-20)")
    lines.append("- Validation bonus (0-20)")
    lines.append("- Artifact completeness bonus (0-10)")
    lines.append("- Total normalized from 70-point base to 100")
    lines.append("- Novelty is tracked as a tag (`tags.novelty`) with score + date")
    lines.append("")

    lines.append("## Current Top Equations (All-Time)")
    lines.append("")
    lines.append(_row(["Rank", "Equation Name", "Equation", "Source", "Score", "Novelty tag", "Units", "Theory", "Animation", "Image/Diagram", "Description"]))
    lines.append(_row(["------", "---------------", "--------", "--------", "-------", "-----------", "-------", "--------", "-----------", "---------------", "-------------"]))
    for i, e in enumerate(entries, start=1):
        novelty = ((e.get("tags", {}) or {}).get("novelty", {}) or {})
        novelty_label = "-"
        if novelty:
            novelty_label = f"{novelty.get('score', '-') } @ {novelty.get('date', '-') }"
        lines.append(
            _row(
                [
                    str(i),
                    str(e.get("name", "")),
                    str(e.get("equationLatex", "")) or "(pending)",
                    str(e.get("source", "")),
                    str(e.get("score", "")),
                    novelty_label,
                    str(e.get("units", "")),
                    str(e.get("theory", "")),
                    _display_artifact(e, "animation"),
                    _display_artifact(e, "image"),
                    str(e.get("description", "")),
                ]
            )
        )
    lines.append("")

    lines.append("## Newest Top-Ranked Equations (This Month)")
    lines.append("")
    lines.append(_row(["Date", "Equation Name", "Score", "Units", "Theory", "Animation", "Image/Diagram", "Short Description"]))
    lines.append(_row(["------", "---------------", "-------", "-------", "--------", "-----------", "---------------", "-------------------"]))
    for e in monthly:
        lines.append(
            _row(
                [
                    str(e.get("date", "")),
                    str(e.get("name", "")),
                    str(e.get("score", "")),
                    str(e.get("units", "")),
                    str(e.get("theory", "")),
                    _display_artifact(e, "animation"),
                    _display_artifact(e, "image"),
                    str(e.get("description", "")),
                ]
            )
        )
    if not monthly:
        lines.append(_row([this_month, "(none yet)", "-", "-", "-", "planned", "planned", "No entries for this month yet."]))
    lines.append("")

    lines.append("## All Equations Since 2025 (Registry)")
    lines.append("")
    lines.append(_row(["First Seen", "Equation Name", "Equation", "Source", "Latest Status", "Latest Score", "Animation", "Image/Diagram"]))
    lines.append(_row(["------------", "---------------", "--------", "--------", "---------------", "--------------", "-----------", "---------------"]))
    for e in registry:
        lines.append(
            _row(
                [
                    str(e.get("firstSeen", "")),
                    str(e.get("name", "")),
                    str(e.get("equationLatex", "")) or "(pending)",
                    str(e.get("source", "")),
                    str(e.get("theory", "")),
                    str(e.get("score", "")),
                    _display_artifact(e, "animation"),
                    _display_artifact(e, "image"),
                ]
            )
        )
    if not registry:
        lines.append(_row(["2025", "(none yet)", "-", "-", "-", "planned", "planned"]))
    lines.append("")

    lines.append("## Update Rules")
    lines.append("")
    lines.append("1. Add every daily candidate to `submissions/YYYY-MM-DD.md`.")
    lines.append("2. Keep `data/equations.json` as source of truth.")
    lines.append("3. Regenerate this file with `python tools/generate_leaderboard.py`.")
    lines.append("4. Keep animation/image columns as links or `planned` status only.")

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    input_path = repo_root / "data" / "equations.json"
    output_path = repo_root / "leaderboard.md"
    generate(input_path, output_path)

    # Keep GitHub Pages (/docs) in sync if present.
    docs_dir = repo_root / "docs"
    if docs_dir.exists():
        try:
            from tools.sync_docs import main as _sync_docs  # type: ignore

            _sync_docs()
        except Exception:
            # Best-effort sync; leaderboard generation should still succeed.
            pass


if __name__ == "__main__":
    main()
