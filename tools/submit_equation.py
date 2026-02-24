from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SUBMISSIONS_JSON = REPO / "data" / "submissions.json"
SUBMISSIONS_DIR = REPO / "submissions"


def _today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _slug(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:48] or "equation"


def _load_json(path: Path, default: dict) -> dict:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _save_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _append_daily_markdown(entry: dict) -> None:
    SUBMISSIONS_DIR.mkdir(parents=True, exist_ok=True)
    day_path = SUBMISSIONS_DIR / f"{entry['submittedAt']}.md"
    if not day_path.exists():
        day_path.write_text(
            f"# Submissions — {entry['submittedAt']}\n\n## Daily Equation Advancement\n\n",
            encoding="utf-8",
        )

    assumptions = entry.get("assumptions", [])
    assumptions_text = "; ".join(assumptions) if assumptions else "(none listed)"
    evidence = entry.get("evidence", [])
    evidence_text = "; ".join(evidence) if evidence else "(none listed)"

    block = (
        f"### {entry['name']}\n"
        f"- Submission ID: {entry['submissionId']}\n"
        f"- Name: {entry['name']}\n"
        f"- Source: {entry['source']}\n"
        f"- Units: {entry['units']}\n"
        f"- Theory: {entry['theory']}\n"
        f"- Description: {entry['description']}\n"
        f"- Equation: {entry['equationLatex']}\n"
        f"- Assumptions: {assumptions_text}\n"
        f"- Evidence: {evidence_text}\n"
        f"- Animation: {entry['animation']['status']}\n"
        f"- Image: {entry['image']['status']}\n"
        f"- Status: {entry['status']}\n\n"
    )
    with day_path.open("a", encoding="utf-8") as f:
        f.write(block)


def main() -> None:
    ap = argparse.ArgumentParser(description="Submit an equation into TopEquations review queue")
    ap.add_argument("--name", required=True)
    ap.add_argument("--equation", required=True, help="LaTeX equation form")
    ap.add_argument("--description", required=True)
    ap.add_argument("--source", default="manual submission")
    ap.add_argument("--units", default="TBD")
    ap.add_argument("--theory", default="PASS-WITH-ASSUMPTIONS")
    ap.add_argument("--submitter", default="local")
    ap.add_argument("--assumption", action="append", default=[])
    ap.add_argument("--evidence", action="append", default=[], help="Validation evidence item (URL, tx hash, run log, screenshot path)")
    args = ap.parse_args()

    submitted_at = _today()
    submission_id = f"sub-{submitted_at}-{_slug(args.name)}"

    db = _load_json(
        SUBMISSIONS_JSON,
        {
            "schemaVersion": 1,
            "lastUpdated": submitted_at,
            "entries": [],
        },
    )

    existing_ids = {str(e.get("submissionId")) for e in db.get("entries", [])}
    i = 2
    base_id = submission_id
    while submission_id in existing_ids:
        submission_id = f"{base_id}-{i}"
        i += 1

    entry = {
        "submissionId": submission_id,
        "submittedAt": submitted_at,
        "submitter": args.submitter,
        "status": "pending",
        "name": args.name.strip(),
        "equationLatex": args.equation.strip(),
        "description": args.description.strip(),
        "source": args.source.strip(),
        "units": args.units.strip(),
        "theory": args.theory.strip(),
        "assumptions": [a.strip() for a in args.assumption if a.strip()],
        "evidence": [x.strip() for x in args.evidence if x.strip()],
        "animation": {"status": "planned", "path": ""},
        "image": {"status": "planned", "path": ""},
        "review": {},
    }

    db.setdefault("entries", []).append(entry)
    db["lastUpdated"] = submitted_at
    _save_json(SUBMISSIONS_JSON, db)
    _append_daily_markdown(entry)

    print(f"submitted: {submission_id}")
    print(f"queue file: {SUBMISSIONS_JSON}")


if __name__ == "__main__":
    main()
