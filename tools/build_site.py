# -*- coding: utf-8 -*-

"""Build the GitHub Pages site (docs/) from data files.

Generates:
  - docs/index.html
  - docs/core.html          (canonical core only)
  - docs/famous.html        (famous equations adjusted)
  - docs/leaderboard.html   (ranked derived only)
  - docs/harvest_preview.html

Usage:
  python tools/build_site.py

This is intentionally dependency-free.
"""

from __future__ import annotations

import html
import json
import re
from datetime import datetime
from pathlib import Path


def _esc(s: object) -> str:
    return html.escape(str(s) if s is not None else "")


def _load_json_safe(path: Path, default: dict | list | None = None):
  """Load JSON defensively; recover first valid object if trailing/corrupt text exists."""
  if default is None:
    default = {}
  try:
    return json.loads(path.read_text(encoding="utf-8"))
  except Exception:
    try:
      raw = path.read_text(encoding="utf-8")
      dec = json.JSONDecoder()
      obj, _ = dec.raw_decode(raw)
      return obj
    except Exception:
      return default


def _badge(text: str, kind: str) -> str:
    return f"<span class='badge badge--{kind}'>{_esc(text)}</span>"


def _status_badge(val: str, kind: str) -> str:
    v = (val or "").upper()
    css = "neutral"
    if kind == "units":
        css = {"OK": "good", "WARN": "warn", "ERROR": "bad"}.get(v, "neutral")
    if kind == "theory":
        if v == "PASS":
            css = "good"
        elif v.startswith("PASS-") or "ASSUMPTION" in v:
            css = "warn"
        elif v == "FAIL":
            css = "bad"
        else:
            css = "neutral"
    return f"<span class='pill pill--{css}' title='{_esc(kind)}'>{_esc(val)}</span>"


def _artifact(val: dict | str | None) -> str:
    if not val:
        return "planned"
    if isinstance(val, str):
        return _esc(val) if val.strip() else "planned"
    path = (val.get("path") or "").strip()
    status = (val.get("status") or "planned").strip() or "planned"
    if path:
        return f"<a href='{_esc(path)}' target='_blank' rel='noopener'>link</a>"
    return _esc(status)


def _page(title: str, body: str, updated: str) -> str:
    # KaTeX for fast, crisp equation rendering.
    katex_css = "https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css"
    katex_js = "https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"
    autorender_js = "https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"

    cachebust = re.sub(r"[^0-9]", "", updated) or "1"

    return f"""<!doctype html>
<html lang='en'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>{_esc(title)}</title>

  <link rel='stylesheet' href='./assets/style.css?v={cachebust}' />
  <link rel='stylesheet' href='{katex_css}' />

  <script defer src='./assets/app.js?v={cachebust}'></script>
  <script defer src='{katex_js}'></script>
  <script defer src='{autorender_js}'></script>
  <script defer>
    window.addEventListener('DOMContentLoaded', () => {{
      if (window.renderMathInElement) {{
        window.renderMathInElement(document.body, {{
          delimiters: [
            {{left: '$$', right: '$$', display: true}},
            {{left: '$', right: '$', display: false}},
          ],
          throwOnError: false,
        }});
      }}
    }});
  </script>
</head>
<body>
  <header class='topbar'>
    <div class='wrap topbar__inner'>
      <div class='brand'>
        <div class='brand__mark'>∑</div>
        <div class='brand__text'>
          <div class='brand__title'>TopEquations</div>
          <div class='brand__sub'>Curated leaderboard + certificate registry</div>
        </div>
      </div>
      <nav class='nav'>
        <a href='./index.html'>Home</a>
        <a href='./core.html'>Core</a>
        <a href='./famous.html'>Famous</a>
        <a href='./leaderboard.html'>Leaderboard</a>
        <a href='./certificates.html'>Certificates</a>
        <a href='./submissions.html'>All Submissions</a>
        <a class='nav__ghost' href='https://github.com/RDM3DC/TopEquations' target='_blank' rel='noopener'>GitHub</a>
        <a class='nav__ghost' href='https://rdm3dc.github.io/TopEquations/leaderboard.html' target='_blank' rel='noopener'>Live Site</a>
      </nav>
    </div>
  </header>

  <main class='wrap'>
    {body}
    <footer class='footer'>
      <div>Last built: <strong>{_esc(updated)}</strong></div>
    </footer>
  </main>
</body>
</html>
"""


def _build_core_cards(repo_root: Path) -> list[str]:

    # Tier 1: Canonical Core (pinned, non-ranked)
    core_path = repo_root / "data" / "core.json"
    core = _load_json_safe(core_path, {"entries": []})
    core_entries = list(core.get("entries", []))

    core_cards: list[str] = []
    for e in core_entries:
        name = e.get("name", "")
        eq = e.get("equationLatex", "") or "(pending)"
        desc = e.get("description", "")
        src = e.get("source", "")
        url = e.get("sourceUrl", "")
        total_score, rb = _rubric_score(e)
        units = str(e.get("units", "WARN")).upper()
        theory = str(e.get("theory", "PASS-WITH-ASSUMPTIONS")).upper()
        anim = _artifact(e.get("animation"))
        img = _artifact(e.get("image"))
        core_cards.append(
            f"""
<section class='card'>
  <div class='card__rank'>CORE</div>
  <div class='card__body'>
    <div class='card__head'>
      <h2 class='card__title'>{_esc(name)}</h2>
      <div class='card__meta'>
        <span class='badge badge--score'>{_esc(f'Score {total_score}')}</span>
        <span class='pill pill--neutral'>Pinned</span>
        <span class='pill pill--{'good' if units == 'OK' else 'warn'}'>{_esc(units)}</span>
        <span class='pill pill--{'good' if theory == 'PASS' else ('bad' if theory == 'FAIL' else 'warn')}'>{_esc(theory)}</span>
        <span class='badge badge--score'>{_esc(src)}</span>
      </div>
    </div>
    <div class='equation'>
      <div class='equation__label'>Canonical equation</div>
      <div class='equation__tex'>$${_esc(eq)}$$</div>
    </div>
    <div class='card__sub'>Reference: <span class='muted'>{_esc(src)}</span></div>
    <div class='grid'>
      <div class='kv'><div class='k'>Description</div><div class='v'>{_esc(desc)}</div></div>
      <div class='kv'><div class='k'>Rubric</div><div class='v'>T {rb['tractability']}/20, P {rb['plausibility']}/20, V {rb['validation']}/20, A {rb['artifact']}/10, normalized to {total_score}/100</div></div>
      <div class='kv'><div class='k'>Novelty tag</div><div class='v'>{_esc(rb['novelty_tag'])}</div></div>
      <div class='kv'><div class='k'>Canonical source</div><div class='v'><a href='{_esc(url)}' target='_blank' rel='noopener'>{_esc(url)}</a></div></div>
      <div class='kv'><div class='k'>Repository</div><div class='v'>{("<a href='" + _esc(e.get('repoUrl','')) + "' target='_blank' rel='noopener'>equation repo &rarr;</a>") if e.get('repoUrl') else '<span class=\'muted\'>—</span>'}</div></div>
      <div class='kv'><div class='k'>Animation</div><div class='v'>{anim}</div></div>
      <div class='kv'><div class='k'>Image/Diagram</div><div class='v'>{img}</div></div>
    </div>
  </div>
</section>
"""
        )

    return core_cards


def _extract_tier_lists(repo_root: Path) -> dict[str, list[str]]:
    tier_lists: dict[str, list[str]] = {"all_time": [], "month": [], "famous": []}

    def _extract_li(ol_html: str) -> list[str]:
        return [m.group(1).strip() for m in re.finditer(r"<li>(.*?)</li>", ol_html, flags=re.I | re.S)]

    try:
        md = (repo_root / "leaderboard.md").read_text(encoding="utf-8")
        if "## Tier Lists" in md and "<table" in md:
            start = md.find("## Tier Lists")
            t0 = md.find("<table", start)
            t1 = md.find("</table>", t0)
            if t0 != -1 and t1 != -1:
                table = md[t0 : t1 + len("</table>")]
                tds = re.findall(r"<td[^>]*>(.*?)</td>", table, flags=re.I | re.S)
                if len(tds) >= 3:
                    ols = []
                    for td in tds[:3]:
                        m = re.search(r"<ol>(.*?)</ol>", td, flags=re.I | re.S)
                        ols.append(m.group(0) if m else "")
                    tier_lists["all_time"] = _extract_li(ols[0])
                    tier_lists["month"] = _extract_li(ols[1])
                    tier_lists["famous"] = _extract_li(ols[2])
    except Exception:
        pass

    return tier_lists


def _load_famous_entries(repo_root: Path) -> list[dict[str, str]]:
    famous_path = repo_root / "data" / "famous_equations.json"
    if famous_path.exists():
        try:
            data = _load_json_safe(famous_path, {"entries": []})
            out = []
            for e in data.get("entries", []):
                out.append(
                    {
                        "name": str(e.get("name", "")).strip(),
                        "equationLatex": str(e.get("equationLatex", "")).strip(),
                        "description": str(e.get("description", "")).strip(),
                        "theory": str(e.get("theory", "PASS-WITH-ASSUMPTIONS")).strip(),
                        "definitions": str(e.get("definitions", "")).strip(),
                        "caveat": str(e.get("caveat", "")).strip(),
                        "tags": e.get("tags", {"novelty": {"score": e.get("novelty", 0), "date": "legacy"}}),
                        "tractability": e.get("tractability", 0),
                        "plausibility": e.get("plausibility", 0),
                        "validation": e.get("validation", 0),
                        "artifactCompleteness": e.get("artifactCompleteness", 0),
                        "units": str(e.get("units", "WARN")).strip(),
                        "animation": e.get("animation", "planned"),
                        "image": e.get("image", "planned"),
                        "assumptions": e.get("assumptions", []),
                        "subtitle": str(e.get("subtitle", "")).strip(),
                        "coreRefs": e.get("coreRefs", []),
                        "repoUrl": str(e.get("repoUrl", "")).strip(),
                    }
                )
            if out:
                return out
        except Exception:
            pass

    # Fallback: try legacy markdown tier-list extraction.
    tier_lists = _extract_tier_lists(repo_root)
    famous_items = tier_lists.get("famous", [])
    out: list[dict[str, str]] = []
    for idx, item in enumerate(famous_items, start=1):
        m = re.search(r"<b>(.*?)</b>", item, flags=re.I | re.S)
        title = m.group(1).strip() if m else f"Famous Equation {idx}"
        body_html = re.sub(r"<b>.*?</b>", "", item, count=1, flags=re.I | re.S).strip()
        body_html = body_html.lstrip("<br/>").strip()

        equation_expr = ""
        for pat in (r"\$\$(.+?)\$\$", r"\\\((.+?)\\\)", r"\$(.+?)\$"):
            mm = re.search(pat, body_html, flags=re.S)
            if mm:
                equation_expr = mm.group(1).strip()
                break

        desc_text = re.sub(r"<br\s*/?>", " ", body_html, flags=re.I)
        desc_text = re.sub(r"<[^>]+>", " ", desc_text)
        desc_text = re.sub(r"\\\(.+?\\\)", " ", desc_text)
        desc_text = re.sub(r"\$\$.+?\$\$", " ", desc_text, flags=re.S)
        desc_text = re.sub(r"\s+", " ", desc_text).strip()

        out.append(
            {
                "name": title,
                "equationLatex": equation_expr or "(pending)",
                "description": desc_text or "Classic equation reformulated in your adjusted framework.",
                "theory": "PASS-WITH-ASSUMPTIONS",
                "definitions": "",
                "caveat": "",
                "tags": {"novelty": {"score": 20, "date": "legacy"}},
                "tractability": 12,
                "plausibility": 12,
                "validation": 0,
                "artifactCompleteness": 0,
                "units": "WARN",
                "animation": "planned",
                "image": "planned",
                "assumptions": [],
            }
        )
    return out


def _famous_score(e: dict) -> tuple[int, dict[str, int]]:
    total, rb = _rubric_score(e)
    return total, rb


def _rubric_score(e: dict) -> tuple[int, dict[str, int]]:
    def _clamp(v: object, lo: int, hi: int) -> int:
        try:
            n = int(float(v))
        except Exception:
            n = lo
        return max(lo, min(hi, n))

    tractability = _clamp(e.get("tractability", 0), 0, 20)
    plausibility = _clamp(e.get("plausibility", 0), 0, 20)
    validation = _clamp(e.get("validation", 0), 0, 20)
    artifact = _clamp(e.get("artifactCompleteness", 0), 0, 10)

    novelty_info = ((e.get("tags", {}) or {}).get("novelty", {}) or {})
    novelty_tag = "-"
    if novelty_info:
      novelty_tag = f"{novelty_info.get('score', '-')} @ {novelty_info.get('date', '-')}"

    units = str(e.get("units", "")).upper()
    theory = str(e.get("theory", "")).upper()
    animation = str(e.get("animation", "planned")).strip().lower()
    image = str(e.get("image", "planned")).strip().lower()

    # Rubric v2: novelty is metadata tag only; not part of ranking total.
    total_raw = tractability + plausibility + validation + artifact
    total = int(round((total_raw / 70.0) * 100.0))
    return total, {
      "novelty_tag": novelty_tag,
        "tractability": tractability,
        "plausibility": plausibility,
      "validation": validation,
      "artifact": artifact,
    }


def build_famous(repo_root: Path, docs: Path) -> None:
    famous_entries = _load_famous_entries(repo_root)
    scored_entries: list[tuple[dict, int, dict[str, int]]] = []
    for e in famous_entries:
        total, breakdown = _famous_score(e)
        scored_entries.append((e, total, breakdown))
    scored_entries.sort(key=lambda x: x[1], reverse=True)

    famous_cards: list[str] = []
    for idx, (e, total_score, rb) in enumerate(scored_entries, start=1):
        title = e.get("name", "") or f"Famous Equation {idx}"
        subtitle = e.get("subtitle", "")
        equation_expr = e.get("equationLatex", "") or "(pending)"
        desc_text = e.get("description", "") or "Classic equation reformulated in your adjusted framework."
        definitions = e.get("definitions", "") or ""
        caveat = e.get("caveat", "") or ""
        units = (e.get("units", "WARN") or "WARN").upper()
        theory = (e.get("theory", "PASS-WITH-ASSUMPTIONS") or "PASS-WITH-ASSUMPTIONS").upper()
        assumptions = e.get("assumptions", []) or []
        core_refs = e.get("coreRefs", []) or []
        if not isinstance(assumptions, list):
            assumptions = [str(assumptions)]
        assumptions_html = "".join(f"<li>{_esc(a)}</li>" for a in assumptions if str(a).strip())
        core_refs_html = ", ".join(f"<a href='core.html#{_esc(r)}'>{_esc(r)}</a>" for r in core_refs) if core_refs else "—"
        theory_css = "warn"
        if theory == "PASS":
            theory_css = "good"
        elif theory == "FAIL":
            theory_css = "bad"
        subtitle_html = f"<div class='card__subtitle muted'>{_esc(subtitle)}</div>" if subtitle else ""

        famous_cards.append(
            f"""
<section class='card'>
  <div class='card__rank'>F{idx}</div>
  <div class='card__body'>
    <div class='card__head'>
      <h2 class='card__title'>{_esc(title)}</h2>
      {subtitle_html}
      <div class='card__meta'>
        <span class='badge badge--score'>{_esc(f'Score {total_score}')}</span>
        <span class='badge badge--score'>Famous</span>
        <span class='pill pill--{'good' if units == 'OK' else 'warn'}'>{_esc(units)}</span>
        <span class='pill pill--{theory_css}'>{_esc(theory)}</span>
        <span class='pill pill--warn'>Adjusted</span>
      </div>
    </div>

    <div class='equation'>
      <div class='equation__label'>Adjusted form</div>
      <div class='equation__tex'>$${_esc(equation_expr)}$$</div>
    </div>

    <div class='card__sub'>Reference: <span class='muted'>famous-adjusted list</span></div>

    <div class='grid'>
      <div class='kv'><div class='k'>Description</div><div class='v'>{_esc(desc_text)}</div></div>
      <div class='kv'><div class='k'>Rubric</div><div class='v'>T {rb['tractability']}/20, P {rb['plausibility']}/20, V {rb['validation']}/20, A {rb['artifact']}/10, normalized to {total_score}/100</div></div>
      <div class='kv'><div class='k'>Novelty tag</div><div class='v'>{_esc(rb['novelty_tag'])}</div></div>
      <div class='kv'><div class='k'>Definitions</div><div class='v'>{_esc(definitions or 'See equation symbols.')}</div></div>
      <div class='kv'><div class='k'>Assumptions</div><div class='v'>{('<ul class=\'ul\'>' + assumptions_html + '</ul>') if assumptions_html else 'None listed.'}</div></div>
      <div class='kv'><div class='k'>Caveat</div><div class='v'>{_esc(caveat or 'Modeling form; not a canonical replacement.')}</div></div>
      <div class='kv'><div class='k'>List index</div><div class='v'>F{idx}</div></div>
      <div class='kv'><div class='k'>Category</div><div class='v'>Famous (Adjusted)</div></div>
      <div class='kv'><div class='k'>Core refs</div><div class='v'>{core_refs_html}</div></div>
      <div class='kv'><div class='k'>Repository</div><div class='v'>{("<a href='" + _esc(e.get('repoUrl','')) + "' target='_blank' rel='noopener'>equation repo &rarr;</a>") if e.get('repoUrl') else '<span class=\'muted\'>—</span>'}</div></div>
    </div>
  </div>
</section>
"""
        )

    body = """
<div class='layout layout--single'>
  <section class='maincol'>

<div class='hero'>
  <div class='hero__left'>
    <h1>Famous Equations (Adjusted)</h1>
    <p>Curated classical forms rewritten in your Phase-Lift / Adaptive-π style, scored with the same leaderboard rubric.</p>
  </div>
</div>

<div class='panel'>
  <h2>Scoring Rubric (0-100)</h2>
  <ul>
    <li>Tractability (0-20)</li>
    <li>Physical plausibility (0-20)</li>
    <li>Validation (0-20)</li>
    <li>Artifact completeness (0-10)</li>
    <li>Total normalized from a 70-point base</li>
    <li>Novelty is shown as a dated tag only</li>
  </ul>
</div>

<div id='famousCards' class='cardrow'>
""" + "\n".join(famous_cards) + """
</div>

  </section>
</div>
"""

    updated = datetime.now().strftime("%Y-%m-%d %H:%M")
    out = docs / "famous.html"
    out.write_text(_page("TopEquations — Famous Equations", body, updated), encoding="utf-8")


def build_core(repo_root: Path, docs: Path) -> None:
    core_cards = _build_core_cards(repo_root)

    body = """
<div class='layout layout--single'>
  <section class='maincol'>

<div class='hero'>
  <div class='hero__left'>
    <h1>Canonical Core</h1>
    <p>Pinned, non-ranked anchor equations with rubric scores.</p>
  </div>
</div>

<div class='panel'>
  <h2>Scoring Rubric (0-100)</h2>
  <ul>
    <li>Tractability (0-20)</li>
    <li>Physical plausibility (0-20)</li>
    <li>Validation (0-20)</li>
    <li>Artifact completeness (0-10)</li>
    <li>Total normalized from a 70-point base</li>
    <li>Novelty is shown as a dated tag only</li>
  </ul>
</div>

<div id='coreCards' class='cardrow'>
""" + "\n".join(core_cards) + """
</div>

  </section>
</div>
"""

    updated = datetime.now().strftime("%Y-%m-%d %H:%M")
    out = docs / "core.html"
    out.write_text(_page("TopEquations — Canonical Core", body, updated), encoding="utf-8")


def build_leaderboard(repo_root: Path, docs: Path) -> None:
    # Ranked derived equations only (display capped to score >= 68).
    DISPLAY_THRESHOLD = 65

    data_path = repo_root / "data" / "equations.json"
    data = json.loads(data_path.read_text(encoding="utf-8"))
    entries_all = list(data.get("entries", []))
    entries_all.sort(key=lambda e: float(e.get("score", 0)), reverse=True)

    entries = [e for e in entries_all if float(e.get("score", 0)) >= DISPLAY_THRESHOLD]

    cards = []
    for i, e in enumerate(entries, start=1):
        name = e.get("name", "")
        eq = e.get("equationLatex", "") or "(pending)"
        src = e.get("source", "")
        desc = e.get("description", "")
        score = e.get("score", "")
        units = e.get("units", "")
        theory = e.get("theory", "")
        date = e.get("date", "")
        eq_id = (e.get("id") or "").strip()
        repo_url = (e.get("repoUrl") or "").strip()

        # Point animation/image links to the equation repo when available
        def _repo_artifact(obj, repo_url):
            if isinstance(obj, dict) and obj.get("path", "").strip() and repo_url:
                fname = Path(obj["path"]).name
                url = f"{repo_url}/blob/main/images/{fname}"
                return f"<a href='{_esc(url)}' target='_blank' rel='noopener'>link</a>"
            return _artifact(obj)

        anim = _repo_artifact(e.get("animation"), repo_url)
        img = _repo_artifact(e.get("image"), repo_url)

        has_latex = "1" if (e.get("equationLatex") or "").strip() else "0"
        # Optional educational metadata
        differential = (e.get("differentialLatex") or "").strip()
        derivation = (e.get("derivation") or "").strip()
        assumptions = e.get("assumptions") or []
        if not isinstance(assumptions, list):
            assumptions = [str(assumptions)]

        def _ul(items: list[str]) -> str:
            if not items:
                return ""
            lis = "".join(f"<li>{_esc(x)}</li>" for x in items if str(x).strip())
            return f"<ul class='ul'>{lis}</ul>" if lis else ""

        extra = ""
        if differential:
          extra += f"<div class='kv'><div class='k'>Differential form</div><div class='v'>$${_esc(differential)}$$</div></div>"
        if derivation:
            extra += f"<div class='kv'><div class='k'>Derivation bridge</div><div class='v'>{_esc(derivation)}</div></div>"
        if assumptions:
            extra += f"<div class='kv'><div class='k'>Assumptions</div><div class='v'>{_ul([str(x) for x in assumptions])}</div></div>"
        if eq_id:
          extra += f"<div class='kv'><div class='k'>Certificate</div><div class='v'><a href='./certificates.html#{_esc(eq_id)}'>view on chain record</a></div></div>"

        if repo_url:
          extra += f"<div class='kv'><div class='k'>Repository</div><div class='v'><a href='{_esc(repo_url)}' target='_blank' rel='noopener'>equation repo &rarr;</a></div></div>"

        cards.append(
            f"""
<section class='card' data-rank='{i}' data-score='{_esc(score)}' data-haslatex='{has_latex}'>
  <div class='card__rank'>#{i}</div>
  <div class='card__body'>
    <div class='card__head'>
      <h2 class='card__title'>{_esc(name)}</h2>
      <div class='card__meta'>
        {_badge(f"Score {score}", 'score')}
        {_status_badge(str(units), 'units')}
        {_status_badge(str(theory), 'theory')}
      </div>
    </div>

    <div class='equation'>
      <div class='equation__label'>Derived equation</div>
      <div class='equation__tex'>$${_esc(eq)}$$</div>
    </div>

    <div class='card__sub'>Reference: <span class='muted'>{_esc(src)}</span></div>

    <div class='grid'>
      <div class='kv'><div class='k'>Description</div><div class='v'>{_esc(desc)}</div></div>
      {extra}
      <div class='kv'><div class='k'>Date</div><div class='v'>{_esc(date)}</div></div>
      <div class='kv'><div class='k'>Animation</div><div class='v'>{anim}</div></div>
      <div class='kv'><div class='k'>Image/Diagram</div><div class='v'>{img}</div></div>
    </div>
  </div>
</section>
"""
        )

    body = """
<div class='layout layout--single'>
  <section class='maincol'>

<div class='hero'>
  <div class='hero__left'>
    <h1>Top Ranked Derived Equations</h1>
    <p>Single-row ranked cards. Canonical anchors live on the separate <a href='./core.html'>Core page</a>.</p>
  </div>
  <div class='hero__right'>
    <div class='controls'>
      <div class='search'>
        <input id='searchBox' type='search' placeholder='Search name / source / equation…' />
      </div>
      <div class='row'>
        <label class='check'>
          <input id='latexOnly' type='checkbox' />
          <span>LaTeX only</span>
        </label>
        <label class='select'>
          <span>Sort</span>
          <select id='sortBy'>
            <option value='score-desc' selected>Score ↓</option>
            <option value='score-asc'>Score ↑</option>
            <option value='rank'>Rank</option>
          </select>
        </label>
      </div>
    </div>
  </div>
</div>

<div id='cards' class='cardrow'>
""" + "\n".join(cards) + """
</div>

  </section>
</div>
"""

    updated = datetime.now().strftime("%Y-%m-%d %H:%M")
    out = docs / "leaderboard.html"
    out.write_text(_page("TopEquations — Leaderboard", body, updated), encoding="utf-8")


def build_index(repo_root: Path, docs: Path) -> None:
    data = _load_json_safe(repo_root / "data" / "equations.json", {"entries": []})
    n = len(data.get("entries", []))

    core = _load_json_safe(repo_root / "data" / "core.json", {"entries": []})
    core_n = len(core.get("entries", []))

    subs = _load_json_safe(repo_root / "data" / "submissions.json", {"entries": []})
    subs_n = len(subs.get("entries", []))
    promoted_n = sum(1 for e in subs.get("entries", []) if str(e.get("status", "")).lower() == "promoted")

    body = f"""
<div class='hero hero--home'>
  <div class='hero__left'>
    <h1>TopEquations</h1>
    <p>Open leaderboard for ranking equations &mdash; from textbook classics to novel discoveries.<br>
    Scored by a dual-layer system, published on-chain with signed certificates.</p>
    <div class='cta'>
      <a class='btn' href='./core.html'>Canonical Core</a>
      <a class='btn btn--ghost' href='./famous.html'>Famous Equations</a>
      <a class='btn btn--ghost' href='./leaderboard.html'>Leaderboard</a>
      <a class='btn btn--ghost' href='./submissions.html'>All Submissions</a>
      <a class='btn btn--ghost' href='https://github.com/RDM3DC/TopEquations/issues/new?template=equation_submission.yml'>Submit an Equation</a>
    </div>
  </div>
  <div class='hero__right'>
    <div class='statbox'>
      <div class='stat'>
        <div class='stat__num'>{_esc(core_n)}</div>
        <div class='stat__label'>Canonical core anchors</div>
      </div>
      <div class='stat'>
        <div class='stat__num'>{_esc(n)}</div>
        <div class='stat__label'>Ranked derived equations</div>
      </div>
      <div class='stat'>
        <div class='stat__num'>{_esc(subs_n)}</div>
        <div class='stat__label'>Total submissions</div>
      </div>
      <div class='stat'>
        <div class='stat__num'>{_esc(promoted_n)}</div>
        <div class='stat__label'>Promoted to leaderboard</div>
      </div>
    </div>
  </div>
</div>

<div class='panel'>
  <h2>How to Submit</h2>
  <p>Anyone &mdash; human or AI agent &mdash; can submit equations. The easiest way:</p>
  <ol>
    <li>Go to <a href='https://github.com/RDM3DC/TopEquations/issues/new?template=equation_submission.yml'><strong>New Equation Submission</strong></a></li>
    <li>Paste a JSON object with your equation, description, and evidence</li>
    <li>The pipeline validates, scores, and (if score &ge; 65) promotes automatically</li>
    <li>You&rsquo;ll receive a receipt comment with your heuristic score, LLM quality score, and blended score</li>
  </ol>
  <p>See the <a href='https://github.com/RDM3DC/TopEquations#how-to-submit-an-equation'>README</a> for JSON format details and tips for high scores.</p>
</div>

<div class='panel'>
  <h2>How Scoring Works</h2>
  <table class='tbl'>
    <thead>
      <tr><th>Layer</th><th>Role</th><th>Details</th></tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Heuristic</strong></td>
        <td>Security gate (deterministic)</td>
        <td>Tractability, plausibility, validation, artifacts, novelty &mdash; no LLM involved</td>
      </tr>
      <tr>
        <td><strong>LLM Review</strong></td>
        <td>Quality assessment (advisory)</td>
        <td>Calibrated GPT-4o-mini: physical validity, novelty, clarity, evidence quality, significance</td>
      </tr>
      <tr>
        <td><strong>Blended</strong></td>
        <td>Final score</td>
        <td>40% heuristic + 60% LLM &mdash; balanced quality signal</td>
      </tr>
    </tbody>
  </table>
</div>

<div class='panel'>
  <h2>Data Structure</h2>
  <ul>
    <li><strong>Canonical Core</strong> &mdash; 14 anchor equations in <code>data/core.json</code></li>
    <li><strong>Ranked Derived</strong> &mdash; promoted equations in <code>data/equations.json</code></li>
    <li><strong>Submissions</strong> &mdash; all submissions in <code>data/submissions.json</code>, promoted after review</li>
    <li><strong>Certificates</strong> &mdash; on-chain ECDSA-signed certificates for every promoted equation</li>
  </ul>
</div>
"""

    updated = datetime.now().strftime("%Y-%m-%d %H:%M")
    (docs / "index.html").write_text(_page("TopEquations", body, updated), encoding="utf-8")


def build_harvest(repo_root: Path, docs: Path) -> None:
    # Keep source harvest data private to repo; do not publish in docs/data.
    body = """
<div class='hero'>
  <div class='hero__left'>
    <h1>Harvest List Hidden</h1>
    <p>The public harvested-equation list is disabled. Candidates are kept privately for later manual submission and review.</p>
  </div>
</div>

<div class='panel'>
  <div class='muted'>Use the submission workflow to promote selected candidates into the ranked board.</div>
</div>
"""

    updated = datetime.now().strftime("%Y-%m-%d %H:%M")
    (docs / "harvest.html").write_text(_page("TopEquations — Harvest", body, updated), encoding="utf-8")


def build_submissions(repo_root: Path, docs: Path) -> None:
    src = repo_root / "data" / "submissions.json"
    data = _load_json_safe(src, {"entries": []})

    dst = docs / "data" / "submissions.json"
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.exists():
        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

    entries = list(data.get("entries", []))
    # Sort by submission date (newest first); scores belong on the leaderboard page
    entries.sort(key=lambda x: x.get("submittedAt", ""), reverse=True)

    total = len(entries)
    promoted = sum(1 for e in entries if str(e.get("status", "")).lower() == "promoted")
    ready = sum(1 for e in entries if str(e.get("status", "")).lower() == "ready")
    review = sum(1 for e in entries if str(e.get("status", "")).lower() == "needs-review")

    cards: list[str] = []
    for idx, e in enumerate(entries, start=1):
        sid = str(e.get("submissionId", ""))
        name = e.get("name", sid)
        status = str(e.get("status", "pending")).lower()
        eq = e.get("equationLatex", "") or "(pending)"
        desc = e.get("description", "")
        source = e.get("source", "")
        submitter = e.get("submitter", "")
        date = e.get("submittedAt", "")
        units = str(e.get("units", "TBD")).upper()
        theory = str(e.get("theory", "")).upper()

        review_data = e.get("review", {}) or {}
        eq_id = str(review_data.get("equationId", "")).strip()

        assumptions = e.get("assumptions", []) or []
        if not isinstance(assumptions, list):
            assumptions = [str(assumptions)]
        assumptions_html = "".join(f"<li>{_esc(a)}</li>" for a in assumptions if str(a).strip())

        evidence = e.get("evidence", []) or []
        evidence_html = ""
        if evidence:
            ev_items = "".join(f"<li>{_esc(ev.get('label', '') if isinstance(ev, dict) else str(ev))}</li>" for ev in evidence)
            evidence_html = f"<div class='kv'><div class='k'>Evidence</div><div class='v'><ul class='ul'>{ev_items}</ul></div></div>"

        anim = _artifact(e.get("animation"))
        img = _artifact(e.get("image"))

        # Status badge styling
        if status == "promoted":
            status_pill = "<span class='pill pill--good'>PROMOTED</span>"
        elif status == "ready":
            status_pill = "<span class='pill pill--warn'>READY</span>"
        else:
            status_pill = "<span class='pill pill--neutral'>NEEDS REVIEW</span>"

        chain_link = ""
        if eq_id and status == "promoted":
            chain_link = f"<div class='kv'><div class='k'>Chain record</div><div class='v'><a href='./certificates.html#{_esc(eq_id)}'>{_esc(eq_id)}</a></div></div>"

        cards.append(
            f"""
<section class='card' data-status='{_esc(status)}'>
  <div class='card__rank'>#{idx}</div>
  <div class='card__body'>
    <div class='card__head'>
      <h2 class='card__title'>{_esc(name)}</h2>
      <div class='card__meta'>
        {status_pill}
        {_status_badge(str(units), 'units')}
        {_status_badge(str(theory), 'theory')}
      </div>
    </div>

    <div class='equation'>
      <div class='equation__label'>Submitted equation</div>
      <div class='equation__tex'>$${_esc(eq)}$$</div>
    </div>

    <div class='card__sub'>Source: <span class='muted'>{_esc(source)}</span> &middot; Submitter: <span class='muted'>{_esc(submitter)}</span></div>

    <div class='grid'>
      <div class='kv'><div class='k'>Description</div><div class='v'>{_esc(desc)}</div></div>
      <div class='kv'><div class='k'>Assumptions</div><div class='v'>{("<ul class='ul'>" + assumptions_html + "</ul>") if assumptions_html else "None listed."}</div></div>
      {evidence_html}
      <div class='kv'><div class='k'>Submitted</div><div class='v'>{_esc(date)}</div></div>
      <div class='kv'><div class='k'>Animation</div><div class='v'>{anim}</div></div>
      <div class='kv'><div class='k'>Image/Diagram</div><div class='v'>{img}</div></div>
      {chain_link}
    </div>
  </div>
</section>
"""
        )

    body = f"""
<div class='layout layout--single'>
  <section class='maincol'>

<div class='hero'>
  <div class='hero__left'>
    <h1>All Submissions</h1>
    <p>Every equation submitted through the pipeline — scored, reviewed, and tracked. Promoted entries carry a chain certificate.</p>
  </div>
  <div class='hero__right'>
    <div class='statbox'>
      <div class='stat'>
        <div class='stat__num'>{_esc(total)}</div>
        <div class='stat__label'>Total submissions</div>
      </div>
      <div class='stat'>
        <div class='stat__num'>{_esc(promoted)}</div>
        <div class='stat__label'>Promoted</div>
      </div>
      <div class='stat'>
        <div class='stat__num'>{_esc(ready)}</div>
        <div class='stat__label'>Ready</div>
      </div>
      <div class='stat'>
        <div class='stat__num'>{_esc(review)}</div>
        <div class='stat__label'>In review</div>
      </div>
    </div>
  </div>
</div>

<div class='panel'>
  <h2>Pipeline</h2>
  <ul>
    <li><strong>Submit</strong> &rarr; equation enters queue with status <em>needs-review</em></li>
    <li><strong>Score</strong> &rarr; heuristic rubric (T/P/V/A out of 70, normalized to 100). Threshold: 68 = ready</li>
    <li><strong>Promote</strong> &rarr; equation moves to the ranked leaderboard + chain certificate</li>
  </ul>
</div>

<div class='panel'>
  <h2>CLI</h2>
  <pre><code>python tools/submit_equation.py --name "..." --equation "..." --description "..." --source "..." --assumption "..."
python tools/score_submission.py
python tools/promote_submission.py --submission-id sub-... --from-review</code></pre>
</div>

<div id='submissionCards' class='cardrow'>
{''.join(cards) if cards else "<p class='muted'>No submissions yet.</p>"}
</div>

  </section>
</div>
"""

    updated = datetime.now().strftime("%Y-%m-%d %H:%M")
    (docs / "submissions.html").write_text(_page("TopEquations — All Submissions", body, updated), encoding="utf-8")


def build_certificates(repo_root: Path, docs: Path) -> None:
    src_cert = repo_root / "data" / "certificates" / "equation_certificates.json"
    src_receipt = repo_root / "data" / "certificates" / "chain_publish_receipt.json"
    cert = _load_json_safe(src_cert, {"entries": []})
    receipt = _load_json_safe(src_receipt, {})

    dst_dir = docs / "data" / "certificates"
    dst_dir.mkdir(parents=True, exist_ok=True)
    if src_cert.exists():
        (dst_dir / "equation_certificates.json").write_text(src_cert.read_text(encoding="utf-8"), encoding="utf-8")
    if src_receipt.exists():
        (dst_dir / "chain_publish_receipt.json").write_text(src_receipt.read_text(encoding="utf-8"), encoding="utf-8")

    rows: list[str] = []
    for e in cert.get("entries", []):
        eq_id = str(e.get("token_id", "")).strip()
        if not eq_id:
            continue
        rows.append(
            f"""
<tr id='{_esc(eq_id)}'>
  <td><code>{_esc(eq_id)}</code></td>
  <td>{_esc(e.get('name', ''))}</td>
  <td>{_esc(e.get('score', ''))}</td>
  <td><code>{_esc(str(e.get('metadata_hash', ''))[:20])}…</code></td>
  <td><code>{_esc(str(e.get('equation_hash', ''))[:20])}…</code></td>
</tr>
"""
        )

    published = receipt.get("published_at", "-")
    count = receipt.get("count", cert.get("count", 0))
    node_url = receipt.get("node_url", "-")

    body = f"""
<div class='layout layout--single'>
  <section class='maincol'>

<div class='hero'>
  <div class='hero__left'>
    <h1>Equation Certificates</h1>
    <p>Signed equation records used for chain provenance and version tracking.</p>
  </div>
</div>

<div class='panel'>
  <div><strong>Published at:</strong> {_esc(published)}</div>
  <div><strong>Node endpoint:</strong> <code>{_esc(node_url)}</code></div>
  <div><strong>Certificates:</strong> {_esc(count)}</div>
  <div class='muted' style='margin-top:8px'>Data files: <code>data/certificates/equation_certificates.json</code> and <code>data/certificates/chain_publish_receipt.json</code></div>
</div>

<div class='panel'>
  <h2>Certificate Index</h2>
  <div style='overflow:auto'>
  <table class='table'>
    <thead>
      <tr>
        <th>Equation ID</th>
        <th>Name</th>
        <th>Score</th>
        <th>Metadata hash</th>
        <th>Equation hash</th>
      </tr>
    </thead>
    <tbody>
      {''.join(rows)}
    </tbody>
  </table>
  </div>
</div>

  </section>
</div>
"""

    updated = datetime.now().strftime("%Y-%m-%d %H:%M")
    (docs / "certificates.html").write_text(_page("TopEquations — Certificates", body, updated), encoding="utf-8")


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    docs = repo_root / "docs"
    (docs / "assets").mkdir(parents=True, exist_ok=True)

    build_index(repo_root, docs)
    build_core(repo_root, docs)
    build_famous(repo_root, docs)
    build_leaderboard(repo_root, docs)
    build_certificates(repo_root, docs)
    build_submissions(repo_root, docs)
    build_harvest(repo_root, docs)

    print("Built docs/*.html")


if __name__ == "__main__":
    main()
