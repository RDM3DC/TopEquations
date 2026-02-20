# Harvested Equation Registry (raw)

This folder contains a **machine-harvested** registry of equations extracted from the RDM3DC local repos.

- Source scan root: `C:\Users\RDM3D\clawdad42\` (all repos)
- Primary output: `equation_harvest.json`
  - `stats`: counts + breakdown
  - `entries[]`: deduped equations (normalized + sha1)

Notes:
- This is **not** the curated leaderboard. The leaderboard uses `data/equations.json`.
- Many harvested items are code assignments or LaTeX snippets; treat as candidates until curated.
- Next planned improvement: harvest from the 2025 conversation corpus with plain-text equation heuristics.
