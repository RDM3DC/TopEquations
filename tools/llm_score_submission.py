"""LLM-based quality scorer for equation submissions.

Security design:
  - Runs ONLY on already-validated, parsed data (never raw user input)
  - Fixed prompt template — user fields are injected as quoted values
  - Output is parsed as strict JSON; only numeric scores are extracted
  - LLM score is advisory (recorded alongside heuristic), not a gate
  - Even if a description contains prompt injection, the LLM output
    is clamped to [0, max] ints and cannot affect promotion logic
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError

REPO = Path(__file__).resolve().parents[1]
SUBMISSIONS_JSON = REPO / "data" / "submissions.json"

# Configurable via environment
API_KEY_ENV = "OPENAI_API_KEY"
API_BASE_ENV = "OPENAI_API_BASE"
MODEL_ENV = "LLM_SCORE_MODEL"

DEFAULT_BASE = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = """\
You are a skeptical, rigorous equation reviewer for a scientific leaderboard.
Score the submitted equation on five axes. Be TOUGH. Most submissions should
score 40-70 total. Only landmark results deserve 80+.

CALIBRATION ANCHORS (use these to set your scale):
  Schrodinger equation (i*hbar*d_psi/dt = H*psi): ~85 total
  Euler identity (e^(i*pi)+1=0):                   ~45 total (elegant but no new physics)
  x = x:                                           ~5 total (tautology)
  A well-structured but unverified new PDE:         ~55 total

Axes (integer scores):
  physical_validity  (0-20): Is it dimensionally consistent and physically correct?
      Ask: could you derive this from first principles? Is it a tautology or
      trivial rearrangement? Penalize if units/dimensions are unclear.
      0 = nonsense/tautology, 10 = plausible but unverified, 20 = rigorously derivable
  novelty            (0-20): Is this genuinely new or a known result restated?
      DEFAULT TO LOW. Assume the equation is a restatement of known work unless
      you can confirm otherwise. Renaming variables in a known equation = 2-5.
      0 = textbook standard, 5 = relabeled known result, 10 = meaningful extension,
      15 = novel combination, 20 = fundamentally new insight
  clarity            (0-20): Are all variables defined? Is the notation standard?
      0 = incomprehensible, 10 = readable but some terms undefined, 20 = publication-ready
  evidence_quality   (0-20): Is it backed by INDEPENDENT evidence?
      Self-citations and self-authored whitepapers cap at 10. Only independent
      replication, peer-reviewed references, or verified experimental data can
      score above 10. Listing assumptions alone = 3-5.
      0 = nothing, 5 = assumptions only, 10 = self-authored proof, 15 = independent
      confirmation, 20 = peer-reviewed + experimental
  significance       (0-20): How impactful is this if correct?
      Most niche results = 5-10. Cross-domain impact = 12-16. Field-changing = 18-20.
      0 = trivial, 10 = useful niche, 15 = cross-domain, 20 = field-changing

ALSO check for reducibility: can the equation be trivially simplified or is it
an over-parameterized version of something simpler? If so, penalize novelty and
significance.

Return ONLY this JSON (no markdown, no extra text):
{"physical_validity": N, "novelty": N, "clarity": N, "evidence_quality": N, "significance": N, "reducible": true/false, "justification": "One sentence summary."}
"""


def _build_user_prompt(entry: dict) -> str:
    """Build the user prompt from sanitized fields only."""
    name = str(entry.get("name", ""))[:200]
    equation = str(entry.get("equationLatex", ""))[:2000]
    description = str(entry.get("description", ""))[:4000]
    units = str(entry.get("units", "TBD"))[:10]
    theory = str(entry.get("theory", "TBD"))[:30]

    assumptions = entry.get("assumptions", []) or []
    if isinstance(assumptions, list):
        assumptions = [str(a)[:500] for a in assumptions[:20]]
    else:
        assumptions = []

    evidence = entry.get("evidence", []) or []
    if isinstance(evidence, list):
        ev_strs = []
        for e in evidence[:20]:
            if isinstance(e, dict):
                ev_strs.append(str(e.get("label", ""))[:500])
            else:
                ev_strs.append(str(e)[:500])
        evidence = ev_strs
    else:
        evidence = []

    return (
        f"Name: {name}\n"
        f"Equation: {equation}\n"
        f"Description: {description}\n"
        f"Units check: {units}\n"
        f"Theory check: {theory}\n"
        f"Assumptions: {json.dumps(assumptions)}\n"
        f"Evidence: {json.dumps(evidence)}\n"
    )


def _call_llm(system: str, user: str, api_key: str, api_base: str, model: str) -> str:
    """Call the OpenAI-compatible chat completions API."""
    url = f"{api_base.rstrip('/')}/chat/completions"
    payload = json.dumps({
        "model": model,
        "temperature": 0.0,
        "max_tokens": 300,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }).encode("utf-8")

    req = Request(url, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {api_key}")

    with urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read().decode("utf-8"))

    return body["choices"][0]["message"]["content"].strip()


def _parse_scores(raw: str) -> dict[str, int]:
    """Extract scores from LLM response. Strict: only accept expected keys."""
    # Strip markdown fences if present
    clean = raw.strip()
    if clean.startswith("```"):
        lines = clean.split("\n")
        if lines[-1].strip() == "```":
            lines = lines[1:-1]
        else:
            lines = lines[1:]
        clean = "\n".join(lines).strip()

    data = json.loads(clean)
    expected = {"physical_validity", "novelty", "clarity", "evidence_quality", "significance"}
    scores = {}
    for key in expected:
        val = data.get(key, 0)
        if not isinstance(val, (int, float)):
            val = 0
        scores[key] = max(0, min(20, int(round(val))))

    scores["llm_total"] = sum(scores.values())
    scores["reducible"] = bool(data.get("reducible", False))
    scores["justification"] = str(data.get("justification", ""))[:500]
    return scores


def score_submission(entry: dict, api_key: str, api_base: str, model: str) -> dict[str, int] | None:
    """Score a single submission via LLM. Returns scores dict or None on failure."""
    user_prompt = _build_user_prompt(entry)
    try:
        raw = _call_llm(SYSTEM_PROMPT, user_prompt, api_key, api_base, model)
        return _parse_scores(raw)
    except (URLError, json.JSONDecodeError, KeyError, ValueError) as exc:
        print(f"LLM scoring failed: {exc}", file=sys.stderr)
        return None


def blend_scores(heuristic_score: int, llm_total: int) -> int:
    """Compute blended score: 40% heuristic + 60% LLM.

    Heuristic is the security gate (deterministic, no LLM involvement).
    LLM provides calibrated quality assessment. The blend gives a more
    accurate final score while keeping the heuristic as the safety floor.
    """
    return int(round(0.4 * heuristic_score + 0.6 * llm_total))


def main() -> None:
    ap = argparse.ArgumentParser(description="LLM-based quality scoring for submissions")
    ap.add_argument("--submission-id", required=True)
    ap.add_argument("--model", default=os.environ.get(MODEL_ENV, DEFAULT_MODEL))
    ap.add_argument("--api-base", default=os.environ.get(API_BASE_ENV, DEFAULT_BASE))
    ap.add_argument("--dry-run", action="store_true", help="Print prompt without calling API")
    args = ap.parse_args()

    api_key = os.environ.get(API_KEY_ENV, "")
    if not api_key and not args.dry_run:
        raise SystemExit(f"Set {API_KEY_ENV} environment variable")

    data = json.loads(SUBMISSIONS_JSON.read_text(encoding="utf-8"))
    entry = None
    for e in data.get("entries", []):
        if str(e.get("submissionId")) == args.submission_id:
            entry = e
            break
    if not entry:
        raise SystemExit(f"submission not found: {args.submission_id}")

    if args.dry_run:
        print("=== SYSTEM PROMPT ===")
        print(SYSTEM_PROMPT)
        print("=== USER PROMPT ===")
        print(_build_user_prompt(entry))
        return

    scores = score_submission(entry, api_key, args.api_base, args.model)
    if not scores:
        raise SystemExit("LLM scoring returned no result")

    # Record LLM scores alongside existing review
    review = entry.get("review", {}) or {}
    review["llm_scores"] = scores
    review["llm_model"] = args.model

    # Compute blended score (heuristic 40% + LLM 60%)
    heuristic_score = int(review.get("score", 0))
    blended = blend_scores(heuristic_score, scores["llm_total"])
    review["blended_score"] = blended
    entry["review"] = review

    data["lastUpdated"] = entry.get("submittedAt", "")
    SUBMISSIONS_JSON.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    print(f"llm_scored: {args.submission_id}")
    print(f"model: {args.model}")
    print(f"blended_score: {blended} (heuristic={heuristic_score}, llm={scores['llm_total']})")
    print(json.dumps(scores, indent=2))


if __name__ == "__main__":
    main()
