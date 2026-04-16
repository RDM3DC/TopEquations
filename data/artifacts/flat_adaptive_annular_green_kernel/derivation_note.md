# Flat-Adaptive Annular Green Kernel

## Candidate equation

For the flat-adaptive radial branch

$$
\pi_f(r)=\pi\lambda_0\left(\frac{r}{r_0}\right)^\beta,
\qquad
w_f(r)=2\pi\lambda_0 r_0^{-\beta}r^{\beta+1},
$$

the exact Dirichlet Green kernel on the annulus $a<r<b$ is

$$
G_\beta(r,\rho)=
\begin{cases}
\dfrac{\bigl(a^{-\beta}-r_<^{-\beta}\bigr)\bigl(r_>^{-\beta}-b^{-\beta}\bigr)}{2\pi\lambda_0 r_0^{-\beta}\,\beta\,\bigl(a^{-\beta}-b^{-\beta}\bigr)}, & \beta\neq 0,\\[10pt]
\dfrac{\ln(r_</a)\,\ln(b/r_>)}{2\pi\lambda_0\ln(b/a)}, & \beta=0,
\end{cases}
$$

where $r_<=\min(r,\rho)$ and $r_>=\max(r,\rho)$.

This kernel solves the radial Dirichlet problem

$$
-\frac{1}{w_f(r)}\frac{d}{dr}\left(w_f(r)\frac{d}{dr}G_\beta(r,\rho)\right)=\frac{\delta(r-\rho)}{w_f(\rho)},
\qquad
G_\beta(a,\rho)=G_\beta(b,\rho)=0.
$$

## Exact reciprocal-shell derivation

For the divergence-form operator

$$
\Delta_f^{\mathrm{rad}}u=\frac{1}{w_f(r)}\frac{d}{dr}\left(w_f(r)u'(r)\right),
$$

the homogeneous equation has the two basic solutions

$$
1,
\qquad
H(r)=\int_a^r \frac{dt}{w_f(t)}.
$$

The Dirichlet Green function for the one-dimensional operator $-(w_f u')'$ is therefore

$$
G(r,\rho)=\frac{H(r_<)K(r_>)}{H(b)},
\qquad
K(r)=\int_r^b \frac{dt}{w_f(t)}.
$$

Since $w_f(t)=2\pi\lambda_0 r_0^{-\beta}t^{\beta+1}$,

$$
H(r)=
\begin{cases}
\dfrac{a^{-\beta}-r^{-\beta}}{2\pi\lambda_0 r_0^{-\beta}\,\beta}, & \beta\neq 0,\\[8pt]
\dfrac{\ln(r/a)}{2\pi\lambda_0}, & \beta=0,
\end{cases}
$$

and

$$
K(r)=
\begin{cases}
\dfrac{r^{-\beta}-b^{-\beta}}{2\pi\lambda_0 r_0^{-\beta}\,\beta}, & \beta\neq 0,\\[8pt]
\dfrac{\ln(b/r)}{2\pi\lambda_0}, & \beta=0.
\end{cases}
$$

Substituting these exact integrals gives the closed form above.

## Structural checks

1. $G_\beta(r,\rho)=G_\beta(\rho,r)$ by construction.
2. $G_\beta(a,\rho)=G_\beta(b,\rho)=0$.
3. The jump condition is exact:

$$
-\bigl[w_f(r)\partial_r G_\beta(r,\rho)\bigr]_{r=\rho^-}^{r=\rho^+}=1.
$$

4. The $\beta\to 0$ limit reproduces the logarithmic $2$D annular kernel exactly.

## Why this matters

1. It is the Green-function completion of the already-promoted annular capacity and harmonic-profile results.
2. The same branch exponent $\beta$ governs harmonic profiles, capacity, and resolvent kernel.
3. The critical branch $\beta=0$ again lands exactly on the logarithmic $2$D law.
4. It gives an exact response kernel for radial forcing on annuli, not just a boundary flux observable.
5. It is a clean bridge from the flat-adaptive radial operator to potential-theory language.