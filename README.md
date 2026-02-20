# TopEquations

Canonical repository for tracking equation discoveries, derivations, rankings, and linked visuals.

## Core files
- `leaderboard.md` — primary ranked board (all-time + newest)
- `data/equations.json` — structured equation records
- `submissions/` — daily run logs and candidate notes
- `tools/generate_leaderboard.py` — rebuilds `leaderboard.md` from `data/equations.json`

## Ranking dimensions
- Equation quality: novelty, tractability, plausibility, validation verdicts
- Artifact completeness: animation/image link attached or planned
- Composite score for leaderboard ordering

## Generate Leaderboard
```powershell
python tools\generate_leaderboard.py
```

## Source workflows
This repo is updated by the OpenClaw daily equation pipeline.
- Derivation: `equations` agent
- Unit checks: `units` agent
- Theory checks: `theory` agent
- Visual production: `animator` and `imager` agents

## Intended use
Use this repository as the main place to save both historical and new equations,
plus ranked animation/image artifacts tied to each equation entry.
