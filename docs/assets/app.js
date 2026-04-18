// Leaderboard UX: search + latex-only filter + sort.
(function(){
  const box = document.getElementById('searchBox');
  const cards = document.getElementById('cards');
  const latexOnly = document.getElementById('latexOnly');
  const sortBy = document.getElementById('sortBy');
  if(!cards) return;

  const items = Array.from(cards.querySelectorAll('.card'));

  function matchesFilters(el){
    const q = (box && box.value ? box.value : '').trim().toLowerCase();
    if(q){
      const t = (el.innerText || '').toLowerCase();
      if(!t.includes(q)) return false;
    }
    if(latexOnly && latexOnly.checked){
      if((el.getAttribute('data-haslatex') || '0') !== '1') return false;
    }
    return true;
  }

  function apply(){
    items.forEach(el => {
      el.style.display = matchesFilters(el) ? '' : 'none';
    });
  }

  function applySort(){
    const mode = sortBy ? sortBy.value : 'rank';
    const visible = items.slice();
    visible.sort((a,b)=>{
      const dateA = Date.parse(a.getAttribute('data-date') || '') || 0;
      const dateB = Date.parse(b.getAttribute('data-date') || '') || 0;
      if(mode === 'score-desc'){
        return (parseFloat(b.getAttribute('data-score')||'0') - parseFloat(a.getAttribute('data-score')||'0'));
      }
      if(mode === 'score-asc'){
        return (parseFloat(a.getAttribute('data-score')||'0') - parseFloat(b.getAttribute('data-score')||'0'));
      }
      if(mode === 'date-desc'){
        return dateB - dateA;
      }
      if(mode === 'date-asc'){
        return dateA - dateB;
      }
      return (parseInt(a.getAttribute('data-rank')||'0',10) - parseInt(b.getAttribute('data-rank')||'0',10));
    });
    visible.forEach(el => cards.appendChild(el));
  }

  if(box) box.addEventListener('input', () => { apply(); });
  if(latexOnly) latexOnly.addEventListener('change', () => { apply(); });
  if(sortBy) sortBy.addEventListener('change', () => { applySort(); apply(); });

  // initial
  applySort();
  apply();
})();

// Equation card copy buttons. Bound globally so it works on every page
// that includes app.js, not just leaderboard pages with #cards.
(function(){
  function copyText(text){
    if(navigator.clipboard && window.isSecureContext){
      return navigator.clipboard.writeText(text);
    }
    // Fallback for older browsers / non-HTTPS local files.
    return new Promise(function(resolve, reject){
      try{
        var ta = document.createElement('textarea');
        ta.value = text;
        ta.setAttribute('readonly', '');
        ta.style.position = 'fixed';
        ta.style.top = '-9999px';
        document.body.appendChild(ta);
        ta.select();
        var ok = document.execCommand('copy');
        document.body.removeChild(ta);
        ok ? resolve() : reject(new Error('execCommand failed'));
      }catch(err){ reject(err); }
    });
  }

  function flash(btn, cls, label){
    var textEl = btn.querySelector('.equation__copy-text');
    var prev = textEl ? textEl.textContent : '';
    btn.classList.add(cls);
    if(textEl) textEl.textContent = label;
    setTimeout(function(){
      btn.classList.remove(cls);
      if(textEl) textEl.textContent = prev || 'Copy';
    }, 1400);
  }

  document.addEventListener('click', function(ev){
    var btn = ev.target.closest && ev.target.closest('.equation__copy');
    if(!btn) return;
    ev.preventDefault();
    var card = btn.closest('.equation');
    if(!card) return;
    var tex = card.getAttribute('data-tex') || '';
    if(!tex){
      flash(btn, 'is-error', 'No LaTeX');
      return;
    }
    copyText(tex).then(function(){
      flash(btn, 'is-copied', 'Copied!');
    }).catch(function(){
      flash(btn, 'is-error', 'Failed');
    });
  });
})();

// "Copy all" button: dumps every visible card's LaTeX to the clipboard,
// honouring the current search/sort state. Each block is preceded by a
// LaTeX-comment header (% #N — Name) so the dump remains valid LaTeX.
(function(){
  function copyText(text){
    if(navigator.clipboard && window.isSecureContext){
      return navigator.clipboard.writeText(text);
    }
    return new Promise(function(resolve, reject){
      try{
        var ta = document.createElement('textarea');
        ta.value = text;
        ta.setAttribute('readonly', '');
        ta.style.position = 'fixed';
        ta.style.top = '-9999px';
        document.body.appendChild(ta);
        ta.select();
        var ok = document.execCommand('copy');
        document.body.removeChild(ta);
        ok ? resolve() : reject(new Error('execCommand failed'));
      }catch(err){ reject(err); }
    });
  }

  function flashAll(btn, cls, label){
    var textEl = btn.querySelector('.copy-all-btn__text');
    var prev = textEl ? textEl.textContent : '';
    btn.classList.add(cls);
    if(textEl) textEl.textContent = label;
    setTimeout(function(){
      btn.classList.remove(cls);
      if(textEl) textEl.textContent = prev || 'Copy all';
    }, 1800);
  }

  function gatherVisibleLatex(){
    var cards = document.getElementById('cards');
    if(!cards) return { count: 0, text: '' };
    var nodes = Array.from(cards.querySelectorAll('.card'));
    var blocks = [];
    var idx = 0;
    nodes.forEach(function(card){
      // Respect search / latex-only filter (which sets display:none).
      if(card.style.display === 'none') return;
      var eq = card.querySelector('.equation[data-tex]');
      if(!eq) return;
      var tex = eq.getAttribute('data-tex') || '';
      if(!tex.trim()) return;
      idx += 1;
      var titleEl = card.querySelector('.card__title');
      var name = titleEl ? titleEl.textContent.trim().replace(/\s+/g, ' ') : '';
      // LaTeX comments are safe headers; \n keeps the dump newline-delimited.
      blocks.push('% #' + idx + (name ? ' — ' + name : '') + '\n' + tex);
    });
    return { count: idx, text: blocks.join('\n\n') + (blocks.length ? '\n' : '') };
  }

  document.addEventListener('click', function(ev){
    var btn = ev.target.closest && ev.target.closest('.copy-all-btn');
    if(!btn) return;
    ev.preventDefault();
    var dump = gatherVisibleLatex();
    if(!dump.count){
      flashAll(btn, 'is-error', 'Nothing to copy');
      return;
    }
    copyText(dump.text).then(function(){
      flashAll(btn, 'is-copied', 'Copied ' + dump.count + ' eq' + (dump.count === 1 ? '' : 's') + '!');
    }).catch(function(){
      flashAll(btn, 'is-error', 'Failed');
    });
  });
})();
