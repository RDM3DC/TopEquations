"""Push research artifacts to an equation's dedicated GitHub repo.

All content is checked for explicit/inappropriate material before submission.
Text files are scanned via the OpenAI Moderation API; binary files are checked
by extension allowlist and filename patterns.

Usage:
    python tools/push_to_equation_repo.py --equation-id eq-arp-redshift --file report.pdf --folder docs
    python tools/push_to_equation_repo.py --equation-id eq-arp-redshift --file plot.png --folder images
    python tools/push_to_equation_repo.py --equation-id eq-arp-redshift --file sim.py --folder simulations --message "Add Monte-Carlo sim"

Requires: gh CLI authenticated, OPENAI_API_KEY env var for moderation
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GITHUB_ORG = "RDM3DC"

ALLOWED_FOLDERS = {"images", "derivations", "simulations", "data", "notes", "docs"}

# Only allow safe file extensions — no executables, no archives with hidden payloads
ALLOWED_EXTENSIONS = {
    # Text / docs
    ".md", ".txt", ".tex", ".bib", ".rst", ".csv", ".tsv", ".json", ".yaml", ".yml",
    ".toml", ".xml", ".html", ".css",
    # Code
    ".py", ".jl", ".m", ".r", ".ipynb", ".nb", ".wl",
    ".c", ".cpp", ".h", ".hpp", ".f90", ".f",
    ".js", ".ts", ".sh", ".ps1",
    # Images
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp", ".tiff", ".tif",
    # Data
    ".hdf5", ".h5", ".npy", ".npz", ".parquet", ".feather", ".arrow",
    ".fits", ".nc", ".mat",
    # Documents
    ".pdf", ".docx", ".pptx", ".xlsx",
}

# Extensions whose content we can read and moderate as text
TEXT_EXTENSIONS = {
    ".md", ".txt", ".tex", ".bib", ".rst", ".csv", ".tsv", ".json", ".yaml", ".yml",
    ".toml", ".xml", ".html", ".css",
    ".py", ".jl", ".m", ".r", ".ipynb", ".nb", ".wl",
    ".c", ".cpp", ".h", ".hpp", ".f90", ".f",
    ".js", ".ts", ".sh", ".ps1",
}

# Filename patterns to reject outright
BANNED_FILENAME_PATTERNS = [
    r"\.exe$", r"\.bat$", r"\.cmd$", r"\.msi$", r"\.dll$", r"\.so$", r"\.dylib$",
    r"\.zip$", r"\.tar$", r"\.gz$", r"\.rar$", r"\.7z$",
    r"\.jar$", r"\.war$", r"\.apk$", r"\.deb$", r"\.rpm$",
]


def _slug(equation_id: str) -> str:
    slug = re.sub(r"[^a-z0-9-]", "-", equation_id.lower())
    return re.sub(r"-+", "-", slug).strip("-")


def _find_equation(equation_id: str) -> dict | None:
    for path in [
        REPO / "data" / "equations.json",
        REPO / "data" / "core.json",
        REPO / "data" / "famous_equations.json",
    ]:
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        for e in data.get("entries", []):
            if e.get("id") == equation_id:
                return e
    return None


def _repo_exists(repo_name: str) -> bool:
    result = subprocess.run(
        ["gh", "repo", "view", f"{GITHUB_ORG}/{repo_name}", "--json", "name"],
        capture_output=True, text=True,
    )
    return result.returncode == 0


# ---------------------------------------------------------------------------
# Content moderation
# ---------------------------------------------------------------------------

def check_extension(filepath: Path) -> str | None:
    """Return an error string if the file extension is not allowed."""
    ext = filepath.suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return f"File extension '{ext}' is not allowed. Permitted: {sorted(ALLOWED_EXTENSIONS)}"
    for pat in BANNED_FILENAME_PATTERNS:
        if re.search(pat, filepath.name, re.IGNORECASE):
            return f"Filename '{filepath.name}' matches a banned pattern."
    return None


def moderate_text_content(text: str, filename: str) -> str | None:
    """Use OpenAI Moderation API to check text for explicit content.

    Returns an error string if flagged, None if clean.
    """
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        return "OPENAI_API_KEY not set — cannot run content moderation. Aborting."

    import urllib.request
    import urllib.error

    # Truncate to 100KB for moderation (API limit is generous but be safe)
    sample = text[:100_000]

    payload = json.dumps({"input": sample}).encode("utf-8")
    req = urllib.request.Request(
        "https://api.openai.com/v1/moderations",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return f"Moderation API error (HTTP {exc.code}). Blocking submission for safety."
    except Exception as exc:
        return f"Moderation API unreachable: {exc}. Blocking submission for safety."

    results = body.get("results", [])
    if not results:
        return "Moderation API returned no results. Blocking for safety."

    result = results[0]
    if result.get("flagged", False):
        # Build a human-readable summary of what was flagged
        cats = result.get("categories", {})
        flagged_cats = [cat for cat, val in cats.items() if val]
        return (
            f"Content in '{filename}' was flagged for: {', '.join(flagged_cats)}. "
            "Submission blocked."
        )

    return None  # Clean


def moderate_file(filepath: Path) -> str | None:
    """Run all moderation checks on a file. Returns error string or None."""
    # 1. Extension check
    err = check_extension(filepath)
    if err:
        return err

    # 2. Size check — 50 MB max
    size = filepath.stat().st_size
    if size > 50 * 1024 * 1024:
        return f"File is {size / 1024 / 1024:.1f} MB — exceeds 50 MB limit."

    # 3. Text content moderation
    ext = filepath.suffix.lower()
    if ext in TEXT_EXTENSIONS:
        try:
            text = filepath.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return "Could not read file as text for moderation. Blocking for safety."

        err = moderate_text_content(text, filepath.name)
        if err:
            return err

    return None  # All checks passed


# ---------------------------------------------------------------------------
# Push logic
# ---------------------------------------------------------------------------

def push_file(
    equation_id: str,
    file_path: Path,
    folder: str,
    commit_message: str | None = None,
    dry_run: bool = False,
) -> bool:
    """Push a single file to the equation's dedicated repo.

    Returns True on success.
    """
    # Validate equation exists
    entry = _find_equation(equation_id)
    if not entry:
        print(f"ERROR: equation '{equation_id}' not found in any data file.", file=sys.stderr)
        return False

    repo_name = _slug(equation_id)
    full_name = f"{GITHUB_ORG}/{repo_name}"

    # Validate repo exists
    if not _repo_exists(repo_name):
        print(f"ERROR: repo {full_name} does not exist. Run create_equation_repo.py first.", file=sys.stderr)
        return False

    # Validate folder
    if folder not in ALLOWED_FOLDERS:
        print(f"ERROR: folder must be one of {sorted(ALLOWED_FOLDERS)}", file=sys.stderr)
        return False

    # Validate file exists
    if not file_path.is_file():
        print(f"ERROR: file not found: {file_path}", file=sys.stderr)
        return False

    # --------------- CONTENT MODERATION ---------------
    print(f"Moderating '{file_path.name}'...")
    err = moderate_file(file_path)
    if err:
        print(f"BLOCKED: {err}", file=sys.stderr)
        return False
    print("  Content check passed.")

    if dry_run:
        print(f"DRY RUN: would push {file_path.name} -> {full_name}/{folder}/")
        return True

    # Clone, copy, commit, push
    with tempfile.TemporaryDirectory() as tmp:
        clone_dir = Path(tmp) / repo_name
        print(f"Cloning {full_name}...")
        result = subprocess.run(
            ["gh", "repo", "clone", full_name, str(clone_dir)],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            print(f"ERROR: clone failed: {result.stderr.strip()[:300]}", file=sys.stderr)
            return False

        # Ensure target folder exists
        dest_dir = clone_dir / folder
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Copy file
        dest_file = dest_dir / file_path.name
        dest_file.write_bytes(file_path.read_bytes())

        # Commit
        msg = commit_message or f"Add {file_path.name} to {folder}/"
        subprocess.run(["git", "add", "-A"], cwd=str(clone_dir), capture_output=True)

        # Check if there's anything to commit
        status = subprocess.run(
            ["git", "status", "--porcelain"], cwd=str(clone_dir),
            capture_output=True, text=True,
        )
        if not status.stdout.strip():
            print("Nothing new to commit (file already exists with same content).")
            return True

        subprocess.run(
            ["git", "commit", "-m", msg],
            cwd=str(clone_dir), capture_output=True,
            env={
                **os.environ,
                "GIT_AUTHOR_NAME": "TopEquations Bot",
                "GIT_COMMITTER_NAME": "TopEquations Bot",
                "GIT_AUTHOR_EMAIL": "bot@topequations.local",
                "GIT_COMMITTER_EMAIL": "bot@topequations.local",
            },
        )

        print("Pushing...")
        push_result = subprocess.run(
            ["git", "push"], cwd=str(clone_dir), capture_output=True, text=True,
        )
        if push_result.returncode != 0:
            print(f"ERROR: push failed: {push_result.stderr.strip()[:300]}", file=sys.stderr)
            return False

    print(f"Done: {file_path.name} -> https://github.com/{full_name}/tree/main/{folder}/")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Push a research artifact to an equation's dedicated repo (with content moderation).",
    )
    parser.add_argument("--equation-id", required=True, help="Equation ID (e.g. eq-arp-redshift)")
    parser.add_argument("--file", required=True, help="Path to the file to push")
    parser.add_argument("--folder", required=True, choices=sorted(ALLOWED_FOLDERS),
                        help="Target folder in the equation repo")
    parser.add_argument("--message", "-m", help="Custom commit message")
    parser.add_argument("--dry-run", action="store_true", help="Check moderation but don't push")
    args = parser.parse_args()

    file_path = Path(args.file).resolve()
    ok = push_file(args.equation_id, file_path, args.folder, args.message, args.dry_run)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
