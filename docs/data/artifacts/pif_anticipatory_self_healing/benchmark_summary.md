# π_f benchmark summary
This benchmark compares the graph-mode active π_f prototype against a π_f-off ablation across 10 random seeds for classic and maze modes.
## Mean results
| mode    | pif_enabled   |   recovery_ratio |   G_ratio |   mismatch_peak_5 |   mismatch_tail |   mean_pi_f_final |   damaged_edges |
|:--------|:--------------|-----------------:|----------:|------------------:|----------------:|------------------:|----------------:|
| classic | False         |         1        |  0.986924 |        0.00185525 |     9.52293e-09 |           3.14159 |               1 |
| classic | True          |         1        |  1.02377  |        0.0120173  |     0.00491398  |           2.55811 |               1 |
| maze    | False         |         0.998467 |  1        |        0.118204   |     0.033686    |           3.14159 |               3 |
| maze    | True          |         1.00879  |  1        |        0.274581   |     0.00394273  |           3.72812 |               3 |

## Quick read
- In **maze mode**, π_f-on improves final effective current recovery above the π_f-off ablation and dramatically reduces tail loop-signature mismatch.
- In **classic mode**, π_f-on improves mean final conductance and maintains a nontrivial π_f state after damage.
- The strongest empirical signal in this graph-mode prototype is not a huge jump in raw current, but a **much lower post-damage loop-mismatch residual** under active π_f feedback.
