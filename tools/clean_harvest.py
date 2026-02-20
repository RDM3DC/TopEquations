"""Clean harvested equation registry by removing empty/None-like entries.

Removes entries where:
- equation is missing/blank
- equation is literally 'None' / 'null'

Writes back to: data/harvest/equation_harvest.json

Usage:
  python tools/clean_harvest.py

Exit code 0 always; prints summary.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
HARVEST = REPO / "data" / "harvest" / "equation_harvest.json"


def is_bad(eq: object) -> bool:
    if eq is None:
        return True
    s = str(eq).strip()
    if not s:
        return True
    if s.lower() in {"none", "null"}:
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
