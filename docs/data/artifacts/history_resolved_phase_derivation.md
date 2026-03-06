# History-Resolved Phase Derivation Note

This note closes the substep-to-full-law bridge for the promoted submission.

## Step 1. Raw edge phase from the network solve

For edge $e=(i,j)$, the nodal solve produces complex current

$$
I_e = G_e (\phi_i - \phi_j), \qquad \theta_{\mathrm{raw},e} = \arg(I_e).
$$

The principal branch alone forgets whether the edge reached the same raw angle by no winding, one extra winding, or one reversed winding.

## Step 2. Branch-resolved state update

The promoted equation advances the resolved phase by the nearest principal increment, clipped by the adaptive ruler:

$$
\theta_{R,e}^{+} = \theta_{R,e} + \operatorname{clip}\!\left(\operatorname{wrap}\!\left(\theta_{\mathrm{raw},e}-\theta_{R,e}\right),-\pi_a,+\pi_a\right).
$$

This preserves branch continuity, while the near-zero freeze safeguard blocks spurious jumps when $|I_e| < z_{\min}$.

## Step 3. Winding and parity are explicit state, not inferred after the fact

The resolved phase defines

$$
w_e = \operatorname{round}\!\left(\frac{\theta_{R,e}}{2\pi}\right), \qquad b_e = (-1)^{w_e}.
$$

These variables are not decorative. They summarize the branch sheet reached by the lifted trajectory and distinguish matched-present states that have identical raw phase but different history.

## Step 4. Entropy and ruler closure

Branch-slip events feed the entropy proxy through $\Delta w_e$, and the entropy proxy drives the ruler update:

$$
S^{+} = S + dt\,[T_1(I,G) + T_2(\Delta w) - \gamma(S-S_{\mathrm{eq}})],
$$

$$
\pi_a^{+} = \pi_a + dt\,[\alpha_\pi S - \mu_\pi(\pi_a-\pi_0)]
$$

with clipping to configured bounds. This is the precise route by which winding history alters later admissible phase increments.

## Step 5. Full conductance law consumes the resolved phase directly

The conductance step is

$$
G_e^{+} = G_e + dt\Big[\alpha_G(S)|I_e|e^{i\theta_{R,e}} - \mu_G(S)G_e - \lambda_s G_e \sin^2\!\left(\frac{\theta_{R,e}}{2\pi_a}\right)\Big].
$$

Substituting the Step 2 update into this law shows the promoted equation is the branch-honest state substep that determines both the reinforcement phase and the suppression gate on the next update.

## Step 6. Recovery limits

- Setting $\theta_R = 0$, $\lambda_s = 0$, and fixed $\alpha_G,\mu_G$ recovers canonical real ARP reinforce/decay.
- Setting principal mode forces $\theta_R^{+} = \theta_{\mathrm{raw}}$, eliminating branch memory by construction.
- Setting $\alpha_\pi = 0$ with $\pi_a(0)=\pi_0$ removes adaptive-ruler dynamics.
- Setting $\lambda_s = 0$ removes phase suppression while preserving the lifted reinforcement phase.

## Operational consequence

The matched-present benchmark family shows why this is a real added state variable. After a warm-up, extra-chirp, and identical resume, two full-model runs can have indistinguishable resumed raw phase but still retain $\Delta\theta_R \approx 2\pi$, different winding/parity, and a nonzero suppression-gap on the next update. The principal baseline collapses those gaps to numerical zero.