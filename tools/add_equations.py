# -*- coding: utf-8 -*-
"""One-shot script to add Equation Sheet v1.1 + AHC equations."""

import json
from pathlib import Path

repo = Path(__file__).resolve().parents[1]

# ── CORE.JSON ──────────────────────────────────────────────────────────────
core_path = repo / "data" / "core.json"
core = json.loads(core_path.read_text(encoding="utf-8"))
existing_ids = {e["id"] for e in core["entries"]}

new_core = [
    {
        "id": "core-phase-ambiguity",
        "name": "Phase Ambiguity (multi-valuedness axiom)",
        "novelty": 15,
        "tractability": 20,
        "plausibility": 20,
        "units": "OK",
        "theory": "PASS",
        "animation": "planned",
        "image": "planned",
        "equationLatex": "z=re^{i\\theta},\\quad \\theta\\equiv\\theta+2\\pi k,\\ k\\in\\mathbb{Z}",
        "description": "Multi-valuedness comes from the (2\u03c0)-quotient on phase. Starting axiom motivating the Phase-Lift framework.",
        "source": "Equation Sheet v1.1 \u00a7A (Eq.1)",
        "sourceUrl": "https://rdm3dc.github.io/canonical-core/papers/04-phase-lift-pros/",
    },
    {
        "id": "core-unwrap-rule",
        "name": "Deterministic Unwrapping Rule",
        "novelty": 20,
        "tractability": 19,
        "plausibility": 19,
        "units": "OK",
        "theory": "PASS",
        "animation": "planned",
        "image": "planned",
        "equationLatex": "\\mathrm{unwrap}(\\theta;\\theta_{\\rm ref})=\\theta+2\\pi\\,\\mathrm{round}\\!\\Big(\\frac{\\theta_{\\rm ref}-\\theta}{2\\pi}\\Big)",
        "description": "Pick the representative closest to the reference. The concrete algorithm behind Phase-Lift: a single deterministic formula for branch selection.",
        "source": "Equation Sheet v1.1 \u00a7A (Eq.3)",
        "sourceUrl": "https://rdm3dc.github.io/canonical-core/papers/04-phase-lift-pros/",
    },
    {
        "id": "core-path-continuity",
        "name": "Path Continuity (Stateful Phase-Lift)",
        "novelty": 20,
        "tractability": 18,
        "plausibility": 18,
        "units": "OK",
        "theory": "PASS",
        "animation": "planned",
        "image": "planned",
        "equationLatex": "\\theta_{R,k}=\\mathrm{unwrap}(\\arg z_k;\\,\\theta_{R,k-1})",
        "description": "Turns phase into a continuous real trajectory by chaining the unwrap rule sample-to-sample (except at true singularities like z=0).",
        "source": "Equation Sheet v1.1 \u00a7A (Eq.4)",
        "sourceUrl": "https://rdm3dc.github.io/canonical-core/papers/04-phase-lift-pros/",
    },
    {
        "id": "core-conformal-metric",
        "name": "Adaptive-\u03c0 Conformal Scale Factor and Metric",
        "novelty": 22,
        "tractability": 16,
        "plausibility": 16,
        "units": "WARN",
        "theory": "PASS-WITH-ASSUMPTIONS",
        "animation": "planned",
        "image": "planned",
        "equationLatex": "\\Omega(x,t):=\\frac{\\pi_a(x,t)}{\\pi},\\qquad g_{ij}(x,t)=\\Omega(x,t)^2\\,\\delta_{ij}",
        "description": "\u03c0\u2090/\u03c0 acts like a local ruler scaling. Defines the conformal metric induced by the adaptive-\u03c0 field on the underlying flat geometry.",
        "source": "Equation Sheet v1.1 \u00a7C (Eq.8)",
        "sourceUrl": "https://rdm3dc.github.io/canonical-core/papers/02-adaptive-pi-geometry/",
    },
    {
        "id": "core-adaptive-arc-length",
        "name": "Adaptive Arc Length",
        "novelty": 20,
        "tractability": 16,
        "plausibility": 15,
        "units": "WARN",
        "theory": "PASS-WITH-ASSUMPTIONS",
        "animation": "planned",
        "image": "planned",
        "equationLatex": "L_g(\\gamma)=\\int_0^1 \\Omega(\\gamma(t),t)\\,|\\dot\\gamma(t)|\\,dt",
        "description": "Distances and penalties are measured in the adaptive geometry: path lengths scale with the local \u03c0\u2090 field.",
        "source": "Equation Sheet v1.1 \u00a7C (Eq.9)",
        "sourceUrl": "https://rdm3dc.github.io/canonical-core/papers/02-adaptive-pi-geometry/",
    },
    {
        "id": "core-pi-a-dynamics",
        "name": "Reinforce/Decay Dynamics for \u03c0\u2090",
        "novelty": 22,
        "tractability": 17,
        "plausibility": 16,
        "units": "OK",
        "theory": "PASS-WITH-ASSUMPTIONS",
        "animation": "planned",
        "image": "planned",
        "equationLatex": "\\frac{d\\pi_a}{dt}=\\alpha_\\pi\\,s(x,t)-\\mu_\\pi(\\pi_a-\\pi_0)",
        "description": "\u03c0\u2090 increases under stimulus (events/errors/curvature) and relaxes toward \u03c0\u2080 (often \u03c0). The core adaptive mechanism of the geometry layer.",
        "source": "Equation Sheet v1.1 \u00a7C (Eq.10)",
        "sourceUrl": "https://rdm3dc.github.io/canonical-core/papers/02-adaptive-pi-geometry/",
    },
    {
        "id": "core-curvature-salience",
        "name": "Curvature as Salience (Curve-Memory Primitive)",
        "novelty": 15,
        "tractability": 20,
        "plausibility": 20,
        "units": "OK",
        "theory": "PASS",
        "animation": "planned",
        "image": "planned",
        "equationLatex": "\\kappa(s)=|\\gamma''(s)|",
        "description": "Salience equals curvature: sharp bends in a trajectory mark events and transitions. Defines the geometric primitive used by curve-memory.",
        "source": "Equation Sheet v1.1 \u00a7E (Eq.12)",
        "sourceUrl": "https://rdm3dc.github.io/canonical-core/papers/02-adaptive-pi-geometry/",
    },
    {
        "id": "core-reinforce-decay-memory",
        "name": "Reinforce/Decay Memory Law (generic)",
        "novelty": 18,
        "tractability": 18,
        "plausibility": 17,
        "units": "OK",
        "theory": "PASS-WITH-ASSUMPTIONS",
        "animation": "planned",
        "image": "planned",
        "equationLatex": "\\frac{dM}{dt}=\\alpha\\,S(t)-\\mu\\,M(t)",
        "description": "A generic time-constant memory law: M grows under stimulus S and decays at rate \u03bc. Can drive s(x,t) for \u03c0\u2090 or any curve-memory trace.",
        "source": "Equation Sheet v1.1 \u00a7E (Eq.13)",
        "sourceUrl": "https://rdm3dc.github.io/canonical-core/papers/01-arp-ain/",
    },
]

# Build lookup
by_id = {e["id"]: e for e in core["entries"]}

# Add new only
for e in new_core:
    if e["id"] not in by_id:
        by_id[e["id"]] = e

# Update existing entries with richer fields from the equation sheet
if "core-phase-lift" in by_id:
    by_id["core-phase-lift"]["source"] = "canonical-core paper 04 / Eq.Sheet \u00a7A (Eq.2)"
    by_id["core-phase-lift"]["equationLatex"] = (
        "(\\,\\,\\,\\,\\,\\u29c9 f\\,\\,\\,)(z;\\theta_{\\rm ref}) "
        ":= f(z)\\ \\text{computed using}\\ \\theta_R=\\mathrm{unwrap}(\\arg z;\\theta_{\\rm ref})"
    )
if "core-pr-root" in by_id:
    by_id["core-pr-root"]["source"] = "canonical-core paper 04 / Eq.Sheet \u00a7A (Eq.5)"
if "core-winding-parity" in by_id:
    e = by_id["core-winding-parity"]
    e["name"] = "Winding Number + \u2124\u2082 Parity Invariants"
    e["equationLatex"] = (
        "w=\\frac{\\Delta\\theta_R}{2\\pi}\\in\\mathbb{Z},"
        "\\qquad \\nu:=w\\bmod 2\\in\\{0,1\\},\\quad b=(-1)^w\\in\\{\\pm1\\}"
    )
    e["description"] = (
        "Counts how many times the lifted phase winds (w); "
        "\u2124\u2082 parity b predicts whether PR-Root returns to the same or opposite sheet."
    )
    e["source"] = "canonical-core papers 02/04 / Eq.Sheet \u00a7B (Eq.6\u20137)"
if "core-arp-ode" in by_id:
    by_id["core-arp-ode"]["source"] = "canonical-core paper 01 / Eq.Sheet \u00a7D (Eq.11)"
    by_id["core-arp-ode"]["description"] = (
        "Canonical Adaptive Resistance Principle update rule for edge conductance. "
        "Edges that carry activity reinforce; unused edges decay (self-organizing backbones)."
    )

# Canonical ordering
ordered_ids = [
    "core-phase-ambiguity",
    "core-phase-lift",
    "core-unwrap-rule",
    "core-path-continuity",
    "core-pr-root",
    "core-winding-parity",
    "core-conformal-metric",
    "core-adaptive-arc-length",
    "core-pi-a",
    "core-pi-a-dynamics",
    "core-arp-ode",
    "core-curvature-salience",
    "core-reinforce-decay-memory",
    "core-phase-lifted-stokes",
]

final_core = []
for oid in ordered_ids:
    if oid in by_id:
        final_core.append(by_id.pop(oid))
for e in by_id.values():
    final_core.append(e)

core["entries"] = final_core
core_path.write_text(json.dumps(core, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"core.json: {len(final_core)} entries")

# ── EQUATIONS.JSON ─────────────────────────────────────────────────────────
eq_path = repo / "data" / "equations.json"
eq_data = json.loads(eq_path.read_text(encoding="utf-8"))
eq_existing = {e["id"] for e in eq_data["entries"]}

new_eqs = [
    {
        "id": "eq-ahc-candidate-unwrap",
        "name": "AHC Candidate Unwrap (standard 2\u03c0 lift)",
        "firstSeen": "2026-02-22",
        "source": "Equation Sheet v1.1 \u00a7F (Eq.14)",
        "score": 70,
        "scores": {"tractability": 18, "plausibility": 17, "validation": 10, "artifactCompleteness": 4},
        "units": "OK",
        "theory": "PASS",
        "animation": {"status": "planned", "path": ""},
        "image": {"status": "planned", "path": ""},
        "description": "Apply standard 2\u03c0 unwrap to each Ramsey measurement relative to the previous lifted phase. First step of the AHC control loop.",
        "assumptions": [
            "Measurement \u03c6_k is a well-defined principal-value phase in (-\u03c0, \u03c0].",
            "Previous lifted phase \u03b8_{R,k-1} is available and trusted.",
        ],
        "date": "2026-02-22",
        "equationLatex": "u_k=\\mathrm{unwrap}(\\phi_k;\\theta_{R,k-1})",
        "tags": {"novelty": {"date": "2026-02-22", "score": 20}},
    },
    {
        "id": "eq-ahc-residual",
        "name": "AHC Residual",
        "firstSeen": "2026-02-22",
        "source": "Equation Sheet v1.1 \u00a7F (Eq.15)",
        "score": 70,
        "scores": {"tractability": 18, "plausibility": 17, "validation": 10, "artifactCompleteness": 4},
        "units": "OK",
        "theory": "PASS",
        "animation": {"status": "planned", "path": ""},
        "image": {"status": "planned", "path": ""},
        "description": "Difference between the unwrapped measurement and the previous lifted-phase state. Feeds the step-limit gate.",
        "date": "2026-02-22",
        "equationLatex": "r_k=u_k-\\theta_{R,k-1}",
        "tags": {"novelty": {"date": "2026-02-22", "score": 18}},
    },
    {
        "id": "eq-ahc-step-limit",
        "name": "AHC Adaptive Step-Limit Update (\u03c0\u2090 clip)",
        "firstSeen": "2026-02-22",
        "source": "Equation Sheet v1.1 \u00a7F (Eq.16)",
        "score": 81,
        "scores": {"tractability": 19, "plausibility": 18, "validation": 14, "artifactCompleteness": 6},
        "units": "OK",
        "theory": "PASS-WITH-ASSUMPTIONS",
        "animation": {"status": "planned", "path": ""},
        "image": {"status": "planned", "path": ""},
        "description": "Core AHC innovation: clip the residual to adaptive bounds \u00b1\u03c0\u2090. Prevents single-run glitches from causing a branch jump. The key robustness mechanism.",
        "assumptions": [
            "\u03c0_{a,k-1} is positive and represents a trusted local phase step-limit.",
            "Clipping to [-\u03c0_a, +\u03c0_a] is a valid monotone saturation nonlinearity.",
        ],
        "date": "2026-02-22",
        "equationLatex": "\\theta_{R,k}=\\theta_{R,k-1}+\\mathrm{clip}(r_k,\\,-\\pi_{a,k-1},\\,\\pi_{a,k-1})",
        "tags": {"novelty": {"date": "2026-02-22", "score": 26}},
    },
    {
        "id": "eq-ahc-event-stimulus",
        "name": "AHC Event Stimulus (phase-jump indicator)",
        "firstSeen": "2026-02-22",
        "source": "Equation Sheet v1.1 \u00a7F (Eq.17)",
        "score": 69,
        "scores": {"tractability": 17, "plausibility": 17, "validation": 10, "artifactCompleteness": 4},
        "units": "OK",
        "theory": "PASS",
        "animation": {"status": "planned", "path": ""},
        "image": {"status": "planned", "path": ""},
        "description": "Binary indicator: 1 when a residual exceeds the current \u03c0\u2090 bound, 0 otherwise. Alternative: curvature-based S_k \u221d |\u0394\u00b2\u03b8_R|. Triggers \u03c0\u2090 widening.",
        "date": "2026-02-22",
        "equationLatex": "S_k=\\mathbf{1}\\{|r_k|>\\pi_{a,k-1}\\}",
        "tags": {"novelty": {"date": "2026-02-22", "score": 19}},
    },
    {
        "id": "eq-ahc-pi-a-update",
        "name": "AHC Adaptive \u03c0\u2090 Update (discrete)",
        "firstSeen": "2026-02-22",
        "source": "Equation Sheet v1.1 \u00a7F (Eq.18)",
        "score": 76,
        "scores": {"tractability": 18, "plausibility": 17, "validation": 12, "artifactCompleteness": 6},
        "units": "OK",
        "theory": "PASS-WITH-ASSUMPTIONS",
        "animation": {"status": "planned", "path": ""},
        "image": {"status": "planned", "path": ""},
        "description": "Discrete version of \u03c0\u2090 dynamics for the AHC loop: widens bound after events (\u03b1_\u03c0 S_k term), relaxes toward \u03c0\u2080 otherwise.",
        "assumptions": [
            "\u03b1_\u03c0 and \u03bc_\u03c0 satisfy stability: \u03b1_\u03c0 large enough to capture real slips, \u03bc_\u03c0 small enough for relaxation.",
            "\u03c0_0 is a stable rest value (typically \u03c0).",
        ],
        "date": "2026-02-22",
        "equationLatex": "\\pi_{a,k}=\\pi_{a,k-1}+\\alpha_\\pi S_k-\\mu_\\pi(\\pi_{a,k-1}-\\pi_0)",
        "tags": {"novelty": {"date": "2026-02-22", "score": 24}},
    },
    {
        "id": "eq-ahc-running-winding",
        "name": "AHC Running Winding + Parity",
        "firstSeen": "2026-02-22",
        "source": "Equation Sheet v1.1 \u00a7F (Eq.19)",
        "score": 79,
        "scores": {"tractability": 18, "plausibility": 17, "validation": 14, "artifactCompleteness": 6},
        "units": "OK",
        "theory": "PASS",
        "animation": {"status": "planned", "path": ""},
        "image": {"status": "planned", "path": ""},
        "description": "Live winding number and parity from the lifted-phase trajectory. w_k counts total accumulated windings; b_k = (-1)^w_k gives the sheet parity at each step.",
        "date": "2026-02-22",
        "equationLatex": "w_k=\\mathrm{round}\\!\\Big(\\frac{\\theta_{R,k}-\\theta_{R,0}}{2\\pi}\\Big),\\qquad b_k=(-1)^{w_k}",
        "tags": {"novelty": {"date": "2026-02-22", "score": 22}},
    },
    {
        "id": "eq-ahc-parity-flip-rate",
        "name": "AHC Parity Flip-Rate (locking observable)",
        "firstSeen": "2026-02-22",
        "source": "Equation Sheet v1.1 \u00a7F (Eq.20)",
        "score": 87,
        "scores": {"tractability": 19, "plausibility": 18, "validation": 16, "artifactCompleteness": 8},
        "units": "OK",
        "theory": "PASS-WITH-ASSUMPTIONS",
        "animation": {"status": "planned", "path": ""},
        "image": {"status": "planned", "path": ""},
        "description": "The key AHC observable: fraction of consecutive steps where parity flips. AHC prediction: r_b drops when \u03b1_\u03c0/\u03bc_\u03c0 is high enough ('parity locking'). This is the primary testable quantity for the qubit Berry-loop experiment.",
        "assumptions": [
            "K is large enough for the ratio to be statistically meaningful.",
            "Parity flips are detected correctly (no double-counting at coincident singularities).",
        ],
        "date": "2026-02-22",
        "equationLatex": "r_b=\\frac{\\#\\{k:\\ b_k\\neq b_{k-1}\\}}{K-1}",
        "tags": {"novelty": {"date": "2026-02-22", "score": 28}},
    },
    {
        "id": "eq-un-wilson-holonomy",
        "name": "U(N) Wilson / Holonomy",
        "firstSeen": "2026-02-22",
        "source": "Equation Sheet v1.1 \u00a7G (Eq.21)",
        "score": 56,
        "scores": {"tractability": 14, "plausibility": 16, "validation": 6, "artifactCompleteness": 2},
        "units": "WARN",
        "theory": "PASS-WITH-ASSUMPTIONS",
        "animation": {"status": "planned", "path": ""},
        "image": {"status": "planned", "path": ""},
        "description": "Path-ordered exponential giving the U(N) holonomy around a closed loop \u03b3. Extends the Phase-Lift framework beyond the U(1) case to non-abelian gauge fields.",
        "assumptions": [
            "Connection A is smooth (or piecewise smooth) along \u03b3.",
            "Path ordering P is needed for non-abelian A (order matters).",
            "N > 1 generalization remains speculative without concrete experimental targets.",
        ],
        "date": "2026-02-22",
        "equationLatex": "U(\\gamma)=\\mathcal{P}\\exp\\!\\Big(-\\oint_\\gamma A\\cdot d\\lambda\\Big)\\in U(N)",
        "tags": {"novelty": {"date": "2026-02-22", "score": 20}},
    },
    {
        "id": "eq-un-det-phase",
        "name": "U(N) Det-Phase on Lifted Branch",
        "firstSeen": "2026-02-22",
        "source": "Equation Sheet v1.1 \u00a7G (Eq.22)",
        "score": 59,
        "scores": {"tractability": 15, "plausibility": 16, "validation": 8, "artifactCompleteness": 2},
        "units": "WARN",
        "theory": "PASS-WITH-ASSUMPTIONS",
        "animation": {"status": "planned", "path": ""},
        "image": {"status": "planned", "path": ""},
        "description": "Same Phase-Lift bookkeeping (integer winding + \u2124\u2082 shadow) applied to the determinant phase of U(N) holonomy. Bridges the U(1) parity framework to non-abelian gauge systems.",
        "assumptions": [
            "det U is nonzero (no degenerate holonomy).",
            "Adaptive \u03c0\u2090 sets the winding period instead of fixed \u03c0.",
            "Physical interpretation of w_det depends on the specific gauge theory.",
        ],
        "date": "2026-02-22",
        "equationLatex": "\\theta_R=\\mathrm{unwrap}(\\arg\\det U;\\theta_{\\rm ref},\\pi_a),\\qquad w_{\\det}=\\frac{\\Delta\\theta_R}{2\\pi_a},\\qquad b(\\gamma)=(-1)^{w_{\\det}}",
        "tags": {"novelty": {"date": "2026-02-22", "score": 22}},
    },
]

added = 0
for e in new_eqs:
    if e["id"] not in eq_existing:
        eq_data["entries"].append(e)
        added += 1

eq_data["lastUpdated"] = "2026-02-22"
eq_data["entries"].sort(key=lambda e: float(e.get("score", 0)), reverse=True)
eq_path.write_text(json.dumps(eq_data, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"equations.json: added {added}, total {len(eq_data['entries'])} entries")

# Print ranking
for i, e in enumerate(eq_data["entries"], 1):
    print(f"  #{i:2d}  Score {e['score']:3d}  {e['name']}")
