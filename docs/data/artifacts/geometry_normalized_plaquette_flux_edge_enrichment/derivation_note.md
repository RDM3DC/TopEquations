# Geometry-Normalized Plaquette-Flux Edge Enrichment

This artifact is a compact visual companion for

$$
f_{\mathrm{sup}}=\frac{\left(\sum_p |\rho_p|\right)^2}{N_p\sum_p |\rho_p|^2},\qquad
f_{\mathrm{edge}}^{(\rho)}=\frac{\sum_{p\in\partial\Omega}|\rho_p|}{\sum_p |\rho_p|},\qquad
\Xi_{\mathrm{edge}}=\frac{f_{\mathrm{edge}}^{(\rho)}}{|\partial\Omega|/N_p}.
$$

The dashboard does two things.

1. It sketches the measurement geometry: a damaged lattice with a distinguished boundary plaquette family $\partial\Omega$ and a local plaquette-flux weight field $|\rho_p|$.
2. It plots the reported large-size values for central-strip damage, showing that $\Xi_{\mathrm{edge}}$ remains close to the geometric boundary baseline $1.0$ at sizes $128$ and $160$.

Interpretation:

- $\Xi_{\mathrm{edge}} > 1$ means genuine edge concentration.
- $\Xi_{\mathrm{edge}} = 1$ means boundary flux is scaling like boundary area.
- $\Xi_{\mathrm{edge}} < 1$ means flux has shifted inward relative to the geometric boundary share.

For the promoted TopEquations entry, the point of the visual is not to claim extreme edge peaking; it is to show that post-damage plaquette-flux weight remains boundary-aligned instead of collapsing into the interior.