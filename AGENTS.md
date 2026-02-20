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
