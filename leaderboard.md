# Equation Leaderboard
_Last updated: 2026-02-19_

This is the canonical ranking board for existing and newly derived equations.

Scoring model (0-120):
- Novelty (0-30)
- Tractability (0-20)
- Physical plausibility (0-20)
- Validation bonus (0-20):
  - units `OK` (+10)
  - theory `PASS` (+10)
- Visual bonus (0-50):
  - animation rank (0-25)
  - image/diagram rank (0-25)

## Current Top Equations (All-Time)

| Rank | Equation Name | Source | Score | Units | Theory | Animation Rank | Image Rank | Description |
|------|---------------|--------|-------|-------|--------|----------------|------------|-------------|
| 1 | ARP Redshift Law (candidate) | discovery-matrix #1 | 78 | WARN | PASS-WITH-ASSUMPTIONS | 8 | 6 | Conductance-decay framing for cosmological redshift with explicit damping terms. |
| 2 | ARP Lyapunov Stability Form | discovery-matrix #2 | 75 | OK | PASS-WITH-ASSUMPTIONS | 7 | 6 | Candidate stability proof template for adaptive conductance dynamics. |
| 3 | Dynamic Constants Coupling | discovery-matrix #3 | 71 | WARN | PASS-WITH-ASSUMPTIONS | 7 | 5 | Proposed coupling of adaptive pi/e/phi/c into one shared field update law. |
| 4 | Curve-Memory 137 Threshold | discovery-matrix #4 | 65 | OK | FAIL | 5 | 6 | Alpha_fs threshold proposal for state transitions; needs formal derivation. |
| 5 | ARP Shield Mechanic | discovery-matrix #5 | 62 | WARN | FAIL | 5 | 4 | Early protective-dynamics equation family for perturbation suppression. |

## Newest Top-Ranked Equations

| Date | Equation Name | Score | Units | Theory | Animation | Image | Short Description |
|------|---------------|-------|-------|--------|-----------|-------|-------------------|
| 2026-02-19 | ARP Redshift Law (candidate) | 78 | WARN | PASS-WITH-ASSUMPTIONS | planned | planned | Conductance-decay to redshift mapping with explicit assumptions. |
| 2026-02-19 | ARP Lyapunov Stability Form | 75 | OK | PASS-WITH-ASSUMPTIONS | planned | planned | Stability form intended for direct repo integration. |
| 2026-02-19 | Dynamic Constants Coupling | 71 | WARN | PASS-WITH-ASSUMPTIONS | planned | planned | Unified adaptive constants proposal from pi_a + ARP + AIN. |

## Artifact Linking Rules

1. Every top equation should link to at least one animation or storyboard plan.
2. Every top equation should link to at least one still image/diagram concept.
3. Use relative paths where possible, for example:
   - `D:\Manimppyythn\media\videos\...` for rendered animations
   - `D:\Manimppyythn\assets\...` or `D:\Manimppyythn\out\...` for images
4. If no artifact exists yet, mark as `planned` and keep equation eligible.

## Update Rules

1. Add every daily candidate to `submissions/YYYY-MM-DD.md`.
2. Promote best 1-3 candidates into `Newest Top-Ranked Equations`.
3. Recompute and sort `Current Top Equations (All-Time)` by score.
4. Keep one-sentence descriptions focused on what each equation does.
5. Do not promote entries without both unit and theory verdicts.
