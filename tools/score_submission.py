from __future__ import annotations

import argparse
import json
import os
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


def _run_llm_scoring(entry: dict, api_key: str, api_base: str, model: str) -> dict | None:
    """Run LLM advisory scoring via llm_score_submission module."""
    from llm_score_submission import score_submission as llm_score
    return llm_score(entry, api_key, api_base, model)


def _blend(heuristic_total: int, llm_total: int) -> int:
    """40% heuristic + 60% LLM."""
    return int(round(0.4 * heuristic_total + 0.6 * llm_total))


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
            if "llm_scores" in metrics:
                row["tags"]["llm"] = metrics["llm_scores"]
            if "blended_score" in metrics:
                row["score"] = metrics["blended_score"]
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
    ap = argparse.ArgumentParser(description="Score pending submissions (heuristic + optional LLM)")
    ap.add_argument("--submission-id", default="")
    ap.add_argument("--all-pending", action="store_true")
    ap.add_argument("--mark-ready-threshold", type=int, default=65)
    ap.add_argument("--include-promoted", action="store_true", help="Allow rescoring submissions already promoted")
    ap.add_argument("--sync-equations", action="store_true", help="When rescoring promoted submissions, sync score back to equations.json")
    ap.add_argument("--llm", action="store_true", help="Run LLM advisory scoring and compute blended score (40%% heuristic + 60%% LLM)")
    ap.add_argument("--llm-model", default=os.environ.get("LLM_SCORE_MODEL", "gpt-4o-mini"))
    ap.add_argument("--llm-api-base", default=os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1"))
    ap.add_argument("--manual-score", type=int, default=-1, help="Override final score with a manual value (0-100)")
    args = ap.parse_args()

    api_key = os.environ.get("OPENAI_API_KEY", "")
    if args.llm and not api_key:
        raise SystemExit("Set OPENAI_API_KEY environment variable for --llm scoring")

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
        heuristic_score = metrics["score"]
        method = "heuristic-v2"

        # LLM advisory layer
        llm_scores = None
        blended = None
        if args.llm:
            llm_scores = _run_llm_scoring(e, api_key, args.llm_api_base, args.llm_model)
            if llm_scores:
                blended = _blend(heuristic_score, llm_scores["llm_total"])
                metrics["llm_scores"] = llm_scores
                metrics["blended_score"] = blended
                method = f"blended-v1 ({args.llm_model})"
                print(f"  llm: {llm_scores['llm_total']} blended: {blended} ({llm_scores.get('justification', '')})")
            else:
                print(f"  llm: FAILED — using heuristic only")

        # Manual override takes precedence over everything
        if args.manual_score >= 0:
            final_score = _clamp(args.manual_score, 0, 100)
            method = "manual-override"
        elif blended is not None:
            final_score = blended
        else:
            final_score = heuristic_score

        metrics["score"] = final_score

        prior_review = e.get("review", {}) or {}
        prior_eqid = str(prior_review.get("equationId", "")).strip()
        review = {
            "date": _today(),
            "equationId": prior_eqid,
            "score": final_score,
            "heuristic_score": heuristic_score,
            "scores": {
                "tractability": metrics["tractability"],
                "plausibility": metrics["plausibility"],
                "validation": metrics["validation"],
                "artifactCompleteness": metrics["artifactCompleteness"],
            },
            "novelty": metrics["novelty"],
            "method": method,
        }
        if llm_scores:
            review["llm_scores"] = llm_scores
            review["llm_model"] = args.llm_model
            review["blended_score"] = blended
        if args.manual_score >= 0:
            review["manual_score"] = args.manual_score
        e["review"] = review

        if status != "promoted":
            e["status"] = "ready" if final_score >= args.mark_ready_threshold else "needs-review"
        if status == "promoted" and args.sync_equations:
            if _sync_equation_score(e, metrics):
                eq_sync += 1
        count += 1
        print(f"scored: {e.get('submissionId')} score={final_score} (h={heuristic_score}) status={e.get('status')}")

    data["lastUpdated"] = _today()
    _save(SUBMISSIONS_JSON, data)
    print(f"updated submissions: {count}")
    if args.sync_equations:
        print(f"synced equations: {eq_sync}")


if __name__ == "__main__":
    main()
