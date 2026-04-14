# Derived Equation: pi_f Loop-Health Balance Law

## Purpose

This note derives a new time-evolution law for the existing loop health observable

$$
\Sigma_{\Gamma}^{(\pi_f)}(t)
=
\exp\!\left[\frac{1}{|\Gamma|}\sum_{e\in\Gamma}\ln\!\left(\frac{\pi_{f,e}(t)}{\pi}\right)\right]
\frac{1+\cos\!\left(\Theta_{\Gamma}(t)/\pi_a(t)\right)}{2},
$$

using the HAFC/EGATL source bundle the user referenced.

The current workspace contains a different EGATL variant at
`AdaptiveCAD-Manim/solver/egatl.py`; that copy does not include the `pi_f`
loop-signature helpers. The derivation below is therefore grounded in the
external source bundle that was explicitly provided, and stored here as a
workspace artifact for reuse.

## Source ingredients

### 1. Existing pi_f loop signature

The source bundle already defines

$$
\pi_{f,e}(t)=\pi |g_e(t)|,
\qquad
\Theta_{\Gamma}(t)=\sum_{e\in\Gamma}\sigma_{\Gamma,e}\,\phi_e(t),
\qquad
\phi_e(t)=\arg g_e(t),
$$

and therefore

$$
\Sigma_{\Gamma}^{(\pi_f)}(t)=M_{\Gamma}(t)\,C_{\Gamma}(t),
$$

with

$$
M_{\Gamma}(t)=\exp\!\left[\frac{1}{|\Gamma|}\sum_{e\in\Gamma}\ln |g_e(t)|\right],
\qquad
C_{\Gamma}(t)=\frac{1+\cos\!\left(\Theta_{\Gamma}(t)/\pi_a(t)\right)}{2}.
$$

The magnitude channel is a geometric mean over the loop. The coherence channel
is a bounded holonomy factor on the adaptive ruler.

### 2. Existing EGATL backend dynamics

The referenced `solver/egatl.py` advances the bond state with the Euler step

$$
\dot G_e=\alpha(S) I_{\mathrm{norm},e}-\mu(S)(G_e-g_{\min}),
$$

$$
\dot \phi_e=\lambda_s\sin\!\left(I_{\phi,e}-\phi_e\right),
\qquad I_{\phi,e}=\arg I_e,
$$

$$
\dot \pi_a=\alpha_{\pi}S-\mu_{\pi}(\pi_a-\pi_0).
$$

The same source bundle defines the entropy-gated coefficients by

$$
\alpha(S)=\alpha_0\,\sigma\!\left(\frac{S-S_c}{\Delta S}\right),
\qquad
\mu(S)=\mu_0\left[1-\frac{1}{2}\sigma\!\left(\frac{S-S_c}{\Delta S}\right)\right],
$$

$$
\sigma(x)=\frac{1}{1+e^{-x}}.
$$

This is enough to derive a closed loop-scale balance law.

## Derivation

Let

$$
x_{\Gamma}(t):=\frac{\Theta_{\Gamma}(t)}{\pi_a(t)}.
$$

Then

$$
\ln \Sigma_{\Gamma}^{(\pi_f)}=\ln M_{\Gamma}+\ln C_{\Gamma}.
$$

### 1. Magnitude channel

Since

$$
\ln M_{\Gamma}=\frac{1}{|\Gamma|}\sum_{e\in\Gamma}\ln G_e,
$$

we get

$$
\frac{\dot M_{\Gamma}}{M_{\Gamma}}=\frac{1}{|\Gamma|}\sum_{e\in\Gamma}\frac{\dot G_e}{G_e}.
$$

Substituting the backend update gives

$$
\frac{\dot M_{\Gamma}}{M_{\Gamma}}
=
\frac{1}{|\Gamma|}\sum_{e\in\Gamma}
\frac{\alpha(S) I_{\mathrm{norm},e}-\mu(S)(G_e-g_{\min})}{G_e}.
$$

### 2. Coherence channel

Because

$$
\frac{1+\cos x}{2}=\cos^2\!\left(\frac{x}{2}\right),
$$

we can write

$$
C_{\Gamma}=\cos^2\!\left(\frac{x_{\Gamma}}{2}\right),
$$

so

$$
\frac{\dot C_{\Gamma}}{C_{\Gamma}}=-\tan\!\left(\frac{x_{\Gamma}}{2}\right)\dot x_{\Gamma}.
$$

Now

$$
\dot x_{\Gamma}=\frac{\dot \Theta_{\Gamma}}{\pi_a}-\frac{\Theta_{\Gamma}}{\pi_a^2}\dot \pi_a.
$$

Since

$$
\Theta_{\Gamma}=\sum_{e\in\Gamma}\sigma_{\Gamma,e}\phi_e,
$$

the phase update yields

$$
\dot \Theta_{\Gamma}
=
\lambda_s\sum_{e\in\Gamma}\sigma_{\Gamma,e}\sin\!\left(I_{\phi,e}-\phi_e\right).
$$

Using the ruler law,

$$
\dot \pi_a=\alpha_{\pi}S-\mu_{\pi}(\pi_a-\pi_0),
$$

we obtain

$$
\frac{\dot C_{\Gamma}}{C_{\Gamma}}
=
-\tan\!\left(\frac{\Theta_{\Gamma}}{2\pi_a}\right)
\left[
\frac{\lambda_s}{\pi_a}\sum_{e\in\Gamma}\sigma_{\Gamma,e}\sin\!\left(I_{\phi,e}-\phi_e\right)
-
\frac{\Theta_{\Gamma}}{\pi_a^2}\left(\alpha_{\pi}S-\mu_{\pi}(\pi_a-\pi_0)\right)
\right].
$$

## Derived equation

Combining the magnitude and coherence channels gives the new law:

$$
\boxed{
\frac{\dot \Sigma_{\Gamma}^{(\pi_f)}}{\Sigma_{\Gamma}^{(\pi_f)}}
=
\frac{1}{|\Gamma|}\sum_{e\in\Gamma}
\frac{\alpha(S) I_{\mathrm{norm},e}-\mu(S)(G_e-g_{\min})}{G_e}
-
\tan\!\left(\frac{\Theta_{\Gamma}}{2\pi_a}\right)
\left[
\frac{\lambda_s}{\pi_a}\sum_{e\in\Gamma}\sigma_{\Gamma,e}\sin\!\left(I_{\phi,e}-\phi_e\right)
-
\frac{\Theta_{\Gamma}}{\pi_a^2}\left(\alpha_{\pi}S-\mu_{\pi}(\pi_a-\pi_0)\right)
\right]
}
$$

or, equivalently,

$$
\dot \Sigma_{\Gamma}^{(\pi_f)}=\Sigma_{\Gamma}^{(\pi_f)}\,\mathcal{R}_{\Gamma}(t),
$$

where the boxed right-hand side is the instantaneous loop-health rate
$\mathcal{R}_{\Gamma}(t)$.

## Euler form used by the backend

Because the source backend uses an Euler step, the discrete update is

$$
\Sigma_{\Gamma,k+1}^{(\pi_f)}
=
\Sigma_{\Gamma,k}^{(\pi_f)}\exp\!\left(\Delta t\,\mathcal{R}_{\Gamma,k}\right)+O(\Delta t^2),
$$

so to first order,

$$
\Sigma_{\Gamma,k+1}^{(\pi_f)}\approx
\Sigma_{\Gamma,k}^{(\pi_f)}\left(1+\Delta t\,\mathcal{R}_{\Gamma,k}\right).
$$

## Physical meaning

### Reinforcement-decay balance

$$
\frac{1}{|\Gamma|}\sum_{e\in\Gamma}
\frac{\alpha(S) I_{\mathrm{norm},e}-\mu(S)(G_e-g_{\min})}{G_e}
$$

is the loop-averaged growth rate of the geometric-mean flat-channel magnitude.

### Phase-slip drive

$$
\frac{\lambda_s}{\pi_a}\sum_{e\in\Gamma}\sigma_{\Gamma,e}\sin\!\left(I_{\phi,e}-\phi_e\right)
$$

drives holonomy motion when current phase and bond phase disagree.

### Adaptive-ruler transport

$$
\frac{\Theta_{\Gamma}}{\pi_a^2}\left(\alpha_{\pi}S-\mu_{\pi}(\pi_a-\pi_0)\right)
$$

captures loop-health change caused purely by ruler drift, even if bond magnitudes do
not collapse.

### Precursor amplification

The factor

$$
\tan\!\left(\frac{\Theta_{\Gamma}}{2\pi_a}\right)
$$

diverges near odd half-holonomy crossings. That gives an analytic precursor
mechanism: modest phase mismatch or ruler drift can force a sharp drop in
$\Sigma_{\Gamma}^{(\pi_f)}$ before full topological failure.

This is the key reason the law is interesting. It explains why the observed
`pi_f` signal can collapse early rather than merely tracking damage after the
fact.

## Limiting cases

### Locked loop

If

$$
I_{\phi,e}\approx \phi_e,
\qquad
\Theta_{\Gamma}\approx 2m\pi_a,
$$

then the tangent factor is small and loop health is controlled mainly by the
magnitude balance.

### Near-threshold loop

If

$$
\Theta_{\Gamma}=2m\pi_a+\delta_{\Gamma},
\qquad
|\delta_{\Gamma}|\ll \pi_a,
$$

then

$$
\tan\!\left(\frac{\Theta_{\Gamma}}{2\pi_a}\right)
\approx
\frac{\delta_{\Gamma}}{2\pi_a},
$$

so the first correction to magnitude-driven growth is linear in the holonomy
offset.

### Pure decay window

If $I_{\mathrm{norm},e}=0$ on the loop, the magnitude term is negative and the
signature decays unless coherence is restored or the ruler motion compensates.

## Why this is not a trivial recombination

The workspace lineage already had:

- a static `pi_f` loop signature,
- explicit EGATL bond dynamics,
- explicit entropy gating,
- explicit adaptive-ruler motion,
- and precursor evidence from retention sweeps.

What it did not have was a derived evolution law for the loop signature itself.
This note provides that bridge. The novelty is not a new static product of old
terms; it is the chain-rule dynamics of an existing observable under the
implemented solver laws.

## Suggested candidate name

**pi_f Loop-Health Balance Law**

This keeps the equation compact while preserving its lineage to the existing
`pi_f` observable and the HAFC/EGATL backend.