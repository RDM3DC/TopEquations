"""Build the GitHub Pages site (docs/) from data files.

Generates:
  - docs/index.html
  - docs/leaderboard.html   (curated list = data/equations.json)
  - docs/harvest_preview.html

Usage:
  python tools/build_site.py

This is intentionally dependency-free.
"""

from __future__ import annotations

import html
import json
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
    return f"""<!doctype html>
<html lang='en'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>{_esc(title)}</title>
  <link rel='stylesheet' href='./assets/style.css' />
  <script defer src='./assets/app.js'></script>
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
        <a href='./leaderboard.html'>Leaderboard</a>
        <a href='./harvest_preview.html'>Harvest preview</a>
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


def build_leaderboard(repo_root: Path, docs: Path) -> None:
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

        cards.append(
            f"""
<section class='card'>
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
      <pre class='equation__tex'>{_esc(eq)}</pre>
    </div>

    <div class='grid'>
      <div class='kv'><div class='k'>Source</div><div class='v'>{_esc(src)}</div></div>
      <div class='kv'><div class='k'>Date</div><div class='v'>{_esc(date)}</div></div>
      <div class='kv'><div class='k'>Animation</div><div class='v'>{anim}</div></div>
      <div class='kv'><div class='k'>Image/Diagram</div><div class='v'>{img}</div></div>
    </div>

    <p class='card__desc'>{_esc(desc)}</p>
  </div>
</section>
"""
        )

    body = """
<div class='hero'>
  <div class='hero__left'>
    <h1>Leaderboard</h1>
    <p>Curated list of the current top equations. Badges show score + units/theory sanity.</p>
  </div>
  <div class='hero__right'>
    <div class='search'>
      <input id='searchBox' type='search' placeholder='Search name / source / equation…' />
    </div>
  </div>
</div>

<div id='cards'>
""" + "\n".join(cards) + """
</div>
"""

    updated = datetime.now().strftime("%Y-%m-%d %H:%M")
    out = docs / "leaderboard.html"
    out.write_text(_page("TopEquations — Leaderboard", body, updated), encoding="utf-8")


def build_index(repo_root: Path, docs: Path) -> None:
    data = json.loads((repo_root / "data" / "equations.json").read_text(encoding="utf-8"))
    n = len(data.get("entries", []))

    harvest = json.loads((repo_root / "data" / "harvest" / "equation_harvest.json").read_text(encoding="utf-8"))
    uniq = harvest.get("stats", {}).get("unique", "?")

    body = f"""
<div class='hero hero--home'>
  <div class='hero__left'>
    <h1>TopEquations</h1>
    <p>A polished GitHub Pages view of the curated leaderboard, plus a raw harvested registry for discovery.</p>
    <div class='cta'>
      <a class='btn' href='./leaderboard.html'>View Leaderboard</a>
      <a class='btn btn--ghost' href='./harvest_preview.html'>Harvest Preview</a>
    </div>
  </div>
  <div class='hero__right'>
    <div class='statbox'>
      <div class='stat'>
        <div class='stat__num'>{_esc(n)}</div>
        <div class='stat__label'>Curated equations</div>
      </div>
      <div class='stat'>
        <div class='stat__num'>{_esc(uniq)}</div>
        <div class='stat__label'>Harvested unique candidates</div>
      </div>
    </div>
  </div>
</div>

<div class='panel'>
  <h2>How it works</h2>
  <ul>
    <li><strong>Curated leaderboard</strong> lives in <code>data/equations.json</code> (human-reviewed).</li>
    <li><strong>Raw harvest</strong> lives in <code>data/harvest/equation_harvest.json</code> (machine-extracted, deduped).</li>
    <li>Pages is served from <code>/docs</code>.</li>
  </ul>
</div>
"""

    updated = datetime.now().strftime("%Y-%m-%d %H:%M")
    (docs / "index.html").write_text(_page("TopEquations", body, updated), encoding="utf-8")


def build_harvest_preview(repo_root: Path, docs: Path) -> None:
    preview_md = (repo_root / "data" / "harvest" / "equation_harvest_preview.md").read_text(encoding="utf-8", errors="ignore")

    # super-light markdown-to-html for our preview (headers + bullets + inline code)
    lines = preview_md.splitlines()
    html_lines = []
    for ln in lines:
        if ln.startswith("# "):
            html_lines.append(f"<h1>{_esc(ln[2:])}</h1>")
        elif ln.startswith("## "):
            html_lines.append(f"<h2>{_esc(ln[3:])}</h2>")
        elif ln.startswith("- "):
            # group list items
            html_lines.append(f"<li>{_esc(ln[2:])}</li>")
        elif ln.strip().startswith("`"):
            html_lines.append(f"<pre class='equation__tex'>{_esc(ln.strip().strip('`'))}</pre>")
        elif ln.strip() == "":
            html_lines.append("")
        else:
            html_lines.append(f"<p>{_esc(ln)}</p>")

    body = """
<div class='hero'>
  <div class='hero__left'>
    <h1>Harvest preview</h1>
    <p>A small peek at the raw harvested registry (deduped). This is intentionally lightweight.</p>
  </div>
</div>

<div class='panel'>
""" + "\n".join(html_lines) + """
</div>
"""

    updated = datetime.now().strftime("%Y-%m-%d %H:%M")
    (docs / "harvest_preview.html").write_text(_page("TopEquations — Harvest preview", body, updated), encoding="utf-8")


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    docs = repo_root / "docs"
    (docs / "assets").mkdir(parents=True, exist_ok=True)

    build_index(repo_root, docs)
    build_leaderboard(repo_root, docs)
    build_harvest_preview(repo_root, docs)

    print("Built docs/*.html")


if __name__ == "__main__":
    main()
