(() => {
  'use strict';
  const chips = [...document.querySelectorAll('[data-filter]')];
  const cards = [...document.querySelectorAll('.tracker-card')];
  const search = document.querySelector('#tracker-search');
  const count = document.querySelector('#result-count');
  const empty = document.querySelector('#no-results');
  if (!chips.length || !cards.length || !search || !count || !empty) return;

  let active = 'all';
  const normalize = value => value.trim().toLowerCase();

  function applyFilters() {
    try {
      const query = normalize(search.value);
      let visible = 0;
      cards.forEach(card => {
        const speciesMatch = active === 'all' || card.dataset.species === active;
        const text = `${card.dataset.search || ''} ${card.textContent}`.toLowerCase();
        const searchMatch = !query || text.includes(query);
        const show = speciesMatch && searchMatch;
        card.hidden = !show;
        if (show) visible += 1;
      });
      count.textContent = query || active !== 'all'
        ? `Showing ${visible} matching tracker${visible === 1 ? '' : 's'}`
        : 'Showing all 22 trackers';
      empty.hidden = visible !== 0;
    } catch (error) {
      console.error('Steady Paws tracker filtering failed:', error);
    }
  }

  chips.forEach(chip => chip.addEventListener('click', () => {
    active = chip.dataset.filter || 'all';
    chips.forEach(item => {
      const selected = item === chip;
      item.classList.toggle('is-active', selected);
      item.setAttribute('aria-pressed', String(selected));
    });
    applyFilters();
  }));

  search.addEventListener('input', applyFilters);
})();
