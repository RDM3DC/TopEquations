"""Sweep the Kirchhoff collapse-identity caveat across affected ARP entries.

Adds a `caveats` field on entries that implicitly assume the equilibrium
proportionality |I_ij| = (mu/alpha) G_ij. References the falsifier entry
eq-kirchhoff-collapse-identity-falsifier and the supporting simulation.

Idempotent: re-running does not duplicate caveats.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
EQUATIONS_JSON = REPO / "data" / "equations.json"

AFFECTED = [
    "eq-paper1-arp-reinforce-decay",
    "eq-arp-temp-conductance",
    "eq-shield-mechanic-arp",
    "eq-hlatn-three-force-conductance-lock",
    "eq-bz-phase-lifted-complex-conductance-entropy-gated",
    "eq-adaptive-damped-harmonic-oscillator",
    "eq-entropy-gated-complex-conductance-arp-network",
    "eq-egatl-hlatn-threeforceconductance",
    "eq-phase-coupled-suppression-conductance-law",
]

CAVEAT = {
    "id": "kirchhoff-collapse-identity",
    "ref": "eq-kirchhoff-collapse-identity-falsifier",
    "addedDate": "2026-04-18",
    "note": (
        "Equilibrium derivations that invoke |I_ij| ~ (mu/alpha) G_ij are "
        "valid only in the frozen-current limit. Under honest Kirchhoff "
        "coupling the residual ||abs(I) - (mu/alpha) G||/||I|| saturates "
        "near 0.6 and never relaxes (12-node random graph, seed 42). "
        "See tools/arp_kirchhoff_sim.py and submissions/arp_lyapunov_and_falsifiability.md."
    ),
}


def main(dry_run: bool = False) -> None:
    data = json.loads(EQUATIONS_JSON.read_text(encoding="utf-8"))
    entries = data.get("entries", [])
    affected_set = set(AFFECTED)

    touched: list[str] = []
    skipped: list[str] = []
    not_found: list[str] = []

    found_ids = set()
    for entry in entries:
        eq_id = entry.get("id")
        if eq_id not in affected_set:
            continue
        found_ids.add(eq_id)
        existing = entry.get("caveats", [])
        if any(c.get("id") == CAVEAT["id"] for c in existing):
            skipped.append(eq_id)
            continue
        existing.append(CAVEAT)
        entry["caveats"] = existing
        touched.append(eq_id)

    not_found = sorted(affected_set - found_ids)

    if not dry_run and touched:
        EQUATIONS_JSON.write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    print(f"touched ({len(touched)}):")
    for t in touched:
        print(f"  + {t}")
    print(f"skipped (already had caveat) ({len(skipped)}):")
    for s in skipped:
        print(f"  = {s}")
    if not_found:
        print(f"not found in registry ({len(not_found)}):")
        for n in not_found:
            print(f"  ? {n}")


if __name__ == "__main__":
    import sys
    main(dry_run="--dry-run" in sys.argv)
