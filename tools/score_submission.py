from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SUBMISSIONS_JSON = REPO / "data" / "submissions.json"
EQUATIONS_JSON = REPO / "data" / "equations.json"


def _today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _save(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _clamp(v: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, int(v)))


def _heuristic(entry: dict) -> dict[str, int]:
    eq = str(entry.get("equationLatex", ""))
    low = eq.lower()

    # --- Tractability (0-20) ---
    tract = 16
    if len(eq) > 300:
        tract -= 3
    elif len(eq) > 180:
        tract -= 1
    if "\\int" in low or "\\sum" in low:
        tract += 1  # structured operations are good
    if "=" in eq:
        tract += 1
    unique_cmds = len(set(re.findall(r'\\[a-zA-Z]+', eq)))
    if unique_cmds >= 4:
        tract += 1

    # --- Plausibility (0-20) ---
    plaus = 16
    if "\\frac" in low or "\\partial" in low or "\\nabla" in low:
        plaus += 2
    if any(tok in low for tok in ["sin", "cos", "exp", "log"]):
        plaus += 1
    if len(eq) > 40:
        plaus += 1  # non-trivial equation

    # --- Validation (0-20) ---
    validation = 8
    assumptions = entry.get("assumptions", []) or []
    if assumptions:
        validation += min(4, len(assumptions))

    evidence = entry.get("evidence", []) or []
    has_dimensional = any(
        "dimension" in str(e).lower() or "unit" in str(e).lower()
        for e in evidence
    )
    if str(entry.get("units", "")).upper() == "OK" and has_dimensional:
        validation += 2

    has_external = any(
        any(kw in str(e).lower() for kw in ["peer", "journal", "arxiv", "doi", "experiment", "replicat"])
        for e in evidence
    )
    if evidence:
        if has_external:
            validation += min(6, len(evidence) * 2)
        else:
            validation += min(4, len(evidence))

    # --- Artifact Completeness (0-10) ---
    artifact = 4
    animation = (entry.get("animation", {}) or {}).get("status", "planned")
    image = (entry.get("image", {}) or {}).get("status", "planned")
    if str(animation).lower() not in ("planned", ""):
        artifact += 3
    if str(image).lower() not in ("planned", ""):
        artifact += 3

    # Penalize if no equals sign (not a proper equation)
    if "=" not in eq:
        tract -= 3
        plaus -= 2

    # --- Novelty (0-30) ---
    novelty = 16
    if unique_cmds >= 8:
        novelty += 6
    elif unique_cmds >= 6:
        novelty += 4
    elif unique_cmds >= 4:
        novelty += 2
    if len(assumptions) >= 3:
        novelty += 3
    elif len(assumptions) >= 2:
        novelty += 2
    elif len(assumptions) >= 1:
        novelty += 1
    if has_external:
        novelty += 2
    # Reward structurally rich equations
    if len(eq) > 80 and unique_cmds >= 5:
        novelty += 2

    tract = _clamp(tract, 0, 20)
    plaus = _clamp(plaus, 0, 20)
    validation = _clamp(validation, 0, 20)
    artifact = _clamp(artifact, 0, 10)
    novelty = _clamp(novelty, 0, 30)

    total = tract + plaus + validation + artifact + novelty
    return {
        "tractability": tract,
        "plausibility": plaus,
        "validation": validation,
        "artifactCompleteness": artifact,
        "novelty": novelty,
        "score": total,
    }


def _pick_entries(data: dict, submission_id: str | None, all_pending: bool, include_promoted: bool) -> list[dict]:
    entries = list(data.get("entries", []))
    if submission_id:
        return [e for e in entries if str(e.get("submissionId")) == submission_id]
    if all_pending:
        if include_promoted:
            return entries
        return [e for e in entries if str(e.get("status", "pending")).lower() == "pending"]
    for e in reversed(entries):
        status = str(e.get("status", "pending")).lower()
        if include_promoted and status in ("pending", "needs-review", "ready", "promoted"):
            return [e]
        if status == "pending":
            return [e]
    return []


def _sync_equation_score(submission: dict, metrics: dict[str, int]) -> bool:
    review = submission.get("review", {}) or {}
    eq_id = str(review.get("equationId", "")).strip()
    eq_data = _load(EQUATIONS_JSON)

    # Fallback if equationId is missing in review (older records).
    if not eq_id:
        sub_name = str(submission.get("name", "")).strip()
        for row in eq_data.get("entries", []):
            if str(row.get("name", "")).strip() == sub_name:
                eq_id = str(row.get("id", "")).strip()
                break
        if not eq_id:
            return False

    updated = False
    for row in eq_data.get("entries", []):
        if str(row.get("id", "")).strip() == eq_id:
            row["score"] = metrics["score"]
            row["scores"] = {
                "tractability": metrics["tractability"],
                "plausibility": metrics["plausibility"],
                "validation": metrics["validation"],
                "artifactCompleteness": metrics["artifactCompleteness"],
            }
            row["tags"] = row.get("tags", {}) or {}
            row["tags"]["novelty"] = {
                "score": metrics["novelty"],
                "date": _today(),
            }
            updated = True
            break

    if updated:
        review = submission.get("review", {}) or {}
        review["equationId"] = eq_id
        submission["review"] = review
        eq_data["lastUpdated"] = _today()
        _save(EQUATIONS_JSON, eq_data)
    return updated


def main() -> None:
    ap = argparse.ArgumentParser(description="Heuristically score pending submissions")
    ap.add_argument("--submission-id", default="")
    ap.add_argument("--all-pending", action="store_true")
    ap.add_argument("--mark-ready-threshold", type=int, default=65)
    ap.add_argument("--include-promoted", action="store_true", help="Allow rescoring submissions already promoted")
    ap.add_argument("--sync-equations", action="store_true", help="When rescoring promoted submissions, sync score back to equations.json")
    args = ap.parse_args()

    data = _load(SUBMISSIONS_JSON)
    targets = _pick_entries(data, args.submission_id.strip() or None, args.all_pending, args.include_promoted)
    if not targets:
        raise SystemExit("no matching pending submission found")

    count = 0
    eq_sync = 0
    for e in targets:
        status = str(e.get("status", "")).lower()
        if status == "promoted" and not args.include_promoted:
            continue
        metrics = _heuristic(e)
        score = metrics["score"]
        prior_review = e.get("review", {}) or {}
        prior_eqid = str(prior_review.get("equationId", "")).strip()
        e["review"] = {
            "date": _today(),
            "equationId": prior_eqid,
            "score": score,
            "scores": {
                "tractability": metrics["tractability"],
                "plausibility": metrics["plausibility"],
                "validation": metrics["validation"],
                "artifactCompleteness": metrics["artifactCompleteness"],
            },
            "novelty": metrics["novelty"],
            "method": "heuristic-v1",
        }
        if status != "promoted":
            e["status"] = "ready" if score >= args.mark_ready_threshold else "needs-review"
        if status == "promoted" and args.sync_equations:
            if _sync_equation_score(e, metrics):
                eq_sync += 1
        count += 1
        print(f"scored: {e.get('submissionId')} score={score} status={e.get('status')}")

    data["lastUpdated"] = _today()
    _save(SUBMISSIONS_JSON, data)
    print(f"updated submissions: {count}")
    if args.sync_equations:
        print(f"synced equations: {eq_sync}")


if __name__ == "__main__":
    main()
