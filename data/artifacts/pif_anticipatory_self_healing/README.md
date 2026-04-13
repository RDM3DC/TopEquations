# π_f 98+ package

This folder packages the work needed to strengthen the **History-Resolved π_f Anticipatory Self-Healing Conductance Law** for a higher-trust TopEquations submission.

## Included
- `benchmark_pif_98plus.py` — executable graph-mode benchmark / ablation script
- `benchmark_results.csv` — seed-by-seed results
- `benchmark_summary.csv` — mode-level averages
- `benchmark_summary.md` — quick written summary
- `benchmark_summary.png` — bar-chart summary
- `classic_trace_seed0.png` — representative classic trace
- `maze_trace_seed0.png` — representative maze trace
- `derivation_bridge.md` — step-by-step parent-law bridge
- `falsifiers.md` — explicit falsification criteria
- `top_equations_evidence_block.md` — stronger evidence language
- `pif_anticipatory_self_healing_dashboard.png` — repo-native dashboard generated from the committed CSV bundle
- `pif_anticipatory_self_healing_preview.gif` — preview animation assembled from the committed figures
- `pif_anticipatory_self_healing_metrics.json` — computed mode deltas plus summary-consistency checks
- `pif_anticipatory_self_healing_report.md` — short report for score-facing claims inside TopEquations

## What is already done
- executable benchmark with `π_f on` vs `π_f off`
- saved CSVs and plots
- derivation bridge
- falsifier list
- stronger evidence block

## What is still missing for the strongest 98+ push
- lattice / EGATL benchmark with the same π_f channel
- `lambda_s = 0` ablation in the full lattice solver
- a direct precursor lead-time benchmark against Bott / Chern
- a public repository that wraps these files into one-click replication

## TopEquations staging note
- The original `benchmark_pif_98plus.py` harness is preserved here as a source snapshot from the upstream package.
- TopEquations does **not** include the imported `hafc_sim` and `hafc_sim_pif_active` modules needed to rerun that harness in-place, so this repo copy should not be treated as a one-command rerun from this directory.
- The repo-native reproduction path inside TopEquations is the validator / renderer below, which checks the committed CSV bundle and regenerates the local dashboard, preview GIF, metrics JSON, and report.

## Run
```bash
python tools/generate_pif_anticipatory_self_healing_artifacts.py
```

## Honest read
This package is enough to make the submission materially stronger. The graph-mode results support the claim that active π_f reduces post-damage loop-mismatch residual and modestly improves maze-mode recovery. The full top-tier claim still needs the lattice-side ablations.
