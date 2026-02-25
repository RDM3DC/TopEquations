"""Reconciliation tool — checks consistency across equations, certificates, chain, and site.

Runs deterministically. Reports drift as structured JSON.
Exit code 0 = all clear, exit code 1 = drift detected.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _load(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    issues: list[dict] = []

    equations = _load(REPO / "data" / "equations.json")
    core = _load(REPO / "data" / "core.json")
    famous = _load(REPO / "data" / "famous_equations.json")
    certs = _load(REPO / "data" / "certificates" / "equation_certificates.json")
    submissions = _load(REPO / "data" / "submissions.json")

    # 1. All equations should have matching certificates
    eq_ids = {e.get("id") for e in equations.get("entries", [])}
    core_ids = {e.get("id") for e in core.get("entries", [])}
    famous_ids = {e.get("id") for e in famous.get("entries", [])}
    all_eq_ids = eq_ids | core_ids | famous_ids

    cert_ids = {c.get("token_id") for c in certs.get("entries", [])}
    missing_certs = all_eq_ids - cert_ids
    if missing_certs:
        issues.append({
            "type": "missing_certificates",
            "severity": "warn",
            "message": f"{len(missing_certs)} equations have no certificate",
            "ids": sorted(missing_certs),
        })

    extra_certs = cert_ids - all_eq_ids
    if extra_certs:
        issues.append({
            "type": "orphan_certificates",
            "severity": "info",
            "message": f"{len(extra_certs)} certificates have no matching equation",
            "ids": sorted(extra_certs),
        })

    # 2. All promoted submissions should have matching equations
    promoted_eq_ids = set()
    for e in submissions.get("entries", []):
        if e.get("status") == "promoted":
            eq_id = (e.get("review") or {}).get("equationId", "")
            if eq_id:
                promoted_eq_ids.add(eq_id)
    missing_promoted = promoted_eq_ids - eq_ids
    if missing_promoted:
        issues.append({
            "type": "promoted_but_missing",
            "severity": "error",
            "message": f"{len(missing_promoted)} promoted submissions missing from equations.json",
            "ids": sorted(missing_promoted),
        })

    # 3. Site freshness — check if docs/leaderboard.html is older than equations.json
    eq_path = REPO / "data" / "equations.json"
    lb_path = REPO / "docs" / "leaderboard.html"
    if eq_path.exists() and lb_path.exists():
        if os.path.getmtime(str(eq_path)) > os.path.getmtime(str(lb_path)):
            issues.append({
                "type": "stale_site",
                "severity": "warn",
                "message": "docs/leaderboard.html is older than data/equations.json",
            })

    # 4. Certificate freshness
    cert_path = REPO / "data" / "certificates" / "equation_certificates.json"
    if eq_path.exists() and cert_path.exists():
        if os.path.getmtime(str(eq_path)) > os.path.getmtime(str(cert_path)):
            issues.append({
                "type": "stale_certificates",
                "severity": "warn",
                "message": "equation_certificates.json is older than equations.json",
            })

    # 5. Pending submissions count
    pending = [e for e in submissions.get("entries", []) if e.get("status") in ("pending", "needs-review")]
    if pending:
        issues.append({
            "type": "pending_submissions",
            "severity": "info",
            "message": f"{len(pending)} submissions awaiting review",
            "ids": [e.get("submissionId") for e in pending],
        })

    # 6. Check all certs have submitter_hash
    certs_without_hash = [c.get("token_id") for c in certs.get("entries", []) if not c.get("submitter_hash")]
    if certs_without_hash:
        issues.append({
            "type": "missing_submitter_hash",
            "severity": "warn",
            "message": f"{len(certs_without_hash)} certificates missing submitter_hash",
            "ids": sorted(certs_without_hash),
        })

    # Output
    report = {
        "status": "CLEAN" if not any(i["severity"] in ("error", "warn") for i in issues) else "DRIFT",
        "issue_count": len(issues),
        "issues": issues,
    }

    print(json.dumps(report, indent=2))

    if report["status"] == "DRIFT":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
