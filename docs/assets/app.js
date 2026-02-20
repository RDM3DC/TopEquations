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
      if(mode === 'score-desc'){
        return (parseFloat(b.getAttribute('data-score')||'0') - parseFloat(a.getAttribute('data-score')||'0'));
      }
      if(mode === 'score-asc'){
        return (parseFloat(a.getAttribute('data-score')||'0') - parseFloat(b.getAttribute('data-score')||'0'));
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
