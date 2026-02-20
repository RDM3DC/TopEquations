"""Harvest equations from local RDM3DC repos into a deduped registry.

Output is written to: data/harvest/equation_harvest.json

This is intentionally conservative (strict-ish filters) to reduce noise.
"""

from __future__ import annotations

import json
import os
import re
import hashlib
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

ROOT_REPOS = Path(r"C:\Users\RDM3D\clawdad42")
OUT_PATH = Path(__file__).resolve().parents[1] / "data" / "harvest" / "equation_harvest.json"
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

MIN_INLINE_LEN = 12
MIN_LATEX_LEN = 8

LATEX_BLOCK_PATTERNS = [
    re.compile(r"\$\$(.+?)\$\$", re.DOTALL),
    re.compile(r"\\\[(.+?)\\\]", re.DOTALL),
    re.compile(r"\\begin\{equation\*?\}(.+?)\\end\{equation\*?\}", re.DOTALL),
    re.compile(r"\\begin\{align\*?\}(.+?)\\end\{align\*?\}", re.DOTALL),
]
INLINE_LATEX = re.compile(r"\$(?!\$)(.+?)(?<!\\)\$", re.DOTALL)

CODE_EQ = re.compile(r"^\s*[^#\n]{0,220}?=.{1,220}$")
MATH_HINT = re.compile(r"[\d\)\(\]\[\+\-\*/\^]|(np\.|math\.)|(sin|cos|tan|exp|log)")

EXTS = {".md", ".tex", ".py", ".txt"}
SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", "node_modules", ".openclaw", "media", "out", "runs"}


@dataclass
class EqHit:
    equation: str
    kind: str  # latex|code
    source: str
    line_start: int | None = None
    line_end: int | None = None
    sha1: str | None = None


def normalize(eq: str) -> str:
    s = eq.strip()
    s = re.sub(r"\s+", " ", s)
    s = s.strip("$")
    return s


def digest(eq: str) -> str:
    return hashlib.sha1(eq.encode("utf-8", errors="ignore")).hexdigest()


def extract_from_text(text: str) -> list[str]:
    hits: list[str] = []
    for pat in LATEX_BLOCK_PATTERNS:
        for m in pat.finditer(text):
            body = m.group(1)
            if body and len(body.strip()) >= MIN_LATEX_LEN:
                hits.append(body.strip())
    for m in INLINE_LATEX.finditer(text):
        body = (m.group(1) or "").strip()
        if len(body) >= MIN_INLINE_LEN and "\n" not in body:
            hits.append(body)
    return hits


def iter_files(root: Path) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(root):
        d = Path(dirpath)
        dirnames[:] = [n for n in dirnames if n not in SKIP_DIRS]
        for fn in filenames:
            p = d / fn
            if p.suffix.lower() in EXTS:
                yield p


def harvest_files(root: Path) -> list[EqHit]:
    out: list[EqHit] = []
    for p in iter_files(root):
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        for eq in extract_from_text(text):
            n = normalize(eq)
            if len(n) < MIN_LATEX_LEN:
                continue
            out.append(EqHit(equation=n, kind="latex", source=str(p)))

        if p.suffix.lower() == ".py":
            lines = text.splitlines()
            for i, line in enumerate(lines, start=1):
                if not CODE_EQ.match(line):
                    continue
                if "==" in line or "!=" in line:
                    continue
                if not MATH_HINT.search(line):
                    continue
                rhs = line.split("=", 1)[1].strip()
                if len(rhs) < 5:
                    continue
                out.append(EqHit(equation=line.strip(), kind="code", source=str(p), line_start=i, line_end=i))

    return out


def main() -> None:
    hits = harvest_files(ROOT_REPOS)

    uniq: dict[str, EqHit] = {}
    for h in hits:
        h.sha1 = digest(h.equation)
        if h.sha1 not in uniq:
            uniq[h.sha1] = h

    uniq_list = list(uniq.values())

    by_kind: dict[str, int] = {}
    for h in uniq_list:
        by_kind[h.kind] = by_kind.get(h.kind, 0) + 1

    payload = {
        "stats": {
            "raw": len(hits),
            "unique": len(uniq_list),
            "by_kind": dict(sorted(by_kind.items(), key=lambda kv: kv[1], reverse=True)),
            "scan_root": str(ROOT_REPOS),
        },
        "entries": [asdict(h) for h in uniq_list],
    }

    OUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_PATH} (unique={len(uniq_list)} raw={len(hits)})")


if __name__ == "__main__":
    main()
