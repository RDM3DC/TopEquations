# AGENTS.md (TopEquations)

This repository is the canonical storage for equation rankings and submissions.

## Daily Equation Workflow
1. Pick a source equation from `C:\Users\RDM3D\.openclaw\workspace\memory\discovery-matrix.md`.
2. Derive at least one new equation/transformation.
3. Score and validate (`units`, `theory`) and store structured results in `data/equations.json`.
4. Write daily entry to `submissions/YYYY-MM-DD.md`.
5. Regenerate `leaderboard.md` by running:
   - `python tools/generate_leaderboard.py`
6. Ensure leaderboard sections include:
   - Current Top Equations (All-Time)
   - Newest Top-Ranked Equations (This Month)
   - All Equations Since 2025 (Registry)
7. Include animation/image links or `planned` status with each ranked equation.
8. Do not use separate animation/image ranking columns.

## OpenClaw Reliable Workflow (Discord/Slack Intake)

Use this flow to avoid no-op responses:

1. Intake
   - Parse structured submission fields from chat (name, equation, description, assumptions, source, submitter).
   - Run `python tools/submit_equation.py ...` and return `submissionId`.
2. Scoring
   - Run `python tools/score_submission.py --submission-id <id>`.
   - Status becomes `ready` (>= threshold) or `needs-review`.
3. Promotion
   - Run `python tools/promote_submission.py --submission-id <id> --from-review`.
4. Site refresh
   - Run `python tools/generate_leaderboard.py` and `python tools/build_site.py`.
5. Chain provenance
   - Run `python tools/export_equation_certificates.py`.
   - Run `python tools/register_equation_certificates.py --node-url <url> --signer-file <path> --mine`.

One-command orchestrator:
- `python tools/openclaw_submission_pipeline.py --submission-id <id> --score --promote --publish-chain --node-url http://127.0.0.1:5000 --signer-file D:/coins2/Adaptive-Curvature-Coin/wallet.json`
