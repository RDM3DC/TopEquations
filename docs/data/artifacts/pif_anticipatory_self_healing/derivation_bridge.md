# Derivation bridge: from parent laws to the π_f anticipatory self-healing law

## Goal
Build a single edge-update law that combines:
1. **history-resolved phase reinforcement**,
2. **adaptive-ruler slip suppression**,
3. **local self-healing / topological repair**, and
4. **flat-adaptive π_f loop-health anticipation**.

## Parent law A: history-resolved phase conductance update
A minimal parent form is an adaptive conductance growth law with history-resolved phase:

- growth term proportional to current magnitude,
- complex phase factor using lifted phase `Theta_e`,
- entropy-dependent gain and decay.

Skeleton:

`dot g_e = alpha_G(S) |J_e| exp(i Theta_e) - mu_G(S) g_e`

This contributes the **history-resolved reinforcement backbone**.

## Parent law B: adaptive-ruler slip suppression
To keep reinforcement controlled under phase slip, add a bounded suppression factor using the adaptive ruler `pi_a`:

`- lambda_s g_e sin^2(Theta_e / (2 pi_a))`

This contributes the **slip / dephasing penalty**.

## Parent law C: local self-healing term
To permit topology-aware recovery, add a local healing factor `C_e`:

`+ chi C_e g_e`

This contributes the **repair / rerouting channel**.

## New ingredient: flat-adaptive π_f precursor gate
Introduce a local loop-health precursor based on π_f loop signatures.
For each loop `ell`, define a loop signature `Sigma_ell^(f)` and compare it to a reference `Sigma_ref,ell^(f)`.
A normalized mismatch is then accumulated onto each edge through the loops containing that edge.

Prototype definition:

`H_e^(f) = sum_{ell contains e} w_{e ell} tanh((Sigma_ell^(f) - Sigma_ref,ell^(f)) / (sigma_ell + eps))`

Interpretation:
- `H_e^(f) > 0` means the edge sits inside a loop region whose π_f behavior departs from healthy reference structure.
- This is an **anticipatory local health signal** rather than a passive readout.

## Combine the pieces
Use `H_e^(f)` to modulate the reinforcement term multiplicatively:

`dot g_e = alpha_G(S) [1 + xi H_e^(f)] |J_e| exp(i Theta_e) - mu_G(S) g_e - lambda_s g_e sin^2(Theta_e / (2 pi_a)) + chi C_e g_e`

## Why multiplicative gating is the cleanest choice
Putting `[1 + xi H_e^(f)]` on the reinforcement term has four advantages:
1. it preserves the parent law when `xi = 0`,
2. it keeps π_f local and edge-specific,
3. it lets π_f bias both strengthening and weakening, and
4. it separates **anticipation** from **repair** (`C_e`).

## Recovery limits / lineage checks
- `xi = 0` recovers the self-healing history-resolved law without π_f anticipation.
- `chi = 0` isolates a pure π_f anticipatory routing law.
- `lambda_s = 0` removes slip suppression and gives an ablation target.
- `xi = chi = 0` recovers the ungated history-resolved conductance update.

## Falsifiable claim
The combined law predicts that **π_f loop-signature mismatch can separate damaged from healthy trajectories earlier than downstream global recovery observables**, while also improving post-damage routing / healing in at least some protocols.
