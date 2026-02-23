#!/usr/bin/env python3
"""
Stochastic Langevin parity-lock simulation (Paper I Eq. 7)
==========================================================

Simulates the noise-robust extension of the Adler/RSJ + ARP system:

    dφ = [Δ − λG sinφ] dt + √(2D) dW          (Eq. 7)
    dG = [α G|sinφ| − μ(G − G₀)] dt            (Eq. 3)

Demonstrates:
  1. Sharp lock/slip transition at D=0 (λG sweep shows critical coupling).
  2. Rounded but detectable transition at finite D.
  3. The 1/π slip-regime asymptote (Eq. 6) survives noise.
  4. ARP self-locking: even weak initial coupling grows via reinforcement.

Outputs:
  - docs/assets/langevin_parity_lock.png (4-panel figure)
  - Console table of r_b vs coupling and noise.

Usage:
    python tools/langevin_parity_lock.py
"""

from __future__ import annotations

import math
import numpy as np
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


# ══════════════════════════════════════════════════════════════════
# Core SDE integrator (Euler–Maruyama)
# ══════════════════════════════════════════════════════════════════
def simulate(
    Delta: float = 1.0,
    lam: float = 1.0,
    G_fixed: float | None = None,
    alpha: float = 2.0,
    mu: float = 0.5,
    G0: float = 0.5,
    D: float = 0.0,
    T: float = 500.0,
    dt: float = 0.005,
    seed: int = 42,
) -> dict:
    """Run one trajectory of the Langevin parity-lock system.

    If G_fixed is set, G is held constant (pure Adler + noise, no ARP).
    Otherwise ARP dynamics evolve G.

    Returns dict with arrays: t, phi, G, b (parity), and scalar r_b.
    """
    rng = np.random.default_rng(seed)
    N = int(T / dt)
    sqrt_2D_dt = math.sqrt(2 * D * dt) if D > 0 else 0.0

    phi = np.zeros(N)
    G = np.zeros(N)

    phi[0] = 0.0
    G[0] = G_fixed if G_fixed is not None else G0

    for i in range(1, N):
        sp = math.sin(phi[i - 1])
        drift_phi = Delta - lam * G[i - 1] * sp
        noise = rng.standard_normal() * sqrt_2D_dt if D > 0 else 0.0
        phi[i] = phi[i - 1] + drift_phi * dt + noise

        if G_fixed is not None:
            G[i] = G_fixed
        else:
            activity = G[i - 1] * abs(sp)
            G[i] = G[i - 1] + (alpha * activity - mu * (G[i - 1] - G0)) * dt
            G[i] = max(G[i], 1e-6)

    # ── Parity from unwrapped phase (net winding) ────────────────
    w = np.floor((phi - phi[0]) / math.pi).astype(int)
    b = np.where(w % 2 == 0, 1, -1).astype(np.int8)

    # r_b: count *net* winding advances (monotonic π-crossings)
    # Use total |Δw| over the trajectory to match Eq. 5 definition
    dw = np.abs(np.diff(w))
    net_flips = int(dw.sum())
    r_b = net_flips / T if T > 0 else 0.0

    t = np.linspace(0, T, N)
    return {
        "t": t, "phi": phi, "G": G, "b": b,
        "r_b": r_b, "net_flips": net_flips,
        "params": {"Delta": Delta, "lam": lam, "G_fixed": G_fixed,
                   "alpha": alpha, "mu": mu, "G0": G0, "D": D,
                   "T": T, "dt": dt},
    }


# ══════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════
def main() -> None:
    Delta = 1.0
    T = 300.0
    dt = 0.005
    r_b_1pi = abs(Delta) / math.pi  # Eq. 6: 0.3183

    print("Langevin Parity-Lock Simulation (Paper I Eq. 7)")
    print("=" * 65)
    print(f"Δ = {Delta},  T = {T},  dt = {dt}")
    print(f"Theoretical slip asymptote |Δ|/π = {r_b_1pi:.4f}\n")

    # ─────────────────────────────────────────────────────────────
    # PART A: Pure Adler sweep (fixed G, no ARP) — shows the
    #         sharp lock/slip transition and 1/π asymptote.
    # ─────────────────────────────────────────────────────────────
    lam_G_values = np.arange(0.0, 2.01, 0.1)  # effective coupling λG
    D_levels = [0.0, 0.02, 0.05, 0.15]

    print("Part A: Fixed-G Adler sweep (no ARP dynamics)")
    print(f"{'λG':>6s}", end="")
    for D in D_levels:
        print(f"  {'D='+str(D):>10s}", end="")
    print()
    print("─" * (6 + 12 * len(D_levels)))

    sweep_data = {D: [] for D in D_levels}  # λG → r_b

    for lG in lam_G_values:
        line = f"{lG:6.2f}"
        for D in D_levels:
            # lam=1, G_fixed=lG → effective coupling = lG
            res = simulate(Delta=Delta, lam=1.0, G_fixed=lG,
                           D=D, T=T, dt=dt, seed=42)
            sweep_data[D].append(res["r_b"])
            line += f"  {res['r_b']:10.4f}"
        print(line)

    print(f"\n|Δ|/π = {r_b_1pi:.4f}  (slip floor)")
    print(f"Lock threshold (D=0): λG_c = |Δ| = {abs(Delta):.1f}\n")

    # ─────────────────────────────────────────────────────────────
    # PART B: ARP self-locking demo — even weak λ locks via G growth
    # ─────────────────────────────────────────────────────────────
    print("Part B: ARP self-locking (G evolves, α=2.0, μ=0.5, G₀=0.5)")
    for lam_val in [0.3, 1.0, 3.0]:
        for D in [0.0, 0.05]:
            res = simulate(Delta=Delta, lam=lam_val, G_fixed=None,
                           alpha=2.0, mu=0.5, G0=0.5,
                           D=D, T=T, dt=dt, seed=42)
            status = "LOCK" if res["r_b"] < 0.05 else "SLIP"
            print(f"  λ={lam_val:.1f}  D={D:.2f}  → r_b={res['r_b']:.4f}"
                  f"  G_final={res['G'][-1]:.3f}  [{status}]")
    print()

    # ─────────────────────────────────────────────────────────────
    # PART C: Detailed traces for figure
    # ─────────────────────────────────────────────────────────────
    T_trace = 100.0
    # Slip (below threshold)
    trace_slip_clean = simulate(Delta=1.0, lam=1.0, G_fixed=0.5,
                                D=0.0, T=T_trace, dt=dt, seed=42)
    trace_slip_noisy = simulate(Delta=1.0, lam=1.0, G_fixed=0.5,
                                D=0.05, T=T_trace, dt=dt, seed=42)
    # Lock (above threshold)
    trace_lock_clean = simulate(Delta=1.0, lam=1.0, G_fixed=2.0,
                                D=0.0, T=T_trace, dt=dt, seed=42)
    trace_lock_noisy = simulate(Delta=1.0, lam=1.0, G_fixed=2.0,
                                D=0.05, T=T_trace, dt=dt, seed=42)
    # ARP self-lock
    trace_arp = simulate(Delta=1.0, lam=0.5, G_fixed=None,
                         alpha=2.0, mu=0.5, G0=0.5,
                         D=0.02, T=T_trace, dt=dt, seed=42)

    # ─────────────────────────────────────────────────────────────
    # Plot
    # ─────────────────────────────────────────────────────────────
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # ── Panel (0,0): Phase trajectories ──────────────────────
        ax = axes[0, 0]
        tt = trace_slip_clean["t"]
        ax.plot(tt, trace_slip_clean["phi"], color="#2ca02c", lw=1,
                alpha=0.9, label="Slip (λG=0.5, D=0)")
        ax.plot(tt, trace_slip_noisy["phi"], color="#98df8a", lw=0.7,
                alpha=0.7, label="Slip (λG=0.5, D=0.05)")
        ax.plot(tt, trace_lock_clean["phi"], color="#1f77b4", lw=1,
                alpha=0.9, label="Lock (λG=2.0, D=0)")
        ax.plot(tt, trace_lock_noisy["phi"], color="#aec7e8", lw=0.7,
                alpha=0.7, label="Lock (λG=2.0, D=0.05)")
        ax.set_ylabel(r"$\phi(t)$", fontsize=12)
        ax.set_xlabel("Time", fontsize=11)
        ax.set_title("Phase trajectories", fontsize=12, fontweight="bold")
        ax.legend(fontsize=8, loc="upper left")

        # ── Panel (0,1): Parity b(t) ────────────────────────────
        ax = axes[0, 1]
        step = max(1, len(tt) // 1500)
        ax.step(tt[::step], trace_slip_clean["b"][::step],
                where="mid", color="#2ca02c", lw=0.8, alpha=0.9,
                label="Slip D=0")
        ax.step(tt[::step], trace_lock_clean["b"][::step],
                where="mid", color="#1f77b4", lw=0.8, alpha=0.9,
                label="Lock D=0")
        ax.step(tt[::step], trace_lock_noisy["b"][::step],
                where="mid", color="#aec7e8", lw=0.8, alpha=0.7,
                label="Lock D=0.05")
        ax.set_ylabel(r"Parity $b(t) = (-1)^{\lfloor\phi/\pi\rfloor}$",
                      fontsize=11)
        ax.set_xlabel("Time", fontsize=11)
        ax.set_yticks([-1, 1])
        ax.set_title("Parity signal", fontsize=12, fontweight="bold")
        ax.legend(fontsize=8, loc="lower right")

        # ── Panel (1,0): r_b vs λG sweep ────────────────────────
        ax = axes[1, 0]
        colors = ["#d62728", "#ff7f0e", "#9467bd", "#8c564b"]
        for idx, D in enumerate(D_levels):
            label = f"D = {D}" if D > 0 else "D = 0 (sharp)"
            ax.plot(lam_G_values, sweep_data[D], "o-",
                    color=colors[idx], lw=2, markersize=4, label=label)
        ax.axhline(r_b_1pi, color="gray", ls="--", lw=1.5,
                   label=r"$|\Delta|/\pi \approx 0.318$")
        ax.axvline(abs(Delta), color="gray", ls=":", lw=1,
                   alpha=0.5, label=r"$\lambda G_c = |\Delta|$")
        ax.set_xlabel(r"Coupling strength $\lambda G$", fontsize=12)
        ax.set_ylabel(r"Flip rate $r_b$", fontsize=12)
        ax.set_title(r"Lock/slip transition: $r_b$ vs $\lambda G$",
                     fontsize=12, fontweight="bold")
        ax.legend(fontsize=8)
        ax.set_ylim(bottom=-0.02)

        # ── Panel (1,1): ARP self-lock (G grows → captures) ─────
        ax = axes[1, 1]
        tt_a = trace_arp["t"]
        ax.plot(tt_a, trace_arp["G"], color="#d62728", lw=1.5,
                label=r"$G(t)$ (ARP, $\lambda$=0.5)")
        ax.axhline(abs(Delta) / 0.5, color="gray", ls="--", lw=1,
                   alpha=0.6, label=r"$G_c = |\Delta|/\lambda$")
        ax.set_ylabel("Coupling $G(t)$", fontsize=12, color="#d62728")
        ax.set_xlabel("Time", fontsize=11)
        ax.set_title("ARP self-locking: $G$ grows to lock threshold",
                     fontsize=12, fontweight="bold")
        ax.legend(fontsize=9, loc="center right")
        ax2 = ax.twinx()
        ax2.plot(tt_a, trace_arp["phi"], color="#1f77b4", lw=0.6,
                 alpha=0.6)
        ax2.set_ylabel(r"$\phi(t)$", fontsize=11, color="#1f77b4")

        plt.suptitle(
            r"Paper I Eq. 7: $\dot\phi = \Delta - \lambda G\sin\phi"
            r" + \sqrt{2D}\,\eta(t)$   +   ARP: $\dot G = \alpha G"
            r"|\sin\phi| - \mu(G-G_0)$",
            fontsize=13, fontweight="bold", y=1.02)
        plt.tight_layout()

        out_dir = REPO / "docs" / "assets"
        out_dir.mkdir(parents=True, exist_ok=True)
        out = out_dir / "langevin_parity_lock.png"
        fig.savefig(str(out), dpi=180, bbox_inches="tight")
        print(f"Figure saved → {out}")

    except ImportError:
        print("(install matplotlib for figure)")


if __name__ == "__main__":
    main()
