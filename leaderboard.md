# Equation Leaderboard
_Last updated: 2026-02-21_

This is the canonical ranking board for existing and newly derived equations.

Scoring model (0-100):
- Tractability (0-20)
- Physical plausibility (0-20)
- Validation bonus (0-20)
- Artifact completeness bonus (0-10)
- Total normalized from 70-point base to 100
- Novelty is tracked as a tag (`tags.novelty`) with score + date

## Current Top Equations (All-Time)

| Rank | Equation Name | Equation | Source | Score | Novelty tag | Units | Theory | Animation | Image/Diagram | Description |
| ------ | --------------- | -------- | -------- | ------- | ----------- | ------- | -------- | ----------- | --------------- | ------------- |
| 1 | ARP Redshift Law (derived mapping) | z(t)=z_0\,(1-e^{-\gamma t}) | discovery-matrix #1 | 91 | 24 @ 2026-02-20 | OK | PASS-WITH-ASSUMPTIONS | ./assets/animations/eq-arp-redshift.mp4 | https://github.com/RDM3DC/ARP-Redshift-Law-d-e-r-i-v-e-d-m-a-p-p-i-n-g.git | A redshift-like relaxation emerges when an ARP-governed transport variable is mapped to a normalized deficit observable. |
| 2 | Phase-Coupled Stability Threshold Law | \frac{dG_{ij}}{dt}=\alpha\,\|I_{ij}\|-\mu\,G_{ij}-\lambda\,G_{ij}\,\sin^2\!\left(\frac{\theta_{R,ij}}{2\pi_a}\right) | derived: ARP + Phase-Lift + Adaptive-Ï€ | 77 | 28 @ 2026-02-20 | OK | PASS-WITH-ASSUMPTIONS | ./assets/animations/eq-arp-phase-critical-collapse.mp4 | planned | Adds a phase-coupled suppression term to ARP: conductance growth is damped by lifted phase accumulation relative to the local period 2Ï€â‚. Predicts a sharp stability/transition-like behavior when Î¸_R approaches half-integer multiples of Ï€â‚ (maximal sinÂ²). Assumptions: Î¸_R,ij is a Phase-Lifted (unwrapped) phase-like observable for edge current; Ï€â‚ sets the relevant phase period; Î» has units 1/time. |
| 3 | Phase-Lifted Complex Conductance Update | \frac{d\tilde G_{ij}}{dt}=\alpha_G\,\|I_{ij}(t)\|\,e^{i\theta_{R,ij}(t)}-\mu_G\,\tilde G_{ij}(t),\qquad \theta_{R,ij}(t)=\mathrm{unwrap}\!\big(\arg I_{ij}(t);\theta_{\rm ref},\pi_a\big) | derived: ARP core + Phase-Lift + Adaptive-Ï€ | 71 | 26 @ 2026-02-20 | OK | PASS-WITH-ASSUMPTIONS | ./assets/animations/eq-arp-phase-lifted-complex-conductance.mp4 | planned | Complex-admittance lift of ARP: conductance grows along the instantaneous current phasor direction using a Phase-Lifted (unwrapped) phase. Assumes phase-coherent transport where a complex ~G is meaningful. Optional variant: include a Z2 parity factor b_ij = (-1)^{w_ij} multiplying e^{iÎ¸_R,ij} to model sign flips under branch crossings. |
| 4 | Temperature-Dependent Conductance Law | G(T)=G_{eq}\,e^{\beta\,(T-T_0)} | daily run 2026-02-19 | 69 | 20 @ 2026-02-19 | OK | PASS | ./assets/animations/eq-arp-temp-conductance.mp4 | planned | Extends ARP equilibrium with an exponential temperature factor for material sensitivity. |

## Newest Top-Ranked Equations (This Month)

| Date | Equation Name | Score | Units | Theory | Animation | Image/Diagram | Short Description |
| ------ | --------------- | ------- | ------- | -------- | ----------- | --------------- | ------------------- |
| 2026-02-20 | ARP Redshift Law (derived mapping) | 91 | OK | PASS-WITH-ASSUMPTIONS | ./assets/animations/eq-arp-redshift.mp4 | https://github.com/RDM3DC/ARP-Redshift-Law-d-e-r-i-v-e-d-m-a-p-p-i-n-g.git | A redshift-like relaxation emerges when an ARP-governed transport variable is mapped to a normalized deficit observable. |
| 2026-02-20 | Phase-Coupled Stability Threshold Law | 77 | OK | PASS-WITH-ASSUMPTIONS | ./assets/animations/eq-arp-phase-critical-collapse.mp4 | planned | Adds a phase-coupled suppression term to ARP: conductance growth is damped by lifted phase accumulation relative to the local period 2Ï€â‚. Predicts a sharp stability/transition-like behavior when Î¸_R approaches half-integer multiples of Ï€â‚ (maximal sinÂ²). Assumptions: Î¸_R,ij is a Phase-Lifted (unwrapped) phase-like observable for edge current; Ï€â‚ sets the relevant phase period; Î» has units 1/time. |
| 2026-02-20 | Phase-Lifted Complex Conductance Update | 71 | OK | PASS-WITH-ASSUMPTIONS | ./assets/animations/eq-arp-phase-lifted-complex-conductance.mp4 | planned | Complex-admittance lift of ARP: conductance grows along the instantaneous current phasor direction using a Phase-Lifted (unwrapped) phase. Assumes phase-coherent transport where a complex ~G is meaningful. Optional variant: include a Z2 parity factor b_ij = (-1)^{w_ij} multiplying e^{iÎ¸_R,ij} to model sign flips under branch crossings. |
| 2026-02-19 | Temperature-Dependent Conductance Law | 69 | OK | PASS | ./assets/animations/eq-arp-temp-conductance.mp4 | planned | Extends ARP equilibrium with an exponential temperature factor for material sensitivity. |

## All Equations Since 2025 (Registry)

| First Seen | Equation Name | Equation | Source | Latest Status | Latest Score | Animation | Image/Diagram |
| ------------ | --------------- | -------- | -------- | --------------- | -------------- | ----------- | --------------- |
| 2025-04 | ARP Redshift Law (derived mapping) | z(t)=z_0\,(1-e^{-\gamma t}) | discovery-matrix #1 | PASS-WITH-ASSUMPTIONS | 91 | ./assets/animations/eq-arp-redshift.mp4 | https://github.com/RDM3DC/ARP-Redshift-Law-d-e-r-i-v-e-d-m-a-p-p-i-n-g.git |
| 2025-06 | ARP Lyapunov Stability Form | V(x)\ge 0,\ V(0)=0;\ \dot V(x)=\nabla V\cdot \dot x\le -\alpha V(x) | discovery-matrix #2 | PASS-WITH-ASSUMPTIONS | 66 | ./assets/animations/eq-arp-lyapunov-stability.mp4 | planned |
| 2026-02 | Phase-Coupled Stability Threshold Law | \frac{dG_{ij}}{dt}=\alpha\,\|I_{ij}\|-\mu\,G_{ij}-\lambda\,G_{ij}\,\sin^2\!\left(\frac{\theta_{R,ij}}{2\pi_a}\right) | derived: ARP + Phase-Lift + Adaptive-Ï€ | PASS-WITH-ASSUMPTIONS | 77 | ./assets/animations/eq-arp-phase-critical-collapse.mp4 | planned |
| 2026-02 | Phase-Lifted Complex Conductance Update | \frac{d\tilde G_{ij}}{dt}=\alpha_G\,\|I_{ij}(t)\|\,e^{i\theta_{R,ij}(t)}-\mu_G\,\tilde G_{ij}(t),\qquad \theta_{R,ij}(t)=\mathrm{unwrap}\!\big(\arg I_{ij}(t);\theta_{\rm ref},\pi_a\big) | derived: ARP core + Phase-Lift + Adaptive-Ï€ | PASS-WITH-ASSUMPTIONS | 71 | ./assets/animations/eq-arp-phase-lifted-complex-conductance.mp4 | planned |
| 2026-02 | Temperature-Dependent Conductance Law | G(T)=G_{eq}\,e^{\beta\,(T-T_0)} | daily run 2026-02-19 | PASS | 69 | ./assets/animations/eq-arp-temp-conductance.mp4 | planned |
| 2026-02 | Curve Memory Fine-Structure Emergence | \alpha^{-1}\approx 137\ \ \text{(emergent resonance condition in curve memory)} | discovery-matrix #4 | PASS-WITH-ASSUMPTIONS | 63 | ./assets/animations/eq-curve-memory-137.mp4 | planned |
| 2026-02 | Shielding Mechanism Law (ARP) | E_{eff}=(1-\lambda)E_{ext},\ \ J_{adapt}=\sigma E_{ext},\ \ 0<\lambda<1 | discovery-matrix #5 | PASS-WITH-ASSUMPTIONS | 63 | ./assets/animations/eq-shield-mechanic-arp.mp4 | planned |
| 2026-02 | Redshift-ARP Superconductivity Law | R_s(z) = R_{s,0} (1 + z)^\alpha | discovery-matrix #1 (supercond.) | PASS-WITH-ASSUMPTIONS | 60 | ./assets/animations/eq-redshift-arp-superc.mp4 | planned |
| 2026-02-20 | Unified Dynamic Constants Law | \dot{\mathbf{c}}=A\,\mathbf{c}\ \ \text{with}\ \mathbf{c}=[\pi_a, e, \varphi, c]^T | discovery-matrix #3 | PASS-WITH-ASSUMPTIONS | 61 | ./assets/animations/eq-dyn-constants-union.mp4 | planned |

## Update Rules

1. Add every daily candidate to `submissions/YYYY-MM-DD.md`.
2. Keep `data/equations.json` as source of truth.
3. Regenerate this file with `python tools/generate_leaderboard.py`.
4. Keep animation/image columns as links or `planned` status only.
