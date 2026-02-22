#!/usr/bin/env python3
"""
πₐ-scaled QWZ topological phase diagram
========================================

Design A — k-dependent coupling (original, re-entrant):
    πₐ(kx) = π(1 + ε cos kx)
    m_eff(kx) = m_base + β·[1/(1+ε cos kx) − 1]

Design B — BZ-averaged uniform ruler (single clean jump):
    m_eff(ε) = m₀ / √(1 − ε²)
    ⟨1/(1+ε cos λ)⟩_BZ = 1/√(1−ε²)  ← exact for |ε|<1

    Critical deformation:  ε_c = √3/2 ≈ 0.8660
    At ε_c the effective mass crosses m = −2 (QWZ phase boundary),
    Chern number jumps C: −1 → 0.  Single transition, trivial forever.

FHS (Fukui–Hatsugai–Suzuki) lattice Chern number, integer-quantised.
"""

import sys
import numpy as np

HAVE_MPL = True
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
except ImportError:
    HAVE_MPL = False
    print("matplotlib not found — table only, no figure.")

# ── BZ grid ───────────────────────────────────────────────────────
N  = 61
dk = 2 * np.pi / N
k1 = np.arange(N) * dk
KX, KY = np.meshgrid(k1, k1, indexing="ij")
SX, SY = np.sin(KX), np.sin(KY)
CX, CY = np.cos(KX), np.cos(KY)


def fhs_chern(hz):
    """Fukui–Hatsugai–Suzuki Chern number and minimum spectral gap."""
    E   = np.sqrt(SX**2 + SY**2 + hz**2)
    gap = float(2 * E.min())

    H = np.empty((N, N, 2, 2), dtype=complex)
    H[..., 0, 0] =  hz;             H[..., 1, 1] = -hz
    H[..., 0, 1] =  SX - 1j * SY;  H[..., 1, 0] =  SX + 1j * SY
    _, vecs = np.linalg.eigh(H)
    u = vecs[..., :, 0]                          # ground state

    u2 = np.roll(u, -1, 0)                       # (i+1, j)
    u3 = np.roll(u2, -1, 1)                      # (i+1, j+1)
    u4 = np.roll(u, -1, 1)                       # (i,   j+1)
    dot = lambda a, b: (np.conj(a) * b).sum(-1)  # <a|b>
    F  = np.imag(np.log(dot(u, u2) * dot(u2, u3)
                       * dot(u3, u4) * dot(u4, u)))
    return int(round(F.sum() / (2 * np.pi))), gap


# ── Parameters ────────────────────────────────────────────────────
m_base = -1.0
beta   =  1.5
eps_all = np.round(np.arange(0, 1.305, 0.01), 4)
eps_B_max = 0.995                               # B diverges at ε = 1

CA, gA = [], []
CB, gB = [], []

eps_c = np.sqrt(3) / 2   # analytic transition for Design B

print(f"FHS lattice Chern scan   N={N}   m₀={m_base}   β={beta}")
print(f"Analytic ε_c (Design B) = √3/2 ≈ {eps_c:.4f}\n")
hdr = (f"{'ε':>6s} │ {'C_A':>3s} {'gap_A':>7s} {'⟨m⟩_A':>8s}"
       f" │ {'C_B':>3s} {'gap_B':>7s} {'m_B':>8s}")
print(hdr)
print("─" * len(hdr))

for eps in eps_all:
    # ── Design A: k-dependent πₐ(kx) ─────────────────────────────
    denom = 1 + eps * CX
    denom = np.where(np.abs(denom) < 1e-8,
                     np.sign(denom + 1e-16) * 1e-8, denom)
    meff_A = m_base + beta * (1.0 / denom - 1)
    cA, gAv = fhs_chern(meff_A + CX + CY)
    CA.append(cA); gA.append(gAv)

    # ── Design B: uniform BZ-averaged ────────────────────────────
    if eps < eps_B_max:
        meff_B = m_base / np.sqrt(max(1 - eps**2, 1e-14))
    else:
        meff_B = -1e6                            # past discriminant
    cB, gBv = fhs_chern(meff_B + CX + CY)
    CB.append(cB); gB.append(gBv)

    # print selected rows
    if abs(eps % 0.05) < 0.006 or eps < 0.006:
        mB_s = f"{meff_B:+8.3f}" if eps < eps_B_max else "   -∞   "
        print(f"{eps:6.2f} │ {cA:+3d} {gAv:7.4f} {meff_A.mean():+8.4f}"
              f" │ {cB:+3d} {gBv:7.4f} {mB_s}")

CA = np.array(CA); gA = np.array(gA)
CB = np.array(CB); gB = np.array(gB)

# ── Transition summary ────────────────────────────────────────────
print(f"\n{'═' * 56}")
print("Design A transitions:")
for i in np.where(np.diff(CA) != 0)[0]:
    print(f"  ε ∈ ({eps_all[i]:.2f}, {eps_all[i+1]:.2f}):  "
          f"C = {CA[i]:+d} → {CA[i+1]:+d}")

print(f"\nDesign B — predicted ε_c = {eps_c:.4f}")
for i in np.where(np.diff(CB) != 0)[0]:
    print(f"  ε ∈ ({eps_all[i]:.2f}, {eps_all[i+1]:.2f}):  "
          f"C = {CB[i]:+d} → {CB[i+1]:+d}")

# ── Plot ──────────────────────────────────────────────────────────
if not HAVE_MPL:
    print("\n(install matplotlib for the figure)")
    sys.exit(0)

fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharex=True,
                         gridspec_kw={"height_ratios": [2.4, 1]})

# ─── Top panel: Chern number ──────────────────────────────────────
ax = axes[0]
ax.step(eps_all, CA, where="mid", color="#1f77b4", lw=2.5,
        label=r"(A) $k$-dependent $\pi_a(k_x)=\pi(1+\varepsilon\cos k_x)$"
              "  [re-entrant]")

mask = eps_all < eps_B_max
ax.step(eps_all[mask], CB[:mask.sum()], where="mid",
        color="#d62728", lw=2.5,
        label=r"(B) uniform $m_{\rm eff}=m_0/\sqrt{1-\varepsilon^2}$"
              "  [single jump]")

ax.axvline(eps_c, color="#2ca02c", ls=":", lw=1.5, alpha=0.8)
ax.text(eps_c + 0.015, 1.15,
        r"$\varepsilon_c=\frac{\sqrt{3}}{2}$",
        fontsize=13, color="#2ca02c", fontweight="bold")

# Re-entrant window annotation (Design A)
dA = np.diff(CA)
t_idx = np.where(dA != 0)[0]
if len(t_idx) >= 2:
    e1, e2 = eps_all[t_idx[0]+1], eps_all[t_idx[1]]
    ax.axvspan(e1, e2, alpha=0.10, color="#1f77b4")
    ax.annotate("re-entrant\nwindow", xy=((e1+e2)/2, 0),
                fontsize=8, color="#1f77b4", ha="center",
                xytext=((e1+e2)/2, 0.8),
                arrowprops=dict(arrowstyle="->", color="#1f77b4", lw=1.2))

ax.axhline(0, color="gray", lw=0.4, ls="--")
ax.set_ylabel("Chern number  $C$", fontsize=12)
ax.set_yticks([-1, 0, 1])
ax.set_ylim(-1.7, 1.7)
ax.legend(fontsize=9.5, loc="upper right")
ax.set_title(
    r"$\pi_a$-Scaled QWZ Phase Diagram  —  FHS Lattice Chern "
    rf"$(N\!=\!{N},\; m_0\!=\!{m_base:g},\; \beta\!=\!{beta:g})$",
    fontsize=13, pad=10)

# Phase labels
ax.text(0.35, -1.45, r"$C\!=\!-1$", fontsize=10, color="#666",
        ha="center", style="italic")
ax.text(1.15, -1.45, r"$C\!=\!0$", fontsize=10, color="#666",
        ha="center", style="italic")

# ─── Bottom panel: min gap ────────────────────────────────────────
ax = axes[1]
ax.plot(eps_all, gA, color="#1f77b4", lw=1.5, alpha=0.7,
        label="(A) min gap")
ax.plot(eps_all[mask], gB[:mask.sum()], color="#d62728", lw=1.5,
        alpha=0.7, label="(B) min gap")
ax.axvline(eps_c, color="#2ca02c", ls=":", lw=1.5, alpha=0.7)
ax.set_ylabel("min spectral gap", fontsize=12)
ax.set_xlabel(r"deformation $\varepsilon$", fontsize=13)
ax.set_xlim(0, 1.3)
ax.set_ylim(0, None)
ax.legend(fontsize=9, loc="upper right")

plt.tight_layout()
out = "docs/assets/pia_qwz_phase_diagram.png"
plt.savefig(out, dpi=180, bbox_inches="tight")
print(f"\nFigure saved → {out}")
