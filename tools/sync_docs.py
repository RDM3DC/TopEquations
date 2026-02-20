"""Build/sync GitHub Pages docs/.

Preferred: generate the fancy HTML pages.

Usage:
  python tools/sync_docs.py

Under the hood this calls:
  python tools/build_site.py

(We keep this file because other scripts call it.)
"""

from __future__ import annotations


def main() -> None:
    # Run the site builder as a script to avoid import/path issues.
    import subprocess
    import sys
    from pathlib import Path

    repo_root = Path(__file__).resolve().parents[1]
    build_script = repo_root / "tools" / "build_site.py"

    subprocess.check_call([sys.executable, str(build_script)])


if __name__ == "__main__":
    main()
