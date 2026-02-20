# Equation Leaderboard
_Last updated: 2026-02-20_

This is the canonical ranking board for existing and newly derived equations.

Scoring model (0-100):
- Novelty (0-30)
- Tractability (0-20)
- Physical plausibility (0-20)
- Validation bonus (0-20):
  - units `OK` (+10)
  - theory `PASS` (+10)
- Artifact completeness bonus (0-10):
  - animation linked (+5)
  - image/diagram linked (+5)

## Current Top Equations (All-Time)

| Rank | Equation Name | Equation | Source | Score | Units | Theory | Animation | Image/Diagram | Description |
| ------ | --------------- | -------- | -------- | ------- | ------- | -------- | ----------- | --------------- | ------------- |
| 1 | ARP Redshift Law (derived mapping) | z(t)=z_0\,(1-e^{-\gamma t}) | discovery-matrix #1 | 88 | OK | PASS-WITH-ASSUMPTIONS | ./assets/animations/eq-arp-redshift.mp4 | planned | A redshift-like relaxation emerges when an ARP-governed transport variable is mapped to a normalized deficit observable. |
| 2 | Phase-Coupled Stability Threshold Law | \frac{dG_{ij}}{dt}=\alpha\,\|I_{ij}\|-\mu\,G_{ij}-\lambda\,G_{ij}\,\sin^2\!\left(\frac{\theta_{R,ij}}{2\pi_a}\right) | derived: ARP + Phase-Lift + Adaptive-π | 82 | OK | PASS-WITH-ASSUMPTIONS | ./assets/animations/eq-arp-phase-critical-collapse.mp4 | planned | Adds a phase-coupled suppression term to ARP: conductance growth is damped by lifted phase accumulation relative to the local period 2πₐ. Predicts a sharp stability/transition-like behavior when θ_R approaches half-integer multiples of πₐ (maximal sin²). Assumptions: θ_R,ij is a Phase-Lifted (unwrapped) phase-like observable for edge current; πₐ sets the relevant phase period; λ has units 1/time. |
| 3 | Phase-Lifted Complex Conductance Update | \frac{d\tilde G_{ij}}{dt}=\alpha_G\,\|I_{ij}(t)\|\,e^{i\theta_{R,ij}(t)}-\mu_G\,\tilde G_{ij}(t),\qquad \theta_{R,ij}(t)=\mathrm{unwrap}\!\big(\arg I_{ij}(t);\theta_{\rm ref},\pi_a\big) | derived: ARP core + Phase-Lift + Adaptive-π | 76 | OK | PASS-WITH-ASSUMPTIONS | ./assets/animations/eq-arp-phase-lifted-complex-conductance.mp4 | planned | Complex-admittance lift of ARP: conductance grows along the instantaneous current phasor direction using a Phase-Lifted (unwrapped) phase. Assumes phase-coherent transport where a complex ~G is meaningful. Optional variant: include a Z2 parity factor b_ij = (-1)^{w_ij} multiplying e^{iθ_R,ij} to model sign flips under branch crossings. |
| 4 | ARP Lyapunov Stability Form | V(x)\ge 0,\ V(0)=0;\ \dot V(x)=\nabla V\cdot \dot x\le -\alpha V(x) | discovery-matrix #2 | 75 | OK | PASS-WITH-ASSUMPTIONS | ./assets/animations/eq-arp-lyapunov-stability.mp4 | planned | Candidate stability proof template for adaptive conductance dynamics. |
| 5 | Unified Dynamic Constants Law | \dot{\mathbf{c}}=A\,\mathbf{c}\ \ \text{with}\ \mathbf{c}=[\pi_a, e, \varphi, c]^T | discovery-matrix #3 | 73 | OK | PASS-WITH-ASSUMPTIONS | ./assets/animations/eq-dyn-constants-union.mp4 | planned | First-order linear coupling for adaptive updates of πₐ, e, ϕ, and c, expressing networked rates of change—models the unification of ARP, AIN, and πₐ system parameters. |
| 6 | Curve Memory Fine-Structure Emergence | \alpha^{-1}\approx 137\ \ \text{(emergent resonance condition in curve memory)} | discovery-matrix #4 | 72 | OK | PASS-WITH-ASSUMPTIONS | ./assets/animations/eq-curve-memory-137.mp4 | planned | Formalizes the emergence of the inverse fine-structure constant (α⁻¹ ≈ 137) via resonant harmonic conditions in curve memory, assuming an equilibrium state governed by ARP-influenced boundary dynamics. |
| 7 | Shielding Mechanism Law (ARP) | E_{eff}=(1-\lambda)E_{ext},\ \ J_{adapt}=\sigma E_{ext},\ \ 0<\lambda<1 | discovery-matrix #5 | 71 | OK | PASS-WITH-ASSUMPTIONS | ./assets/animations/eq-shield-mechanic-arp.mp4 | planned | Proposes a shielding effect in ARP systems, modeled as a fractional reduction of the external field. The effective field is E_eff = (1 − λ)E_ext, while the induced adaptive current follows J_adapt = σE_ext, with 0 < λ < 1. |
| 8 | Redshift-ARP Superconductivity Law | R_s(z) = R_{s,0} (1 + z)^\alpha | discovery-matrix #1 (supercond.) | 70 | OK | PASS-WITH-ASSUMPTIONS | ./assets/animations/eq-redshift-arp-superc.mp4 | planned | Proposes a cosmological scaling for critical superconducting resistance: R_s(z) = R_{s,0} (1+z)^alpha. Assumes layered structure, universal conductance constant, ARP regime dominant. |
| 9 | Temperature-Dependent Conductance Law | G(T)=G_{eq}\,e^{\beta\,(T-T_0)} | daily run 2026-02-19 | 68 | OK | PASS | ./assets/animations/eq-arp-temp-conductance.mp4 | planned | Extends ARP equilibrium with an exponential temperature factor for material sensitivity. |

## Newest Top-Ranked Equations (This Month)

| Date | Equation Name | Score | Units | Theory | Animation | Image/Diagram | Short Description |
| ------ | --------------- | ------- | ------- | -------- | ----------- | --------------- | ------------------- |
| 2026-02-20 | ARP Redshift Law (derived mapping) | 88 | OK | PASS-WITH-ASSUMPTIONS | ./assets/animations/eq-arp-redshift.mp4 | planned | A redshift-like relaxation emerges when an ARP-governed transport variable is mapped to a normalized deficit observable. |
| 2026-02-20 | Phase-Coupled Stability Threshold Law | 82 | OK | PASS-WITH-ASSUMPTIONS | ./assets/animations/eq-arp-phase-critical-collapse.mp4 | planned | Adds a phase-coupled suppression term to ARP: conductance growth is damped by lifted phase accumulation relative to the local period 2πₐ. Predicts a sharp stability/transition-like behavior when θ_R approaches half-integer multiples of πₐ (maximal sin²). Assumptions: θ_R,ij is a Phase-Lifted (unwrapped) phase-like observable for edge current; πₐ sets the relevant phase period; λ has units 1/time. |
| 2026-02-20 | Phase-Lifted Complex Conductance Update | 76 | OK | PASS-WITH-ASSUMPTIONS | ./assets/animations/eq-arp-phase-lifted-complex-conductance.mp4 | planned | Complex-admittance lift of ARP: conductance grows along the instantaneous current phasor direction using a Phase-Lifted (unwrapped) phase. Assumes phase-coherent transport where a complex ~G is meaningful. Optional variant: include a Z2 parity factor b_ij = (-1)^{w_ij} multiplying e^{iθ_R,ij} to model sign flips under branch crossings. |
| 2026-02-19 | ARP Lyapunov Stability Form | 75 | OK | PASS-WITH-ASSUMPTIONS | ./assets/animations/eq-arp-lyapunov-stability.mp4 | planned | Candidate stability proof template for adaptive conductance dynamics. |
| 2026-02-20 | Unified Dynamic Constants Law | 73 | OK | PASS-WITH-ASSUMPTIONS | ./assets/animations/eq-dyn-constants-union.mp4 | planned | First-order linear coupling for adaptive updates of πₐ, e, ϕ, and c, expressing networked rates of change—models the unification of ARP, AIN, and πₐ system parameters. |
| 2026-02-20 | Curve Memory Fine-Structure Emergence | 72 | OK | PASS-WITH-ASSUMPTIONS | ./assets/animations/eq-curve-memory-137.mp4 | planned | Formalizes the emergence of the inverse fine-structure constant (α⁻¹ ≈ 137) via resonant harmonic conditions in curve memory, assuming an equilibrium state governed by ARP-influenced boundary dynamics. |
| 2026-02-20 | Shielding Mechanism Law (ARP) | 71 | OK | PASS-WITH-ASSUMPTIONS | ./assets/animations/eq-shield-mechanic-arp.mp4 | planned | Proposes a shielding effect in ARP systems, modeled as a fractional reduction of the external field. The effective field is E_eff = (1 − λ)E_ext, while the induced adaptive current follows J_adapt = σE_ext, with 0 < λ < 1. |
| 2026-02-20 | Redshift-ARP Superconductivity Law | 70 | OK | PASS-WITH-ASSUMPTIONS | ./assets/animations/eq-redshift-arp-superc.mp4 | planned | Proposes a cosmological scaling for critical superconducting resistance: R_s(z) = R_{s,0} (1+z)^alpha. Assumes layered structure, universal conductance constant, ARP regime dominant. |
| 2026-02-19 | Temperature-Dependent Conductance Law | 68 | OK | PASS | ./assets/animations/eq-arp-temp-conductance.mp4 | planned | Extends ARP equilibrium with an exponential temperature factor for material sensitivity. |

## All Equations Since 2025 (Registry)

| First Seen | Equation Name | Equation | Source | Latest Status | Latest Score | Animation | Image/Diagram |
| ------------ | --------------- | -------- | -------- | --------------- | -------------- | ----------- | --------------- |
| 2025-04 | ARP Redshift Law (derived mapping) | z(t)=z_0\,(1-e^{-\gamma t}) | discovery-matrix #1 | PASS-WITH-ASSUMPTIONS | 88 | ./assets/animations/eq-arp-redshift.mp4 | planned |
| 2025-06 | ARP Lyapunov Stability Form | V(x)\ge 0,\ V(0)=0;\ \dot V(x)=\nabla V\cdot \dot x\le -\alpha V(x) | discovery-matrix #2 | PASS-WITH-ASSUMPTIONS | 75 | ./assets/animations/eq-arp-lyapunov-stability.mp4 | planned |
| 2026-02 | Phase-Coupled Stability Threshold Law | \frac{dG_{ij}}{dt}=\alpha\,\|I_{ij}\|-\mu\,G_{ij}-\lambda\,G_{ij}\,\sin^2\!\left(\frac{\theta_{R,ij}}{2\pi_a}\right) | derived: ARP + Phase-Lift + Adaptive-π | PASS-WITH-ASSUMPTIONS | 82 | ./assets/animations/eq-arp-phase-critical-collapse.mp4 | planned |
| 2026-02 | Phase-Lifted Complex Conductance Update | \frac{d\tilde G_{ij}}{dt}=\alpha_G\,\|I_{ij}(t)\|\,e^{i\theta_{R,ij}(t)}-\mu_G\,\tilde G_{ij}(t),\qquad \theta_{R,ij}(t)=\mathrm{unwrap}\!\big(\arg I_{ij}(t);\theta_{\rm ref},\pi_a\big) | derived: ARP core + Phase-Lift + Adaptive-π | PASS-WITH-ASSUMPTIONS | 76 | ./assets/animations/eq-arp-phase-lifted-complex-conductance.mp4 | planned |
| 2026-02 | Curve Memory Fine-Structure Emergence | \alpha^{-1}\approx 137\ \ \text{(emergent resonance condition in curve memory)} | discovery-matrix #4 | PASS-WITH-ASSUMPTIONS | 72 | ./assets/animations/eq-curve-memory-137.mp4 | planned |
| 2026-02 | Shielding Mechanism Law (ARP) | E_{eff}=(1-\lambda)E_{ext},\ \ J_{adapt}=\sigma E_{ext},\ \ 0<\lambda<1 | discovery-matrix #5 | PASS-WITH-ASSUMPTIONS | 71 | ./assets/animations/eq-shield-mechanic-arp.mp4 | planned |
| 2026-02 | Redshift-ARP Superconductivity Law | R_s(z) = R_{s,0} (1 + z)^\alpha | discovery-matrix #1 (supercond.) | PASS-WITH-ASSUMPTIONS | 70 | ./assets/animations/eq-redshift-arp-superc.mp4 | planned |
| 2026-02 | Temperature-Dependent Conductance Law | G(T)=G_{eq}\,e^{\beta\,(T-T_0)} | daily run 2026-02-19 | PASS | 68 | ./assets/animations/eq-arp-temp-conductance.mp4 | planned |
| 2026-02-20 | Unified Dynamic Constants Law | \dot{\mathbf{c}}=A\,\mathbf{c}\ \ \text{with}\ \mathbf{c}=[\pi_a, e, \varphi, c]^T | discovery-matrix #3 | PASS-WITH-ASSUMPTIONS | 73 | ./assets/animations/eq-dyn-constants-union.mp4 | planned |

## Update Rules

1. Add every daily candidate to `submissions/YYYY-MM-DD.md`.
2. Keep `data/equations.json` as source of truth.
3. Regenerate this file with `python tools/generate_leaderboard.py`.
4. Keep animation/image columns as links or `planned` status only.
