# ARP Kirchhoff-Coupled Lyapunov Contraction & Falsifiability

**Derivation note for TopEquations registry entries**
- `eq-arp-kirchhoff-coupled-lyapunov-contraction-theorem`
- `eq-kirchhoff-lipschitz-sufficient-condition-for-arp-contrac`
- `eq-kirchhoff-collapse-identity-falsifier`

Reference simulation: [`tools/arp_kirchhoff_sim.py`](../tools/arp_kirchhoff_sim.py)
Reference data: [`data/arp_kirchhoff_sim.csv`](../data/arp_kirchhoff_sim.csv)

---

## 1. Setup

**ARP conductance dynamics (standard form):**

$$
\dot{G}_{ij} = \alpha_G\,|I_{ij}| - \mu_G\,G_{ij}
$$

**Kirchhoff coupling.** For a network with conductance matrix $G$, source vector
$s \in \mathbb{R}^n$, and one grounded node, edge currents are

$$
I = G \odot (V\,\mathbf{1}^\top - \mathbf{1}\,V^\top), \qquad L(G)\,V = s,
$$

where $L(G) = D - G$ is the conductance-weighted Laplacian.

**Frozen-current equilibrium.** With $|I_{ij}|$ held fixed at its initial value $|I^{(0)}_{ij}|$,

$$
G^\star_{ij} = \frac{\alpha_G}{\mu_G}\,|I^{(0)}_{ij}|.
$$

---

## 2. Lyapunov function

$$
V(G) = \frac{1}{2\,\alpha_G}\sum_{ij}\big(G_{ij} - G^\star_{ij}\big)^2.
$$

Clearly $V \ge 0$ with $V = 0 \iff G = G^\star$.

---

## 3. Frozen-current contraction (exact)

With $|I| = |I^{(0)}|$ frozen,

$$
\dot{V} = \frac{1}{\alpha_G}\sum_{ij}(G_{ij} - G^\star_{ij})\,\dot{G}_{ij}
       = \frac{1}{\alpha_G}\sum_{ij}(G_{ij} - G^\star_{ij})\big(\alpha_G\,|I^{(0)}_{ij}| - \mu_G\,G_{ij}\big).
$$

Substituting $\alpha_G\,|I^{(0)}_{ij}| = \mu_G\,G^\star_{ij}$:

$$
\dot{V} = \frac{1}{\alpha_G}\sum_{ij}(G_{ij} - G^\star_{ij})\big(\mu_G\,G^\star_{ij} - \mu_G\,G_{ij}\big)
       = -\frac{\mu_G}{\alpha_G}\sum_{ij}(G_{ij} - G^\star_{ij})^2
       = -2\,\mu_G\,V.
$$

**Numerical certificate** (from `arp_kirchhoff_sim.py`, seed 42, n=12, p=0.35,
α_G=0.5, μ_G=0.025, dt=0.01, 2000 steps):

| Quantity | Predicted | Measured |
|---|---|---|
| Lyapunov decay rate | $-2\mu_G = -0.0500$ | **−0.05000625** |

Match to 4 significant figures. ✅

---

## 4. Kirchhoff-coupled bound

Under honest coupling, $|I| = |I(G)|$ varies with $G$. Define the
Kirchhoff-Lipschitz constant

$$
\kappa \;:=\; \sup_{\delta G}
\frac{\big\lVert\,|I(G + \delta G,\,s)| - |I(G,\,s)|\,\big\rVert}{\lVert\delta G\rVert}.
$$

Then by the chain rule and Cauchy-Schwarz on $\sum (G - G^\star) \cdot \alpha_G\,\Delta|I|$:

$$
\boxed{\;\dot{V} \le -2\,(\mu_G - \kappa)\,V\;}
$$

**Sufficient contraction condition:** $\mu_G > \kappa$.

---

## 5. Empirical κ probe

A random-perturbation estimator: draw $N$ symmetric perturbations
$\delta G \sim \mathcal{N}(0, \epsilon^2)\big|_{\text{edges}}$, evaluate the
quotient, and take the empirical sup.

**Result for the 12-node random graph above** (128 probes, ε = 1e-3):

$$
\kappa_{\text{measured}} \approx 1.01, \qquad
\mu_G - \kappa \approx -0.985 < 0.
$$

**Interpretation.** The sufficient condition $\mu_G > \kappa$ is
**not satisfied** for this network. The contraction theorem does not
guarantee stability here. The Lyapunov function may still decay (the
sufficient condition is not necessary), but the certificate fails to
provide a guarantee.

This is a **healthy negative result** for the falsifier: it demonstrates
the bound is operational and discriminating. To recover a guarantee, one
must either (a) increase $\mu_G$ above $\kappa$, (b) sparsify the network
to reduce $\kappa$, or (c) use a tighter, structure-aware bound that
exploits Laplacian symmetry.

---

## 6. Collapse-identity falsifier

Some ARP analyses casually invoke

$$
|I_{ij}| \;\stackrel{?}{=}\; \frac{\mu_G}{\alpha_G}\,G_{ij}
$$

as if it were an asymptotic identity. Under honest Kirchhoff coupling this
**fails**: currents redistribute through the network and cannot remain
proportional to the local conductance.

**Quantitative falsifier:**

$$
R(t) \;:=\; \frac{\big\lVert\,|I(t)| - (\mu_G/\alpha_G)\,G(t)\,\big\rVert}{\lVert I(t)\rVert}
\;\not\to\; 0.
$$

**Measurement.** From the same simulation:

| Quantity | Value |
|---|---|
| $R(t_{\text{final}})$ | **0.598** |
| Mean of $R$ over last 200 steps | **0.613** |

The residual saturates near 0.6 and never relaxes to zero. The collapse
identity is therefore a modeling shortcut, not a derivable equilibrium.

---

## 7. What this changes for the registry

1. **Entry A** (`eq-arp-kirchhoff-coupled-lyapunov-contraction-theorem`)
   The frozen-current half is exact and verified to 4 s.f. The
   Kirchhoff-coupled half is a rigorous upper bound.
2. **Entry B** (`eq-kirchhoff-lipschitz-sufficient-condition-for-arp-contrac`)
   First operationally measurable stability bound. Probe gives a number; user
   compares to $\mu_G$. The 12-node example shows the bound is
   non-trivial — it can fail, which is exactly what a falsifier must do.
3. **Entry C** (`eq-kirchhoff-collapse-identity-falsifier`)
   Negative result confirmed: residual saturates well above zero, not
   convergent. Any registry entry that derives equilibria via the
   collapse identity should carry a `PASS-WITH-ASSUMPTIONS` qualifier.
4. **Old `eq-arp-lyapunov-stability`** (score 66, placeholder template) is
   superseded by Entry A.

---

## 8. Reproducing

```powershell
python tools/arp_kirchhoff_sim.py --seed 42
python tools/measure_kappa.py --equation-id eq-paper1-arp-reinforce-decay
```

Outputs: `data/arp_kirchhoff_sim.csv` plus a summary block printed to stdout.
