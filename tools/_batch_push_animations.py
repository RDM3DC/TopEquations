"""Batch-push all animations to their corresponding equation repos.

This is a one-time script. It maps animation filenames to equation IDs
and uses push_to_equation_repo.push_file() for each.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Add tools/ to path so we can import push_to_equation_repo
sys.path.insert(0, str(Path(__file__).resolve().parent))
from push_to_equation_repo import push_file

ANIM_DIR = Path(r"C:\Users\RDM3D\clawdad42\1080p60")

# Map: animation filename -> equation ID
MAPPING = {
    # Derived / leaderboard equations
    "Eq1ARPCoreLaw.mp4": "core-arp-ode",
    "Eq2ARPRedshift.mp4": "eq-arp-redshift",
    "Eq3PhaseCoupledThreshold.mp4": "eq-arp-phase-critical-collapse",
    "Eq4PhaseLiftedComplexConductance.mp4": "eq-arp-phase-lifted-complex-conductance",
    "Eq5ARPLyapunov.mp4": "eq-arp-lyapunov-stability",
    "Eq6UnifiedDynamicConstants.mp4": "eq-dyn-constants-union",
    "Eq7CurveMemory137.mp4": "eq-curve-memory-137",
    "Eq8ShieldingMechanism.mp4": "eq-shield-mechanic-arp",
    "Eq9RedshiftARPSuperconductivity.mp4": "eq-redshift-arp-superc",
    "Eq10TempConductance.mp4": "eq-arp-temp-conductance",
    "BZPhaseLiftConductance.mp4": "eq-bz-phase-lifted-complex-conductance-entropy-gated",
    "BZAveragedRulerQWZ.mp4": "eq-qwz-bz-avg-ruler-mass",
    "AHCParityLocking.mp4": "eq-ahc-parity-flip-rate",
    "PiAModulatedQWZMass.mp4": "eq-qwz-pia-modulated-mass",
    "AdaptiveQWZReEntrance.mp4": "eq-qwz-pia-modulated-mass",  # second animation for same eq

    # Core equations
    "PhaseLiftExplained.mp4": "core-phase-lift",
    "PRRootExplained.mp4": "core-pr-root",
    "WindingParityExplained.mp4": "core-winding-parity",
    "HysteresisMemory.mp4": "core-reinforce-decay-memory",
    "ParityLockingBifurcation.mp4": "eq-parity-pump",
    "AdaptivePiGeometry.mp4": "eq-arp-gradient-flow-bridge",
    "APGP0CoreModel.mp4": "core-pi-a-dynamics",
}


def main() -> None:
    ok = 0
    fail = 0
    skip = 0

    for filename, eq_id in MAPPING.items():
        filepath = ANIM_DIR / filename
        if not filepath.exists():
            print(f"SKIP (missing): {filename}")
            skip += 1
            continue

        print(f"\n{'='*60}")
        print(f"Pushing {filename} -> {eq_id}/images/")
        print(f"{'='*60}")

        success = push_file(
            equation_id=eq_id,
            file_path=filepath,
            folder="images",
            commit_message=f"Add animation: {filename}",
        )
        if success:
            ok += 1
        else:
            fail += 1

    print(f"\n{'='*60}")
    print(f"DONE: {ok} pushed, {fail} failed, {skip} skipped")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
