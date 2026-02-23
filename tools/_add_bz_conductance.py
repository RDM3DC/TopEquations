import json, pathlib

eq_path = pathlib.Path("data/equations.json")
d = json.loads(eq_path.read_text(encoding="utf-8"))
existing = {e["id"] for e in d["entries"]}

# 1) Add new equation (scored at 89)
new_eq = {
    "id": "eq-bz-phase-lifted-complex-conductance-entropy-gated",
    "name": "BZ-Averaged Phase-Lifted Complex Conductance Update (Entropy-Gated)",
    "firstSeen": "2026-02-22",
    "source": "derived: Core Eqs 2\u20134, 6\u20137, 10\u201311 + Leaderboard #3 + #10 (chat: PR Root Guide convo 2026-02-22)",
    "score": 89,
    "scores": {"tractability": 19, "plausibility": 19, "validation": 16, "artifactCompleteness": 8},
    "units": "OK",
    "theory": "PASS-WITH-ASSUMPTIONS",
    "animation": {"status": "linked", "path": "./assets/animations/BZPhaseLiftConductance.mp4"},
    "image": {"status": "planned", "path": ""},
    "description": "BZ-average the Phase-Lifted complex ARP drive, gate reinforcement by BZ phase coherence, and couple nonnegative entropy production to slip events + rate modulation.",
    "equationLatex": "\\frac{d\\tilde{G}_{ij}}{dt}=\\alpha_G(S)\\,\\mathcal{C}_{ij}(t)\\,J^{\\mathrm{PL}}_{ij}(t)-\\mu_G(S)\\,\\tilde{G}_{ij}(t)",
    "differentialLatex": "\\frac{dS}{dt}=\\sum_{ij}\\frac{|I_{ij}|^2}{T_{ij}}\\,\\operatorname{Re}\\!\\left(\\frac{1}{\\tilde{G}_{ij}}\\right)+\\kappa\\sum_{ij}\\Xi_{ij}(t)-\\gamma\\,(S-S_{\\rm eq})",
    "derivation": "Definitions: (1) Phase-Lift per mode: \\theta_{R,ij}(k,t)=\\mathrm{unwrap}(\\theta_{ij}(k,t);\\theta_{R,ij}(k,t-\\Delta t),\\pi_a(k,t)) with stored integer sheet index w_{ij}(k,t)\\in\\mathbb{Z}, parity b_{ij}(k,t)=(-1)^{w_{ij}(k,t)}. (2) BZ Phase-Lifted drive: J^{\\mathrm{PL}}_{ij}(t)=\\frac{\\int_{\\mathrm{BZ}} w(k,t)|I_{ij}(k,t)|e^{i\\theta_{R,ij}(k,t)}\\,d^dk}{\\int_{\\mathrm{BZ}} w(k,t)\\,d^dk}. (3) Coherence gate: \\mathcal{C}_{ij}(t)=\\frac{|\\int_{\\mathrm{BZ}} w(k,t)e^{i\\theta_{R,ij}(k,t)}\\,d^dk|}{\\int_{\\mathrm{BZ}} w(k,t)\\,d^dk}\\in[0,1]. (4) Slip entropy: \\Xi_{ij}(t)=\\sum_{k} w(k,t)|\\Delta w_{ij}(k,t)| (nonzero only on integer sheet jumps). (5) Self-consistent ruler coupling: \\langle 1/\\pi_a\\rangle_{\\mathrm{BZ}}=\\frac{1}{\\pi\\sqrt{1-\\varepsilon_{\\mathrm{eff}}^2}}\\Rightarrow \\varepsilon_{\\mathrm{eff}}(t)=\\sqrt{1-\\left(\\frac{1}{\\pi\\langle 1/\\pi_a\\rangle_{\\mathrm{BZ}}}\\right)^2},\\ \\ m_{\\mathrm{eff}}(\\varepsilon_{\\mathrm{eff}})=\\frac{m_0}{\\sqrt{1-\\varepsilon_{\\mathrm{eff}}^2}} (uniform feed into QWZ Hamiltonian).",
    "assumptions": [
        "Weights w(k,t) are user-chosen (occupation f(k,t), purity Tr \\rho(k,t)^2, or exp(-\\eta s(k,t))).",
        "\\pi_a(k,t)=\\pi(1+\\varepsilon(k)\\cos\\lambda) or a general positive field; \\varepsilon_{\\mathrm{eff}} inversion assumes the cosine form and |\\varepsilon_{\\mathrm{eff}}|<1.",
        "Entropy production term uses Re(1/\\tilde G) to ensure nonnegative dissipated power for passive response.",
        "Chern/topology computed with the gauge-invariant Fukui\u2013Hatsugai\u2013Suzuki lattice method; Phase-Lift provides continuous plaquette-arg history and slip detection only."
    ],
    "date": "2026-02-22",
    "tags": {"novelty": {"date": "2026-02-22", "score": 29}}
}

if new_eq["id"] not in existing:
    d["entries"].append(new_eq)
    print(f"Added: {new_eq['name']}  (score {new_eq['score']})")
else:
    print(f"SKIP (exists): {new_eq['id']}")

# 2) Link animations to the two QWZ equations that now have them
anim_links = {
    "eq-qwz-pia-modulated-mass": "./assets/animations/PiAModulatedQWZMass.mp4",
    "eq-qwz-bz-avg-ruler-mass":  "./assets/animations/BZAveragedRulerQWZ.mp4",
}
for e in d["entries"]:
    if e["id"] in anim_links:
        e["animation"] = {"status": "linked", "path": anim_links[e["id"]]}
        print(f"Linked animation: {e['id']} \u2192 {anim_links[e['id']]}")

d["lastUpdated"] = "2026-02-22"
d["entries"].sort(key=lambda x: float(x.get("score", 0)), reverse=True)
eq_path.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")

print(f"\nTotal: {len(d['entries'])} entries")
for i, e in enumerate(d["entries"][:10], 1):
    a = "\u2713" if e.get("animation", {}).get("status") == "linked" else " "
    print(f"  #{i:2d}  [{a}]  Score {e['score']:3d}  {e['name']}")
