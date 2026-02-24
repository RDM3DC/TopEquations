"""Score core equations with derivative-boost validation.

For each core equation, counts how many promoted derived equations
(in equations.json) reference the same concepts. Each derivative adds
+2 to validation (capped at 12). Artifacts with linked animations/images
also contribute.

Updates core.json in-place with validation, artifactCompleteness, and
a computed score field.

Usage:
  python tools/score_core.py
  python tools/score_core.py --dry-run
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CORE_JSON = REPO / "data" / "core.json"
EQUATIONS_JSON = REPO / "data" / "equations.json"
SUBMISSIONS_JSON = REPO / "data" / "submissions.json"

# Map core equation ids to keywords that indicate a derived equation
# uses that core concept.  Checked against derived equation name,
# description, and source (case-insensitive).
CORE_KEYWORD_MAP: dict[str, list[str]] = {
    "core-phase-ambiguity": ["phase", "branch", "multi-valued", "2pi"],
    "core-phase-lift": ["phase-lift", "phase lift", "resolved phase", "unwrap"],
    "core-unwrap-rule": ["unwrap", "phase-lift", "branch-safe"],
    "core-path-continuity": ["path continuity", "stateful phase", "resolved phase", "branch-safe"],
    "core-pr-root": ["pr-root", "phase-resolved root", "sqrt"],
    "core-winding-parity": ["winding", "parity", "holonomy", "z2", "z₂"],
    "core-conformal-metric": ["conformal", "adaptive-pi", "adaptive-π", "metric", "ruler"],
    "core-adaptive-arc-length": ["arc length", "adaptive geometry", "conformal"],
    "core-pi-a": ["adaptive-pi", "adaptive-π", "pi_a", "πₐ", "pi-a"],
    "core-pi-a-dynamics": ["adaptive-pi", "adaptive-π", "reinforce", "decay", "pi_a", "entropy"],
    "core-arp-ode": ["conductance", "arp", "adaptive resistance", "g_ij", "reinforcement"],
    "core-curvature-salience": ["curvature", "salience", "kappa"],
    "core-reinforce-decay-memory": ["reinforce", "decay", "memory", "stimulus"],
    "core-phase-lifted-stokes": ["stokes", "holonomy", "quantization", "phase-lift"],
}


def _today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _save(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _clamp(v: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, int(v)))


def _count_derivatives(core_id: str, derived_entries: list[dict]) -> int:
    keywords = CORE_KEYWORD_MAP.get(core_id, [])
    if not keywords:
        return 0
    count = 0
    for d in derived_entries:
        text = " ".join([
            str(d.get("name", "")),
            str(d.get("description", "")),
            str(d.get("source", "")),
            str(d.get("equationLatex", "")),
        ]).lower()
        if any(kw.lower() in text for kw in keywords):
            count += 1
    return count


def _artifact_score(entry: dict) -> int:
    score = 0
    for key in ("animation", "image"):
        val = entry.get(key)
        if isinstance(val, dict):
            status = str(val.get("status", "")).lower()
            path = str(val.get("path", "")).strip()
            if path or status in ("linked", "complete", "done"):
                score += 2
            elif status in ("in-progress",):
                score += 1
        elif isinstance(val, str) and val.strip() and val.strip().lower() not in ("planned", ""):
            score += 2
    return score


def main() -> None:
    ap = argparse.ArgumentParser(description="Score core equations with derivative-boost validation")
    ap.add_argument("--dry-run", action="store_true", help="Print scores without saving")
    args = ap.parse_args()

    core = _load(CORE_JSON)
    equations = _load(EQUATIONS_JSON)
    derived_entries = list(equations.get("entries", []))

    # Also count promoted submissions
    if SUBMISSIONS_JSON.exists():
        subs = _load(SUBMISSIONS_JSON)
        promoted = [e for e in subs.get("entries", [])
                    if str(e.get("status", "")).lower() == "promoted"]
        derived_entries.extend(promoted)

    updated = 0
    for entry in core.get("entries", []):
        core_id = entry.get("id", "")
        t = _clamp(entry.get("tractability", 0), 0, 20)
        p = _clamp(entry.get("plausibility", 0), 0, 20)

        # Validation: base from theory/units + derivative boost
        v = 0
        if str(entry.get("theory", "")).upper() in ("PASS",):
            v += 4
        elif "ASSUMPTION" in str(entry.get("theory", "")).upper():
            v += 2
        if str(entry.get("units", "")).upper() == "OK":
            v += 2

        n_deriv = _count_derivatives(core_id, derived_entries)
        deriv_boost = min(12, n_deriv * 2)
        v += deriv_boost
        v = _clamp(v, 0, 20)

        a = _clamp(_artifact_score(entry), 0, 10)

        total = int(round(((t + p + v + a) / 70.0) * 100.0))

        entry["validation"] = v
        entry["artifactCompleteness"] = a
        entry["score"] = total
        entry["derivativeCount"] = n_deriv

        status = "ready" if total >= 65 else "needs-boost"
        print(f"{total:3d}  {core_id:45s}  T{t} P{p} V{v} A{a}  derivs={n_deriv}  [{status}]")
        updated += 1

    if not args.dry_run:
        _save(CORE_JSON, core)
        print(f"\nupdated core.json: {updated} entries")
    else:
        print(f"\n(dry run — {updated} entries would be updated)")


if __name__ == "__main__":
    main()
