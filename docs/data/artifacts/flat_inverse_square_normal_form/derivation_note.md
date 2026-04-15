# Flat-Adaptive Inverse-Square Normal Form

## Law Statement

For the power-law flat branch

$$
\pi_f(r)=\pi\lambda_0\left(\frac{r}{r_0}\right)^\beta,
\qquad
w_f(r)=2\pi_f(r)r=2\pi\lambda_0 r_0^{-\beta}r^{\beta+1},
$$

the radial operator is

$$
\Delta_f^{\mathrm{rad}}u
=\frac{1}{w_f}\frac{d}{dr}\left(w_f u_r\right)
=u''+\frac{\beta+1}{r}u'.
$$

Define the half-density transform

$$
u(r)=w_f(r)^{-1/2}\,\psi(r).
$$

Since $w_f(r)\propto r^{\beta+1}$, the constant prefactor is irrelevant for conjugation, so this is the same as

$$
u(r)=c\,r^{-(\beta+1)/2}\psi(r).
$$

Then the exact conjugated operator is

$$
\sqrt{w_f(r)}\,\Delta_f^{\mathrm{rad}}\!\left(w_f(r)^{-1/2}\psi(r)\right)
=\psi''(r)-\frac{\beta^2-1}{4r^2}\psi(r).
$$

Equivalently, the eigenvalue problem becomes

$$
-\psi''(r)+\frac{\beta^2-1}{4r^2}\psi(r)=\kappa^2\psi(r).
$$

## Direct Derivation

Let

$$
m=\frac{\beta+1}{2},
\qquad
u=r^{-m}\psi.
$$

Then

$$
u'=-mr^{-m-1}\psi+r^{-m}\psi',
$$

and because $w_f\propto r^{2m}$,

$$
w_fu' \propto -m r^{m-1}\psi + r^m\psi'.
$$

Differentiate once more:

$$
\frac{d}{dr}(w_fu')
\propto -m(m-1)r^{m-2}\psi + r^m\psi''.
$$

Now divide by $w_f\propto r^{2m}$ and multiply by $\sqrt{w_f}\propto r^m$:

$$
\sqrt{w_f}\,\Delta_f^{\mathrm{rad}}(w_f^{-1/2}\psi)
=\psi''-m(m-1)\frac{1}{r^2}\psi.
$$

Since

$$
m(m-1)=\frac{(\beta+1)(\beta-1)}{4}=\frac{\beta^2-1}{4},
$$

the inverse-square normal form follows.

## Energy Identity

For compactly supported $u$, with $\psi=\sqrt{w_f}\,u$, one gets

$$
\int_0^\infty w_f |u_r|^2\,dr
=\int_0^\infty |\psi'|^2\,dr
+\frac{\beta^2-1}{4}\int_0^\infty \frac{|\psi|^2}{r^2}\,dr.
$$

Applying the one-dimensional Hardy inequality

$$
\int_0^\infty |\psi'|^2\,dr
\ge \frac14\int_0^\infty \frac{|\psi|^2}{r^2}\,dr,
$$

gives the sharp weighted Hardy bound

$$
\int_0^\infty w_f |u_r|^2\,dr
\ge \frac{\beta^2}{4}\int_0^\infty \frac{|u|^2}{r^2}w_f\,dr.
$$

## Branch Markers

- $\beta=-1$: $w_f$ is constant and $V_\beta(r)=0$.
- $\beta=0$: $V_\beta(r)=-1/(4r^2)$, the critical logarithmic branch.
- $|\beta|<1$: attractive inverse-square well.
- $|\beta|>1$: repulsive inverse-square barrier.

## Why This Is a Strong Submission Candidate

- Exact internal result of the existing flat-$\pi_f$ framework.
- Strictly extends the already-known radial operator entry instead of restating it.
- Connects effective dimension, spectral normal form, and Hardy sharpness through the same parameter $\beta$.
- Produces clean artifacts: one derivation note, one plot, and one explainer animation.