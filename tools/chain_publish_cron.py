"""Local chain publish cron — picks up unpublished certificates and publishes them.

Run this on a schedule (e.g., Windows Task Scheduler every hour) on the machine
where the blockchain node is running.

Usage:
    python tools/chain_publish_cron.py
    python tools/chain_publish_cron.py --node-url http://127.0.0.1:5000 --signer-file D:/coins2/Adaptive-Curvature-Coin/wallet.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def main() -> None:
    ap = argparse.ArgumentParser(description="Local chain publish cron")
    ap.add_argument("--node-url", default="http://127.0.0.1:5000")
    ap.add_argument("--signer-file", default="D:/coins2/Adaptive-Curvature-Coin/wallet.json")
    args = ap.parse_args()

    cert_path = REPO / "data" / "certificates" / "equation_certificates.json"
    receipt_path = REPO / "data" / "certificates" / "chain_publish_receipt.json"
    eq_path = REPO / "data" / "equations.json"

    if not cert_path.exists():
        print("No certificate file found, nothing to publish.")
        return

    # Check if certs are newer than last publish receipt
    if receipt_path.exists():
        import os
        if os.path.getmtime(str(cert_path)) <= os.path.getmtime(str(receipt_path)):
            print("Certificates already published (cert file not newer than receipt). Skipping.")
            return

    # Re-export certificates first to pick up any new equations
    print("Exporting certificates...")
    subprocess.run(
        [sys.executable, "tools/export_equation_certificates.py"],
        check=True,
        cwd=str(REPO),
    )

    # Publish to chain
    print("Publishing to chain...")
    subprocess.run(
        [
            sys.executable, "tools/register_equation_certificates.py",
            "--node-url", args.node_url,
            "--signer-file", args.signer_file,
            "--mine",
        ],
        check=True,
        cwd=str(REPO),
    )

    # Generate receipts for any promoted submissions that don't have one yet
    subs = json.loads((REPO / "data" / "submissions.json").read_text(encoding="utf-8"))
    receipts_dir = REPO / "data" / "certificates" / "receipts"
    for entry in subs.get("entries", []):
        if entry.get("status") != "promoted":
            continue
        sid = entry.get("submissionId", "")
        receipt_file = receipts_dir / f"receipt-{sid}.json"
        if receipt_file.exists():
            continue
        print(f"Generating receipt for {sid}...")
        subprocess.run(
            [
                sys.executable, "tools/generate_submitter_receipt.py",
                "--submission-id", sid,
                "--signer-file", args.signer_file,
            ],
            check=True,
            cwd=str(REPO),
        )

    # Git commit and push if there are changes
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, cwd=str(REPO),
    )
    if result.stdout.strip():
        print("Committing chain publish results...")
        subprocess.run(["git", "add", "-A"], check=True, cwd=str(REPO))
        subprocess.run(
            ["git", "commit", "-m", "Chain publish cron: certificates published"],
            check=True, cwd=str(REPO),
        )
        subprocess.run(["git", "push"], check=True, cwd=str(REPO))
        print("Pushed.")
    else:
        print("No changes to commit.")

    print("Done.")


if __name__ == "__main__":
    main()
