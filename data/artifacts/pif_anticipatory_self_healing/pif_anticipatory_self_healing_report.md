# History-Resolved pi_f Anticipatory Self-Healing Bundle Report

Generated: 2026-04-13T01:35:25.682183+00:00

## Headline findings
- Maze-mode recovery ratio improves by +0.010319 with pi_f enabled.
- Maze-mode tail mismatch falls by 0.029743, a 88.30% relative reduction.
- Classic-mode final conductance ratio rises by +0.036845 with pi_f enabled.
- Classic-mode tail mismatch increases by +0.004914, so the current evidence is stronger in maze mode than in classic mode.
- The committed 10-seed bundle is numerically deterministic across listed seeds (max seed std = 0.000e+00).

## Validation
- Summary rows match grouped benchmark results: True
- Max absolute summary difference: 1.110e-16
- Max seed standard deviation in committed bundle: 0.000e+00

## Limits
- The graph-mode benchmark harness is preserved as a source snapshot, but TopEquations does not include the imported hafc_sim or hafc_sim_pif_active modules needed to rerun it in-place.
- Current evidence is graph-mode only; lattice or EGATL ablations with the same pi_f channel are still missing.
- A direct precursor lead-time comparison against Bott or Chern observables is not yet part of this bundle.

## Generated files
- data/artifacts/pif_anticipatory_self_healing/pif_anticipatory_self_healing_dashboard.png
- data/artifacts/pif_anticipatory_self_healing/pif_anticipatory_self_healing_preview.gif
- data/artifacts/pif_anticipatory_self_healing/pif_anticipatory_self_healing_metrics.json
