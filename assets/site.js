(() => {
  'use strict';

  const chips = [...document.querySelectorAll('[data-filter]')];
  const familyChoices = [...document.querySelectorAll('.family-choice')];
  const moreButton = document.querySelector('.family-more');
  const moreFamily = document.querySelector('#more-family');
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
  let journeyStarted = false;
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
      const browsing = journeyStarted || Boolean(query) || activeGroup !== 'all';
      let visible = 0;

      cards.forEach(card => {
        const cardGroup = card.dataset.group || '';
        const groupMatch = activeGroup === 'all' || cardGroup === activeGroup;
        const searchMatch = !query || cardText(card).includes(query);
        const show = browsing && groupMatch && familyMatches(card) && searchMatch;
        card.hidden = !show;
        if (show) visible += 1;
      });

      if (!browsing) {
        count.textContent = 'Pick your family member above to see their care paperwork.';
        empty.hidden = true;
        return;
      }

      count.textContent = visible === 1
        ? '1 care form ready for you'
        : `${visible} care forms ready for you`;
      empty.hidden = visible !== 0;
    } catch (error) {
      console.error('Steady Paws care-paperwork filtering failed:', error);
    }
  }

  function setActiveChip(group) {
    chips.forEach(item => {
      const selected = (item.dataset.filter || 'all') === group;
      item.classList.toggle('is-active', selected);
      item.setAttribute('aria-pressed', String(selected));
    });
  }

  function clearFamilySelection() {
    familyChoices.forEach(item => {
      item.classList.remove('is-selected');
      item.setAttribute('aria-pressed', 'false');
    });
  }

  function selectFamily(choice) {
    try {
      activeGroup = choice.dataset.familyGroup || 'all';
      familyLabel = choice.dataset.familyLabel || 'family member';
      familyTerms = normalize(choice.dataset.familyTerm || '')
        .split(/\s*\|\s*/)
        .filter(Boolean);
      journeyStarted = true;
      search.value = '';

      clearFamilySelection();
      choice.classList.add('is-selected');
      choice.setAttribute('aria-pressed', 'true');
      setActiveChip(activeGroup);

      if (journeyHeading) journeyHeading.textContent = 'What tough time are they going through?';
      if (journeyCopy) {
        journeyCopy.textContent = activeGroup === 'all'
          ? 'Here is every Steady Paws care form. Choose the one that best matches what your family member and veterinary team are working through.'
          : `Here is the care paperwork that fits your ${familyLabel}. Choose what their veterinary team is helping them manage.`;
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

  if (moreButton && moreFamily) {
    moreButton.addEventListener('click', () => {
      const opening = moreFamily.hidden;
      moreFamily.hidden = !opening;
      moreButton.setAttribute('aria-expanded', String(opening));
      moreButton.classList.toggle('is-open', opening);
      if (opening) moreFamily.querySelector('.family-choice')?.focus();
    });
  }

  chips.forEach(chip => chip.addEventListener('click', () => {
    activeGroup = chip.dataset.filter || 'all';
    familyLabel = '';
    familyTerms = [];
    journeyStarted = true;
    clearFamilySelection();
    setActiveChip(activeGroup);
    if (journeyCopy) journeyCopy.textContent = 'Browse the complete care-paperwork collection or search for what your family member is going through.';
    applyFilters();
  }));

  search.addEventListener('input', () => {
    if (normalize(search.value)) journeyStarted = true;
    applyFilters();
  });

  applyFilters();
})();
