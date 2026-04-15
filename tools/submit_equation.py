from __future__ import annotations

import argparse
import json
import re
import unicodedata
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SUBMISSIONS_JSON = REPO / "data" / "submissions.json"
EQUATIONS_JSON = REPO / "data" / "equations.json"
SUBMISSIONS_DIR = REPO / "submissions"


def _today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _slug(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:48] or "equation"


def _normalize_text(s: str) -> str:
    s = unicodedata.normalize("NFKC", s or "")
    s = s.lower().strip()
    return re.sub(r"\s+", " ", s)


_TEX_COMMAND_ESCAPE_RE = re.compile(r"\\\\(?=[A-Za-z!,:;|])")


def _normalize_texish_text(s: str) -> str:
    s = unicodedata.normalize("NFKC", s or "").strip()
    while True:
        normalized = _TEX_COMMAND_ESCAPE_RE.sub(lambda _: "\\", s)
        if normalized == s:
            return normalized
        s = normalized


def _normalize_texish_list(values: object) -> list[str]:
    if not isinstance(values, list):
        return []

    normalized_values: list[str] = []
    for value in values:
        cleaned = _normalize_texish_text(str(value))
        if cleaned:
            normalized_values.append(cleaned)
    return normalized_values


def _load_json(path: Path, default: dict) -> dict:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _save_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _find_duplicate_warnings(db: dict, equations: dict, name: str, equation_latex: str) -> list[str]:
    warnings: list[str] = []
    normalized_name = _normalize_text(name)
    normalized_equation = _normalize_text(equation_latex)

    promoted_name_matches = [
        str(e.get("id", "")).strip()
        for e in equations.get("entries", [])
        if _normalize_text(str(e.get("name", ""))) == normalized_name
    ]
    if promoted_name_matches:
        warnings.append(
            "Exact name match with promoted equation(s): " + ", ".join(promoted_name_matches[:5])
        )

    promoted_equation_matches = [
        str(e.get("id", "")).strip()
        for e in equations.get("entries", [])
        if normalized_equation and _normalize_text(str(e.get("equationLatex", ""))) == normalized_equation
    ]
    if promoted_equation_matches:
        warnings.append(
            "Exact equation match with promoted equation(s): " + ", ".join(promoted_equation_matches[:5])
        )

    pending_matches = [
        str(e.get("submissionId", "")).strip()
        for e in db.get("entries", [])
        if _normalize_text(str(e.get("name", ""))) == normalized_name
        and str(e.get("status", "")).lower() != "promoted"
    ]
    if pending_matches:
        warnings.append(
            "Exact name match with existing submission(s): " + ", ".join(pending_matches[:5])
        )

    return warnings


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
    ap.add_argument("--animation-status", default="planned")
    ap.add_argument("--animation-path", default="")
    ap.add_argument("--image-status", default="planned")
    ap.add_argument("--image-path", default="")
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
    equations = _load_json(EQUATIONS_JSON, {"entries": []})

    existing_ids = {str(e.get("submissionId")) for e in db.get("entries", [])}
    i = 2
    base_id = submission_id
    while submission_id in existing_ids:
        submission_id = f"{base_id}-{i}"
        i += 1

    equation = _normalize_texish_text(args.equation)
    description = _normalize_texish_text(args.description)
    assumptions = _normalize_texish_list(args.assumption)
    evidence = _normalize_texish_list(args.evidence)

    duplicate_warnings = _find_duplicate_warnings(db, equations, args.name.strip(), equation)

    entry = {
        "submissionId": submission_id,
        "submittedAt": submitted_at,
        "submitter": args.submitter,
        "status": "pending",
        "name": args.name.strip(),
        "equationLatex": equation,
        "description": description,
        "source": args.source.strip(),
        "units": args.units.strip(),
        "theory": args.theory.strip(),
        "assumptions": assumptions,
        "evidence": evidence,
        "animation": {
            "status": args.animation_status.strip(),
            "path": args.animation_path.strip(),
        },
        "image": {
            "status": args.image_status.strip(),
            "path": args.image_path.strip(),
        },
        "duplicateWarnings": duplicate_warnings,
        "review": {},
    }

    db.setdefault("entries", []).append(entry)
    db["lastUpdated"] = submitted_at
    _save_json(SUBMISSIONS_JSON, db)
    _append_daily_markdown(entry)

    print(f"submitted: {submission_id}")
    print(f"queue file: {SUBMISSIONS_JSON}")
    for warning in duplicate_warnings:
        print(f"duplicate-warning: {warning}")


if __name__ == "__main__":
    main()
