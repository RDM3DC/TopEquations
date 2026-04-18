"""ARP Kirchhoff-Coupled Lyapunov simulation.

Reference simulation backing three TopEquations registry entries:
  - eq-arp-kirchhoff-coupled-lyapunov-contraction-theorem
  - eq-kirchhoff-lipschitz-sufficient-condition-for-arp-contrac
  - eq-kirchhoff-collapse-identity-falsifier

Reproduces:
  - Predicted vs. measured Lyapunov decay rate (-2 mu_G).
  - Kirchhoff-Lipschitz constant kappa via random-perturbation probe.
  - Collapse-identity residual saturation under honest Kirchhoff coupling.

Usage:
  python tools/arp_kirchhoff_sim.py
  python tools/arp_kirchhoff_sim.py --csv data/arp_kirchhoff_sim.csv --seed 42

ARP dynamics:
    dG_ij/dt = alpha_G |I_ij| - mu_G G_ij
    I = L(G) s,  L = D - W,  W_ij = G_ij,  D = diag(sum_j G_ij)
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
DEFAULT_CSV = REPO / "data" / "arp_kirchhoff_sim.csv"


def random_graph(n: int, p: float, rng: np.random.Generator) -> np.ndarray:
    """Erdos-Renyi adjacency mask (symmetric, no self-loops)."""
    a = (rng.random((n, n)) < p).astype(float)
    a = np.triu(a, k=1)
    return a + a.T


def initial_conductance(mask: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    g = mask * rng.uniform(0.1, 1.0, size=mask.shape)
    g = np.triu(g, k=1)
    return g + g.T


def laplacian(G: np.ndarray) -> np.ndarray:
    return np.diag(G.sum(axis=1)) - G


def edge_currents(G: np.ndarray, s: np.ndarray) -> np.ndarray:
    """Symmetric edge-current matrix I_ij = G_ij * (V_i - V_j).

    V solves L(G) V = s with the first node grounded (V_0 = 0).
    """
    n = G.shape[0]
    L = laplacian(G)
    L_red = L[1:, 1:]
    s_red = s[1:]
    V = np.zeros(n)
    V[1:] = np.linalg.solve(L_red, s_red)
    diff = V[:, None] - V[None, :]
    return G * diff


def step(G: np.ndarray, s: np.ndarray, alpha_G: float, mu_G: float, dt: float,
         frozen_I: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray]:
    """One Euler step. Returns (G_next, I_used)."""
    if frozen_I is None:
        I = edge_currents(G, s)
    else:
        I = frozen_I
    G_next = G + dt * (alpha_G * np.abs(I) - mu_G * G)
    G_next = np.triu(G_next, k=1)
    G_next = G_next + G_next.T
    return G_next, I


def lyapunov(G: np.ndarray, G_star: np.ndarray, alpha_G: float) -> float:
    diff = G - G_star
    return float(np.sum(diff * diff) / (2.0 * alpha_G))


def measure_kappa(G: np.ndarray, s: np.ndarray, rng: np.random.Generator,
                  n_probes: int = 64, eps: float = 1e-3) -> float:
    """Empirical Kirchhoff-Lipschitz constant.

    kappa := sup_{delta G} ||abs(I(G+dG)) - abs(I(G))|| / ||dG||
    estimated by random symmetric perturbations.
    """
    I0 = np.abs(edge_currents(G, s))
    mask = (G > 0).astype(float)
    best = 0.0
    for _ in range(n_probes):
        dG = rng.normal(scale=eps, size=G.shape) * mask
        dG = np.triu(dG, k=1)
        dG = dG + dG.T
        I1 = np.abs(edge_currents(G + dG, s))
        num = np.linalg.norm(I1 - I0)
        den = np.linalg.norm(dG)
        if den > 0:
            best = max(best, num / den)
    return best


def collapse_residual(G: np.ndarray, I: np.ndarray, alpha_G: float, mu_G: float) -> float:
    """Normalized residual ||abs(I) - (mu_G/alpha_G) G|| / ||I||."""
    target = (mu_G / alpha_G) * G
    num = np.linalg.norm(np.abs(I) - target)
    den = np.linalg.norm(I)
    return float(num / den) if den > 0 else 0.0


def run(seed: int = 42, n: int = 12, p: float = 0.35, alpha_G: float = 0.5,
        mu_G: float = 0.025, dt: float = 0.01, steps: int = 2000,
        csv_path: Path = DEFAULT_CSV) -> dict:
    rng = np.random.default_rng(seed)
    mask = random_graph(n, p, rng)
    while not np.all(mask.sum(axis=1) > 0):  # ensure connected-ish
        mask = random_graph(n, p, rng)

    s = rng.normal(size=n)
    s = s - s.mean()  # zero-sum source (Kirchhoff balance)

    G = initial_conductance(mask, rng)

    # Frozen-current equilibrium G* uses fixed currents from initial state
    I0 = edge_currents(G, s)
    G_star = (alpha_G / mu_G) * np.abs(I0)
    G_star = G_star * mask  # respect topology

    # ---- Frozen-current run: should give exact dV/dt = -2 mu_G V ----
    G_frozen = G.copy()
    V_frozen = [lyapunov(G_frozen, G_star, alpha_G)]
    for _ in range(steps):
        G_frozen, _ = step(G_frozen, s, alpha_G, mu_G, dt, frozen_I=I0)
        V_frozen.append(lyapunov(G_frozen, G_star, alpha_G))
    V_frozen = np.array(V_frozen)

    # ---- Coupled run: honest Kirchhoff dynamics ----
    G_coup = G.copy()
    V_coup = [lyapunov(G_coup, G_star, alpha_G)]
    res_coup = []
    for _ in range(steps):
        G_coup, I = step(G_coup, s, alpha_G, mu_G, dt, frozen_I=None)
        V_coup.append(lyapunov(G_coup, G_star, alpha_G))
        res_coup.append(collapse_residual(G_coup, I, alpha_G, mu_G))
    V_coup = np.array(V_coup)
    res_coup = np.array(res_coup)

    # ---- Decay-rate fit on frozen run (skip first few transient samples) ----
    t = np.arange(len(V_frozen)) * dt
    mask_fit = (V_frozen > 1e-12)
    slope_frozen = np.polyfit(t[mask_fit], np.log(V_frozen[mask_fit]), 1)[0]

    # ---- kappa probe at initial state ----
    kappa = measure_kappa(G, s, rng, n_probes=128, eps=1e-3)

    # ---- Write CSV: time, V_frozen, V_coupled, collapse_residual ----
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["t", "V_frozen", "V_coupled", "collapse_residual"])
        for i in range(len(V_frozen)):
            res = res_coup[i - 1] if i > 0 else float("nan")
            w.writerow([f"{t[i]:.4f}", f"{V_frozen[i]:.8e}", f"{V_coup[i]:.8e}",
                       f"{res:.6f}" if not math.isnan(res) else "nan"])

    summary = {
        "n_nodes": n,
        "n_edges": int(mask.sum() / 2),
        "alpha_G": alpha_G,
        "mu_G": mu_G,
        "dt": dt,
        "steps": steps,
        "predicted_decay_rate": -2.0 * mu_G,
        "measured_decay_rate_frozen": float(slope_frozen),
        "kappa_measured": kappa,
        "mu_G_minus_kappa": mu_G - kappa,
        "contraction_holds": bool(mu_G > kappa),
        "collapse_residual_final": float(res_coup[-1]),
        "collapse_residual_mean_last200": float(res_coup[-200:].mean()),
        "csv": str(csv_path),
    }
    return summary


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--n", type=int, default=12)
    ap.add_argument("--p", type=float, default=0.35)
    ap.add_argument("--alpha", type=float, default=0.5, dest="alpha_G")
    ap.add_argument("--mu", type=float, default=0.025, dest="mu_G")
    ap.add_argument("--dt", type=float, default=0.01)
    ap.add_argument("--steps", type=int, default=2000)
    ap.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    args = ap.parse_args()

    summary = run(seed=args.seed, n=args.n, p=args.p, alpha_G=args.alpha_G,
                  mu_G=args.mu_G, dt=args.dt, steps=args.steps, csv_path=args.csv)
    print("--- ARP Kirchhoff-Lyapunov Simulation ---")
    for k, v in summary.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
