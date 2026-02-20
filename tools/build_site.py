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


def _artifact(val: dict | None) -> str:
    if not val:
        return "planned"
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
            {{left: '\\[', right: '\\]', display: true}},
            {{left: '$', right: '$', display: false}},
            {{left: '\\(', right: '\\)', display: false}},
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
          <div class='brand__sub'>Curated leaderboard + harvested registry</div>
        </div>
      </div>
      <nav class='nav'>
        <a href='./index.html'>Home</a>
        <a href='./core.html'>Core</a>
        <a href='./famous.html'>Famous</a>
        <a href='./leaderboard.html'>Leaderboard</a>
        <a href='./harvest.html'>All harvested</a>
        <a class='nav__ghost' href='https://github.com/RDM3DC/TopEquations' target='_blank' rel='noopener'>GitHub</a>
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
    core = json.loads(core_path.read_text(encoding="utf-8"))
    core_entries = list(core.get("entries", []))

    core_cards: list[str] = []
    for e in core_entries:
        name = e.get("name", "")
        eq = e.get("equationLatex", "") or "(pending)"
        desc = e.get("description", "")
        src = e.get("source", "")
        url = e.get("sourceUrl", "")
        core_cards.append(
            f"""
<section class='card'>
  <div class='card__rank'>CORE</div>
  <div class='card__body'>
    <div class='card__head'>
      <h2 class='card__title'>{_esc(name)}</h2>
      <div class='card__meta'>
        <span class='pill pill--neutral'>Pinned</span>
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
      <div class='kv'><div class='k'>Canonical source</div><div class='v'><a href='{_esc(url)}' target='_blank' rel='noopener'>{_esc(url)}</a></div></div>
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


def build_famous(repo_root: Path, docs: Path) -> None:
    tier_lists = _extract_tier_lists(repo_root)
    famous_items = tier_lists.get("famous", [])

    famous_cards: list[str] = []
    for idx, item in enumerate(famous_items, start=1):
        m = re.search(r"<b>(.*?)</b>", item, flags=re.I | re.S)
        title = m.group(1).strip() if m else f"Famous Equation {idx}"
        body_html = re.sub(r"<b>.*?</b>", "", item, count=1, flags=re.I | re.S).strip()
        body_html = body_html.lstrip("<br/>").strip()

        # Extract one primary math expression to keep card equation format consistent.
        equation_expr = ""
        for pat in (r"\$\$(.+?)\$\$", r"\\\((.+?)\\\)", r"\$(.+?)\$"):
            mm = re.search(pat, body_html, flags=re.S)
            if mm:
                equation_expr = mm.group(1).strip()
                break
        if not equation_expr:
            equation_expr = "(pending)"

        # Description should be plain text to avoid KaTeX error styling.
        desc_text = re.sub(r"<br\s*/?>", " ", body_html, flags=re.I)
        desc_text = re.sub(r"<[^>]+>", " ", desc_text)
        desc_text = re.sub(r"\\\(.+?\\\)", " ", desc_text)
        desc_text = re.sub(r"\$\$.+?\$\$", " ", desc_text, flags=re.S)
        desc_text = re.sub(r"\s+", " ", desc_text).strip()
        if not desc_text:
            desc_text = "Classic equation reformulated in your adjusted framework."

        famous_cards.append(
            f"""
<section class='card'>
  <div class='card__rank'>F{idx}</div>
  <div class='card__body'>
    <div class='card__head'>
      <h2 class='card__title'>{_esc(title)}</h2>
      <div class='card__meta'>
        <span class='badge badge--score'>Famous</span>
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
      <div class='kv'><div class='k'>List index</div><div class='v'>F{idx}</div></div>
      <div class='kv'><div class='k'>Category</div><div class='v'>Famous (Adjusted)</div></div>
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
    <p>Curated classical forms rewritten in your Phase-Lift / Adaptive-π style.</p>
  </div>
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
    <p>Pinned, non-ranked anchor equations.</p>
  </div>
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
    # Ranked derived equations only.
    data_path = repo_root / "data" / "equations.json"
    data = json.loads(data_path.read_text(encoding="utf-8"))
    entries = list(data.get("entries", []))
    entries.sort(key=lambda e: float(e.get("score", 0)), reverse=True)

    cards = []
    for i, e in enumerate(entries, start=1):
        name = e.get("name", "")
        eq = e.get("equationLatex", "") or "(pending)"
        src = e.get("source", "")
        desc = e.get("description", "")
        score = e.get("score", "")
        units = e.get("units", "")
        theory = e.get("theory", "")
        anim = _artifact(e.get("animation"))
        img = _artifact(e.get("image"))
        date = e.get("date", "")

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
            extra += f"<div class='kv'><div class='k'>Differential form</div><div class='v'>$$${_esc(differential)}$$</div></div>"
        if derivation:
            extra += f"<div class='kv'><div class='k'>Derivation bridge</div><div class='v'>{_esc(derivation)}</div></div>"
        if assumptions:
            extra += f"<div class='kv'><div class='k'>Assumptions</div><div class='v'>{_ul([str(x) for x in assumptions])}</div></div>"

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
    data = json.loads((repo_root / "data" / "equations.json").read_text(encoding="utf-8"))
    n = len(data.get("entries", []))

    core = json.loads((repo_root / "data" / "core.json").read_text(encoding="utf-8"))
    core_n = len(core.get("entries", []))

    harvest = json.loads((repo_root / "data" / "harvest" / "equation_harvest.json").read_text(encoding="utf-8"))
    uniq = harvest.get("stats", {}).get("unique", "?")

    body = f"""
<div class='hero hero--home'>
  <div class='hero__left'>
    <h1>TopEquations</h1>
    <p><strong>Canonical Core</strong> and <strong>Ranked Derived</strong> are split into dedicated pages.</p>
    <div class='cta'>
      <a class='btn' href='./core.html'>Canonical Core</a>
      <a class='btn btn--ghost' href='./famous.html'>Famous Equations</a>
      <a class='btn btn--ghost' href='./leaderboard.html'>Ranked Derived</a>
      <a class='btn btn--ghost' href='./harvest.html'>Browse Harvest</a>
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
    </div>
  </div>
</div>

<div class='panel'>
  <h2>Structure</h2>
  <ul>
    <li><strong>Canonical Core</strong> lives in <code>data/core.json</code> and links out to Canonical Core docs.</li>
    <li><strong>Ranked derived equations</strong> live in <code>data/equations.json</code>.</li>
    <li><strong>Raw harvest</strong> lives in <code>data/harvest/equation_harvest.json</code> (deduped).</li>
  </ul>
</div>
"""

    updated = datetime.now().strftime("%Y-%m-%d %H:%M")
    (docs / "index.html").write_text(_page("TopEquations", body, updated), encoding="utf-8")


def build_harvest(repo_root: Path, docs: Path) -> None:
    # Copy harvest json into docs so the client can fetch it.
    src_json = repo_root / "data" / "harvest" / "equation_harvest.json"
    dst_json = docs / "data" / "harvest" / "equation_harvest.json"
    dst_json.parent.mkdir(parents=True, exist_ok=True)
    dst_json.write_text(src_json.read_text(encoding="utf-8"), encoding="utf-8")

    body = """
<div class='hero'>
  <div class='hero__left'>
    <h1>All harvested equations</h1>
    <p>~15k deduped candidates harvested from local RDM3DC repos. Default view is <strong>LaTeX-only</strong> (best looking).</p>
  </div>
  <div class='hero__right'>
    <div class='controls'>
      <div class='search'>
        <input id='harvestSearch' type='search' placeholder='Search equation text / source…' />
      </div>
      <div class='row'>
        <label class='check'>
          <input id='harvestLatexOnly' type='checkbox' checked />
          <span>LaTeX only</span>
        </label>
      </div>
    </div>
  </div>
</div>

<div class='panel'>
  <div class='muted'>Source file: <code>data/harvest/equation_harvest.json</code></div>
  <div id='harvestMeta' class='muted' style='margin-top:8px'>Loading…</div>
</div>

<div id='harvestList' class='cardrow'></div>

<script defer src='./assets/harvest.js'></script>
"""

    updated = datetime.now().strftime("%Y-%m-%d %H:%M")
    (docs / "harvest.html").write_text(_page("TopEquations — Harvest", body, updated), encoding="utf-8")


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    docs = repo_root / "docs"
    (docs / "assets").mkdir(parents=True, exist_ok=True)

    build_index(repo_root, docs)
    build_core(repo_root, docs)
    build_famous(repo_root, docs)
    build_leaderboard(repo_root, docs)
    build_harvest(repo_root, docs)

    print("Built docs/*.html")


if __name__ == "__main__":
    main()
