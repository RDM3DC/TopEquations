from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SUBMISSIONS_JSON = REPO / "data" / "submissions.json"
EQUATIONS_JSON = REPO / "data" / "equations.json"


def _today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _slug(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:56] or "submission"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _save(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _clamp(v: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, int(v)))


def main() -> None:
    ap = argparse.ArgumentParser(description="Promote a pending submission into ranked equations")
    ap.add_argument("--submission-id", required=True)
    ap.add_argument("--tractability", type=int, default=-1)
    ap.add_argument("--plausibility", type=int, default=-1)
    ap.add_argument("--validation", type=int, default=-1)
    ap.add_argument("--artifact", type=int, default=-1, help="Artifact completeness 0-10")
    ap.add_argument("--novelty", type=int, default=-1, help="Novelty tag score")
    ap.add_argument("--from-review", action="store_true", help="Use review scores already stored in submissions.json")
    ap.add_argument("--equation-id", default="", help="Optional override for final equation id")
    ap.add_argument("--manual-score", type=int, default=-1, help="Override final score (0-100)")
    args = ap.parse_args()

    submissions = _load(SUBMISSIONS_JSON)
    equations = _load(EQUATIONS_JSON)

    entry = None
    for e in submissions.get("entries", []):
        if str(e.get("submissionId")) == args.submission_id:
            entry = e
            break

    if not entry:
        raise SystemExit(f"submission not found: {args.submission_id}")
    if str(entry.get("status", "")).lower() == "promoted":
        raise SystemExit(f"submission already promoted: {args.submission_id}")

    if args.from_review:
        review = entry.get("review", {}) or {}
        scores = review.get("scores", {}) or {}
        tract = _clamp(scores.get("tractability", 0), 0, 20)
        plaus = _clamp(scores.get("plausibility", 0), 0, 20)
        validation = _clamp(scores.get("validation", 0), 0, 20)
        artifact = _clamp(scores.get("artifactCompleteness", 0), 0, 10)
        novelty = _clamp(review.get("novelty", 0), 0, 30)
    else:
        if min(args.tractability, args.plausibility, args.validation, args.artifact, args.novelty) < 0:
            raise SystemExit("manual promotion requires --tractability --plausibility --validation --artifact --novelty, or use --from-review")
        tract = _clamp(args.tractability, 0, 20)
        plaus = _clamp(args.plausibility, 0, 20)
        validation = _clamp(args.validation, 0, 20)
        artifact = _clamp(args.artifact, 0, 10)
        novelty = _clamp(args.novelty, 0, 30)

    total = tract + plaus + validation + artifact + novelty

    # Use blended score from review if available, or manual override
    if args.manual_score >= 0:
        total = _clamp(args.manual_score, 0, 100)
    elif args.from_review:
        review = entry.get("review", {}) or {}
        if review.get("blended_score"):
            total = int(review["blended_score"])
        elif review.get("score"):
            total = int(review["score"])

    eid = args.equation_id.strip() or f"eq-{_slug(entry.get('name', 'submission'))}"
    existing_ids = {str(x.get("id")) for x in equations.get("entries", [])}
    if eid in existing_ids:
        eid = f"{eid}-{_slug(args.submission_id)[-8:]}"

    repo_url = f"https://github.com/RDM3DC/{eid}"

    promoted = {
        "id": eid,
        "name": entry.get("name", ""),
        "firstSeen": _today(),
        "source": entry.get("source", "manual submission"),
        "submitter": entry.get("submitter", "unknown"),
        "repoUrl": repo_url,
        "score": total,
        "scores": {
            "tractability": tract,
            "plausibility": plaus,
            "validation": validation,
            "artifactCompleteness": artifact,
        },
        "units": entry.get("units", "TBD"),
        "theory": entry.get("theory", "PASS-WITH-ASSUMPTIONS"),
        "animation": entry.get("animation", {"status": "planned", "path": ""}),
        "image": entry.get("image", {"status": "planned", "path": ""}),
        "description": entry.get("description", ""),
        "assumptions": entry.get("assumptions", []),
        "date": _today(),
        "equationLatex": entry.get("equationLatex", ""),
        "tags": {
            "novelty": {
                "score": novelty,
                "date": _today(),
            }
        },
    }

    equations.setdefault("entries", []).append(promoted)
    equations["lastUpdated"] = _today()

    entry["status"] = "promoted"
    entry["review"] = {
        "date": _today(),
        "equationId": eid,
        "score": total,
        "scores": promoted["scores"],
        "novelty": novelty,
    }
    submissions["lastUpdated"] = _today()

    _save(EQUATIONS_JSON, equations)
    _save(SUBMISSIONS_JSON, submissions)

    print(f"promoted: {args.submission_id} -> {eid} (score {total})")


if __name__ == "__main__":
    main()
