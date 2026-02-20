# Equation Harvest Preview

Unique: 15088 (raw 22205)

## First 20

- **code** from `C:\Users\RDM3D\clawdad42\acm_find_137.py`

  `mem = cma3d.curve_memory_3d(np.array(pts), levels=3)`

- **code** from `C:\Users\RDM3D\clawdad42\acm_find_137.py`

  `g = mem['pack']['global']`

- **code** from `C:\Users\RDM3D\clawdad42\acm_find_137.py`

  `k1 = g['kappa_L1']; k2 = g['kappa_L2']; t1 = g['tau_L1']; t2 = g['tau_L2']`

- **code** from `C:\Users\RDM3D\clawdad42\acm_find_137.py`

  `print(f"{name}: L={mem['L']:.3f}, kappa_L1={k1:.6f}, kappa_L2={k2:.6f}, tau_L1={t1:.6f}, tau_L2={t2:.6f}, k1/k2={(k1/(k2+1e-12)):.6f}")`

- **code** from `C:\Users\RDM3D\clawdad42\acm_find_137.py`

  `t = np.linspace(0, 6*np.pi, 600)`

- **code** from `C:\Users\RDM3D\clawdad42\acm_find_137.py`

  `helix = np.stack([np.cos(t), np.sin(t), 0.1*t], axis=1)`

- **code** from `C:\Users\RDM3D\clawdad42\acm_find_137.py`

  `t2 = np.linspace(0, 12*np.pi, 800)`

- **code** from `C:\Users\RDM3D\clawdad42\acm_find_137.py`

  `r = 0.01 * t2`

- **code** from `C:\Users\RDM3D\clawdad42\acm_find_137.py`

  `spiral3 = np.stack([r*np.cos(t2), r*np.sin(t2), 0.02*t2], axis=1)`

- **code** from `C:\Users\RDM3D\clawdad42\acm_find_137.py`

  `theta = np.linspace(0, 2*np.pi, 400)`

- **code** from `C:\Users\RDM3D\clawdad42\acm_find_137.py`

  `circle = np.stack([np.cos(theta), np.sin(theta), np.zeros_like(theta)], axis=1)`

- **code** from `C:\Users\RDM3D\clawdad42\acm_find_137.py`

  `noise = 0.005 * np.random.RandomState(0).randn(*helix.shape)`

- **code** from `C:\Users\RDM3D\clawdad42\acm_find_137.py`

  `noisy = helix + noise`

- **code** from `C:\Users\RDM3D\clawdad42\acm_find_137.py`

  `val = g['kappa_L1'] * 1000.0`

- **code** from `C:\Users\RDM3D\clawdad42\acm_find_137.py`

  `print(f"{name} kappa_L1*1000 = {val:.6f}")`

- **latex** from `C:\Users\RDM3D\clawdad42\Adaptive-Curvature-Memory-ACM-\README.md`

  `\kappa(s) = \left\| \frac{d\mathbf{T}}{ds} \right\|`

- **latex** from `C:\Users\RDM3D\clawdad42\Adaptive-Curvature-Memory-ACM-\README.md`

  `\begin{aligned} \frac{d\mathbf{T}}{ds} &= \kappa(s)\,\mathbf{N}(s) \\\ \frac{d\mathbf{N}}{ds} &= -\kappa(s)\,\mathbf{T}(s) + \tau(s)\,\mathbf{B}(s) \\\ \frac{d\mathbf{B}}{ds} &= -\tau(s)\,\mathbf{N}(s) \end{aligned}`

- **latex** from `C:\Users\RDM3D\clawdad42\Adaptive-Curvature-Memory-ACM-\README.md`

  `\mathcal{M} = \big( L,\; u,\; \kappa(u),\; \tau(u) \big)`

- **latex** from `C:\Users\RDM3D\clawdad42\Adaptive-Curvature-Memory-ACM-\README.md`

  `\ell_i = \|\mathbf{p}_{i+1}-\mathbf{p}_i\|, \quad s_j = \sum_{i=0}^{j-1}\ell_i, \quad L = s_N`

- **latex** from `C:\Users\RDM3D\clawdad42\Adaptive-Curvature-Memory-ACM-\README.md`

  `\mathbf{t}_i = \frac{\mathbf{p}_{i+1}-\mathbf{p}_i}{\ell_i}`
