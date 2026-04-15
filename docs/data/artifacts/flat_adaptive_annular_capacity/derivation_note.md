# Flat-Adaptive Annular Capacity Law

## Candidate equation

For the flat-adaptive radial branch

$$
\pi_f(r)=\pi\lambda_0\left(\frac{r}{r_0}\right)^{\beta},
\qquad
w_f(r)=2\pi\lambda_0 r_0^{-\beta} r^{\beta+1},
$$

the exact Dirichlet annular capacity between radii $a<b$ is

$$
\mathcal C_f(a,b;\beta)=
\begin{cases}
\dfrac{2\pi\lambda_0 r_0^{-\beta}\,\beta}{a^{-\beta}-b^{-\beta}}, & \beta\neq 0,\\[8pt]
\dfrac{2\pi\lambda_0}{\ln(b/a)}, & \beta=0.
\end{cases}
$$

This is the transport observable attached to the already-promoted flat-adaptive radial operator and recovers the logarithmic $2$D annular law exactly at the critical branch $\beta=0$.

## Derivation

In the radial sector, the flat-adaptive operator is

$$
\Delta_f^{\mathrm{rad}}u = u'' + \frac{\beta+1}{r}u'.
$$

Equivalently,

$$
\Delta_f^{\mathrm{rad}}u = \frac{1}{w_f(r)}\,\frac{d}{dr}\!\left(w_f(r)u'(r)\right),
\qquad
w_f(r)=2\pi\lambda_0 r_0^{-\beta}r^{\beta+1}.
$$

For the annular Dirichlet problem on $a<r<b$ with $u(a)=1$ and $u(b)=0$, the Euler-Lagrange equation is

$$
\frac{d}{dr}\!\left(w_f(r)u'(r)\right)=0.
$$

Hence the radial flux is constant:

$$
-w_f(r)u'(r)=\mathcal C_f(a,b;\beta).
$$

Solving for $u'$ gives

$$
u'(r)=-\frac{\mathcal C_f(a,b;\beta)}{2\pi\lambda_0 r_0^{-\beta}}\,r^{-\beta-1}.
$$

Integrating from $a$ to $b$ and using $u(a)-u(b)=1$ yields

$$
1=\frac{\mathcal C_f(a,b;\beta)}{2\pi\lambda_0 r_0^{-\beta}}\int_a^b r^{-\beta-1}\,dr.
$$

For $\beta\neq 0$,

$$
\int_a^b r^{-\beta-1}\,dr = \frac{a^{-\beta}-b^{-\beta}}{\beta},
$$

so

$$
\mathcal C_f(a,b;\beta)=\frac{2\pi\lambda_0 r_0^{-\beta}\,\beta}{a^{-\beta}-b^{-\beta}}.
$$

For $\beta=0$,

$$
\int_a^b r^{-1}\,dr = \ln\!\left(\frac{b}{a}\right),
$$

so

$$
\mathcal C_f(a,b;0)=\frac{2\pi\lambda_0}{\ln(b/a)}.
$$

## Exact harmonic profile

The annular harmonic profile is also explicit:

$$
u_{\beta}(r)=
\begin{cases}
\dfrac{r^{-\beta}-b^{-\beta}}{a^{-\beta}-b^{-\beta}}, & \beta\neq 0,\\[8pt]
\dfrac{\ln(b/r)}{\ln(b/a)}, & \beta=0.
\end{cases}
$$

This exhibits the exact crossover from power-law to logarithmic radial response at $\beta=0$.

## Effective-dimension rewrite

Using the already-promoted identity

$$
d_{\mathrm{eff}}=\beta+2,
$$

the noncritical branch can be rewritten as

$$
\mathcal C_f(a,b;\beta)=\frac{2\pi\lambda_0 r_0^{-(d_{\mathrm{eff}}-2)}\,(d_{\mathrm{eff}}-2)}{a^{-(d_{\mathrm{eff}}-2)}-b^{-(d_{\mathrm{eff}}-2)}},
\qquad d_{\mathrm{eff}}\neq 2.
$$

So the flat-adaptive annulus has the exact Euclidean radial capacity law of dimension $d_{\mathrm{eff}}$, with the critical logarithmic $2$D law appearing at $d_{\mathrm{eff}}=2$.

## Why this is strong

1. It is exact, not asymptotic.
2. It converts the branch exponent $\beta$ into a measurable transport observable.
3. It cleanly recovers the logarithmic $2$D capacity at the critical branch $\beta=0$.
4. It makes the effective-dimension dictionary operational rather than purely formal.
5. It is directly compatible with the inverse-square normal form and the harmonic profile of the branch.