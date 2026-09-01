(() => {
  'use strict';

  const chips = [...document.querySelectorAll('[data-filter]')];
  const familyChoices = [...document.querySelectorAll('.family-choice')];
  const moreButton = document.querySelector('.family-more');
  const moreFamily = document.querySelector('#more-family');
  const cards = [...document.querySelectorAll('.condition-card')];
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
    return `${card.dataset.search || ''} ${card.textContent}`.toLowerCase();
  }

  function variantText(variant) {
    return `${variant.dataset.species || ''} ${variant.dataset.search || ''} ${variant.textContent}`.toLowerCase();
  }

  function variantFitsFamily(variant) {
    const group = variant.dataset.group || '';
    const groupMatch = activeGroup === 'all' || group === activeGroup;
    if (!groupMatch) return false;
    if (!familyTerms.length) return true;
    const text = variantText(variant);
    return familyTerms.some(term => text.includes(term));
  }

  function applyFilters() {
    try {
      const query = normalize(search.value);
      const browsing = journeyStarted || Boolean(query) || activeGroup !== 'all';
      let visible = 0;

      cards.forEach(card => {
        const variants = [...card.querySelectorAll('.tracker-variant')];
        const queryMatchesCard = !query || cardText(card).includes(query);
        let visibleVariants = 0;

        variants.forEach(variant => {
          const searchMatch = !query || queryMatchesCard || variantText(variant).includes(query);
          const showVariant = browsing && variantFitsFamily(variant) && searchMatch;
          variant.hidden = !showVariant;
          if (showVariant) visibleVariants += 1;
        });

        const showCard = browsing && visibleVariants > 0;
        card.hidden = !showCard;
        card.classList.toggle('has-multiple-variants', visibleVariants > 1);
        if (showCard) visible += 1;
      });

      if (!browsing) {
        count.textContent = 'Pick your family member above to see their primary health concerns.';
        empty.hidden = true;
        return;
      }

      count.textContent = visible === 1
        ? '1 primary health concern ready to choose'
        : `${visible} primary health concerns ready to choose`;
      empty.hidden = visible !== 0;
    } catch (error) {
      console.error('Steady Paws health-concern filtering failed:', error);
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

      if (journeyHeading) journeyHeading.textContent = 'What is the biggest health concern right now?';
      if (journeyCopy) {
        journeyCopy.textContent = activeGroup === 'all'
          ? 'Each health concern appears once. Open the concern you need and choose the version made for your family member.'
          : `Choose the main health concern you want to track for your ${familyLabel}. Their form has room to note other conditions they are living with too.`;
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
    if (journeyHeading) journeyHeading.textContent = 'Browse primary health concerns';
    if (journeyCopy) journeyCopy.textContent = 'Each concern is listed once. When several tailored forms exist, choose the one made for your family member.';
    applyFilters();
  }));

  search.addEventListener('input', () => {
    if (normalize(search.value)) journeyStarted = true;
    applyFilters();
  });

  applyFilters();
})();
