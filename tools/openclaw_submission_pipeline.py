from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True, cwd=str(REPO))


def main() -> None:
    ap = argparse.ArgumentParser(description="OpenClaw end-to-end submission pipeline")
    ap.add_argument("--submission-id", required=True)
    ap.add_argument("--score", action="store_true", help="Score pending submission first")
    ap.add_argument("--rescore", action="store_true", help="Allow rescoring already promoted submissions")
    ap.add_argument("--sync-equations", action="store_true", help="Sync rescored values back into equations.json")
    ap.add_argument("--promote", action="store_true", help="Promote after scoring (or existing review)")
    ap.add_argument("--threshold", type=int, default=65, help="Used by score step for ready/needs-review status")
    ap.add_argument("--publish-chain", action="store_true", help="Export and publish certificate records")
    ap.add_argument("--node-url", default="http://127.0.0.1:5000")
    ap.add_argument("--signer-file", default="D:/coins2/Adaptive-Curvature-Coin/wallet.json")
    args = ap.parse_args()

    py = sys.executable

    if args.score:
        score_cmd = [
            py,
            "tools/score_submission.py",
            "--submission-id",
            args.submission_id,
            "--mark-ready-threshold",
            str(args.threshold),
        ]
        if args.rescore:
            score_cmd.append("--include-promoted")
        if args.sync_equations:
            score_cmd.append("--sync-equations")
        _run(score_cmd)

    if args.promote:
        _run([
            py,
            "tools/promote_submission.py",
            "--submission-id",
            args.submission_id,
            "--from-review",
        ])

        _run([py, "tools/generate_leaderboard.py"])
        _run([py, "tools/build_site.py"])

    if args.publish_chain:
        _run([py, "tools/export_equation_certificates.py"])
        _run(
            [
                py,
                "tools/register_equation_certificates.py",
                "--node-url",
                args.node_url,
                "--signer-file",
                args.signer_file,
                "--mine",
            ]
        )
        _run([py, "tools/build_site.py"])


if __name__ == "__main__":
    main()
