"""Score a batch of harvested equations and optionally promote high-scoring ones.

Policy (Ryan, 2026-02-20):
- Every run scores the next N harvested equations (deterministic cursor).
- If score >= THRESHOLD, promote into data/equations.json (ranked board).
- Otherwise, record into data/harvest/scored_candidates.json and show on harvest page.

Heuristic scoring (no external dependencies):
- Not meant to be perfect; it's a lightweight auto-triage.
- Can be replaced later with LLM-assisted scoring.

Usage:
  python tools/score_harvest_batch.py --batch 10 --threshold 68

Writes:
- data/harvest/scored_candidates.json
- data/equations.json (if promotions occur)
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
HARVEST = REPO / "data" / "harvest" / "equation_harvest.json"
SCORED = REPO / "data" / "harvest" / "scored_candidates.json"
RANKED = REPO / "data" / "equations.json"


def _now_date() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _slug(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:40] or "harvest"


def _safe_id(eq: str) -> str:
    # stable-enough id based on common tokens
    head = re.sub(r"\\\\[a-zA-Z]+", "", eq)
    head = re.sub(r"\s+", " ", head).strip()
    return "eq-harvest-" + _slug(head)


def _heuristic_scores(eq: str, source: str) -> dict:
    s = eq
    low = s.lower()

    # Novelty (0-30)
    novelty = 8
    if "arp" in low or "g_{ij}" in low or "\\dot{g" in low:
        novelty += 6
    if "\\pi_a" in low or "π_a" in s:
        novelty += 7
    if "theta_r" in low or "phase" in low or "unwrap" in low:
        novelty += 4
    if "canonical-core" in (source or "").lower():
        novelty += 2
    novelty = max(0, min(30, novelty))

    # Tractability (0-20)
    tract = 14
    if len(s) > 180:
        tract -= 3
    if "\\int" in low or "\\sum" in low:
        tract -= 1
    if "=" in s or "\\boxed" in low:
        tract += 1
    tract = max(0, min(20, tract))

    # Plausibility (0-20)
    plaus = 14
    if "\\frac" in low or "\\partial" in low or "\\nabla" in low:
        plaus += 1
    if any(tok in low for tok in ["sin", "cos", "exp", "log"]):
        plaus += 1
    plaus = max(0, min(20, plaus))

    # Validation bonus (0-20)
    # Auto-checks are limited; default low.
    validation = 4
    if "=" in s:
        validation += 2
    validation = max(0, min(20, validation))

    # Artifact completeness (0-10)
    artifact = 0

    total = novelty + tract + plaus + validation + artifact
    return {
        "total": int(total),
        "novelty": int(novelty),
        "tractability": int(tract),
        "plausibility": int(plaus),
        "validation": int(validation),
        "artifactCompleteness": int(artifact),
    }


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", type=int, default=10)
    ap.add_argument("--threshold", type=int, default=68)
    args = ap.parse_args()

    harvest = _load_json(HARVEST)
    harvest_entries = list(harvest.get("entries", []))

    scored = _load_json(SCORED) if SCORED.exists() else {"schemaVersion": 1, "lastUpdated": _now_date(), "cursor": 0, "entries": []}
    cursor = int(scored.get("cursor", 0) or 0)

    ranked = _load_json(RANKED)
    ranked_entries = list(ranked.get("entries", []))
    ranked_ids = {str(e.get("id")) for e in ranked_entries}

    already_scored_sha1 = {str(e.get("sha1")) for e in scored.get("entries", []) if e.get("sha1")}

    picked: list[dict] = []
    i = cursor
    while i < len(harvest_entries) and len(picked) < args.batch:
        he = harvest_entries[i]
        kind = str(he.get("kind", "")).lower()
        if "latex" not in kind:
            i += 1
            continue
        if he.get("sha1") and str(he.get("sha1")) in already_scored_sha1:
            i += 1
            continue
        picked.append({"_harvest_index": i, **he})
        i += 1

    # advance cursor regardless (so we don't spin)
    scored["cursor"] = i
    scored["lastUpdated"] = _now_date()

    promotions = 0
    for he in picked:
        eq = str(he.get("equation", "") or "").strip()
        src = str(he.get("source", "") or "")
        sc = _heuristic_scores(eq, src)

        entry = {
            "equation": eq,
            "kind": he.get("kind"),
            "source": src,
            "line_start": he.get("line_start"),
            "sha1": he.get("sha1"),
            "scoredAt": _now_date(),
            "score": sc["total"],
            "scores": {
                "novelty": sc["novelty"],
                "tractability": sc["tractability"],
                "plausibility": sc["plausibility"],
                "validation": sc["validation"],
                "artifactCompleteness": sc["artifactCompleteness"],
            },
        }

        if sc["total"] >= args.threshold:
            # Promote to ranked board.
            rid = _safe_id(eq)
            # ensure uniqueness
            if rid in ranked_ids:
                rid = rid + "-" + (he.get("sha1") or "")[:8]
            ranked_ids.add(rid)

            ranked_entries.append(
                {
                    "id": rid,
                    "name": "Harvest candidate (auto-scored)",
                    "firstSeen": _now_date(),
                    "source": f"harvest: {src}",
                    "score": sc["total"],
                    "scores": {
                        "novelty": sc["novelty"],
                        "tractability": sc["tractability"],
                        "plausibility": sc["plausibility"],
                        "validation": sc["validation"],
                        "artifactCompleteness": sc["artifactCompleteness"],
                    },
                    "units": "TBD",
                    "theory": "TBD",
                    "animation": {"status": "planned", "path": ""},
                    "image": {"status": "planned", "path": ""},
                    "description": "Auto-promoted from harvest after heuristic scoring (review recommended).",
                    "date": _now_date(),
                    "equationLatex": eq,
                }
            )
            promotions += 1
        else:
            scored.setdefault("entries", []).append(entry)

    # Only touch the ranked board if promotions occurred.
    if promotions:
        ranked["entries"] = ranked_entries
        ranked["lastUpdated"] = _now_date()

    # Update scored stats
    stats = scored.get("stats", {}) or {}
    stats["count"] = len(scored.get("entries", []))
    scored["stats"] = stats

    _write_json(SCORED, scored)
    _write_json(RANKED, ranked)

    print(f"score_harvest_batch: picked={len(picked)} cursor={cursor}->{i} promoted={promotions} scored_only={len(picked)-promotions}")


if __name__ == "__main__":
    main()
