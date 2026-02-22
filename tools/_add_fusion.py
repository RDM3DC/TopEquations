import json
from pathlib import Path

eq_path = Path("data/equations.json")
d = json.loads(eq_path.read_text(encoding="utf-8"))
existing = {e["id"] for e in d["entries"]}

new_eqs = [
    {
        "id": "eq-pi-a-gauged-phase-lift",
        "name": "\u03c0\u2090-Gauged Phase-Lift (adaptive unwrap + invariants)",
        "firstSeen": "2026-02-22",
        "source": "4-pillar fusion \u00a71",
        "score": 61,
        "scores": {"tractability": 19, "plausibility": 18, "validation": 4, "artifactCompleteness": 2},
        "units": "OK",
        "theory": "PASS-WITH-ASSUMPTIONS",
        "animation": {"status": "planned", "path": ""},
        "image": {"status": "planned", "path": ""},
        "description": "Generalizes Phase-Lift unwrapping from fixed 2\u03c0 to adaptive 2\u03c0\u2090: sheet jumps happen in units of the local identification length. Derives \u03c0\u2090-gauged winding w_a and \u2124\u2082 shadow parity b_a. Novel: the unit of winding is no longer constant, coupling topology to a geometry field.",
        "differentialLatex": "m_k = \\arg\\min_{m\\in\\mathbb{Z}} |\\theta(t_k)+2\\pi_a(t_k)\\,m - \\theta_R(t_{k-1})|",
        "derivation": "Apply the nearest-sheet Phase-Lift rule but replace the fixed period 2\u03c0 with the local adaptive period 2\u03c0\u2090(t_k). The resolved phase is \u03b8_R(t_k) = \u03b8(t_k) + 2\u03c0_a(t_k) m_k. Winding w_a[\u03b3] counts net integer sheet transitions; b_a = (-1)^{w_a} gives holonomy parity.",
        "assumptions": [
            "z(t) \u2260 0 along the path (no singularity crossings).",
            "\u03c0_a(t) > 0 everywhere (positive phase-period field).",
            "Nearest-sheet rule is unambiguous (no exact midpoints between sheets)."
        ],
        "date": "2026-02-22",
        "equationLatex": "\\theta_R(t_k) = \\theta(t_k) + 2\\pi_a(t_k)\\,m_k,\\quad w_a[\\gamma]:=\\sum_k m_k,\\quad b_a[\\gamma]=(-1)^{w_a}",
        "tags": {"novelty": {"date": "2026-02-22", "score": 28}}
    },
    {
        "id": "eq-parity-pump",
        "name": "Parity Pump (\u03c0\u2090-gradient \u2124\u2082 flip mechanism)",
        "firstSeen": "2026-02-22",
        "source": "4-pillar fusion \u00a72",
        "score": 63,
        "scores": {"tractability": 18, "plausibility": 18, "validation": 6, "artifactCompleteness": 2},
        "units": "OK",
        "theory": "PASS-WITH-ASSUMPTIONS",
        "animation": {"status": "planned", "path": ""},
        "image": {"status": "planned", "path": ""},
        "description": "Novel mechanism: parity can flip due to geometry-field motion, not only due to circling a branch point. A Z\u2082 pump controlled by ln(\u03c0\u2090) dynamics. Conjecture: if \u0394\u03b8=0 but \u222b d(ln \u03c0\u2090) \u2260 0 over a closed loop, admissible lifts exist where b_a flips \u2014 the adaptive-\u03c0 analog of geometric phase without dynamical phase.",
        "differentialLatex": "\\dot\\varphi = \\frac{\\dot\\theta_R}{2\\pi_a} - \\varphi\\,\\frac{d}{dt}\\big(\\ln\\pi_a\\big)",
        "derivation": "Define dimensionless lifted phase \u03c6(t) := \u03b8_R(t)/(2\u03c0_a(t)). Differentiate: d\u03c6/dt = d\u03b8_R/dt / (2\u03c0_a) - \u03b8_R/(2\u03c0_a) \u00b7 d\u03c0_a/dt / \u03c0_a = d\u03b8_R/dt / (2\u03c0_a) - \u03c6 \u00b7 d(ln \u03c0_a)/dt. Half-integer crossings of \u03c6 flip b_a.",
        "assumptions": [
            "Smooth limit applies (continuous \u03c0_a and \u03b8_R).",
            "\u03c0_a > 0 everywhere (no degenerate period).",
            "Parity pump conjecture assumes closed-loop topology with nontrivial ln(\u03c0_a) circulation."
        ],
        "date": "2026-02-22",
        "equationLatex": "\\varphi(t) := \\frac{\\theta_R(t)}{2\\pi_a(t)},\\qquad \\int_\\gamma d(\\ln\\pi_a)\\neq 0 \\;\\Rightarrow\\; b_a[\\gamma]\\text{ can flip}",
        "tags": {"novelty": {"date": "2026-02-22", "score": 30}}
    },
    {
        "id": "eq-arp-gradient-flow-bridge",
        "name": "ARP as Gradient Flow in Adaptive-\u03c0 Geometry",
        "firstSeen": "2026-02-22",
        "source": "4-pillar fusion \u00a73",
        "score": 66,
        "scores": {"tractability": 18, "plausibility": 18, "validation": 8, "artifactCompleteness": 2},
        "units": "OK",
        "theory": "PASS-WITH-ASSUMPTIONS",
        "animation": {"status": "planned", "path": ""},
        "image": {"status": "planned", "path": ""},
        "description": "Bridge theorem: ARP reinforcement is proportional to edge energy contributions in a \u03c0\u2090-weighted Dirichlet landscape. ARP is a 'lazy' gradient flow where \u03a9 = \u03c0_a/\u03c0 changes what counts as a short/cheap path. Prediction: increasing \u03c0\u2090 in a region re-routes the ARP backbone away, even under the same boundary forcing. '\u03c0\u2090 sculpts geodesics; ARP discovers them.'",
        "differentialLatex": "\\mathcal{E}(\\phi;G,\\Omega)=\\frac{1}{2}\\sum_{(i,j)} \\Omega_{ij}\\,G_{ij}\\,(\\phi_i-\\phi_j)^2",
        "derivation": "On a graph with adaptive-\u03c0 weight \u03a9_{ij} and ARP conductance G_{ij}, the Dirichlet energy is E = (1/2) \u03a3 \u03a9_{ij} G_{ij} (\u03c6_i - \u03c6_j)\u00b2. Kirchhoff potentials give |I_{ij}| = G_{ij}|\u03c6_i - \u03c6_j|. ARP reinforce \u221d |I_{ij}| = edge contribution to \u221aE geometry. Hence ARP is gradient descent on the weighted energy landscape.",
        "assumptions": [
            "Network is connected; Kirchhoff potentials are well-defined per step.",
            "\u03a9_{ij} is sampled from the continuous \u03c0_a field at edge midpoints.",
            "Budget/normalization constraint forces edge competition (not all edges grow)."
        ],
        "date": "2026-02-22",
        "equationLatex": "\\dot G_{ij}=\\alpha_G\\,|I_{ij}|-\\mu_G\\,G_{ij},\\quad |I_{ij}|\\propto \\frac{\\partial\\sqrt{\\mathcal{E}}}{\\partial(\\sqrt{\\Omega_{ij}G_{ij}})}",
        "tags": {"novelty": {"date": "2026-02-22", "score": 29}}
    },
    {
        "id": "eq-cm-integration-state",
        "name": "Curve-Memory Integration State (unified closed loop)",
        "firstSeen": "2026-02-22",
        "source": "4-pillar fusion \u00a74",
        "score": 57,
        "scores": {"tractability": 17, "plausibility": 17, "validation": 4, "artifactCompleteness": 2},
        "units": "OK",
        "theory": "PASS-WITH-ASSUMPTIONS",
        "animation": {"status": "planned", "path": ""},
        "image": {"status": "planned", "path": ""},
        "description": "Defines a unified integration state s(t) = (\u03b8_R, w_a, b_a, \u03c0_a, M_k) bundling Phase-Lift, winding/parity, adaptive-\u03c0, and curve-memory features. Curve-memory curvature drives \u03c0_a, \u03c0_a changes phase unwrapping sensitivity, parity flips become detectable stable motifs. Turns topological sheet changes into an event grammar.",
        "derivation": "Bundle lifted phase \u03b8_R, gauged winding w_a, parity b_a, adaptive period \u03c0_a, and curve-memory jets M_k into a single state vector. Drive \u03c0_a via d\u03c0_a/dt = \u03b1_\u03c0 \u03ba_mem - \u03bc_\u03c0(\u03c0_a - \u03c0) where \u03ba_mem is trajectory curvature from curve-memory. This closes the loop: CM \u2192 events \u2192 \u03c0_a \u2192 unwrap sensitivity \u2192 parity \u2192 CM motifs.",
        "assumptions": [
            "Curve-memory features M_k are well-defined (sufficient trajectory history).",
            "\u03ba_mem is a smooth or piecewise-smooth curvature proxy.",
            "Feedback loop is stable under the chosen (\u03b1_\u03c0, \u03bc_\u03c0) parameters."
        ],
        "date": "2026-02-22",
        "equationLatex": "s(t)=\\big(\\theta_R,\\,w_a,\\,b_a,\\,\\pi_a,\\,M_k\\big),\\quad \\dot\\pi_a=\\alpha_\\pi\\,\\kappa_{\\text{mem}}-\\mu_\\pi(\\pi_a-\\pi)",
        "tags": {"novelty": {"date": "2026-02-22", "score": 27}}
    },
    {
        "id": "eq-adaptive-monodromy-spectrum",
        "name": "Adaptive Monodromy Spectrum (bifurcation framework)",
        "firstSeen": "2026-02-22",
        "source": "4-pillar fusion \u00a75",
        "score": 54,
        "scores": {"tractability": 16, "plausibility": 16, "validation": 4, "artifactCompleteness": 2},
        "units": "WARN",
        "theory": "PASS-WITH-ASSUMPTIONS",
        "animation": {"status": "planned", "path": ""},
        "image": {"status": "planned", "path": ""},
        "description": "For loop families \u03b3_\u03bb under \u03c0\u2090 evolution, the Adaptive Monodromy Pair M_a(\u03b3) = (w_a, b_a) \u2208 \u2124 \u00d7 {\u00b11} traces out a reachable set that can bifurcate: parity flips occur without classical winding as (\u03b1_\u03c0, \u03bc_\u03c0) or CM thresholds vary. Defines a research program: map bifurcation diagrams of M_a vs parameters.",
        "assumptions": [
            "Loop family \u03b3_\u03bb is smoothly parameterized.",
            "\u03c0_a evolves by reinforce/decay dynamics during deformation.",
            "Bifurcation analysis assumes sufficient parameter separation."
        ],
        "date": "2026-02-22",
        "equationLatex": "\\mathcal{M}_a(\\gamma)=\\big(w_a(\\gamma),\\,b_a(\\gamma)\\big)\\in\\mathbb{Z}\\times\\{\\pm1\\}",
        "tags": {"novelty": {"date": "2026-02-22", "score": 26}}
    },
]

added = 0
for e in new_eqs:
    if e["id"] not in existing:
        d["entries"].append(e)
        added += 1

d["lastUpdated"] = "2026-02-22"
d["entries"].sort(key=lambda e: float(e.get("score", 0)), reverse=True)
eq_path.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Added {added}, total {len(d['entries'])} entries")
for i, e in enumerate(d["entries"], 1):
    print(f"  #{i:2d}  Score {e['score']:3d}  {e['name']}")
