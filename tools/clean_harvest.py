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
MATH_SIGNAL = re.compile(
    r"(\\[a-zA-Z]+)|"  # LaTeX commands
    r"[=<>±≈∝→←↔]|"     # relations
    r"[\d]|"           # numbers
    r"[\+\-\*/\^_]|" # operators / latex subscripts
    r"[()\[\]{}]|"     # grouping
    r"[αβγδλμνπϕφθκΩΔΣΓ]|"  # common greek glyphs
    r"(\\frac|\\dot|\\ddot|\\int|\\sum|\\prod|\\nabla|\\partial|\\sqrt|\\log|\\exp)"
)

MOSTLY_WORDS = re.compile(r"^[A-Za-z\s,;:\-']+$")
WORD_TOKEN = re.compile(r"[A-Za-z]+")

# Strong math markers: equations/relations and explicit symbolic structure.
STRONG_MATH = re.compile(
    r"(\\[a-zA-Z]+)|"  # LaTeX commands
    r"[=<>±≈∝→←↔]|"     # explicit relations
    r"\b(d/d|dx|dt)\b|"  # derivative-style markers
    r"[\+\-\*/\^_]"  # operators/subscripts/superscripts
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

    # If it's basically plain English with no math markers, drop it.
    if MOSTLY_WORDS.match(s) and not MATH_SIGNAL.search(s):
        return True

    # Require at least some math signal.
    if not MATH_SIGNAL.search(s):
        return True

    # Drop sentence-like prose false positives that contain weak math hints
    # but no strong equation structure.
    words = len(WORD_TOKEN.findall(s))
    has_strong = bool(STRONG_MATH.search(s))
    if words >= 8 and not has_strong:
        return True

    # Common prose lead-ins from extracted narrative text.
    if PROSE_PREFIX.search(s) and not has_strong:
        return True

    # Full-sentence style text with weak/no symbolic relation is usually junk.
    if s.endswith((".", ";")) and words >= 8 and not has_strong:
        return True

    # Super-short fragments are usually junk.
    if len(s) < 4:
        return True

    return False


def main() -> None:
    data = json.loads(HARVEST.read_text(encoding="utf-8"))
    entries = list(data.get("entries", []))

    before = len(entries)
    kept = [e for e in entries if not is_bad(e.get("equation"))]
    removed = before - len(kept)

    data["entries"] = kept

    # Recompute simple stats
    stats = data.get("stats", {}) or {}
    stats["unique"] = len(kept)
    data["stats"] = stats

    HARVEST.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"clean_harvest: before={before} removed={removed} after={len(kept)}")


if __name__ == "__main__":
    main()
