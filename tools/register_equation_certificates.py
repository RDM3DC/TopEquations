from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib import error, request

from ecdsa import SECP256k1, SigningKey


def sign_transaction(private_key_hex: str, tx_data: dict) -> str:
    message = json.dumps(tx_data, sort_keys=True)
    sk = SigningKey.from_string(bytes.fromhex(private_key_hex), curve=SECP256k1)
    sig = sk.sign(message.encode("utf-8"))
    return sig.hex()


def post_json(url: str, payload: dict, timeout: int = 8) -> tuple[int, str]:
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            return int(resp.status), resp.read().decode("utf-8")
    except error.HTTPError as ex:
        return int(ex.code), ex.read().decode("utf-8")


def get_json(url: str, timeout: int = 8) -> tuple[int, str]:
    req = request.Request(url, method="GET")
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            return int(resp.status), resp.read().decode("utf-8")
    except error.HTTPError as ex:
        return int(ex.code), ex.read().decode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Register TopEquations certificates on chain")
    parser.add_argument("--cert-file", default="data/certificates/equation_certificates.json")
    parser.add_argument("--wallet-file", default="D:/coins2/Adaptive-Curvature-Coin/wallet.json")
    parser.add_argument("--node-url", default="http://127.0.0.1:5000")
    parser.add_argument("--limit", type=int, default=0, help="Optional max number of certificates to publish")
    parser.add_argument("--mine", action="store_true", help="Call /mine_block after publishing")
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[1]
    cert_path = (repo / args.cert_file).resolve()
    wallet_path = Path(args.wallet_file)

    cert_doc = json.loads(cert_path.read_text(encoding="utf-8"))
    wallet = json.loads(wallet_path.read_text(encoding="utf-8"))
    sender = wallet["public_key"]
    priv = wallet["private_key"]

    entries = cert_doc.get("entries", [])
    if args.limit and args.limit > 0:
        entries = entries[: args.limit]

    results = []
    for cert in entries:
        tx_data = {
            "sender": sender,
            "receiver": "equation-ledger",
            "amount": 0,
            "type": "equation_certificate",
            "equation_id": cert.get("token_id"),
            "metadata_hash": cert.get("metadata_hash"),
            "equation_hash": cert.get("equation_hash"),
            "score": cert.get("score"),
            "version": cert.get("version", 1),
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        signature = sign_transaction(priv, tx_data)
        payload = {"transaction": tx_data, "signature": signature}
        status, body = post_json(f"{args.node_url}/add_transaction", payload)
        results.append({"equation_id": cert.get("token_id"), "status": status, "response": body})

    mine_result = None
    if args.mine:
        status, body = get_json(f"{args.node_url}/mine_block")
        mine_result = {"status": status, "response": body}

    receipt = {
        "published_at": datetime.now(timezone.utc).isoformat(),
        "node_url": args.node_url,
        "cert_file": str(cert_path),
        "wallet_file": str(wallet_path),
        "count": len(results),
        "results": results,
        "mine_result": mine_result,
    }

    out = repo / "data" / "certificates" / "chain_publish_receipt.json"
    out.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(f"wrote: {out}")
    ok = sum(1 for r in results if r["status"] in (200, 201))
    print(f"published ok: {ok}/{len(results)}")
    if mine_result:
        print(f"mine status: {mine_result['status']}")


if __name__ == "__main__":
    main()
