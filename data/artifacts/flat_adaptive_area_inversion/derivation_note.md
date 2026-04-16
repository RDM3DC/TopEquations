# Flat-Adaptive Area Inversion and Exponent Recovery

## Candidate equation

Let $A_f(R)$ be the flat-adaptive disk area out to radius $R$ in the radial branch. Then

$$
\pi_f(R)=\frac{1}{2R}\frac{dA_f}{dR}.
$$

For the exact power-law branch,

$$
\pi_f(r)=\pi\lambda_0\left(\frac{r}{r_0}\right)^\beta,
\qquad
A_f(R)=\int_0^R 2\pi_f(r)\,r\,dr
=\frac{2\pi\lambda_0 r_0^{-\beta}}{\beta+2}R^{\beta+2},
$$

so the area-growth exponent recovers the effective dimension and the branch exponent:

$$
d_{\mathrm{eff}}(R)=\frac{R A_f'(R)}{A_f(R)},
\qquad
\beta(R)=d_{\mathrm{eff}}(R)-2.
$$

In the pure power-law branch, $d_{\mathrm{eff}}(R)$ and $\beta(R)$ are constants and the exact identity reduces to

$$
d_{\mathrm{eff}}=\beta+2.
$$

## Exact derivation

The flat-adaptive shell weight already used by the promoted radial operator and annular capacity law is

$$
w_f(r)=2\pi\lambda_0 r_0^{-\beta}r^{\beta+1}=2\pi_f(r)\,r.
$$

Therefore

$$
A_f(R)=\int_0^R w_f(r)\,dr,
$$

and differentiation gives the shell-area identity

$$
A_f'(R)=w_f(R)=2\pi_f(R)R.
$$

Rearranging yields the inversion law

$$
\pi_f(R)=\frac{1}{2R}\frac{dA_f}{dR}.
$$

## Power-law recovery of $\beta$ and $d_{\mathrm{eff}}$

If

$$
A_f(R)=C R^{\beta+2},
$$

then

$$
\frac{R A_f'(R)}{A_f(R)}=\beta+2.
$$

So a direct measurement of area growth recovers

$$
d_{\mathrm{eff}}=\frac{R A_f'(R)}{A_f(R)},
\qquad
\beta=\frac{R A_f'(R)}{A_f(R)}-2.
$$

This turns the effective-dimension identity into a measurable geometric inversion law rather than a purely formal coefficient match.

## Why this matters

1. It is exact and local in radius.
2. It reconstructs the flat-adaptive ruler from area data alone.
3. It converts the promoted $d_{\mathrm{eff}}=\beta+2$ identity into a recovery formula.
4. It connects the radial operator, annular capacity, and shell geometry through the same derivative identity.
5. It is a clean observable-facing entry that was implicit in the artifacts but not visible as its own leaderboard statement.