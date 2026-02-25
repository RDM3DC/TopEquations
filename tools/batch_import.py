"""Batch-import equations from a JSON file into the submission queue.

Usage:
  python tools/batch_import.py submissions/incoming/grok_batch.json
  python tools/batch_import.py submissions/incoming/grok_batch.json --score --promote

The input file should be a JSON array of objects, each with at minimum:
  - name          (string, required)
  - equation      (string, LaTeX, required)
  - description   (string, required)

Optional fields (sensible defaults are used when omitted):
  - source        (string, default "external-agent")
  - submitter     (string, default "external")
  - units         (string, default "TBD")
  - theory        (string, default "PASS-WITH-ASSUMPTIONS")
  - assumptions   (list of strings)
  - evidence      (list of strings)

After import, each entry lands in data/submissions.json as status=pending.
Pass --score to auto-score every imported submission.
Pass --promote to also promote anything that meets threshold.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SUBMIT_SCRIPT = REPO / "tools" / "submit_equation.py"
SCORE_SCRIPT = REPO / "tools" / "score_submission.py"
PROMOTE_SCRIPT = REPO / "tools" / "promote_submission.py"


def main() -> None:
    ap = argparse.ArgumentParser(description="Batch-import equations from a JSON array file")
    ap.add_argument("file", type=Path, help="Path to JSON array file")
    ap.add_argument("--score", action="store_true", help="Auto-score after import")
    ap.add_argument("--promote", action="store_true", help="Auto-promote ready submissions after scoring")
    ap.add_argument("--source", default=None, help="Override source tag for all entries")
    ap.add_argument("--submitter", default=None, help="Override submitter for all entries")
    args = ap.parse_args()

    data = json.loads(args.file.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        print("error: input file must contain a JSON array of submission objects")
        sys.exit(1)

    imported_ids: list[str] = []
    for i, entry in enumerate(data):
        name = entry.get("name", "").strip()
        equation = entry.get("equation", "").strip()
        description = entry.get("description", "").strip()

        if not name or not equation or not description:
            print(f"skip [{i}]: missing name, equation, or description")
            continue

        cmd = [
            sys.executable, str(SUBMIT_SCRIPT),
            "--name", name,
            "--equation", equation,
            "--description", description,
            "--source", args.source or entry.get("source", "external-agent"),
            "--submitter", args.submitter or entry.get("submitter", "external"),
            "--units", entry.get("units", "TBD"),
            "--theory", entry.get("theory", "PASS-WITH-ASSUMPTIONS"),
        ]
        for assumption in entry.get("assumptions", []):
            if assumption.strip():
                cmd.extend(["--assumption", assumption.strip()])
        for evidence in entry.get("evidence", []):
            if evidence.strip():
                cmd.extend(["--evidence", evidence.strip()])

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"fail [{i}] {name}: {result.stderr.strip()}")
            continue

        # Parse submission ID from output like "submitted: sub-2026-02-24-name"
        for line in result.stdout.splitlines():
            if line.startswith("submitted:"):
                sid = line.split(":", 1)[1].strip()
                imported_ids.append(sid)
                print(f"imported: {sid}")
                break

    print(f"\nimported {len(imported_ids)} of {len(data)} entries")

    if not imported_ids:
        return

    if args.score:
        print("\n--- scoring ---")
        for sid in imported_ids:
            result = subprocess.run(
                [sys.executable, str(SCORE_SCRIPT), "--submission-id", sid],
                capture_output=True, text=True,
            )
            for line in result.stdout.splitlines():
                if "score=" in line or "status=" in line:
                    print(line)

    if args.promote:
        print("\n--- promoting ready ---")
        for sid in imported_ids:
            result = subprocess.run(
                [sys.executable, str(PROMOTE_SCRIPT), "--submission-id", sid, "--from-review"],
                capture_output=True, text=True,
            )
            out = result.stdout.strip()
            if out:
                print(out)
            elif result.returncode != 0:
                err = result.stderr.strip().split("\n")[-1] if result.stderr.strip() else "not eligible"
                print(f"skip {sid}: {err}")


if __name__ == "__main__":
    main()
