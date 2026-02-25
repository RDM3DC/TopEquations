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
You are a rigorous equation reviewer for a scientific leaderboard.
Score the submitted equation on these five axes. Return ONLY a JSON object.

Axes (integer scores):
  physical_validity  (0-20): Is the equation physically/mathematically correct?
      0 = nonsense or tautology, 10 = plausible but unverified, 20 = rigorously correct
  novelty            (0-20): Is this equation original or a known result?
      0 = textbook standard, 10 = interesting variation, 20 = genuinely new insight
  clarity            (0-20): Is the equation clearly stated with defined variables?
      0 = incomprehensible, 10 = somewhat clear, 20 = crystal clear with all terms defined
  evidence_quality   (0-20): How well is it supported by assumptions and evidence?
      0 = no support, 10 = some assumptions listed, 20 = strong evidence chain
  significance       (0-20): How impactful is this equation if correct?
      0 = trivial, 10 = useful niche result, 20 = field-changing

Return ONLY this JSON (no markdown, no explanation):
{"physical_validity": N, "novelty": N, "clarity": N, "evidence_quality": N, "significance": N}
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
        "temperature": 0.2,
        "max_tokens": 200,
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
    entry["review"] = review

    data["lastUpdated"] = entry.get("submittedAt", "")
    SUBMISSIONS_JSON.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    print(f"llm_scored: {args.submission_id}")
    print(f"model: {args.model}")
    print(json.dumps(scores, indent=2))


if __name__ == "__main__":
    main()
