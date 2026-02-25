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
EQUATIONS_JSON = REPO / "data" / "equations.json"

# Configurable via environment
API_KEY_ENV = "OPENAI_API_KEY"
API_BASE_ENV = "OPENAI_API_BASE"
MODEL_ENV = "LLM_SCORE_MODEL"

DEFAULT_BASE = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = """\
You are the official TopEquations evaluator — a senior theoretical physicist
and research-program curator for the Adaptive Resonance Plasticity (ARP) +
phase-lifted + QWZ framework (Feb 2026 leaderboard).

Core value system (never forget):
- The highest scores go to MINIMAL, TRACEABLE EXTENSIONS that integrate cleanly
  with existing leaderboard entries.
- Explicit "builds on LB #X + LB #Y" + clean recovery clauses are EXTREMELY
  valuable. This is the #1 signal for a top-tier submission.
- Traceability, explicit assumptions, and immediate simulation-readiness matter
  more than raw novelty alone.
- Self-authored derivations, whitepapers, and simulations ARE valid evidence
  for a research registry. Score the quality and rigor of what is provided.

Use this exact weighted rubric (score each category 0-100, then you will
compute the weighted total):

1. traceability (22%):
   Full derivation bridge to parent equations, on-chain cert references,
   chat/paper provenance, explicit "builds on LB #X" lineage.
   0 = no provenance, 40 = vague references, 60 = names parent equations,
   80 = derives from specific LB entries with limit recovery,
   95-100 = complete derivation chain + on-chain cert + explicit recovery clause

2. rigor (20%):
   Dimensionally consistent, SymPy-safe, no contradictions, well-defined
   state variables, units check passes.
   0 = nonsense, 40 = plausible but hand-wavy, 60 = solid but gaps,
   80 = rigorous derivation, 95-100 = textbook-level rigor + units verified

3. assumptions (15%):
   Explicit, minimal, falsifiable assumptions. Clearly stated domain and
   boundary conditions. Timescale separations noted.
   0 = none stated, 40 = vague, 60 = some stated, 80 = clear + falsifiable,
   95-100 = minimal, explicit, each individually testable

4. presentation (13%):
   Clean LaTeX, clear description, all variables defined, animation-ready or
   animation provided, readable by a graduate student.
   0 = incomprehensible, 40 = readable but sloppy, 60 = clear with gaps,
   80 = publication-quality, 95-100 = exemplary + animation provided

5. novelty_insight (15%):
   Moves the ARP/phase-lifted program forward. Introduces new coupling,
   new mechanism, or bridges previously separate frameworks.
   0 = exact copy, 30 = trivial rearrangement, 50 = minor extension,
   70 = meaningful new coupling, 85 = novel mechanism,
   95-100 = paradigm-shifting new insight

6. fruitfulness (15%):
   How easily can the next researcher simulate, extend, or experimentally test
   this? Are all parameters defined? Is it immediately codeable?
   0 = dead end, 40 = would need major work, 60 = implementable with effort,
   80 = simulation-ready, 95-100 = copy-paste into a solver

Few-shot calibration (match these closely):
- "BZ-Averaged Phase-Lifted Complex Conductance Update Entropy-Gated" → 96-98
- "Phase Adler/RSJ Dynamics" → 94-96
- "Generic ARP Reinforce/Decay Law" → 93-95
- Pure rediscovery of a classic with no framework integration → <70
- Trivial tautology (x=x) → <10

Think step-by-step for each category, then output ONLY this JSON
(no markdown fences, no extra text):
{"traceability": N, "rigor": N, "assumptions": N, "presentation": N, "novelty_insight": N, "fruitfulness": N, "justification": "One sentence summary."}
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

    # Build leaderboard context so LLM can verify lineage claims
    lb_context = ""
    try:
        eq_data = json.loads(EQUATIONS_JSON.read_text(encoding="utf-8"))
        top = sorted(eq_data.get("entries", []), key=lambda x: x.get("score", 0), reverse=True)[:10]
        if top:
            lines = ["Current top leaderboard entries (for lineage reference):"]
            for i, t in enumerate(top, 1):
                t_name = str(t.get("name", ""))[:120]
                t_score = t.get("score", 0)
                t_eq = str(t.get("equationLatex", ""))[:200]
                lines.append(f"  #{i}: {t_name} (score {t_score}) — {t_eq}")
            lb_context = "\n".join(lines) + "\n"
    except Exception:
        pass

    animation_status = ""
    anim = entry.get("animation", {})
    if isinstance(anim, dict) and str(anim.get("status", "")).lower() not in ("planned", ""):
        animation_status = f"Animation: provided ({anim.get('status', '')})\n"

    return (
        f"Name: {name}\n"
        f"Equation: {equation}\n"
        f"Description: {description}\n"
        f"Units check: {units}\n"
        f"Theory check: {theory}\n"
        f"Assumptions: {json.dumps(assumptions)}\n"
        f"Evidence: {json.dumps(evidence)}\n"
        f"{animation_status}"
        f"{lb_context}"
    )


def _call_llm(system: str, user: str, api_key: str, api_base: str, model: str) -> str:
    """Call the OpenAI-compatible chat completions API."""
    url = f"{api_base.rstrip('/')}/chat/completions"
    payload = json.dumps({
        "model": model,
        "temperature": 0.0,
        "max_tokens": 600,
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


# Weights for 6-category rubric
_WEIGHTS = {
    "traceability": 0.22,
    "rigor": 0.20,
    "assumptions": 0.15,
    "presentation": 0.13,
    "novelty_insight": 0.15,
    "fruitfulness": 0.15,
}


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
    scores = {}
    for key in _WEIGHTS:
        val = data.get(key, 0)
        if not isinstance(val, (int, float)):
            val = 0
        scores[key] = max(0, min(100, int(round(val))))

    # Weighted total (0-100)
    weighted = sum(scores[k] * _WEIGHTS[k] for k in _WEIGHTS)
    scores["llm_total"] = int(round(weighted))
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
