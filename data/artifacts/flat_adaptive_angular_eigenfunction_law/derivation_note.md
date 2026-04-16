# Flat-Adaptive Angular Eigenfunction Law

## Candidate equation

Let the angular flat-adaptive ruler be a positive, smooth, $2\pi$-periodic field $\lambda(\theta)>0$. Define

$$
L_\theta^{(f)}
=-\frac{1}{\lambda(\theta)}\frac{d}{d\theta}\left(\frac{1}{\lambda(\theta)}\frac{d}{d\theta}\right),
\qquad
\Phi_f(\theta)=\int_0^\theta \lambda(\vartheta)\,d\vartheta,
\qquad
\Lambda_f=\Phi_f(2\pi).
$$

Then the exact angular eigenfunctions are the pulled-back circle modes

$$
\phi_n^{(c)}(\theta)=\cos\!\left(\omega_n\Phi_f(\theta)\right),
\qquad
\phi_n^{(s)}(\theta)=\sin\!\left(\omega_n\Phi_f(\theta)\right),
\qquad
\omega_n=\frac{2\pi n}{\Lambda_f},
$$

and they satisfy

$$
L_\theta^{(f)}\phi_n=\omega_n^2\phi_n.
$$

The same change of variable gives weighted orthogonality in the flat-adaptive angular measure

$$
\langle f,g\rangle_f=\int_0^{2\pi} f(\theta)g(\theta)\,\lambda(\theta)\,d\theta,
$$

so every sufficiently regular periodic angular field admits the generalized Fourier expansion

$$
u(\theta)=a_0+\sum_{n\ge 1}\left[a_n\cos\!\left(\omega_n\Phi_f(\theta)\right)+b_n\sin\!\left(\omega_n\Phi_f(\theta)\right)\right].
$$

## Exact flattening derivation

Introduce the flat-adaptive arc variable

$$
s=\Phi_f(\theta)=\int_0^\theta \lambda(\vartheta)\,d\vartheta.
$$

Then

$$
\frac{d}{ds}=\frac{1}{\lambda(\theta)}\frac{d}{d\theta}.
$$

Substituting this identity into the operator gives

$$
L_\theta^{(f)}
=-\frac{1}{\lambda(\theta)}\frac{d}{d\theta}\left(\frac{1}{\lambda(\theta)}\frac{d}{d\theta}\right)
=-\frac{d^2}{ds^2}.
$$

So the flat-adaptive angular sector is exactly the ordinary Laplacian on a circle of length $\Lambda_f$ in the $s$ variable.

## Eigenfunctions and eigenvalues

On a circle of length $\Lambda_f$, the standard periodic eigenbasis is

$$
\cos\!\left(\frac{2\pi n}{\Lambda_f}s\right),
\qquad
\sin\!\left(\frac{2\pi n}{\Lambda_f}s\right),
\qquad n\in\mathbb N.
$$

Pulling back along $s=\Phi_f(\theta)$ gives the claimed basis in $\theta$, with eigenvalue $\omega_n^2$.

## Weighted orthogonality

Because $ds=\lambda(\theta)\,d\theta$, the flat-adaptive inner product is exactly the Euclidean $L^2$ inner product on the flattened circle:

$$
\int_0^{2\pi} f(\theta)g(\theta)\,\lambda(\theta)\,d\theta
=\int_0^{\Lambda_f} f(s)g(s)\,ds.
$$

Therefore the pulled-back sine and cosine modes inherit ordinary orthogonality from the flat circle.

## Why this matters

1. It is the missing angular companion to the already-promoted radial flat-adaptive branch.
2. It upgrades the framework from radial-only identities to a full periodic spectral basis.
3. The generalized Fourier expansion is exact, not asymptotic.
4. The same ruler field $\lambda(\theta)$ controls operator geometry, mode spacing, and orthogonality.
5. It gives a clean separation interface for later Helmholtz, Green-kernel, and Sturm-Liouville extensions.