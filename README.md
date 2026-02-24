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

## Submission Workflow
Submit a candidate:
```powershell
python tools\submit_equation.py --name "Example" --equation "\\frac{dG}{dt}=..." --description "..." --source "discord" --submitter "ryan"
```

Score a pending submission:
```powershell
python tools\score_submission.py --submission-id sub-YYYY-MM-DD-example
```

Promote into ranked board (from stored review):
```powershell
python tools\promote_submission.py --submission-id sub-YYYY-MM-DD-example --from-review
```

All-in-one pipeline (score + promote + certificates):
```powershell
python tools\openclaw_submission_pipeline.py --submission-id sub-YYYY-MM-DD-example --score --promote --publish-chain --node-url http://127.0.0.1:5000 --signer-file D:/coins2/Adaptive-Curvature-Coin/wallet.json
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
