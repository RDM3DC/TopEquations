"""Create a dedicated GitHub repository for an equation.

Each equation gets its own repo under RDM3DC/ for storing images, derivations,
simulations, and discussion. The main TopEquations repo links out to each.

Usage:
    python tools/create_equation_repo.py --equation-id eq-arp-redshift
    python tools/create_equation_repo.py --all --tier derived
    python tools/create_equation_repo.py --all --tier core
    python tools/create_equation_repo.py --all

Requires: gh CLI authenticated (gh auth login)
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GITHUB_ORG = "RDM3DC"


def _load(path: Path) -> dict:
    if not path.exists():
        return {"entries": []}
    return json.loads(path.read_text(encoding="utf-8"))


def _save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _slug(equation_id: str) -> str:
    """Convert equation ID to a valid GitHub repo name."""
    # eq-arp-redshift -> eq-arp-redshift (already fine)
    # core-phase-ambiguity -> core-phase-ambiguity
    slug = re.sub(r"[^a-z0-9-]", "-", equation_id.lower())
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug


def _repo_name(equation_id: str) -> str:
    return _slug(equation_id)


def _repo_exists(repo_name: str) -> bool:
    result = subprocess.run(
        ["gh", "repo", "view", f"{GITHUB_ORG}/{repo_name}", "--json", "name"],
        capture_output=True, text=True,
    )
    return result.returncode == 0


def _build_readme(entry: dict, tier: str) -> str:
    name = entry.get("name", "Unnamed Equation")
    eq_id = entry.get("id", "")
    latex = entry.get("equationLatex", entry.get("equation", ""))
    desc = entry.get("description", "")
    score = entry.get("score", "")
    subtitle = entry.get("subtitle", "")

    # Get assumptions and evidence if available
    assumptions = entry.get("assumptions", []) or []
    evidence = entry.get("evidence", []) or []
    units = entry.get("units", "")
    theory = entry.get("theory", "")

    lines = [
        f"# {name}",
        "",
    ]
    if subtitle:
        lines.append(f"*{subtitle}*")
        lines.append("")

    lines.extend([
        f"**ID:** `{eq_id}`  ",
        f"**Tier:** {tier}  ",
    ])
    if score:
        lines.append(f"**Score:** {score}  ")
    if units:
        lines.append(f"**Units:** {units}  ")
    if theory:
        lines.append(f"**Theory:** {theory}  ")

    lines.extend([
        "",
        "## Equation",
        "",
        "$$",
        latex,
        "$$",
        "",
    ])

    if desc:
        lines.extend([
            "## Description",
            "",
            desc,
            "",
        ])

    if assumptions:
        lines.extend(["## Assumptions", ""])
        for a in assumptions:
            lines.append(f"- {a}")
        lines.append("")

    if evidence:
        lines.extend(["## Evidence", ""])
        for e in evidence:
            if isinstance(e, dict):
                lines.append(f"- {e.get('label', str(e))}")
            else:
                lines.append(f"- {e}")
        lines.append("")

    lines.extend([
        "## Repository Structure",
        "",
        "```",
        "images/       # Visualizations, plots, diagrams",
        "derivations/  # Step-by-step derivations and proofs",
        "simulations/  # Computational models and code",
        "data/         # Numerical data, experimental results",
        "notes/        # Research notes and references",
        "```",
        "",
        "## Links",
        "",
        f"- [TopEquations Leaderboard](https://rdm3dc.github.io/TopEquations/leaderboard.html)",
        f"- [TopEquations Main Repo](https://github.com/{GITHUB_ORG}/TopEquations)",
        f"- [Certificates](https://rdm3dc.github.io/TopEquations/certificates.html)",
        "",
        "---",
        f"*Part of the [TopEquations](https://github.com/{GITHUB_ORG}/TopEquations) project.*",
        "",
    ])

    return "\n".join(lines)


def _create_repo(entry: dict, tier: str, dry_run: bool = False) -> str | None:
    eq_id = entry.get("id", "")
    repo_name = _repo_name(eq_id)
    full_name = f"{GITHUB_ORG}/{repo_name}"
    name = entry.get("name", "Unnamed")

    if _repo_exists(repo_name):
        print(f"  exists: {full_name}")
        return f"https://github.com/{full_name}"

    if dry_run:
        safe_name = name.encode("ascii", errors="replace").decode("ascii")
        print(f"  would create: {full_name} -- {safe_name}")
        return None

    desc = f"TopEquations: {name}"[:350]

    # Create the repo
    result = subprocess.run(
        [
            "gh", "repo", "create", full_name,
            "--public",
            "--description", desc,
            "--clone=false",
        ],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"  FAILED to create {full_name}: {result.stderr.strip()[:200]}", file=sys.stderr)
        return None

    print(f"  created: {full_name}")

    # Initialize with README and folder structure via a temp clone
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp) / repo_name
        subprocess.run(
            ["git", "clone", f"https://github.com/{full_name}.git", str(tmp_path)],
            capture_output=True, text=True,
        )

        # Write README
        readme = _build_readme(entry, tier)
        (tmp_path / "README.md").write_text(readme, encoding="utf-8")

        # Create folder structure with .gitkeep files
        for folder in ["images", "derivations", "simulations", "data", "notes"]:
            (tmp_path / folder).mkdir(exist_ok=True)
            (tmp_path / folder / ".gitkeep").write_text("", encoding="utf-8")

        # Commit and push
        subprocess.run(["git", "add", "-A"], cwd=str(tmp_path), capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", f"Initialize equation repo: {name}"],
            cwd=str(tmp_path), capture_output=True,
            env={**__import__("os").environ, "GIT_AUTHOR_NAME": "TopEquations Bot",
                 "GIT_COMMITTER_NAME": "TopEquations Bot",
                 "GIT_AUTHOR_EMAIL": "bot@topequations.local",
                 "GIT_COMMITTER_EMAIL": "bot@topequations.local"},
        )
        push_result = subprocess.run(
            ["git", "push", "origin", "main"],
            cwd=str(tmp_path), capture_output=True, text=True,
        )
        # Some repos default to 'master'
        if push_result.returncode != 0:
            subprocess.run(
                ["git", "push", "origin", "HEAD"],
                cwd=str(tmp_path), capture_output=True, text=True,
            )

    repo_url = f"https://github.com/{full_name}"
    print(f"  initialized: {repo_url}")
    return repo_url


def _find_entry(equation_id: str) -> tuple[dict, str] | None:
    """Find an equation by ID across all data files. Returns (entry, tier)."""
    for path, tier in [
        (REPO / "data" / "equations.json", "derived"),
        (REPO / "data" / "core.json", "core"),
        (REPO / "data" / "famous_equations.json", "famous"),
    ]:
        data = _load(path)
        for e in data.get("entries", []):
            if e.get("id") == equation_id:
                return e, tier
    return None


def _all_entries(tier_filter: str | None) -> list[tuple[dict, str, Path]]:
    """Get all entries, optionally filtered by tier."""
    results = []
    sources = [
        (REPO / "data" / "core.json", "core"),
        (REPO / "data" / "equations.json", "derived"),
        (REPO / "data" / "famous_equations.json", "famous"),
    ]
    for path, tier in sources:
        if tier_filter and tier != tier_filter:
            continue
        data = _load(path)
        for e in data.get("entries", []):
            results.append((e, tier, path))
    return results


def main() -> None:
    ap = argparse.ArgumentParser(description="Create dedicated GitHub repos for equations")
    grp = ap.add_mutually_exclusive_group(required=True)
    grp.add_argument("--equation-id", help="Create repo for a specific equation")
    grp.add_argument("--all", action="store_true", help="Create repos for all equations")
    ap.add_argument("--tier", choices=["core", "derived", "famous"],
                     help="Filter by tier (only with --all)")
    ap.add_argument("--dry-run", action="store_true", help="Show what would be created without doing it")
    ap.add_argument("--update-links", action="store_true",
                     help="Update data files with repoUrl for existing repos")
    args = ap.parse_args()

    created = 0
    updated = 0

    if args.equation_id:
        found = _find_entry(args.equation_id)
        if not found:
            raise SystemExit(f"equation not found: {args.equation_id}")
        entry, tier = found
        url = _create_repo(entry, tier, dry_run=args.dry_run)
        if url:
            entry["repoUrl"] = url
            created += 1
    else:
        entries = _all_entries(args.tier)
        print(f"Processing {len(entries)} equations...")
        for entry, tier, data_path in entries:
            eq_id = entry.get("id", "")
            if not eq_id:
                continue
            print(f"[{tier}] {eq_id}")
            url = _create_repo(entry, tier, dry_run=args.dry_run)
            if url:
                entry["repoUrl"] = url
                created += 1

    # Save updated data files with repoUrl links
    if not args.dry_run and (created > 0 or args.update_links):
        for path, tier in [
            (REPO / "data" / "equations.json", "derived"),
            (REPO / "data" / "core.json", "core"),
            (REPO / "data" / "famous_equations.json", "famous"),
        ]:
            data = _load(path)
            changed = False
            for entry in data.get("entries", []):
                eq_id = entry.get("id", "")
                repo_name = _repo_name(eq_id)
                expected_url = f"https://github.com/{GITHUB_ORG}/{repo_name}"
                if entry.get("repoUrl") != expected_url:
                    if args.update_links or _repo_exists(repo_name):
                        entry["repoUrl"] = expected_url
                        changed = True
                        updated += 1
            if changed:
                _save(path, data)

    print(f"\nDone. Created: {created}, Updated links: {updated}")


if __name__ == "__main__":
    main()
