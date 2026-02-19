# TopEquations

Canonical repository for tracking equation discoveries, derivations, rankings, and linked visuals.

## Core files
- `leaderboard.md` — primary ranked board (all-time + newest)
- `data/equations.json` — structured equation records
- `submissions/` — daily run logs and candidate notes

## Ranking dimensions
- Equation quality: novelty, tractability, plausibility, validation verdicts
- Visual impact: animation quality and image/diagram quality
- Composite score for leaderboard ordering

## Source workflows
This repo is updated by the OpenClaw daily equation pipeline.
- Derivation: `equations` agent
- Unit checks: `units` agent
- Theory checks: `theory` agent
- Visual production: `animator` and `imager` agents

## Intended use
Use this repository as the main place to save both historical and new equations,
plus ranked animation/image artifacts tied to each equation entry.
