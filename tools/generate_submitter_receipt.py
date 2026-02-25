from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from ecdsa import SECP256k1, SigningKey

REPO = Path(__file__).resolve().parents[1]


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sign_receipt(private_key_hex: str, receipt_data: dict) -> str:
    message = json.dumps(receipt_data, sort_keys=True)
    sk = SigningKey.from_string(bytes.fromhex(private_key_hex), curve=SECP256k1)
    sig = sk.sign(message.encode("utf-8"))
    return sig.hex()


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate a signed receipt for a submitter")
    ap.add_argument("--submission-id", required=True)
    ap.add_argument("--signer-file", default="D:/coins2/Adaptive-Curvature-Coin/wallet.json")
    ap.add_argument("--out-dir", default="data/certificates/receipts")
    args = ap.parse_args()

    signer = json.loads(Path(args.signer_file).read_text(encoding="utf-8"))
    priv = signer["private_key"]
    pub = signer["public_key"]

    # Load submission data
    submissions_path = REPO / "data" / "submissions.json"
    submissions = json.loads(submissions_path.read_text(encoding="utf-8"))
    entry = None
    for e in submissions.get("entries", []):
        if str(e.get("submissionId")) == args.submission_id:
            entry = e
            break

    if not entry:
        raise SystemExit(f"submission not found: {args.submission_id}")

    # Load the matching equation (if promoted)
    equation_id = (entry.get("review") or {}).get("equationId", "")
    equation_hash = ""
    metadata_hash = ""
    if equation_id:
        certs_path = REPO / "data" / "certificates" / "equation_certificates.json"
        if certs_path.exists():
            certs = json.loads(certs_path.read_text(encoding="utf-8"))
            for c in certs.get("entries", []):
                if c.get("token_id") == equation_id:
                    equation_hash = c.get("equation_hash", "")
                    metadata_hash = c.get("metadata_hash", "")
                    break

    submitter = entry.get("submitter", "unknown")
    submitter_hash = sha256_text(submitter)

    receipt_data = {
        "type": "submitter_receipt",
        "submission_id": args.submission_id,
        "equation_id": equation_id,
        "submitter_hash": submitter_hash,
        "equation_hash": equation_hash,
        "metadata_hash": metadata_hash,
        "score": (entry.get("review") or {}).get("score", 0),
        "status": entry.get("status", ""),
        "issued_at": datetime.now(timezone.utc).isoformat(),
        "issuer_pubkey": pub,
    }

    signature = sign_receipt(priv, receipt_data)

    receipt = {
        **receipt_data,
        "signature": signature,
        "verify_note": (
            "To verify: hash the receipt_data fields (all keys except 'signature' and "
            "'verify_note') as sorted JSON, then check the ECDSA-SECP256k1 signature "
            "against issuer_pubkey."
        ),
    }

    out_dir = REPO / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"receipt-{args.submission_id}.json"
    out_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    print(f"receipt: {out_path}")
    print(f"submitter_hash: {submitter_hash}")
    print(f"equation_id: {equation_id}")
    print(f"signature: {signature[:24]}...")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
