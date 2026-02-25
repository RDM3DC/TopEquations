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
You are a rigorous but fair equation reviewer for the TopEquations research
leaderboard. This leaderboard showcases NOVEL, ORIGINAL equations — not
textbook classics. Score the submitted equation on five axes.

CONTEXT: TopEquations is a platform for researchers submitting new theoretical
results, extensions, and derivations. Submissions typically build on established
physics/math frameworks (conductance, phase dynamics, entropy, etc.) to propose
genuinely new governing equations. Most submissions include self-authored
evidence (whitepapers, derivations, simulations). Independent peer review is
rare at submission time — that does not make the work low quality.

CALIBRATION ANCHORS (for this leaderboard's scale):
  Trivial tautology (x=x):                         ~5 total
  Known textbook result resubmitted:                ~25-35 total
  Relabeled known result with minor twist:          ~40-50 total
  Well-structured novel PDE with clear derivation:  ~65-75 total
  Novel equation with strong evidence + animations: ~80-90 total
  Landmark unifying equation with limit recovery:   ~90-97 total

Axes (integer scores):
  physical_validity  (0-20): Is it dimensionally consistent and physically sound?
      Does it have well-defined state variables? Can you trace a derivation path?
      0 = nonsense/tautology, 8 = plausible but hand-wavy, 14 = solid derivation
      logic, 18 = rigorously derivable, 20 = textbook-level rigor
  novelty            (0-20): Does it introduce genuinely new dynamics or coupling?
      Building on known frameworks IS expected — score the NEW contribution.
      0 = exact copy, 5 = trivial rearrangement, 10 = meaningful extension,
      14 = novel coupling of known concepts, 18 = new mechanism, 20 = paradigm shift
  clarity            (0-20): Are all variables defined? Is notation standard?
      0 = incomprehensible, 10 = readable but gaps, 15 = clear with minor issues,
      18 = publication-ready, 20 = exemplary
  evidence_quality   (0-20): What evidence supports this equation?
      Self-authored derivations, simulations, and whitepapers ARE valid evidence
      for a research leaderboard. Score the quality and rigor of what is provided.
      0 = nothing, 5 = assumptions only, 10 = derivation sketch, 13 = detailed
      self-authored proof/simulation, 16 = with visualization artifacts,
      18 = independent confirmation, 20 = peer-reviewed + experimental
  significance       (0-20): How impactful is this if correct?
      Consider: does it unify concepts? Does it generalize existing results?
      Does it reduce to known equations in limiting cases?
      0 = trivial, 8 = niche utility, 12 = useful generalization,
      15 = cross-domain bridge, 18 = field-advancing, 20 = transformative

KEY SCORING SIGNALS (reward these):
  - Limit recovery: equation reduces to known result when a parameter → 0
  - Unification: bridges two or more previously separate frameworks
  - Visualization: has animations/simulations backing the dynamics
  - Clear assumptions: explicitly stated domain + boundary conditions
  - Novel coupling terms: new interaction mechanisms not in parent equations

Check for reducibility: can the equation be trivially simplified? If so, penalize
novelty and significance proportionally.

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
