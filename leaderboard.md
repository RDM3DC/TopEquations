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
| ------ | --------------- | -------- | ------- | ------- | -------- | ----------- | --------------- | ------------- |
| 1 | ARP Redshift Law (candidate) | discovery-matrix #1 | 78 | WARN | PASS-WITH-ASSUMPTIONS | planned | planned | Conductance-decay framing for cosmological redshift with explicit damping terms. |
| 2 | ARP Lyapunov Stability Form | discovery-matrix #2 | 75 | OK | PASS-WITH-ASSUMPTIONS | planned | planned | Candidate stability proof template for adaptive conductance dynamics. |
| 3 | Temperature-dependent conductance law | daily run 2026-02-19 | 68 | OK | PASS | planned | planned | Extends ARP equilibrium with an exponential temperature factor for material sensitivity. |

## Newest Top-Ranked Equations (This Month)

| Date | Equation Name | Score | Units | Theory | Animation | Image/Diagram | Short Description |
| ------ | --------------- | ------- | ------- | -------- | ----------- | --------------- | ------------------- |
| 2026-02-19 | ARP Redshift Law (candidate) | 78 | WARN | PASS-WITH-ASSUMPTIONS | planned | planned | Conductance-decay framing for cosmological redshift with explicit damping terms. |
| 2026-02-19 | ARP Lyapunov Stability Form | 75 | OK | PASS-WITH-ASSUMPTIONS | planned | planned | Candidate stability proof template for adaptive conductance dynamics. |
| 2026-02-19 | Temperature-dependent conductance law | 68 | OK | PASS | planned | planned | Extends ARP equilibrium with an exponential temperature factor for material sensitivity. |

## All Equations Since 2025 (Registry)

| First Seen | Equation Name | Source | Latest Status | Latest Score | Animation | Image/Diagram |
| ------------ | --------------- | -------- | --------------- | -------------- | ----------- | --------------- |
| 2025-04 | ARP Redshift Law (candidate) | discovery-matrix #1 | PASS-WITH-ASSUMPTIONS | 78 | planned | planned |
| 2025-06 | ARP Lyapunov Stability Form | discovery-matrix #2 | PASS-WITH-ASSUMPTIONS | 75 | planned | planned |
| 2026-02 | Temperature-dependent conductance law | daily run 2026-02-19 | PASS | 68 | planned | planned |

## Update Rules

1. Add every daily candidate to `submissions/YYYY-MM-DD.md`.
2. Keep `data/equations.json` as source of truth.
3. Regenerate this file with `python tools/generate_leaderboard.py`.
4. Keep animation/image columns as links or `planned` status only.
