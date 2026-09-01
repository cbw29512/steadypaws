(() => {
  'use strict';

  const chips = [...document.querySelectorAll('[data-filter]')];
  const familyChoices = [...document.querySelectorAll('.family-choice')];
  const cards = [...document.querySelectorAll('.tracker-card')];
  const search = document.querySelector('#tracker-search');
  const count = document.querySelector('#result-count');
  const empty = document.querySelector('#no-results');
  const journeyHeading = document.querySelector('#journey-heading');
  const journeyCopy = document.querySelector('#journey-copy');
  const library = document.querySelector('#library');
  if (!chips.length || !cards.length || !search || !count || !empty) return;

  let activeGroup = 'all';
  let familyTerms = [];
  let familyLabel = '';
  const normalize = value => value.trim().toLowerCase();

  function cardText(card) {
    return `${card.dataset.species || ''} ${card.dataset.search || ''} ${card.textContent}`.toLowerCase();
  }

  function familyMatches(card) {
    if (!familyTerms.length) return true;
    const text = cardText(card);
    return familyTerms.some(term => text.includes(term));
  }

  function applyFilters() {
    try {
      const query = normalize(search.value);
      let visible = 0;

      cards.forEach(card => {
        const cardGroup = card.dataset.group || '';
        const groupMatch = activeGroup === 'all' || cardGroup === activeGroup;
        const searchMatch = !query || cardText(card).includes(query);
        const show = groupMatch && familyMatches(card) && searchMatch;
        card.hidden = !show;
        if (show) visible += 1;
      });

      const guided = Boolean(familyLabel);
      count.textContent = guided || query || activeGroup !== 'all'
        ? `Showing ${visible} care tracker${visible === 1 ? '' : 's'}`
        : `Showing all ${cards.length} trackers`;
      empty.hidden = visible !== 0;
    } catch (error) {
      console.error('Steady Paws tracker filtering failed:', error);
    }
  }

  function setActiveChip(group) {
    chips.forEach(item => {
      const selected = (item.dataset.filter || 'all') === group;
      item.classList.toggle('is-active', selected);
      item.setAttribute('aria-pressed', String(selected));
    });
  }

  function selectFamily(choice) {
    try {
      activeGroup = choice.dataset.familyGroup || 'all';
      familyLabel = choice.dataset.familyLabel || 'family member';
      familyTerms = normalize(choice.dataset.familyTerm || '')
        .split(/\s*\|\s*|\s+/)
        .filter(Boolean);
      search.value = '';

      familyChoices.forEach(item => {
        const selected = item === choice;
        item.classList.toggle('is-selected', selected);
        item.setAttribute('aria-pressed', String(selected));
      });
      setActiveChip(activeGroup);

      if (journeyHeading) journeyHeading.textContent = 'What tough time are they going through?';
      if (journeyCopy) {
        journeyCopy.textContent = activeGroup === 'all'
          ? 'Here is the whole Steady Paws library. Choose the form that best matches what your veterinary team is helping them through.'
          : `We are showing the care forms that fit your ${familyLabel}. Choose what their veterinary team is helping them manage.`;
      }

      applyFilters();
      if (library) {
        const behavior = window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth';
        library.scrollIntoView({ behavior, block: 'start' });
      }
    } catch (error) {
      console.error('Steady Paws family picker failed:', error);
    }
  }

  familyChoices.forEach(choice => {
    choice.setAttribute('aria-pressed', 'false');
    choice.addEventListener('click', () => selectFamily(choice));
  });

  chips.forEach(chip => chip.addEventListener('click', () => {
    activeGroup = chip.dataset.filter || 'all';
    familyLabel = '';
    familyTerms = [];
    familyChoices.forEach(item => {
      item.classList.remove('is-selected');
      item.setAttribute('aria-pressed', 'false');
    });
    setActiveChip(activeGroup);
    if (journeyCopy) journeyCopy.textContent = 'Browse the full library or search for the health problem or care challenge you have in mind.';
    applyFilters();
  }));

  search.addEventListener('input', applyFilters);
  applyFilters();
})();
