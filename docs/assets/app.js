// tiny client-side search for the leaderboard cards
(function(){
  const box = document.getElementById('searchBox');
  const cards = document.getElementById('cards');
  if(!box || !cards) return;

  const items = Array.from(cards.querySelectorAll('.card'));

  function apply(){
    const q = (box.value || '').trim().toLowerCase();
    if(!q){
      items.forEach(el => el.style.display = '');
      return;
    }
    items.forEach(el => {
      const t = (el.innerText || '').toLowerCase();
      el.style.display = t.includes(q) ? '' : 'none';
    });
  }

  box.addEventListener('input', apply);
})();
