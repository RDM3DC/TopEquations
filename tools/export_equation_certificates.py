from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main() -> None:
    repo = Path(__file__).resolve().parents[1]
    src_path = repo / "data" / "equations.json"
    out_path = repo / "data" / "certificates" / "equation_certificates.json"

    raw = src_path.read_text(encoding="utf-8")
    doc = json.loads(raw)

    entries = []
    for e in doc.get("entries", []):
        equation_latex = e.get("equationLatex", "")
        cert = {
            "token_id": e.get("id", ""),
            "name": e.get("name", ""),
            "equation_latex": equation_latex,
            "equation_hash": sha256_text(equation_latex),
            "score": e.get("score", 0),
            "scores": e.get("scores", {}),
            "novelty": (e.get("tags", {}) or {}).get("novelty", {}),
            "source": e.get("source", ""),
            "date": e.get("date", ""),
            "description": e.get("description", ""),
            "units": e.get("units", ""),
            "theory": e.get("theory", ""),
            "artifact_refs": {
                "animation": (e.get("animation", {}) or {}).get("path", ""),
                "image": (e.get("image", {}) or {}).get("path", ""),
            },
            "version": 1,
        }
        cert_blob = json.dumps(cert, sort_keys=True, separators=(",", ":"))
        cert["metadata_hash"] = sha256_text(cert_blob)
        entries.append(cert)

    payload = {
        "schema": "top-equations-certificate-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_file": str(src_path),
        "source_sha256": sha256_text(raw),
        "count": len(entries),
        "entries": entries,
    }

    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"wrote: {out_path}")
    print(f"certificates: {len(entries)}")


if __name__ == "__main__":
    main()
