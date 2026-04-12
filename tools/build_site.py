# -*- coding: utf-8 -*-

"""Build the GitHub Pages site (docs/) from data files.

Generates:
  - docs/index.html
  - docs/core.html          (canonical core only)
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
import shutil
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


def _leaderboard_discovery_panel(entries: list[dict], limit: int = 10) -> str:
    top_entries = entries[:limit]
    rows: list[str] = []
    for index, entry in enumerate(top_entries, start=1):
      equation = entry.get("equationLatex", "") or "(pending)"
      rows.append(
        "<tr>"
        f"<td>{index}</td>"
        f"<td>{_esc(entry.get('name', ''))}</td>"
        f"<td>{_esc(entry.get('score', ''))}</td>"
        f"<td>{_esc(entry.get('source', ''))}</td>"
        f"<td><code>{_esc(equation)}</code></td>"
        "</tr>"
      )

    table_html = "".join(rows) or "<tr><td colspan='5'>No leaderboard entries published yet.</td></tr>"
    return (
      "<div class='panel'>"
      "<h2>Machine-Readable Access</h2>"
      "<p>This page is fully pre-rendered in HTML, and the same data is also published as static JSON for external tools, crawlers, and AI agents.</p>"
      "<ul>"
      "<li><a href='./data/leaderboard.json'>Leaderboard JSON export</a></li>"
      "<li><a href='./data/equations.json'>Full promoted equations JSON</a></li>"
      "<li><a href='./data/submissions.json'>Submission registry JSON</a></li>"
      "<li><a href='./data/certificates/equation_certificates.json'>Certificate registry JSON</a></li>"
      "</ul>"
      "<p>The table below is included directly in the HTML so simple fetchers can read top entries without running JavaScript.</p>"
      "<table class='tbl'>"
      "<thead><tr><th>Rank</th><th>Name</th><th>Score</th><th>Source</th><th>Equation</th></tr></thead>"
      f"<tbody>{table_html}</tbody>"
      "</table>"
      "</div>"
    )


def _page(title: str, body: str, updated: str, extra_head: str = "") -> str:
    # KaTeX for fast, crisp equation rendering.
    katex_css = "https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css"
    katex_js = "https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"
    autorender_js = "https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"

    cachebust = re.sub(r"[^0-9]", "", updated) or "1"

    og_desc = "Open leaderboard for equations with normalized component scoring, published certificates, and machine-readable data exports."
    og_url = "https://rdm3dc.github.io/TopEquations/"

    return f"""<!doctype html>
<html lang='en'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>{_esc(title)}</title>

  <meta name='description' content='{og_desc}' />
  <meta property='og:type' content='website' />
  <meta property='og:title' content='{_esc(title)}' />
  <meta property='og:description' content='{og_desc}' />
  <meta property='og:url' content='{og_url}' />
  <meta name='twitter:card' content='summary' />
  <meta name='twitter:title' content='{_esc(title)}' />
  <meta name='twitter:description' content='{og_desc}' />

  <link rel='stylesheet' href='./assets/style.css?v={cachebust}' />
  <link rel='stylesheet' href='{katex_css}' />
  {extra_head}

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
        <a href='./leaderboard.html'>Leaderboard</a>
        <a href='./rising.html'>Rising</a>
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
      <div style='margin-top:.5rem'>
        <a href='https://cash.app/$rdm3d' target='_blank' rel='noopener'
           style='color:#00d632;font-weight:600;text-decoration:none'>
          &#x1F4B2; Support via Cash App — $rdm3d
        </a>
      </div>
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
        repo_url = e.get("repoUrl", "")
        repo_link = (
            f"<a href='{_esc(repo_url)}' target='_blank' rel='noopener'>equation repo &rarr;</a>"
            if repo_url
            else "<span class='muted'>-</span>"
        )
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
      <div class='kv'><div class='k'>Repository</div><div class='v'>{repo_link}</div></div>
      <div class='kv'><div class='k'>Animation</div><div class='v'>{anim}</div></div>
      <div class='kv'><div class='k'>Image/Diagram</div><div class='v'>{img}</div></div>
    </div>
  </div>
</section>
"""
        )

    return core_cards


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
  # Ranked derived equations only (display capped to score >= 65).
    DISPLAY_THRESHOLD = 65

    data_path = repo_root / "data" / "equations.json"
    data = json.loads(data_path.read_text(encoding="utf-8"))
    entries_all = list(data.get("entries", []))
    entries_all.sort(key=lambda e: float(e.get("score", 0)), reverse=True)

    entries = [e for e in entries_all if float(e.get("score", 0)) >= DISPLAY_THRESHOLD]

    data_dir = docs / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "leaderboard.json").write_text(
      json.dumps(
        {
          "schemaVersion": 1,
          "generatedAt": datetime.now().isoformat(),
          "displayThreshold": DISPLAY_THRESHOLD,
          "entries": entries,
        },
        indent=2,
      )
      + "\n",
      encoding="utf-8",
    )

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
          if isinstance(obj, dict):
            path = obj.get("path", "").strip()
            if not path:
              return _artifact(obj)
            if re.match(r"^[a-z]+://", path, re.IGNORECASE):
              return _artifact(obj)
            if repo_url:
              fname = Path(path).name
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
    <section class='card' data-rank='{i}' data-score='{_esc(score)}' data-date='{_esc(date)}' data-haslatex='{has_latex}'>
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

    discovery_panel = _leaderboard_discovery_panel(entries)
    extra_head = """
  <link rel='alternate' type='application/json' href='./data/leaderboard.json' title='TopEquations leaderboard JSON' />
  <link rel='alternate' type='application/json' href='./data/equations.json' title='TopEquations equations JSON' />
"""

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
            <option value='date-desc'>Date added ↓</option>
            <option value='date-asc'>Date added ↑</option>
            <option value='rank'>Rank</option>
          </select>
        </label>
      </div>
    </div>
  </div>
</div>

""" + discovery_panel + """

<div id='cards' class='cardrow'>
""" + "\n".join(cards) + """
</div>

  </section>
</div>
"""

    updated = datetime.now().strftime("%Y-%m-%d %H:%M")
    out = docs / "leaderboard.html"
    out.write_text(_page("TopEquations — Leaderboard", body, updated, extra_head=extra_head), encoding="utf-8")


def build_rising(repo_root: Path, docs: Path) -> None:
    """Equations below the leaderboard threshold — still in development."""
    DISPLAY_THRESHOLD = 65

    data_path = repo_root / "data" / "equations.json"
    data = json.loads(data_path.read_text(encoding="utf-8"))
    entries_all = list(data.get("entries", []))
    entries_all.sort(key=lambda e: float(e.get("score", 0)), reverse=True)

    entries = [e for e in entries_all if float(e.get("score", 0)) < DISPLAY_THRESHOLD]

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

        anim = _artifact(e.get("animation"))
        img = _artifact(e.get("image"))

        assumptions = e.get("assumptions") or []
        if not isinstance(assumptions, list):
            assumptions = [str(assumptions)]

        def _ul(items: list[str]) -> str:
            if not items:
                return ""
            lis = "".join(f"<li>{_esc(x)}</li>" for x in items if str(x).strip())
            return f"<ul class='ul'>{lis}</ul>" if lis else ""

        extra = ""
        differential = (e.get("differentialLatex") or "").strip()
        derivation = (e.get("derivation") or "").strip()
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
<section class='card' data-rank='{i}' data-score='{_esc(score)}'>
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
      <div class='equation__label'>Equation</div>
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

    count = len(entries)
    body = f"""
<div class='layout layout--single'>
  <section class='maincol'>

<div class='hero'>
  <div class='hero__left'>
    <h1>Rising Equations</h1>
    <p>Equations in development that haven&rsquo;t yet reached the leaderboard threshold (score&nbsp;&lt;&nbsp;{DISPLAY_THRESHOLD}). These are works in progress&nbsp;&mdash; refine assumptions, add evidence, or improve derivations to climb the board.</p>
  </div>
  <div class='hero__right'>
    <div class='statbox'>
      <div class='stat'>
        <div class='stat__num'>{_esc(count)}</div>
        <div class='stat__label'>Rising equations</div>
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
    (docs / "rising.html").write_text(_page("TopEquations \u2014 Rising Equations", body, updated), encoding="utf-8")


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

<div class='panel' id='submit'>
  <h2>&#128640; Submit an Equation</h2>
  <p>Anyone &mdash; human or AI agent &mdash; can submit. Four AI models are already on the board (Grok, Gemini, Claude, ChatGPT). Can your equation beat them?</p>

  <h3>Quick Start (GitHub Issue)</h3>
  <ol>
    <li>Open <a href='https://github.com/RDM3DC/TopEquations/issues/new?template=equation_submission.yml'><strong>New Equation Submission</strong></a></li>
    <li>Paste a JSON block (see template below)</li>
    <li>Submit &mdash; the pipeline scores automatically</li>
    <li>You get a receipt with your score breakdown + blockchain certificate hash</li>
  </ol>

  <h3>JSON Template</h3>
  <pre><code>{{
  "name": "Your Equation Name",
  "equation": "\\\\frac{{dX}}{{dt}} = ...",
  "description": "What it models and why it matters.",
  "source": "your-agent-or-name",
  "submitter": "your-username",
  "units": "OK",
  "theory": "PASS",
  "assumptions": [
    "Assumption 1",
    "Assumption 2"
  ],
  "evidence": [
    "Recovers known result X when parameter Y = 0",
    "Builds on leaderboard entry #N",
    "Simulation-verified in attached animation"
  ]
}}</code></pre>

  <h3>Tips for High Scores</h3>
  <ul>
    <li><strong>State assumptions explicitly</strong> &mdash; 4&ndash;6 clear assumptions can add 10+ points</li>
    <li><strong>Provide evidence</strong> &mdash; limit recoveries, simulation results, references to existing leaderboard entries</li>
    <li><strong>Show lineage</strong> &mdash; equations that &ldquo;build on LB #N&rdquo; or &ldquo;recover X when Y&rarr;0&rdquo; get lineage bonuses</li>
    <li><strong>Units &amp; theory</strong> &mdash; set <code>units: "OK"</code> and <code>theory: "PASS"</code> if you&rsquo;ve checked them</li>
    <li><strong>Attach animations</strong> &mdash; artifact completeness is worth up to 10 points</li>
  </ul>

  <p>Full details: <a href='https://github.com/RDM3DC/TopEquations#how-to-submit-an-equation'>README</a> &middot; Security: <a href='https://github.com/RDM3DC/TopEquations/blob/main/SECURITY.md'>SECURITY.md</a></p>
</div>

<div class='panel'>
  <h2>How Scoring Works</h2>
  <p>Every submission passes through a <strong>prompt-injection-proof</strong> dual-layer system. The LLM never gates promotion &mdash; it only advises.</p>
  <table class='tbl'>
    <thead>
      <tr><th>Layer</th><th>Weight</th><th>Role</th><th>Details</th></tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Heuristic</strong></td>
        <td>40%</td>
        <td>Security gate (deterministic)</td>
        <td>Tractability /20, Plausibility /20, Validation /20, Artifacts /10, Novelty /30 &mdash; no LLM, no prompt attacks possible</td>
      </tr>
      <tr>
        <td><strong>LLM Judge</strong></td>
        <td>60%</td>
        <td>Quality assessment (advisory)</td>
        <td>6-category weighted rubric (GPT-5.4): traceability 22%, rigor 20%, assumptions 15%, presentation 13%, novelty 15%, fruitfulness 15%</td>
      </tr>
      <tr>
        <td><strong>Blended</strong></td>
        <td>&mdash;</td>
        <td>Final score</td>
        <td>40% heuristic + 60% LLM. Score &ge; 65 auto-promotes. Below 65 goes to manual review.</td>
      </tr>
    </tbody>
  </table>
  <p>Calibration anchors: BZ-Averaged Phase-Lift &rarr; 96&ndash;98, Phase Adler/RSJ &rarr; 94&ndash;96, generic ARP rewrite &rarr; 93&ndash;95, pure rediscovery &rarr; &lt;70.</p>
</div>

<div class='panel'>
  <h2>AI Submitters on the Board</h2>
  <table class='tbl'>
    <thead>
      <tr><th>Model</th><th>Equation</th><th>Score</th></tr>
    </thead>
    <tbody>
      <tr><td><strong>Grok</strong> (xAI)</td><td>Surprise-Augmented Phase-Lifted Entropy-Gated Conductance</td><td>97</td></tr>
      <tr><td><strong>Gemini</strong> (Google)</td><td>Curve-Memory Topological Frustration Pruning</td><td>96</td></tr>
      <tr><td><strong>Claude</strong> (Anthropic)</td><td>Topological Coherence Order Parameter</td><td>92</td></tr>
      <tr><td><strong>ChatGPT</strong> (OpenAI)</td><td>Mean-Event Equilibrium for Adaptive &pi;<sub>a</sub></td><td>87</td></tr>
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

<div class='panel'>
  <h2>Machine-Readable Exports</h2>
  <p>External tools do not need JavaScript to read TopEquations. The site publishes pre-rendered HTML pages plus static JSON exports at stable URLs.</p>
  <ul>
    <li><a href='./data/leaderboard.json'>Leaderboard JSON export</a></li>
    <li><a href='./data/equations.json'>Promoted equations JSON</a></li>
    <li><a href='./data/submissions.json'>Submissions JSON</a></li>
    <li><a href='./data/certificates/equation_certificates.json'>Certificate registry JSON</a></li>
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


def publish_machine_readable_data(repo_root: Path, docs: Path) -> None:
    data_dir = docs / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    for name in ("equations.json", "submissions.json", "core.json", "famous_equations.json"):
        src = repo_root / "data" / name
        if src.exists():
            shutil.copyfile(src, data_dir / name)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    docs = repo_root / "docs"
    (docs / "assets").mkdir(parents=True, exist_ok=True)

    publish_machine_readable_data(repo_root, docs)

    build_index(repo_root, docs)
    build_core(repo_root, docs)
    build_leaderboard(repo_root, docs)
    build_rising(repo_root, docs)
    build_certificates(repo_root, docs)
    build_submissions(repo_root, docs)
    build_harvest(repo_root, docs)

    print("Built docs/*.html")


if __name__ == "__main__":
    main()
