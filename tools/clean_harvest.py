"""Clean harvested equation registry by removing junk / non-equation entries.

This harvest contains true equations plus some false positives (especially from inline $...$).
We remove entries where:
- equation is missing/blank
- equation is literally 'None' / 'null'
- equation looks like plain English / non-math text (low math signal)

Writes back to: data/harvest/equation_harvest.json

Usage:
  python tools/clean_harvest.py

Exit code 0 always; prints summary.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
HARVEST = REPO / "data" / "harvest" / "equation_harvest.json"

# Heuristics: keep items that look like actual math.
# "Strong" signal excludes bare digits/list markers.
STRONG_SIGNAL = re.compile(
    r"[=<>±≈∝→←↔]|"          # relations
    r"[\+\*/\^_]|"          # operators / latex subscripts (exclude '-' because it appears in prose)
    r"[()\[\]{}]|"          # grouping
    r"[αβγδλμνπϕφθκΩΔΣΓ]|"   # common greek glyphs
    r"(\\frac|\\dot|\\ddot|\\int|\\sum|\\prod|\\nabla|\\partial|\\sqrt|\\log|\\exp)"  # math commands
)

WEAK_PROSE = re.compile(r"^[A-Za-z\s:;,'\-]+$")

# Markdown-ish junk captured from $...$ or bracket blocks
MD_JUNK = re.compile(r"^\s*(\d+\.|[-*])\s+\*\*.*\*\*\s*$")

MOSTLY_WORDS = re.compile(r"^[A-Za-z\s,;:\-']+$")
WORD_TOKEN = re.compile(r"[A-Za-z]+")

# Extra structural math markers (beyond STRONG_SIGNAL)
STRUCTURE = re.compile(
    r"(\\frac|\\int|\\sum|\\prod|\\nabla|\\partial|\\sqrt)|"
    r"\b(d/d|dx|dt)\b|"
    r"[=<>±≈∝→←↔]"
)

PROSE_PREFIX = re.compile(
    r"^(for\s+|and\s+|to\s+|can\s+|is\s+|example\s*:|implementation\s+note)",
    re.IGNORECASE,
)


def is_bad(eq: object) -> bool:
    if eq is None:
        return True
    s = str(eq).strip()
    if not s:
        return True
    low = s.lower()
    if low in {"none", "null"}:
        return True

    # Markdown-ish junk
    if MD_JUNK.match(s) or "**" in s:
        return True

    # Drop weak prose strings (letters/punct only) unless they have real structure.
    if WEAK_PROSE.match(s) and not STRUCTURE.search(s):
        return True

    # Require at least some strong math signal.
    if not STRONG_SIGNAL.search(s):
        return True

    # Drop sentence-like prose false positives.
    words = len(WORD_TOKEN.findall(s))
    has_structure = bool(STRUCTURE.search(s))
    if words >= 8 and not has_structure:
        return True

    # Common prose lead-ins from extracted narrative text.
    if PROSE_PREFIX.search(s) and not has_structure:
        return True

    # Full-sentence style text with weak/no symbolic relation is usually junk.
    if s.endswith((".", ";")) and words >= 8 and not has_structure:
        return True

    # Super-short fragments are usually junk.
    if len(s) < 4:
        return True

    return False


def main() -> None:
    data = json.loads(HARVEST.read_text(encoding="utf-8"))
    entries = list(data.get("entries", []))

    before = len(entries)
    # Remove code captures (Python/JS lines) — harvest UI should be equation-first.
    # If we ever want code back, we can add a CLI flag; for now keep LaTeX/math-only.
    kept = [e for e in entries if str(e.get("kind", "")).lower() != "code" and not is_bad(e.get("equation"))]
    removed = before - len(kept)

    data["entries"] = kept

    # Recompute simple stats
    stats = data.get("stats", {}) or {}
    stats["unique"] = len(kept)

    by_kind: dict[str, int] = {}
    for e in kept:
        k = str(e.get("kind", "unknown"))
        by_kind[k] = by_kind.get(k, 0) + 1
    stats["by_kind"] = by_kind

    data["stats"] = stats

    HARVEST.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"clean_harvest: before={before} removed={removed} after={len(kept)}")


if __name__ == "__main__":
    main()
