# Falsifiers for the π_f anticipatory self-healing claim

The anticipatory claim should be treated as failed if one or more of the following happen consistently:

1. **No precursor separation**
   The π_f loop-mismatch signal does not separate damaged and undamaged trajectories before later global observables diverge.

2. **No ablation benefit**
   Runs with `xi > 0` do not improve any recovery metric relative to the matched `xi = 0` baseline.

3. **Pure overfitting / no transfer**
   Gains disappear when the damage pattern, seed, or graph topology changes.

4. **Suppression dominates everything**
   The law only appears to help because `lambda_s` is tuned aggressively, while π_f itself contributes no independent value.

5. **No stable limit recovery**
   The parameter limits `xi = 0`, `chi = 0`, and `lambda_s = 0` fail to recover the advertised parent behaviors.

6. **Artifacts not reproducible**
   Independent reruns from the provided script do not reproduce the reported summary tables and plots.
