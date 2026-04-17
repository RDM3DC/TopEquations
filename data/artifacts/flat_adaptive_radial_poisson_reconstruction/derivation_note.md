# Flat-Adaptive Radial Poisson Reconstruction Law

## Candidate equation

Let the flat-adaptive radial operator be written in the general branch form

$$
\Delta_f^{\mathrm{rad}}u
=u''(r)+\left(\frac{1}{r}+\frac{\pi_f'(r)}{\pi_f(r)}\right)u'(r).
$$

Assume on an interval $I\subset(0,\infty)$ that

$$
\Delta_f^{\mathrm{rad}}u=f,
\qquad
u\in C^2(I),
\qquad
f\in C^0(I),
\qquad
\pi_f(r)>0,
\qquad
u'(r)\neq 0.
$$

Then the flat-adaptive branch is recovered up to one multiplicative constant by

$$
\pi_f(r)
=\pi_f(r_*)
\exp\!\left(
\int_{r_*}^{r}
\left[
\frac{f(s)-u''(s)}{u'(s)}-\frac{1}{s}
\right]ds
\right),
$$

and equivalently by the cleaner form

$$
\pi_f(r)
=\pi_f(r_*)
\frac{r_*u'(r_*)}{r u'(r)}
\exp\!\left(
\int_{r_*}^{r}\frac{f(s)}{u'(s)}\,ds
\right).
$$

## Exact derivation

Starting from

$$
u''(r)+\left(\frac{1}{r}+\frac{\pi_f'(r)}{\pi_f(r)}\right)u'(r)=f(r),
$$

the nonvanishing condition on $u'$ gives the logarithmic-derivative law

$$
\frac{\pi_f'(r)}{\pi_f(r)}
=\frac{f(r)-u''(r)}{u'(r)}-\frac{1}{r}.
$$

Integrating from $r_*$ to $r$ yields

$$
\log \pi_f(r)-\log \pi_f(r_*)
=\int_{r_*}^{r}
\left[
\frac{f(s)-u''(s)}{u'(s)}-\frac{1}{s}
\right]ds,
$$

which exponentiates to the quadrature formula above.

To obtain the cleaner form, split the integrand:

$$
\frac{f-u''}{u'}-\frac{1}{r}
=\frac{f}{u'}-\frac{u''}{u'}-\frac{1}{r}.
$$

On any interval where $u'$ has fixed sign,

$$
\int_{r_*}^{r}\frac{u''(s)}{u'(s)}\,ds
=\log|u'(r)|-\log|u'(r_*)|,
$$

and

$$
\int_{r_*}^{r}\frac{ds}{s}=\log\frac{r}{r_*}.
$$

Substituting these identities gives

$$
\pi_f(r)
=\pi_f(r_*)
\frac{r_*u'(r_*)}{r u'(r)}
\exp\!\left(
\int_{r_*}^{r}\frac{f(s)}{u'(s)}\,ds
\right).
$$

## Flux form

The flat-adaptive shell weight is

$$
w_f(r)=2\pi_f(r)r.
$$

The radial Poisson law becomes

$$
\frac{1}{w_f}(w_fu')'=f
\qquad\Longleftrightarrow\qquad
(w_fu')'=w_f f.
$$

Define the shell flux

$$
J_f(r):=w_f(r)u'(r)=2\pi_f(r)r\,u'(r).
$$

Then

$$
J_f'(r)=w_f(r)f(r)=\frac{J_f(r)}{u'(r)}f(r),
$$

so

$$
\frac{J_f'(r)}{J_f(r)}=\frac{f(r)}{u'(r)}.
$$

Integrating gives

$$
J_f(r)=J_f(r_*)\exp\!\left(\int_{r_*}^{r}\frac{f(s)}{u'(s)}\,ds\right),
$$

and hence

$$
\pi_f(r)=\frac{J_f(r_*)}{2r u'(r)}\exp\!\left(\int_{r_*}^{r}\frac{f(s)}{u'(s)}\,ds\right).
$$

## Structural checks

### Harmonic case

If $f=0$, then

$$
\pi_f(r)=\pi_f(r_*)\frac{r_*u'(r_*)}{r u'(r)},
$$

so

$$
2\pi_f(r)r\,u'(r)=\text{constant}.
$$

This is exactly the harmonic-flux inversion law already implicit in the flat-adaptive annular transport branch.

### Power-law consistency test

If the reconstructed branch belongs to the exact power-law family

$$
\pi_f(r)=\pi\lambda_0\left(\frac{r}{r_0}\right)^\beta,
$$

then

$$
\frac{\pi_f'(r)}{\pi_f(r)}=\frac{\beta}{r},
$$

so the inverse law gives the observable exponent

$$
\beta_{\mathrm{obs}}(r)=r\,\frac{f(r)-u''(r)}{u'(r)}-1.
$$

For a true power-law branch, $\beta_{\mathrm{obs}}(r)$ must be constant on the interval.

## Turning points and identifiability

The reconstruction requires division by $u'(r)$. At a turning point $u'(r_0)=0$, the local equation reduces to

$$
u''(r_0)=f(r_0),
$$

so that point alone does not determine $\pi_f'(r_0)/\pi_f(r_0)$. Recovery therefore has to be carried out on monotone subintervals and stitched by one calibration datum.

## Practical recovery rule

Given measured $u(r)$ and known $f(r)$:

1. Split the radius range into intervals where $u'(r)\neq 0$ and keeps fixed sign.
2. On each interval, compute

   $$
   g(r):=\frac{f(r)-u''(r)}{u'(r)}-\frac{1}{r}.
   $$

3. Integrate

   $$
   \log\pi_f(r)=\log\pi_f(r_*)+\int_{r_*}^{r}g(s)\,ds.
   $$

4. Fix the multiplicative constant from one calibration datum, such as one known $\pi_f(r_*)$, one shell-flux measurement, or an independent area-growth observable.

## Why this matters

1. It closes the flat-adaptive inverse-recovery law in exact quadrature form rather than leaving it only as a logarithmic derivative.
2. It makes the Poisson branch as operational as the already-promoted area-inversion, annular-capacity, and Green-kernel entries.
3. It yields an exact power-law diagnostic $\beta_{\mathrm{obs}}(r)$ for testing whether measured data actually lies on a pure branch.
4. It shows that the hard part is not algebraic solvability but stable reconstruction near zeros of $u'$ and under noisy differentiation.
