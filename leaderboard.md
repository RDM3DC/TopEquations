# Equation Leaderboard
_Last updated: 2026-02-19_

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

| Rank | Equation Name | Source | Score | Units | Theory | Animation | Image/Diagram | Description |
|------|---------------|--------|-------|-------|--------|-----------|---------------|-------------|
| 1 | ARP Redshift Law (candidate) | discovery-matrix #1 | 78 | WARN | PASS-WITH-ASSUMPTIONS | planned | planned | Conductance-decay framing for cosmological redshift with explicit damping terms. |
| 2 | ARP Lyapunov Stability Form | discovery-matrix #2 | 75 | OK | PASS-WITH-ASSUMPTIONS | planned | planned | Candidate stability proof template for adaptive conductance dynamics. |
| 3 | Dynamic Constants Coupling | discovery-matrix #3 | 71 | WARN | PASS-WITH-ASSUMPTIONS | planned | planned | Proposed coupling of adaptive pi/e/phi/c into one shared field update law. |
| 4 | Curve-Memory 137 Threshold | discovery-matrix #4 | 65 | OK | FAIL | planned | planned | Alpha_fs threshold proposal for state transitions; needs formal derivation. |
| 5 | ARP Shield Mechanic | discovery-matrix #5 | 62 | WARN | FAIL | planned | planned | Early protective-dynamics equation family for perturbation suppression. |

## Newest Top-Ranked Equations (This Month)

| Date | Equation Name | Score | Units | Theory | Animation | Image/Diagram | Short Description |
|------|---------------|-------|-------|--------|-----------|---------------|-------------------|
| 2026-02-19 | ARP Redshift Law (candidate) | 78 | WARN | PASS-WITH-ASSUMPTIONS | planned | planned | Conductance-decay to redshift mapping with explicit assumptions. |
| 2026-02-19 | ARP Lyapunov Stability Form | 75 | OK | PASS-WITH-ASSUMPTIONS | planned | planned | Stability form intended for direct repo integration. |
| 2026-02-19 | Dynamic Constants Coupling | 71 | WARN | PASS-WITH-ASSUMPTIONS | planned | planned | Unified adaptive constants proposal from pi_a + ARP + AIN. |

## All Equations Since 2025 (Registry)

| First Seen | Equation Name | Family | Source | Latest Status | Latest Score | Animation | Image/Diagram |
|------------|---------------|--------|--------|---------------|--------------|-----------|---------------|
| 2025-03 | ARP Core ODE `dG/dt = alpha|I| - muG` | ARP | 2025 corpus / ARP repo | active | 74 | planned | planned |
| 2025-03 | ARP Equilibrium `G_eq = alpha/mu * |I_eq|` | ARP | discovery-matrix | active | 76 | planned | planned |
| 2025-03 | AIN Coupled Dynamics (G,C,L) | AIN | discovery-matrix | pending formalization | 67 | planned | planned |
| 2025-04 | ARP Redshift Law (candidate) | Physics/ARP | discovery-matrix #1 | in review | 78 | planned | planned |
| 2025-05 | Dynamic Constants Coupling | Constants | discovery-matrix #3 | in review | 71 | planned | planned |
| 2025-05 | Curve-Memory 137 Threshold | Curve Memory | discovery-matrix #4 | validation pending | 65 | planned | planned |
| 2025-06 | ARP Lyapunov Stability Form | ARP/Math | discovery-matrix #2 | in review | 75 | planned | planned |
| 2025-08 | ARP Shield Mechanic | ARP/Physics | discovery-matrix #5 | concept | 62 | planned | planned |
| 2026-02 | Temperature-dependent conductance law | ARP/Physics | daily run 2026-02-19 | candidate | 68 | planned | planned |

## Artifact Linking Rules

1. Every top equation should link to at least one animation or storyboard plan.
2. Every top equation should link to at least one still image/diagram concept.
3. Use relative paths where possible, for example:
   - `D:\Manimppyythn\media\videos\...` for rendered animations
   - `D:\Manimppyythn\assets\...` or `D:\Manimppyythn\out\...` for images
4. If no artifact exists yet, mark as `planned` and keep equation eligible.
5. Artifact columns are links/status fields only; they are not separately ranked.

## Update Rules

1. Add every daily candidate to `submissions/YYYY-MM-DD.md`.
2. Promote best 1-3 candidates into `Newest Top-Ranked Equations`.
3. Recompute and sort `Current Top Equations (All-Time)` by score.
4. Keep `All Equations Since 2025 (Registry)` updated when any equation is first seen or status changes.
5. Keep one-sentence descriptions focused on what each equation does.
6. Do not promote entries without both unit and theory verdicts.
