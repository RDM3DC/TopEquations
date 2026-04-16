# Flat-Adaptive Separated Radial Sturm-Liouville Law

## Candidate equation

For the radial power-law branch

$$
\lambda(r)=\lambda_0\left(\frac{r}{r_0}\right)^\beta,
$$

consider the weighted polar Helmholtz operator

$$
\Delta_f u
=\frac{1}{\lambda(r)r}\frac{d}{dr}\left(\lambda(r)r\,\frac{\partial u}{\partial r}\right)
+\frac{1}{\lambda(r)^2 r^2}\frac{\partial^2 u}{\partial \theta^2}.
$$

Under the separated ansatz

$$
u(r,\theta)=R_n(r)e^{in\theta},
$$

the Helmholtz problem $-\Delta_f u=k^2 u$ reduces exactly to the radial Sturm-Liouville equation

$$
-\frac{d}{dr}\left(\lambda(r)r\,R_n'(r)\right)+\frac{n^2}{\lambda(r)r}R_n(r)=k^2\lambda(r)r\,R_n(r).
$$

Equivalently, after division by $\lambda(r)r$,

$$
R_n''(r)+\left(\frac{\beta+1}{r}\right)R_n'(r)
+\left[k^2-\frac{n^2 r_0^{2\beta}}{\lambda_0^2 r^{2\beta+2}}\right]R_n(r)=0.
$$

## Exact separation derivation

The angular derivative of the separated mode is

$$
\frac{\partial^2}{\partial \theta^2}e^{in\theta}=-n^2 e^{in\theta}.
$$

Substituting $u(r,\theta)=R_n(r)e^{in\theta}$ into $-\Delta_f u=k^2 u$ gives

$$
-\frac{1}{\lambda r}\frac{d}{dr}\left(\lambda r R_n'\right)e^{in\theta}
+\frac{n^2}{\lambda^2 r^2}R_n e^{in\theta}=k^2 R_n e^{in\theta}.
$$

Multiplying through by $\lambda(r)r$ yields the Sturm-Liouville form

$$
-\frac{d}{dr}\left(\lambda(r)r\,R_n'(r)\right)+\frac{n^2}{\lambda(r)r}R_n(r)=k^2\lambda(r)r\,R_n(r).
$$

So the weight function is exactly

$$
p(r)=w(r)=\lambda(r)r.
$$

## Immediate checks

1. When $n=0$, the equation collapses to

$$
-\frac{d}{dr}\left(\lambda(r)r\,R_0'(r)\right)=k^2\lambda(r)r\,R_0(r),
$$

which is the spectral version of the already-promoted radial operator.

2. On a finite annulus or bounded radial interval, the equation is in standard self-adjoint Sturm-Liouville divergence form with respect to the measure $\lambda(r)r\,dr$.

3. The same flat branch factor $\lambda(r)$ controls both the principal part and the angular barrier term.

## Why this matters

1. It upgrades the flat-adaptive radial branch from $n=0$ theory to exact mode-by-mode separation.
2. It is the natural radial companion to the angular eigenfunction law.
3. It supplies the spectral equation behind separated Green kernels, Helmholtz modes, and annular eigenvalue problems.
4. It keeps the same flat branch exponent $\beta$ in both transport weight and centrifugal penalty.
5. It is a strict extension of the promoted radial operator rather than a duplicate of it.