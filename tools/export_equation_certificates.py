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
    core_path = repo / "data" / "core.json"
    famous_path = repo / "data" / "famous_equations.json"
    out_path = repo / "data" / "certificates" / "equation_certificates.json"

    raw = src_path.read_text(encoding="utf-8")
    doc = json.loads(raw)

    # Also include core equations on the chain
    core_raw = ""
    core_entries: list[dict] = []
    if core_path.exists():
        core_raw = core_path.read_text(encoding="utf-8")
        core_doc = json.loads(core_raw)
        core_entries = list(core_doc.get("entries", []))

    # Also include famous equations on the chain
    famous_raw = ""
    famous_entries: list[dict] = []
    if famous_path.exists():
        famous_raw = famous_path.read_text(encoding="utf-8")
        famous_doc = json.loads(famous_raw)
        famous_entries = list(famous_doc.get("entries", []))

    entries = []

    # Core equations first (tagged as tier: core)
    for e in core_entries:
        equation_latex = e.get("equationLatex", "")
        t = e.get("tractability", 0)
        p = e.get("plausibility", 0)
        v = e.get("validation", 0)
        a = e.get("artifactCompleteness", 0)
        score = e.get("score", int(round(((t + p + v + a) / 70.0) * 100.0)))
        cert = {
            "token_id": e.get("id", ""),
            "name": e.get("name", ""),
            "equation_latex": equation_latex,
            "equation_hash": sha256_text(equation_latex),
            "score": score,
            "scores": {
                "tractability": t,
                "plausibility": p,
                "validation": v,
                "artifactCompleteness": a,
            },
            "novelty": {"score": e.get("novelty", 0), "date": "core"},
            "source": e.get("source", ""),
            "date": "core",
            "description": e.get("description", ""),
            "units": e.get("units", ""),
            "theory": e.get("theory", ""),
            "tier": "core",
            "artifact_refs": {
                "animation": (e.get("animation", {}) if isinstance(e.get("animation"), dict) else {}).get("path", ""),
                "image": (e.get("image", {}) if isinstance(e.get("image"), dict) else {}).get("path", ""),
            },
            "version": 1,
        }
        cert_blob = json.dumps(cert, sort_keys=True, separators=(",", ":"))
        cert["metadata_hash"] = sha256_text(cert_blob)
        entries.append(cert)

    # Derived equations (tagged as tier: derived)
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
            "tier": "derived",
            "version": 1,
        }
        cert_blob = json.dumps(cert, sort_keys=True, separators=(",", ":"))
        cert["metadata_hash"] = sha256_text(cert_blob)
        entries.append(cert)

    # Famous equations (tagged as tier: famous)
    for e in famous_entries:
        equation_latex = e.get("equationLatex", "")
        t = e.get("tractability", 0)
        p = e.get("plausibility", 0)
        v = e.get("validation", 0)
        a = e.get("artifactCompleteness", 0)
        score = int(round(((t + p + v + a) / 70.0) * 100.0))
        cert = {
            "token_id": e.get("id", ""),
            "name": e.get("name", ""),
            "equation_latex": equation_latex,
            "equation_hash": sha256_text(equation_latex),
            "score": score,
            "scores": {
                "tractability": t,
                "plausibility": p,
                "validation": v,
                "artifactCompleteness": a,
            },
            "novelty": {"score": e.get("novelty", 0), "date": "famous"},
            "source": "famous-adjusted",
            "date": "famous",
            "description": e.get("description", ""),
            "units": e.get("units", ""),
            "theory": e.get("theory", ""),
            "tier": "famous",
            "coreRefs": e.get("coreRefs", []),
            "version": 1,
        }
        cert_blob = json.dumps(cert, sort_keys=True, separators=(",", ":"))
        cert["metadata_hash"] = sha256_text(cert_blob)
        entries.append(cert)

    payload = {
        "schema": "top-equations-certificate-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_file": str(src_path),
        "source_sha256": sha256_text(raw + core_raw + famous_raw),
        "count": len(entries),
        "entries": entries,
    }

    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"wrote: {out_path}")
    print(f"certificates: {len(entries)}")


if __name__ == "__main__":
    main()
