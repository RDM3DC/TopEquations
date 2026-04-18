"""Stability probe: measure the Kirchhoff-Lipschitz constant kappa.

For an ARP-style equation entry, this generates a representative random
Kirchhoff network, measures kappa empirically, and reports whether the
sufficient contraction condition mu_G > kappa holds.

Implements the falsifier defined in:
  eq-kirchhoff-lipschitz-sufficient-condition-for-arp-contrac
  eq-arp-kirchhoff-coupled-lyapunov-contraction-theorem

Usage:
  python tools/measure_kappa.py --equation-id eq-paper1-arp-reinforce-decay
  python tools/measure_kappa.py --mu 0.1 --alpha 0.5 --n 12 --seed 42
  python tools/measure_kappa.py --all-arp           # scan all ARP-tagged entries
  python tools/measure_kappa.py --write-certificates # update equations.json
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
EQUATIONS_JSON = REPO / "data" / "equations.json"
CERT_JSON = REPO / "data" / "certificates" / "kappa_certificates.json"

# Reuse the simulation primitives.
import sys
sys.path.insert(0, str(REPO / "tools"))
from arp_kirchhoff_sim import (  # noqa: E402
    edge_currents,
    initial_conductance,
    measure_kappa,
    random_graph,
)

# Heuristic: which equation IDs are ARP-conductance-style and benefit from kappa?
ARP_TAG_KEYWORDS = (
    "arp", "conductance", "reinforce", "decay-memory", "kirchhoff",
)


def _is_arp(entry: dict) -> bool:
    text = " ".join([
        str(entry.get("id", "")),
        str(entry.get("name", "")),
        str(entry.get("description", "")),
    ]).lower()
    return any(k in text for k in ARP_TAG_KEYWORDS)


def probe_network(n: int, p: float, mu_G: float, alpha_G: float, seed: int,
                  n_probes: int = 128, eps: float = 1e-3) -> dict:
    """Generate a random Kirchhoff network and measure kappa."""
    rng = np.random.default_rng(seed)
    mask = random_graph(n, p, rng)
    while not np.all(mask.sum(axis=1) > 0):
        mask = random_graph(n, p, rng)
    G = initial_conductance(mask, rng)
    s = rng.normal(size=n)
    s = s - s.mean()
    kappa = measure_kappa(G, s, rng, n_probes=n_probes, eps=eps)
    holds = bool(mu_G > kappa)
    margin = float(mu_G - kappa)
    return {
        "n_nodes": n,
        "n_edges": int(mask.sum() / 2),
        "edge_density": p,
        "mu_G": mu_G,
        "alpha_G": alpha_G,
        "seed": seed,
        "n_probes": n_probes,
        "epsilon": eps,
        "kappa_measured": float(kappa),
        "mu_G_minus_kappa": margin,
        "contraction_holds": holds,
        "verdict": "PASS" if holds else "FAIL_SUFFICIENT_CONDITION",
    }


def write_certificate(eq_id: str, cert: dict) -> None:
    CERT_JSON.parent.mkdir(parents=True, exist_ok=True)
    if CERT_JSON.exists():
        store = json.loads(CERT_JSON.read_text(encoding="utf-8"))
    else:
        store = {"certificates": {}}
    store["certificates"][eq_id] = {
        **cert,
        "computedAt": datetime.now().isoformat(timespec="seconds"),
        "falsifierRef": "eq-kirchhoff-lipschitz-sufficient-condition-for-arp-contrac",
    }
    CERT_JSON.write_text(
        json.dumps(store, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--equation-id", type=str, default=None)
    ap.add_argument("--all-arp", action="store_true", help="scan all ARP-tagged entries")
    ap.add_argument("--n", type=int, default=12)
    ap.add_argument("--p", type=float, default=0.35)
    ap.add_argument("--mu", type=float, default=0.025, dest="mu_G")
    ap.add_argument("--alpha", type=float, default=0.5, dest="alpha_G")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--probes", type=int, default=128)
    ap.add_argument("--write-certificates", action="store_true",
                    help="persist kappa certificates to data/certificates/kappa_certificates.json")
    args = ap.parse_args()

    targets: list[str] = []
    if args.all_arp:
        data = json.loads(EQUATIONS_JSON.read_text(encoding="utf-8"))
        targets = [e["id"] for e in data.get("entries", []) if _is_arp(e) and e.get("id")]
    elif args.equation_id:
        targets = [args.equation_id]
    else:
        targets = ["(adhoc)"]

    print(f"--- Kirchhoff-Lipschitz kappa probe ({len(targets)} target(s)) ---")
    pass_count = 0
    fail_count = 0
    for eq_id in targets:
        cert = probe_network(
            n=args.n, p=args.p, mu_G=args.mu_G, alpha_G=args.alpha_G,
            seed=args.seed, n_probes=args.probes,
        )
        verdict = cert["verdict"]
        kappa = cert["kappa_measured"]
        margin = cert["mu_G_minus_kappa"]
        print(f"  {eq_id:<60s} kappa={kappa:.4f}  mu-kappa={margin:+.4f}  {verdict}")
        if cert["contraction_holds"]:
            pass_count += 1
        else:
            fail_count += 1
        if args.write_certificates and eq_id != "(adhoc)":
            write_certificate(eq_id, cert)

    print(f"--- summary: {pass_count} PASS, {fail_count} FAIL_SUFFICIENT_CONDITION ---")
    if args.write_certificates:
        print(f"certificates written: {CERT_JSON}")


if __name__ == "__main__":
    main()
