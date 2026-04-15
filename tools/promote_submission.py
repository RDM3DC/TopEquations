from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SUBMISSIONS_JSON = REPO / "data" / "submissions.json"
EQUATIONS_JSON = REPO / "data" / "equations.json"


def _today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _slug(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:56] or "submission"


def _normalize_text(s: str) -> str:
    s = unicodedata.normalize("NFKC", s or "")
    s = s.lower().strip()
    return re.sub(r"\s+", " ", s)


_TEX_COMMAND_ESCAPE_RE = re.compile(r"\\\\(?=[A-Za-z!,:;|])")


def _normalize_texish_text(s: str) -> str:
    s = unicodedata.normalize("NFKC", s or "").strip()
    while True:
        normalized = _TEX_COMMAND_ESCAPE_RE.sub(lambda _: "\\", s)
        if normalized == s:
            return normalized
        s = normalized


def _normalize_texish_list(values: object) -> list[str]:
    if not isinstance(values, list):
        return []

    normalized_values: list[str] = []
    for value in values:
        cleaned = _normalize_texish_text(str(value))
        if cleaned:
            normalized_values.append(cleaned)
    return normalized_values


def _find_exact_equation_match(equations: dict, equation_latex: str) -> dict | None:
    normalized_equation = _normalize_text(equation_latex)
    if not normalized_equation:
        return None

    for existing in equations.get("entries", []):
        if _normalize_text(str(existing.get("equationLatex", ""))) == normalized_equation:
            return existing

    return None


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _save(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _clamp(v: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, int(v)))


def _sync_daily_markdown_status(entry: dict, status: str, equation_id: str = "") -> None:
    submitted_at = str(entry.get("submittedAt", "")).strip()
    submission_id = str(entry.get("submissionId", "")).strip()
    if not submitted_at or not submission_id:
        return

    day_path = REPO / "submissions" / f"{submitted_at}.md"
    if not day_path.exists():
        return

    text = day_path.read_text(encoding="utf-8")
    marker = f"- Submission ID: {submission_id}"
    block_start = text.find(marker)
    if block_start < 0:
        return

    next_heading = text.find("\n### ", block_start)
    block_end = len(text) if next_heading < 0 else next_heading
    block = text[block_start:block_end]

    if re.search(r"(?m)^- Status: .*$", block):
        block = re.sub(r"(?m)^- Status: .*$", f"- Status: {status}", block, count=1)
    else:
        block = block.rstrip() + f"\n- Status: {status}\n"

    if equation_id:
        if re.search(r"(?m)^- Equation ID: .*$", block):
            block = re.sub(r"(?m)^- Equation ID: .*$", f"- Equation ID: {equation_id}", block, count=1)
        else:
            block = block.rstrip() + f"\n- Equation ID: {equation_id}\n"
    else:
        block = re.sub(r"(?m)^- Equation ID: .*$\n?", "", block)

    day_path.write_text(text[:block_start] + block + text[block_end:], encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Promote a pending submission into ranked equations")
    ap.add_argument("--submission-id", required=True)
    ap.add_argument("--tractability", type=int, default=-1)
    ap.add_argument("--plausibility", type=int, default=-1)
    ap.add_argument("--validation", type=int, default=-1)
    ap.add_argument("--artifact", type=int, default=-1, help="Artifact completeness 0-10")
    ap.add_argument("--novelty", type=int, default=-1, help="Novelty tag score")
    ap.add_argument("--from-review", action="store_true", help="Use review scores already stored in submissions.json")
    ap.add_argument("--equation-id", default="", help="Optional override for final equation id")
    ap.add_argument("--manual-score", type=int, default=-1, help="Override final score (0-100)")
    args = ap.parse_args()

    submissions = _load(SUBMISSIONS_JSON)
    equations = _load(EQUATIONS_JSON)

    entry = None
    for e in submissions.get("entries", []):
        if str(e.get("submissionId")) == args.submission_id:
            entry = e
            break

    if not entry:
        raise SystemExit(f"submission not found: {args.submission_id}")
    if str(entry.get("status", "")).lower() == "promoted":
        raise SystemExit(f"submission already promoted: {args.submission_id}")

    entry["equationLatex"] = _normalize_texish_text(str(entry.get("equationLatex", "")))
    entry["description"] = _normalize_texish_text(str(entry.get("description", "")))
    entry["assumptions"] = _normalize_texish_list(entry.get("assumptions", []))
    entry["evidence"] = _normalize_texish_list(entry.get("evidence", []))

    if args.from_review:
        review = entry.get("review", {}) or {}
        scores = review.get("scores", {}) or {}
        tract = _clamp(scores.get("tractability", 0), 0, 20)
        plaus = _clamp(scores.get("plausibility", 0), 0, 20)
        validation = _clamp(scores.get("validation", 0), 0, 20)
        artifact = _clamp(scores.get("artifactCompleteness", 0), 0, 10)
        novelty = _clamp(review.get("novelty", 0), 0, 30)
    else:
        if min(args.tractability, args.plausibility, args.validation, args.artifact, args.novelty) < 0:
            raise SystemExit("manual promotion requires --tractability --plausibility --validation --artifact --novelty, or use --from-review")
        tract = _clamp(args.tractability, 0, 20)
        plaus = _clamp(args.plausibility, 0, 20)
        validation = _clamp(args.validation, 0, 20)
        artifact = _clamp(args.artifact, 0, 10)
        novelty = _clamp(args.novelty, 0, 30)

    total = tract + plaus + validation + artifact + novelty

    # Use blended score from review if available, or manual override
    if args.manual_score >= 0:
        total = _clamp(args.manual_score, 0, 150)
    elif args.from_review:
        review = entry.get("review", {}) or {}
        if review.get("blended_score"):
            total = int(review["blended_score"])
        elif review.get("score"):
            total = int(review["score"])

    duplicate_match = _find_exact_equation_match(equations, str(entry.get("equationLatex", "")))
    if duplicate_match:
        canonical_id = str(duplicate_match.get("id", "")).strip()
        if not canonical_id:
            raise SystemExit(f"duplicate match missing equation id for: {args.submission_id}")

        entry["status"] = "duplicate"
        entry["review"] = {
            "date": _today(),
            "equationId": canonical_id,
            "score": total,
            "scores": {
                "tractability": tract,
                "plausibility": plaus,
                "validation": validation,
                "artifactCompleteness": artifact,
            },
            "novelty": novelty,
            "disposition": "duplicate",
            "note": f"Exact equation match with promoted equation {canonical_id}; submission retained in the log without creating a second leaderboard entry.",
        }
        submissions["lastUpdated"] = _today()
        _save(SUBMISSIONS_JSON, submissions)
        _sync_daily_markdown_status(entry, "duplicate", canonical_id)

        print(f"duplicate: {args.submission_id} -> {canonical_id} (no new equation created)")

        try:
            from tools.build_site import main as _build_site
            _build_site()
            print("docs/*.html rebuilt")
        except Exception:
            try:
                import subprocess, sys
                subprocess.run(
                    [sys.executable, str(REPO / "tools" / "build_site.py")],
                    cwd=str(REPO), check=True,
                )
                print("docs/*.html rebuilt (subprocess)")
            except Exception as exc:
                print(f"warning: site rebuild skipped: {exc}")
        return

    eid = args.equation_id.strip() or f"eq-{_slug(entry.get('name', 'submission'))}"
    existing_ids = {str(x.get("id")) for x in equations.get("entries", [])}
    if eid in existing_ids:
        eid = f"{eid}-{_slug(args.submission_id)[-8:]}"

    repo_url = f"https://github.com/RDM3DC/{eid}"

    promoted = {
        "id": eid,
        "name": entry.get("name", ""),
        "firstSeen": _today(),
        "source": entry.get("source", "manual submission"),
        "submitter": entry.get("submitter", "unknown"),
        "repoUrl": repo_url,
        "score": total,
        "scores": {
            "tractability": tract,
            "plausibility": plaus,
            "validation": validation,
            "artifactCompleteness": artifact,
        },
        "units": entry.get("units", "TBD"),
        "theory": entry.get("theory", "PASS-WITH-ASSUMPTIONS"),
        "animation": entry.get("animation", {"status": "planned", "path": ""}),
        "image": entry.get("image", {"status": "planned", "path": ""}),
        "description": entry.get("description", ""),
        "assumptions": entry.get("assumptions", []),
        "date": _today(),
        "equationLatex": entry.get("equationLatex", ""),
        "tags": {
            "novelty": {
                "score": novelty,
                "date": _today(),
            }
        },
    }

    equations.setdefault("entries", []).append(promoted)
    equations["lastUpdated"] = _today()

    entry["status"] = "promoted"
    entry["review"] = {
        "date": _today(),
        "equationId": eid,
        "score": total,
        "scores": promoted["scores"],
        "novelty": novelty,
    }
    submissions["lastUpdated"] = _today()

    _save(EQUATIONS_JSON, equations)
    _save(SUBMISSIONS_JSON, submissions)
    _sync_daily_markdown_status(entry, "promoted", eid)

    print(f"promoted: {args.submission_id} -> {eid} (score {total})")

    # Export certificates first so the rebuilt site always reflects the new entry.
    try:
        import subprocess
        import sys
        subprocess.run(
            [sys.executable, str(REPO / "tools" / "export_equation_certificates.py")],
            cwd=str(REPO), check=True,
        )
        print("certificates exported")
    except Exception as exc:
        print(f"warning: certificate export skipped: {exc}")

    # Rebuild leaderboard and site so local promotions are immediately visible.
    try:
        from tools.generate_leaderboard import main as _gen_lb
        _gen_lb()
        print("leaderboard.md rebuilt")
    except Exception:
        try:
            import subprocess, sys
            subprocess.run(
                [sys.executable, str(REPO / "tools" / "generate_leaderboard.py")],
                cwd=str(REPO), check=True,
            )
            print("leaderboard.md rebuilt (subprocess)")
        except Exception as exc:
            print(f"warning: leaderboard rebuild skipped: {exc}")

    try:
        from tools.build_site import main as _build_site
        _build_site()
        print("docs/*.html rebuilt")
    except Exception:
        try:
            import subprocess, sys
            subprocess.run(
                [sys.executable, str(REPO / "tools" / "build_site.py")],
                cwd=str(REPO), check=True,
            )
            print("docs/*.html rebuilt (subprocess)")
        except Exception as exc:
            print(f"warning: site rebuild skipped: {exc}")


if __name__ == "__main__":
    main()
