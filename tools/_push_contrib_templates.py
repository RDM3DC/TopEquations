"""Push a CONTRIBUTING guide + GitHub Issue template to every equation repo.

One-time script. For each equation repo under RDM3DC/:
  1. Clones the repo
  2. Adds .github/ISSUE_TEMPLATE/artifact_submission.yml
  3. Adds a 'Contributing' section to the README
  4. Commits and pushes

Usage:
    python tools/_push_contrib_templates.py
    python tools/_push_contrib_templates.py --dry-run
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GITHUB_ORG = "RDM3DC"

ISSUE_TEMPLATE = """\
name: Add Research Artifact
description: Submit an image, derivation, simulation, data file, or note for this equation.
title: "Add: [brief description]"
labels: ["artifact-submission"]
body:
  - type: markdown
    attributes:
      value: |
        Thanks for contributing! Attach your file(s) and fill in the details below.

  - type: input
    id: folder
    attributes:
      label: Target folder
      description: Where should this file go?
      placeholder: "images / derivations / simulations / data / notes / docs"
    validations:
      required: true

  - type: textarea
    id: description
    attributes:
      label: What is this?
      description: Briefly describe what you're contributing and how it relates to the equation.
      placeholder: "Phase portrait generated from numerical integration of the ODE with scipy..."
    validations:
      required: true

  - type: input
    id: submitter
    attributes:
      label: Your name or agent ID
      placeholder: "e.g. claude-anthropic, ryan, grok-xai"
    validations:
      required: false

  - type: textarea
    id: files
    attributes:
      label: Files
      description: Drag and drop your files here, or paste links to them.
      placeholder: "Drag files here..."
    validations:
      required: true

  - type: checkboxes
    id: confirm
    attributes:
      label: Confirmation
      options:
        - label: This content is relevant to the equation and contains no explicit, violent, or hateful material.
          required: true
"""

CONTRIB_SECTION = """
## Contributing

You can add images, derivations, simulations, data, or notes to this repo:

| Folder | What goes here |
|--------|---------------|
| `images/` | Plots, diagrams, phase portraits, animations (.png, .jpg, .mp4, ...) |
| `derivations/` | Step-by-step derivations and proofs (.tex, .md, .pdf) |
| `simulations/` | Computational models and code (.py, .ipynb, .jl, .m) |
| `data/` | Numerical results, experimental measurements (.csv, .hdf5, .npy) |
| `notes/` | Research notes, lit reviews, references (.md, .bib, .txt) |
| `docs/` | Formal documents, validation plans (.md, .pdf) |

**Three ways to contribute:**
1. **GitHub Issue** — click [New Issue](../../issues/new?template=artifact_submission.yml) and attach your file
2. **Pull Request** — fork, add files, open a PR
3. **CLI** — `python tools/push_to_equation_repo.py --equation-id {eq_id} --file <path> --folder <folder>`

All submissions are content-moderated. See the [full contributing guide](https://github.com/RDM3DC/TopEquations/blob/main/CONTRIBUTING.md).
"""


def _load_all_equations() -> list[tuple[str, str]]:
    """Return list of (equation_id, equation_name) across all tiers."""
    results = []
    for path, _tier in [
        (REPO / "data" / "equations.json", "derived"),
        (REPO / "data" / "core.json", "core"),
        (REPO / "data" / "famous_equations.json", "famous"),
    ]:
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        for e in data.get("entries", []):
            eid = e.get("id", "")
            name = e.get("name", "")
            if eid:
                results.append((eid, name))
    return results


def _repo_exists(repo_name: str) -> bool:
    result = subprocess.run(
        ["gh", "repo", "view", f"{GITHUB_ORG}/{repo_name}", "--json", "name"],
        capture_output=True, text=True,
    )
    return result.returncode == 0


def _process_repo(eq_id: str, eq_name: str, dry_run: bool) -> bool:
    import re
    repo_name = re.sub(r"[^a-z0-9-]", "-", eq_id.lower())
    repo_name = re.sub(r"-+", "-", repo_name).strip("-")
    full_name = f"{GITHUB_ORG}/{repo_name}"

    if not _repo_exists(repo_name):
        print(f"  SKIP (no repo): {full_name}")
        return False

    if dry_run:
        print(f"  DRY RUN: would update {full_name}")
        return True

    with tempfile.TemporaryDirectory() as tmp:
        clone_dir = Path(tmp) / repo_name
        result = subprocess.run(
            ["git", "clone", f"https://github.com/{full_name}.git", str(clone_dir)],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            print(f"  FAIL clone: {result.stderr.strip()[:200]}")
            return False

        # 1. Add issue template
        template_dir = clone_dir / ".github" / "ISSUE_TEMPLATE"
        template_dir.mkdir(parents=True, exist_ok=True)
        (template_dir / "artifact_submission.yml").write_text(ISSUE_TEMPLATE, encoding="utf-8")

        # 2. Update README with Contributing section (if not already there)
        readme_path = clone_dir / "README.md"
        if readme_path.exists():
            readme = readme_path.read_text(encoding="utf-8")
        else:
            readme = f"# {eq_name}\n\n**ID:** `{eq_id}`\n"

        if "## Contributing" not in readme:
            section = CONTRIB_SECTION.replace("{eq_id}", eq_id)
            # Insert before the final "---" or at end
            if readme.rstrip().endswith("---"):
                readme = readme.rstrip().rstrip("-").rstrip() + "\n" + section + "\n---\n"
            else:
                readme = readme.rstrip() + "\n" + section
            readme_path.write_text(readme, encoding="utf-8")

        # 3. Commit and push
        subprocess.run(["git", "add", "-A"], cwd=str(clone_dir), capture_output=True)
        status = subprocess.run(
            ["git", "status", "--porcelain"], cwd=str(clone_dir),
            capture_output=True, text=True,
        )
        if not status.stdout.strip():
            print(f"  no changes: {full_name}")
            return True

        subprocess.run(
            ["git", "commit", "-m", "Add contributing guide and artifact submission template"],
            cwd=str(clone_dir), capture_output=True,
            env={
                **os.environ,
                "GIT_AUTHOR_NAME": "TopEquations Bot",
                "GIT_COMMITTER_NAME": "TopEquations Bot",
                "GIT_AUTHOR_EMAIL": "bot@topequations.local",
                "GIT_COMMITTER_EMAIL": "bot@topequations.local",
            },
        )
        push_result = subprocess.run(
            ["git", "push"], cwd=str(clone_dir), capture_output=True, text=True,
        )
        if push_result.returncode != 0:
            print(f"  FAIL push: {push_result.stderr.strip()[:200]}")
            return False

    print(f"  updated: {full_name}")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    equations = _load_all_equations()
    print(f"Found {len(equations)} equations\n")

    ok = fail = skip = 0
    for eq_id, eq_name in equations:
        print(f"{eq_id}:")
        result = _process_repo(eq_id, eq_name, args.dry_run)
        if result:
            ok += 1
        else:
            fail += 1

    print(f"\nDone: {ok} updated, {fail} failed/skipped")


if __name__ == "__main__":
    main()
