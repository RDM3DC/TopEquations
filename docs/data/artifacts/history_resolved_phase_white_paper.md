# History-Resolved Phase as a State Variable in Entropy-Gated Adaptive Complex Networks

## Abstract

This paper summarizes the current state of the History-Resolved Phase with Adaptive Ruler program. The central claim is modest but concrete: branch-resolved phase is not merely a smoother numerical unwrap. When promoted to explicit state, the resolved phase $\theta_R$ and its induced winding/parity variables $(w,b)$ retain operationally relevant history that the principal branch discards. In the current adaptive-complex-network implementation, that retained history changes the next conductance update through both the lifted reinforcement phase and the phase-suppression gate. The evidence presently supports this as a rigorous, executable, lineage-preserving extension of the ARP plus Adaptive-$\pi$ plus Phase-Lift stack. The evidence does not yet justify calling it a wholly new top-level dynamical paradigm. What is justified is stronger than a cosmetic refinement: the mechanism produces matched-present state separation, operational memory gaps, and a reproducible onset threshold in a benchmarked protocol family.

## 1. Scope and Position

This white paper records what is currently established.

- The work builds directly on White Paper 01 (ARP/AIN) for reinforce/decay conductance dynamics.
- It builds on White Paper 02 (Adaptive-$\pi$) for the entropy-driven adaptive ruler.
- It builds on White Paper 04 (Phase-Lift / PR-Root) for branch-resolved continuity and winding/parity bookkeeping.
- It uses the phase-lock versus slip backbone from the Phase (Adler/RSJ) dynamics lineage.
- It is implemented and benchmarked in the local `hrphasenet` package and associated benchmark harness.

The goal is not to replace the parent framework. The goal is to close a specific defect: principal-branch phase loses branch history even when that history remains dynamically relevant to the next update.

## 2. Problem Statement

For an edge $e=(i,j)$ with complex conductance $G_e$ and nodal potentials $(\phi_i,\phi_j)$, the instantaneous complex current is

$$
I_e = G_e(\phi_i - \phi_j), \qquad \theta_{\mathrm{raw},e} = \arg(I_e).
$$

The principal branch stores only $\theta_{\mathrm{raw},e} \in (-\pi,\pi]$. Two trajectories that arrive at the same present raw phase can therefore appear identical even when one has completed an additional winding and the other has not. If the conductance update depends on resolved phase history, then the principal representation is not only lossy but dynamically misleading.

The specific scientific question is therefore:

Can branch history be elevated to explicit state in a way that is traceable, bounded, executable, and operationally distinguishable from principal-branch evolution?

## 3. Core State Law

The promoted history-resolved phase update is

$$
\theta_R^{+}=\theta_R+\operatorname{clip}\!\left(\operatorname{wrap}\!\left(\theta_{\mathrm{raw}}-\theta_R\right),-\pi_a,+\pi_a\right).
$$

Interpretation:

- `wrap` chooses the nearest principal increment relative to the previous resolved phase.
- `clip` limits each admissible increment to the adaptive ruler interval $[-\pi_a,+\pi_a]$.
- The near-zero safeguard freezes the update whenever $|I| < z_{\min}$ so undefined or unstable raw angles do not create spurious branch jumps.

This is the smallest state law in the current stack that preserves branch continuity while respecting the adaptive ruler.

## 4. Explicit Winding and Parity State

The resolved phase defines

$$
w = \operatorname{round}\!\left(\frac{\theta_R}{2\pi}\right), \qquad b = (-1)^w.
$$

This matters because $(w,b)$ are not post hoc labels. They summarize which branch sheet the trajectory currently occupies. The current benchmark program shows that two runs can share the same resumed raw phase while differing in $\theta_R$, $w$, and $b$.

That is the first nontrivial result: branch sheet occupancy can remain operationally distinct after present observables re-align.

## 5. Closure with Entropy and Adaptive Ruler Dynamics

The resolved-phase update sits inside the existing entropy-gated adaptive-complex-network stack.

The entropy proxy evolves schematically as

$$
S^{+} = S + dt\,[T_1(I,G) + T_2(\Delta w) - \gamma(S-S_{\mathrm{eq}})],
$$

and the adaptive ruler evolves as

$$
\pi_a^{+} = \pi_a + dt\,[\alpha_\pi S - \mu_\pi(\pi_a-\pi_0)],
$$

with clipping to configured bounds.

The key closure is that branch-slip information enters the entropy pathway through $\Delta w$, and the entropy state in turn regulates admissible future phase motion through $\pi_a$. This creates a feedback loop between history, admissible motion, and subsequent conductance evolution.

## 6. Full Conductance Update

The full conductance step is

$$
G_e^{+} = G_e + dt\Big[\alpha_G(S)|I_e|e^{i\theta_{R,e}} - \mu_G(S)G_e - \lambda_s G_e \sin^2\!\left(\frac{\theta_{R,e}}{2\pi_a}\right)\Big].
$$

This gives two direct channels by which branch-resolved state matters:

1. The reinforcement term is phase-lifted through $e^{i\theta_R}$.
2. The suppression term depends explicitly on $\theta_R/(2\pi_a)$.

The core operational claim of the present work is therefore precise:

> $\theta_R$ is a state variable because changing it, while holding resumed raw phase effectively fixed, changes the next update.

## 7. Recovery Limits and Backward Compatibility

The construction is intentionally lineage-preserving.

- Setting $\theta_R = 0$, $\lambda_s = 0$, and fixed $\alpha_G,\mu_G$ recovers canonical real ARP reinforce/decay.
- Setting principal mode forces $\theta_R^{+} = \theta_{\mathrm{raw}}$, eliminating branch memory by construction.
- Setting $\alpha_\pi = 0$ with $\pi_a(0)=\pi_0$ removes adaptive-ruler dynamics.
- Setting $\lambda_s = 0$ removes phase suppression while preserving lifted reinforcement.

These limits are important because they show the present mechanism extends rather than overwrites the existing framework.

## 8. What Is Empirically Established So Far

All current evidence comes from the local benchmark harness `tools/benchmark_history_resolved_phase.py`, the local `hrphasenet` implementation, and the upstream `pytest` suite.

### 8.1 Test-Suite Replication

The local environment reproduces the upstream package test suite with

- `118 passed in 1.50s`

This does not prove the scientific claim, but it verifies that the implementation is internally stable enough to support targeted experiments.

### 8.2 Monodromy Sanity Check

For one full winding on $z(t)=e^{it}$ over 100 steps, the resolved phase returns

- $\theta_R \approx 2\pi$
- $w=1$
- $b=-1$

This confirms that the lifted state keeps track of a full winding rather than collapsing back to principal angle zero.

### 8.3 Near-Zero Freeze Safeguard

The update freezes exactly at near-zero magnitude and remains active above the threshold.

This matters because otherwise branch-memory claims could be contaminated by spurious jumps generated at numerically ill-posed angles.

### 8.4 Boundedness

Current boundedness checks report

- $\max |G| = 0.838200923759266$ after 200 driven steps
- $\pi_a = 1.6179656505832332$ after 100 periodic steps

under the tested parameter set.

This does not prove global boundedness, but it does support tractable finite-time operation in the tested regime.

### 8.5 Matched-Present State Separation

The matched-present protocol is the central result so far.

Protocol:

1. Warm up two identical networks for 30 steps under the same constant drive.
2. Apply an extra chirp to one branch while the other receives the matched-present control protocol.
3. Resume identical driving for both branches.

Result:

- Principal raw-phase gap remains approximately $7.06\times 10^{-14}$.
- Principal resolved-phase gap remains approximately $7.11\times 10^{-14}$.
- Full raw-phase gap remains approximately $7.27\times 10^{-14}$.
- Full resolved-phase gap remains $6.283185307179659 \approx 2\pi$.
- Principal winding/parity remain identical.
- Full winding/parity differ.

Interpretation:

The present raw phase can be effectively matched while the history-resolved state remains separated by one full winding.

### 8.6 Operational Memory Gap

The stronger operational question is whether the state separation changes the next update.

Measured values:

- Principal current-magnitude gap: $1.300626273348371\times 10^{-13}$
- Full current-magnitude gap: $1.7014167852380524\times 10^{-13}$
- Principal suppression-gap: $5.881032315722067\times 10^{-29}$
- Full suppression-gap: $0.10359844158580957$

Interpretation:

The current magnitudes are matched to numerical noise in both runs, yet the full model produces a nontrivial suppression difference while the principal model collapses to zero. This is the clearest current evidence that branch history is not merely descriptive but operational.

### 8.7 Threshold Sweep

Sweeping the chirp endpoint over $\omega_{\mathrm{end}} \in \{12,16,20\}$ yields:

- principal $\Delta\theta_R \sim 10^{-13}$ across the sweep
- full $\Delta\theta_R \approx 2\pi$ across the sweep
- full suppression gaps between $0.10344091777618011$ and $0.10585806677309485$

This shows the effect is not confined to a single cherry-picked chirp endpoint.

### 8.8 Onset Phase Diagram

The strongest regime-level result so far is the onset map over

- $\pi_0 \in \{\pi/4,\pi/3,\pi/2,2\pi/3,3\pi/4\}$
- $\omega_{\mathrm{end}} \in \{8,10,12,14,16,18,20\}$

Observed pattern:

- For every tested $\pi_0$, the principal model remains collapsed across the entire sweep.
- For every tested $\pi_0$, the full model remains off below threshold at $\omega_{\mathrm{end}}=8,10$.
- For every tested $\pi_0$, the full model turns on at the same threshold $\omega_{\mathrm{end}}=12$.
- Above threshold, the full model closes the parity-winding loop with $\Delta\theta_R = 2\pi$ and suppression gaps in $[3.348226\times 10^{-3}, 1.092192\times 10^{-1}]$.

Interpretation:

The current data supports a reproducible onset boundary for branch-memory activation in the tested protocol family.

## 9. What We Can Claim Safely

Based on the present derivation and benchmarks, the following claims are supported.

### Supported

- $\theta_R$ is a branch-resolved state variable in the tested adaptive-network model.
- Winding and parity are operationally relevant, not merely descriptive labels.
- The full model can preserve one-full-winding separation after resumed raw phase re-aligns.
- That separation can change the next suppression term while principal mode collapses to zero.
- The benchmarked protocol family shows a reproducible onset threshold at $\omega_{\mathrm{end}}=12$ across the tested $\pi_0$ values.
- The implementation is executable, bounded in tested finite-time runs, and regression-tested.

### Not Yet Supported

- A proof of global boundedness or asymptotic stability for all admissible parameters.
- A claim that the mechanism is a wholly new top-level dynamical paradigm.
- A claim that the onset threshold is universal beyond the tested protocol family and parameter window.
- A first-principles derivation from deeper microscopic physics beyond the current network formalism.

## 10. Falsifiability

The current program is falsifiable in straightforward ways.

It would be materially weakened or falsified if any of the following fail under rerun:

- The monodromy benchmark fails to preserve one-full-winding bookkeeping.
- The near-zero freeze benchmark fails, allowing spurious branch jumps.
- The matched-present state-separation benchmark no longer preserves $\Delta\theta_R \approx 2\pi$ in full mode while principal mode collapses.
- The operational memory-gap benchmark loses the nonzero suppression gap in full mode under matched-present current magnitudes.
- The onset map no longer reproduces the common threshold at $\omega_{\mathrm{end}}=12$ across the tested $\pi_0$ set.
- Ablation limits fail to recover principal or ARP-style behavior.

## 11. Implementation Summary

The current reference implementation lives in the local `hrphasenet` package, and the score-facing benchmark harness is `tools/benchmark_history_resolved_phase.py`.

Published supporting artifacts currently include:

- `data/artifacts/history_resolved_phase_derivation.md`
- `data/artifacts/history_resolved_phase_benchmark_report.md`
- `data/artifacts/history_resolved_phase_benchmark_report.json`
- `data/artifacts/parity_lock_deformation_table.md`
- the animation and poster artifacts linked from the promoted submission record

## 12. Current Interpretation

The best current interpretation is this:

History-resolved phase provides a disciplined way to carry branch-sheet information through an entropy-gated adaptive network so that branch history can influence later dynamics without breaking the parent framework's recovery limits. The present evidence shows that this matters operationally in at least one well-defined protocol family. The mechanism is therefore scientifically stronger than a cosmetic unwrap rule. At the same time, the evidence currently supports it as a rigorous extension of the existing ARP plus Adaptive-$\pi$ plus Phase-Lift stack, not yet as an independent foundational theory.

That is the honest state of the work so far.

## 13. Next Scientific Steps

If the goal is to strengthen the scientific case beyond the current level, the most valuable next steps are:

1. Build a broader phase diagram showing whether the onset threshold survives changes in drive family, graph topology, and entropy-gate parameters.
2. Derive analytical conditions for when matched-present trajectories can remain raw-phase aligned while preserving distinct winding/parity classes.
3. Establish sharper boundedness or Lyapunov-style results for the coupled $G$-$S$-$\pi_a$-$\theta_R$ system.
4. Demonstrate a qualitatively distinct attractor or transition class that cannot be reproduced by the principal or ARP-limit ablations.
5. Connect the current network-level branch-closure law to a more first-principles microscopic origin if a deeper foundational claim is desired.

## References and Lineage

- White Paper 01: ARP/AIN reinforce-decay conductance law
- White Paper 02: Adaptive-$\pi$ ruler dynamics
- White Paper 04: Phase-Lift / PR-Root branch-resolved continuity
- Phase (Adler/RSJ) Dynamics entry in the current leaderboard lineage
- Local `hrphasenet` implementation and benchmark harness