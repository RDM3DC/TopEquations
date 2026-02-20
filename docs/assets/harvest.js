// Harvest page: fetch JSON and lazy-render a lot of equations with KaTeX.
(function(){
  const listEl = document.getElementById('harvestList');
  const metaEl = document.getElementById('harvestMeta');
  const searchEl = document.getElementById('harvestSearch');
  const latexOnlyEl = document.getElementById('harvestLatexOnly');
  if(!listEl || !metaEl || !searchEl) return;

  const SRC = './data/harvest/equation_harvest.json';

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

  function renderChunk(){
    const end = Math.min(cursor + PAGE, filtered.length);
    if(cursor >= end) return;

    const frag = document.createDocumentFragment();

    for(let i=cursor;i<end;i++){
      const e = filtered[i];
      const card = document.createElement('section');
      card.className = 'card';
      card.innerHTML = `
        <div class='card__rank'>#${i+1}</div>
        <div class='card__body'>
          <div class='card__head'>
            <h2 class='card__title'>${esc(e.kind || 'equation')}</h2>
            <div class='card__meta'>
              <span class='badge badge--score'>sha1 ${esc((e.sha1||'').slice(0,8))}</span>
              <span class='pill pill--neutral'>${esc(e.source_type || '')}</span>
            </div>
          </div>
          <div class='equation'>
            <div class='equation__label'>Equation</div>
            <div class='equation__tex'>$$${esc(e.equation)}$$</div>
          </div>
          <div class='grid'>
            <div class='kv'><div class='k'>Source</div><div class='v'>${esc(e.source || '')}</div></div>
            <div class='kv'><div class='k'>Line</div><div class='v'>${esc(e.line_start || '')}</div></div>
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

  fetch(SRC)
    .then(r => r.json())
    .then(d => {
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
      resetFilter();
    })
    .catch(err => {
      metaEl.textContent = 'Failed to load harvest JSON.';
      console.error(err);
    });
})();
