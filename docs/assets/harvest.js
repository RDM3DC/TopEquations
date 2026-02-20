// Harvest page: fetch JSON and lazy-render a lot of equations with KaTeX.
(function(){
  const listEl = document.getElementById('harvestList');
  const metaEl = document.getElementById('harvestMeta');
  const searchEl = document.getElementById('harvestSearch');
  const latexOnlyEl = document.getElementById('harvestLatexOnly');
  if(!listEl || !metaEl || !searchEl) return;

  const SRC = './data/harvest/equation_harvest.json';
  const SCORED = './data/harvest/scored_candidates.json';

  let entries = [];
  let filtered = [];
  let cursor = 0;
  const PAGE = 120;

  // Default to LaTeX-only view (best-looking equations)
  let kindMode = 'latex';

  function esc(s){
    return (''+s)
      .replaceAll('&','&amp;')
      .replaceAll('<','&lt;')
      .replaceAll('>','&gt;');
  }

  function compactPath(p){
    if(!p) return 'unknown';
    const parts = String(p).split('\\');
    if(parts.length <= 3) return p;
    return `${parts[parts.length-3]}\\${parts[parts.length-2]}\\${parts[parts.length-1]}`;
  }

  function inferTitle(eq, idx){
    const s = String(eq || '').trim();
    const m = s.match(/^\s*([^=]{1,70})=/);
    if(m){
      return m[1].replace(/\\[a-zA-Z]+/g, '').replace(/[{}]/g, '').trim() || `Harvested Equation #${idx}`;
    }
    return `Harvested Equation #${idx}`;
  }

  function inferDescription(eq, src){
    const s = String(eq || '');
    const srcHint = compactPath(src);
    let kind = 'symbolic relation';
    if(/d\/?dt|\\dot|\\ddot/.test(s)) kind = 'time-evolution relation';
    else if(/\\partial|\\nabla|grad|div|curl/i.test(s)) kind = 'field/gradient relation';
    else if(/\\int|\\sum|\\prod/.test(s)) kind = 'integral or aggregate relation';
    else if(/=/.test(s)) kind = 'algebraic identity/equation';
    return `Auto-described ${kind} harvested from ${srcHint}.`;
  }

  function renderChunk(){
    const end = Math.min(cursor + PAGE, filtered.length);
    if(cursor >= end) return;

    const frag = document.createDocumentFragment();

    for(let i=cursor;i<end;i++){
      const e = filtered[i];
      const rank = i + 1;
      const kind = (e.kind || 'equation');
      const isLatex = kind.toLowerCase().includes('latex');
      const src = e.source || '';
      const ref = src ? `${src}${e.line_start ? `#L${e.line_start}` : ''}` : 'harvest-entry';
      const eqLabel = isLatex ? 'Derived equation' : 'Expression';
      const eqBody = isLatex ? `$$${esc(e.equation || '')}$$` : esc(e.equation || '');
      const title = inferTitle(e.equation, rank);
      const desc = inferDescription(e.equation, src);

      const card = document.createElement('section');
      card.className = 'card';
      card.innerHTML = `
        <div class='card__rank'>#${rank}</div>
        <div class='card__body'>
          <div class='card__head'>
            <h2 class='card__title'>${esc(title)}</h2>
            <div class='card__meta'>
              <span class='badge badge--score'>${esc(kind)}</span>
              <span class='pill pill--neutral'>${esc(e.source_type || '')}</span>
            </div>
          </div>
          <div class='equation'>
            <div class='equation__label'>${eqLabel}</div>
            <div class='equation__tex'>${eqBody}</div>
          </div>
          <div class='card__sub'>Reference: <span class='muted'>${esc(ref)}</span></div>
          <div class='grid'>
            <div class='kv'><div class='k'>Description</div><div class='v'>${esc(desc)}</div></div>
            <div class='kv'><div class='k'>Source</div><div class='v'>${esc(src || 'unknown')}</div></div>
            <div class='kv'><div class='k'>Line</div><div class='v'>${esc(e.line_start || '')}</div></div>
            <div class='kv'><div class='k'>SHA1</div><div class='v'>${esc((e.sha1||'').slice(0,12) || 'n/a')}</div></div>
            <div class='kv'><div class='k'>Source type</div><div class='v'>${esc(e.source_type || 'file')}</div></div>
          </div>
        </div>
      `;
      frag.appendChild(card);
    }

    listEl.appendChild(frag);
    cursor = end;

    // KaTeX auto-render for the newly inserted nodes.
    if(window.renderMathInElement){
      window.renderMathInElement(listEl, {
        delimiters: [
          {left: '$$', right: '$$', display: true},
          {left: '$', right: '$', display: false},
          {left: '\\[', right: '\\]', display: true},
          {left: '\\(', right: '\\)', display: false},
        ],
        throwOnError: false,
      });
    }
  }

  function resetFilter(){
    const q = (searchEl.value || '').trim().toLowerCase();
    cursor = 0;
    listEl.innerHTML = '';

    const base = (kindMode === 'latex')
      ? entries.filter(e => (e.kind||'').toLowerCase().includes('latex'))
      : entries;

    if(!q){
      filtered = base;
    }else{
      filtered = base.filter(e => {
        const s = ((e.equation||'') + ' ' + (e.source||'')).toLowerCase();
        return s.includes(q);
      });
    }

    metaEl.textContent = `${filtered.length.toLocaleString()} matches` + (kindMode==='latex' ? ' (LaTeX)' : '');
    renderChunk();
  }

  const io = new IntersectionObserver((items) => {
    for(const it of items){
      if(it.isIntersecting){
        renderChunk();
      }
    }
  }, {rootMargin: '900px'});

  const sentinel = document.createElement('div');
  sentinel.style.height = '1px';
  listEl.after(sentinel);
  io.observe(sentinel);

  searchEl.addEventListener('input', () => {
    // debounce-ish
    clearTimeout(searchEl._t);
    searchEl._t = setTimeout(resetFilter, 120);
  });

  if(latexOnlyEl){
    latexOnlyEl.addEventListener('change', () => {
      kindMode = latexOnlyEl.checked ? 'latex' : 'all';
      resetFilter();
    });
    kindMode = latexOnlyEl.checked ? 'latex' : 'all';
  }

  function renderScoredBox(scored){
    if(!scored || !Array.isArray(scored.entries) || scored.entries.length===0) return;
    const items = scored.entries.slice().sort((a,b)=> (b.score||0)-(a.score||0)).slice(0,60);

    const box = document.createElement('section');
    box.className = 'panel';
    box.innerHTML = `
      <h2>Scored harvest candidates (not promoted)</h2>
      <div class='muted'>Showing top ${items.length} by score. Threshold promotions go to the ranked leaderboard.</div>
      <div class='cardrow' style='margin-top:12px'>
        ${items.map((e,idx)=>{
          const eq = String(e.equation||'');
          const src = String(e.source||'');
          const title = inferTitle(eq, idx+1);
          return `
          <section class='card'>
            <div class='card__rank'>S</div>
            <div class='card__body'>
              <div class='card__head'>
                <h2 class='card__title'>${esc(title)}</h2>
                <div class='card__meta'>
                  <span class='badge badge--score'>Score ${esc(e.score||0)}</span>
                  <span class='pill pill--neutral'>harvest</span>
                </div>
              </div>
              <div class='equation'>
                <div class='equation__label'>Equation</div>
                <div class='equation__tex'>$$${esc(eq)}$$</div>
              </div>
              <div class='card__sub'>Source: <span class='muted'>${esc(compactPath(src))}</span></div>
            </div>
          </section>`;
        }).join('')}
      </div>
    `;

    // Insert above the search UI
    metaEl.parentElement?.parentElement?.insertBefore(box, metaEl.parentElement);

    if(window.renderMathInElement){
      window.renderMathInElement(box, {
        delimiters: [
          {left: '$$', right: '$$', display: true},
          {left: '$', right: '$', display: false},
          {left: '\\[', right: '\\]', display: true},
          {left: '\\(', right: '\\)', display: false},
        ],
        throwOnError: false,
      });
    }
  }

  Promise.all([
    fetch(SRC).then(r=>r.json()),
    fetch(SCORED).then(r=> r.ok ? r.json() : null).catch(()=>null),
  ])
    .then(([d, scored]) => {
      entries = d.entries || [];
      // normalize expected fields
      entries = entries.map(x => ({
        equation: x.equation,
        kind: x.kind,
        source: x.source,
        line_start: x.line_start,
        source_type: x.source_type || x.sourceType || 'file',
        sha1: x.sha1,
      }));

      const st = d.stats || {};
      const u = st.unique || entries.length;
      metaEl.textContent = `${u.toLocaleString()} unique harvested equations`;

      renderScoredBox(scored);
      resetFilter();
    })
    .catch(err => {
      metaEl.textContent = 'Failed to load harvest JSON.';
      console.error(err);
    });
})();
