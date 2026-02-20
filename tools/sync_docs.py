"""Sync GitHub Pages docs/ copies from repo root markdown files.

Usage:
  python tools/sync_docs.py

Copies:
  - leaderboard.md -> docs/leaderboard.md
  - data/harvest/equation_harvest_preview.md -> docs/harvest_preview.md

This keeps GitHub Pages (/docs) updated after regenerating leaderboard.
"""

from __future__ import annotations

from pathlib import Path
import shutil


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    docs = repo_root / "docs"
    docs.mkdir(parents=True, exist_ok=True)

    src_leaderboard = repo_root / "leaderboard.md"
    dst_leaderboard = docs / "leaderboard.md"

    src_preview = repo_root / "data" / "harvest" / "equation_harvest_preview.md"
    dst_preview = docs / "harvest_preview.md"

    if src_leaderboard.exists():
        shutil.copyfile(src_leaderboard, dst_leaderboard)
        print(f"Synced: {src_leaderboard} -> {dst_leaderboard}")
    else:
        print(f"Missing: {src_leaderboard}")

    if src_preview.exists():
        shutil.copyfile(src_preview, dst_preview)
        print(f"Synced: {src_preview} -> {dst_preview}")
    else:
        print(f"Missing: {src_preview}")


if __name__ == "__main__":
    main()
