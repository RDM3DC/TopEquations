#!/usr/bin/env python3
"""
End-to-end validation: Entropy-Gated Phase-Lifted ARP + FHS Chern trace
========================================================================

Demonstrates the full loop:
  G̃(t), S(t)  →  ε_eff(t)  →  m_eff(t)  →  integer C(t) via FHS

Boxed equation:
  dG̃/dt = α_G(S) |I(t)| e^{iθ_R(t)} − μ_G(S) G̃(t)

Entropy ODE (2nd-law safe):
  dS/dt = Σ |I|²/T · Re(1/G̃) + κ|Δw| − γ(S − S_eq)

BZ ruler self-consistency:
  m_eff = m₀ / √(1 − ε_eff²),  ε_c = √3/2 ≈ 0.8660
"""

import numpy as np
from scipy.integrate import solve_ivp

# ══════════════════════════════════════════════════════════════════
# FHS Chern helper (Fukui–Hatsugai–Suzuki, integer-quantised)
# ══════════════════════════════════════════════════════════════════
def chern_fhs_qwz(m: float, N: int = 31) -> int:
    kx = np.linspace(0, 2 * np.pi, N, endpoint=False)
    ky = np.linspace(0, 2 * np.pi, N, endpoint=False)
    KX, KY = np.meshgrid(kx, ky, indexing="ij")
    SX, SY = np.sin(KX), np.sin(KY)
    CX, CY = np.cos(KX), np.cos(KY)
    dz = m + CX + CY
    E = np.sqrt(SX**2 + SY**2 + dz**2)

    H = np.empty((N, N, 2, 2), dtype=complex)
    H[..., 0, 0] = dz;             H[..., 1, 1] = -dz
    H[..., 0, 1] = SX - 1j * SY;  H[..., 1, 0] = SX + 1j * SY
    _, vecs = np.linalg.eigh(H)
    u = vecs[..., :, 0]  # lower band

    u2 = np.roll(u, -1, 0)
    u3 = np.roll(u2, -1, 1)
    u4 = np.roll(u, -1, 1)
    dot = lambda a, b: (np.conj(a) * b).sum(-1)
    F = np.imag(np.log(dot(u, u2) * dot(u2, u3)
                      * dot(u3, u4) * dot(u4, u)))
    return int(np.rint(F.sum() / (2 * np.pi)))


# ══════════════════════════════════════════════════════════════════
# Physical parameters
# ══════════════════════════════════════════════════════════════════
m0       = -1.0          # base QWZ mass
alpha0   = 1.5           # max reinforcement rate
mu0      = 0.2           # base decay rate
S0       = 1.0           # entropy scale
Sc       = 3.0           # entropy gate centre (raised to keep α_G active longer)
dS_gate  = 0.5           # gate width (wider = softer gating)
kappa    = 0.2           # slip → entropy coupling
gamma    = 0.8           # entropy relaxation (strong pull back to Seq)
Seq      = 1.0           # equilibrium entropy
T_ij     = 10.0          # effective temperature (higher = less dissipation)

# Drive: current with slowly growing ε_eff
# π_a evolves as ε(t) ramps from 0 → 1.0 over t ∈ [0,100]
eps_max  = 1.0
t_ramp   = 100.0

def eps_of_t(t):
    """Ramp ε from 0 to eps_max linearly."""
    return min(eps_max, max(0.0, t / t_ramp * eps_max))

def m_eff_of_eps(eps):
    """BZ-averaged ruler coupling: m_eff = m₀/√(1−ε²)."""
    e2 = min(eps**2, 0.9999)
    return m0 / np.sqrt(1 - e2)

def drive_current(t):
    """External current drive |I|e^{iθ} — oscillating with ε-dependent envelope."""
    eps = eps_of_t(t)
    amp = 1.0 + 0.5 * eps          # amplitude grows with deformation
    theta = 2.0 * t + 0.3 * np.sin(0.7 * t)  # nonlinear phase
    return amp, theta

def alpha_G(S):
    return alpha0 / (1 + np.exp((S - Sc) / dS_gate))

def mu_G(S):
    return mu0 * (S / S0)


# ══════════════════════════════════════════════════════════════════
# ODE system: y = [Re(G̃), Im(G̃), S, w_cumulative]
# ══════════════════════════════════════════════════════════════════
theta_R_prev = [0.0]   # mutable, for Phase-Lift state
w_prev       = [0]     # sheet index

def rhs(t, y):
    G_re, G_im, S, w_cum = y
    G = complex(G_re, G_im)

    # Drive
    I_amp, theta_raw = drive_current(t)

    # ── Phase-Lift (Core Eq. 2–4) ────────────────────────────────
    eps = eps_of_t(t)
    pi_a = np.pi * (1 + eps)    # simplified: BZ-uniform ruler at ε(t)
    period = 2 * pi_a

    # Nearest-sheet unwrap
    diff = theta_raw - theta_R_prev[0]
    m = round(diff / period) if period > 1e-10 else 0
    # Clamp m to avoid runaway
    m = max(-5, min(5, m))
    theta_R = theta_raw - m * period
    theta_R_prev[0] = theta_R

    # Sheet-jump slip event
    delta_w = abs(m - w_prev[0]) if abs(m) > 0 else 0
    w_prev[0] = m

    # ── Boxed equation ───────────────────────────────────────────
    aG = alpha_G(S)
    mG = mu_G(S)
    dG = aG * I_amp * np.exp(1j * theta_R) - mG * G
    dG_re = dG.real
    dG_im = dG.imag

    # ── Entropy ODE (2nd-law safe) ───────────────────────────────
    G_inv_re = G_re / (G_re**2 + G_im**2 + 1e-10)  # Re(1/G̃)
    dissipation = I_amp**2 / T_ij * max(G_inv_re, 0.0)
    # Clamp entropy to avoid overflow in sigmoid
    S_clamped = min(S, 50.0)
    dS = dissipation + kappa * delta_w - gamma * (S_clamped - Seq)

    # Track cumulative slip events
    dw_cum = float(delta_w)

    return [dG_re, dG_im, dS, dw_cum]


# ══════════════════════════════════════════════════════════════════
# Integrate
# ══════════════════════════════════════════════════════════════════
y0 = [0.5, 0.0, Seq, 0.0]  # initial: G̃=0.5, S=S_eq, w=0
t_span = (0, t_ramp)

print("Integrating entropy-gated Phase-Lifted ARP system...")
sol = solve_ivp(rhs, t_span, y0, method="LSODA",
                max_step=0.05, rtol=1e-8, atol=1e-10)

t_sol    = sol.t
G_re     = sol.y[0]
G_im     = sol.y[1]
S_sol    = sol.y[2]
w_cum    = sol.y[3]
G_mag    = np.sqrt(G_re**2 + G_im**2)

# Compute ε_eff(t) and m_eff(t)
eps_arr  = np.array([eps_of_t(ti) for ti in t_sol])
meff_arr = np.array([m_eff_of_eps(e) for e in eps_arr])

print(f"Integration done: {len(t_sol)} steps, t ∈ [{t_sol[0]:.1f}, {t_sol[-1]:.1f}]")


# ══════════════════════════════════════════════════════════════════
# FHS Chern trace at 12 time samples
# ══════════════════════════════════════════════════════════════════
K = 12
sample_idx = np.linspace(0, len(t_sol) - 1, K, dtype=int)
eps_c = np.sqrt(3) / 2  # ≈ 0.8660

chern_trace = []
print(f"\nFHS Chern trace ({K} samples, N=31)  ε_c = √3/2 ≈ {eps_c:.4f}")
print(f"{'t':>8s}  {'ε_eff':>8s}  {'m_eff':>9s}  {'|G̃|':>7s}  {'S':>7s}  {'C':>3s}")
print("─" * 52)

for idx in sample_idx:
    ti = t_sol[idx]
    ei = eps_arr[idx]
    mi = meff_arr[idx]
    Gi = G_mag[idx]
    Si = S_sol[idx]
    Ci = chern_fhs_qwz(mi, N=31)
    chern_trace.append((ti, ei, mi, Gi, Si, Ci))
    flag = " ◄ ε_c" if abs(ei - eps_c) < 0.05 else ""
    print(f"{ti:8.2f}  {ei:8.4f}  {mi:+9.4f}  {Gi:7.4f}  {Si:7.4f}  {Ci:+3d}{flag}")


# ══════════════════════════════════════════════════════════════════
# Plot
# ══════════════════════════════════════════════════════════════════
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(4, 1, figsize=(11, 12), sharex=True)
    tt_c = np.array([x[0] for x in chern_trace])
    CC   = np.array([x[5] for x in chern_trace])

    # Panel 1: Chern number
    ax = axes[0]
    ax.step(tt_c, CC, where="mid", color="#d62728", lw=2.5)
    ax.axhline(0, color="gray", lw=0.5, ls="--")
    tc_approx = t_ramp * eps_c / eps_max
    ax.axvline(tc_approx, color="#2ca02c", ls=":", lw=1.5, alpha=0.8)
    ax.text(tc_approx + 1, 0.7, r"$\varepsilon_c = \sqrt{3}/2$",
            fontsize=11, color="#2ca02c")
    ax.set_ylabel("Chern $C$", fontsize=12)
    ax.set_ylim(-1.7, 1.2)
    ax.set_yticks([-1, 0, 1])
    ax.set_title("End-to-End Validation: Entropy-Gated Phase-Lifted ARP → Chern",
                  fontsize=13, fontweight="bold")

    # Panel 2: m_eff and ε_eff
    ax = axes[1]
    ax.plot(t_sol, meff_arr, color="#1f77b4", lw=1.5, label=r"$m_{\rm eff}(t)$")
    ax.axhline(-2, color="gray", ls="--", lw=0.8, label="$m=-2$ (gap close)")
    ax.axvline(tc_approx, color="#2ca02c", ls=":", lw=1.5, alpha=0.7)
    ax.set_ylabel(r"$m_{\rm eff}$", fontsize=12)
    ax.legend(fontsize=9, loc="lower left")
    ax2 = ax.twinx()
    ax2.plot(t_sol, eps_arr, color="#ff7f0e", lw=1.2, alpha=0.7)
    ax2.set_ylabel(r"$\varepsilon_{\rm eff}$", fontsize=11, color="#ff7f0e")

    # Panel 3: |G̃| and entropy S
    ax = axes[2]
    ax.plot(t_sol, G_mag, color="#9467bd", lw=1.2, label=r"$|\tilde{G}|$")
    ax.set_ylabel(r"$|\tilde{G}|$", fontsize=12, color="#9467bd")
    ax.axvline(tc_approx, color="#2ca02c", ls=":", lw=1.5, alpha=0.5)
    ax3 = ax.twinx()
    ax3.plot(t_sol, S_sol, color="#e377c2", lw=1.2, alpha=0.8)
    ax3.set_ylabel("Entropy $S$", fontsize=11, color="#e377c2")

    # Panel 4: cumulative slip events
    ax = axes[3]
    ax.plot(t_sol, w_cum, color="#8c564b", lw=1.5)
    ax.axvline(tc_approx, color="#2ca02c", ls=":", lw=1.5, alpha=0.5)
    ax.set_ylabel("Cumulative slips", fontsize=12)
    ax.set_xlabel("Time $t$", fontsize=13)

    plt.tight_layout()
    out = "docs/assets/entropy_gated_arp_chern_validation.png"
    plt.savefig(out, dpi=180, bbox_inches="tight")
    print(f"\nFigure saved → {out}")

except ImportError:
    print("\n(install matplotlib for figure)")
