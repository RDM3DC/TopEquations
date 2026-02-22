import json, pathlib, sys

eq_path = pathlib.Path("data/equations.json")
d = json.loads(eq_path.read_text(encoding="utf-8"))
existing = {e["id"] for e in d["entries"]}

new = [
  {
    "id": "eq-adaptive-phase-lift-unwrapping",
    "name": "Adaptive Phase-Lift Unwrap Recurrence (pi_a-gauged)",
    "firstSeen": "2026-02-22",
    "source": "chat: PR Root Guide convo 2026-02-22",
    "score": 0,
    "scores": { "novelty": 0, "tractability": 0, "plausibility": 0, "validation": 0, "artifactCompleteness": 0 },
    "units": "OK",
    "theory": "PASS-WITH-ASSUMPTIONS",
    "animation": { "status": "planned", "path": "" },
    "image": { "status": "planned", "path": "" },
    "description": "Adaptive Phase-Lift recurrence: unwrap arg using local identification length 2\u03c0_a (not fixed 2\u03c0); yields integer sheet count and Z2 parity tracking.",
    "date": "2026-02-22",
    "equationLatex": "\\theta_R(t_k)=\\theta(t_k)+2\\pi_a(t_k)m_k,\\quad m_k=\\arg\\min_{m\\in\\mathbb{Z}}\\left|\\theta(t_k)+2\\pi_a(t_k)m-\\theta_R(t_{k-1})\\right|"
  },
  {
    "id": "eq-dimensionless-phase-flow",
    "name": "Dimensionless Lifted Phase Flow (pi_a-driven pump term)",
    "firstSeen": "2026-02-22",
    "source": "chat: PR Root Guide convo 2026-02-22",
    "score": 0,
    "scores": { "novelty": 0, "tractability": 0, "plausibility": 0, "validation": 0, "artifactCompleteness": 0 },
    "units": "OK",
    "theory": "PASS-WITH-ASSUMPTIONS",
    "animation": { "status": "planned", "path": "" },
    "image": { "status": "planned", "path": "" },
    "description": "Defines \u03c6=\u03b8_R/(2\u03c0_a) and shows \u03c0_a dynamics can drive half-integer crossings (a Z2 pump mechanism) even with smooth \u03b8_R.",
    "date": "2026-02-22",
    "equationLatex": "\\varphi:=\\theta_R/(2\\pi_a),\\quad \\dot\\varphi=\\dot\\theta_R/(2\\pi_a)-\\varphi\\,\\frac{d}{dt}(\\ln\\pi_a)"
  },
  {
    "id": "eq-adaptive-discriminant-set",
    "name": "Adaptive Discriminant Set for Parity/Winding Stability",
    "firstSeen": "2026-02-22",
    "source": "chat: PR Root Guide convo 2026-02-22",
    "score": 0,
    "scores": { "novelty": 0, "tractability": 0, "plausibility": 0, "validation": 0, "artifactCompleteness": 0 },
    "units": "OK",
    "theory": "PASS-WITH-ASSUMPTIONS",
    "animation": { "status": "planned", "path": "" },
    "image": { "status": "planned", "path": "" },
    "description": "Singular set where the lift can fail and winding/parity may change; away from D, w and b are homotopy invariants.",
    "date": "2026-02-22",
    "equationLatex": "\\mathcal{D}=\\{z=0\\}\\cup\\{\\pi_a=0\\}"
  },
  {
    "id": "eq-adaptive-connection-chern",
    "name": "Adaptive Connection and Adaptive Chern Number (Theorem B candidate)",
    "firstSeen": "2026-02-22",
    "source": "chat: PR Root Guide convo 2026-02-22",
    "score": 0,
    "scores": { "novelty": 0, "tractability": 0, "plausibility": 0, "validation": 0, "artifactCompleteness": 0 },
    "units": "OK",
    "theory": "PASS-WITH-ASSUMPTIONS",
    "animation": { "status": "planned", "path": "" },
    "image": { "status": "planned", "path": "" },
    "description": "Defines a rescaled connection \u00c2=A/(2\u03c0_a) and curvature F\u0302=d\u00c2; C_a is integer-valued when the rescaling is globally well-defined.",
    "date": "2026-02-22",
    "equationLatex": "\\widehat A:=A/(2\\pi_a),\\quad \\widehat F:=d\\widehat A,\\quad C_a:=\\frac{1}{2\\pi}\\int_{T^2}\\widehat F\\in\\mathbb{Z}"
  },
  {
    "id": "eq-parity-from-adaptive-chern",
    "name": "Parity Pump Law from Adaptive Chern",
    "firstSeen": "2026-02-22",
    "source": "chat: PR Root Guide convo 2026-02-22",
    "score": 0,
    "scores": { "novelty": 0, "tractability": 0, "plausibility": 0, "validation": 0, "artifactCompleteness": 0 },
    "units": "OK",
    "theory": "PASS-WITH-ASSUMPTIONS",
    "animation": { "status": "planned", "path": "" },
    "image": { "status": "planned", "path": "" },
    "description": "Mod-2 holonomy/parity flip controlled by the integer adaptive Chern invariant.",
    "date": "2026-02-22",
    "equationLatex": "b_{\\mathrm{pumped}}=(-1)^{C_a}"
  },
  {
    "id": "eq-qwz-pia-modulated-mass",
    "name": "pi_a-Modulated QWZ Mass (momentum-dependent; re-entrant transitions)",
    "firstSeen": "2026-02-22",
    "source": "chat: PR Root Guide convo 2026-02-22",
    "score": 0,
    "scores": { "novelty": 0, "tractability": 0, "plausibility": 0, "validation": 0, "artifactCompleteness": 0 },
    "units": "WARN",
    "theory": "PASS-WITH-ASSUMPTIONS",
    "animation": { "status": "planned", "path": "" },
    "image": { "status": "planned", "path": "" },
    "description": "Couples the QWZ topological mass to the adaptive ruler, making m_eff depend on k_x; numerically produces multiple gap closings and re-entrant Chern sectors.",
    "date": "2026-02-22",
    "equationLatex": "\\pi_a(\\lambda)=\\pi(1+\\epsilon\\cos\\lambda),\\quad m_{\\mathrm{eff}}(k_x)=m_0+\\beta\\left(\\frac{1}{1+\\epsilon\\cos k_x}-1\\right)"
  },
  {
    "id": "eq-qwz-bz-avg-ruler-mass",
    "name": "BZ-Averaged Ruler Coupling for Single-Jump QWZ Transition",
    "firstSeen": "2026-02-22",
    "source": "chat: PR Root Guide convo 2026-02-22",
    "score": 0,
    "scores": { "novelty": 0, "tractability": 0, "plausibility": 0, "validation": 0, "artifactCompleteness": 0 },
    "units": "OK",
    "theory": "PASS-WITH-ASSUMPTIONS",
    "animation": { "status": "planned", "path": "" },
    "image": { "status": "planned", "path": "" },
    "description": "BZ-average removes k-oscillation: <(1+\u03b5 cos\u03bb)^{-1}> = (1-\u03b5^2)^{-1/2}, giving a uniform m_eff(\u03b5) and a single Chern jump at \u03b5_c (for m0=-1: \u03b5_c=\u221a3/2).",
    "date": "2026-02-22",
    "equationLatex": "\\left\\langle\\frac{1}{1+\\epsilon\\cos\\lambda}\\right\\rangle_{BZ}=\\frac{1}{\\sqrt{1-\\epsilon^2}},\\quad m_{\\mathrm{eff}}(\\epsilon)=\\frac{m_0}{\\sqrt{1-\\epsilon^2}}\\ (|\\epsilon|<1),\\quad \\epsilon_c=\\sqrt{1-(|m_0|/2)^2}"
  },
  {
    "id": "eq-qwz-engineered-single-jump",
    "name": "Engineered Pinch-to-Transition Mass Drive (single-jump toy)",
    "firstSeen": "2026-02-22",
    "source": "chat: PR Root Guide convo 2026-02-22",
    "score": 0,
    "scores": { "novelty": 0, "tractability": 0, "plausibility": 0, "validation": 0, "artifactCompleteness": 0 },
    "units": "WARN",
    "theory": "PASS-WITH-ASSUMPTIONS",
    "animation": { "status": "planned", "path": "" },
    "image": { "status": "planned", "path": "" },
    "description": "Monotone coupling that forces one Chern jump near \u03b5\u21921^- (useful as a controllable toy model; clamp to trivial mass after the discriminant).",
    "date": "2026-02-22",
    "equationLatex": "m_{\\mathrm{eff}}(\\epsilon)=m_0-\\beta\\frac{\\epsilon^p}{1-\\epsilon}\\ (\\epsilon<1),\\quad m_{\\mathrm{eff}}(\\epsilon)=m_{\\mathrm{triv}}\\ (\\epsilon\\ge 1)"
  },
  {
    "id": "eq-arp-weighted-dirichlet-energy",
    "name": "Weighted Dirichlet Energy (ARP learns Omega-geodesics)",
    "firstSeen": "2026-02-22",
    "source": "chat: PR Root Guide convo 2026-02-22",
    "score": 0,
    "scores": { "novelty": 0, "tractability": 0, "plausibility": 0, "validation": 0, "artifactCompleteness": 0 },
    "units": "OK",
    "theory": "PASS-WITH-ASSUMPTIONS",
    "animation": { "status": "planned", "path": "" },
    "image": { "status": "planned", "path": "" },
    "description": "Graph Dirichlet energy with adaptive-\u03c0 weights \u03a9_ij; suggests ARP reinforcement concentrates conductance on \u03a9-weighted shortest paths / backbones.",
    "date": "2026-02-22",
    "equationLatex": "\\mathcal{E}(\\phi;G,\\Omega)=\\frac12\\sum_{(i,j)}\\Omega_{ij}G_{ij}(\\phi_i-\\phi_j)^2"
  }
]

added = 0
for e in new:
    if e["id"] not in existing:
        d["entries"].append(e)
        existing.add(e["id"])
        added += 1
    else:
        print(f"  SKIP (exists): {e['id']}")

d["lastUpdated"] = "2026-02-22"
d["entries"].sort(key=lambda x: float(x.get("score", 0)), reverse=True)
eq_path.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Added {added}, total {len(d['entries'])} entries")
