(() => {
  'use strict';

  const supportPrompt = document.querySelector('#support-after-download');
  const journeyHeading = document.querySelector('#journey-heading');
  const journeyCopy = document.querySelector('#journey-copy');
  const resultCount = document.querySelector('#result-count');

  function refreshPetFirstCopy(target) {
    if (!(target instanceof Element)) return;

    const familyChoice = target.closest('.family-choice');
    if (familyChoice) {
      window.setTimeout(() => {
        if (journeyHeading) journeyHeading.textContent = 'What pet health concern are you tracking?';
        if (journeyCopy) {
          const group = familyChoice.dataset.familyGroup || 'all';
          const label = familyChoice.dataset.familyLabel || 'pet';
          journeyCopy.textContent = group === 'all'
            ? 'Each health concern appears once. Open the concern you need and choose the version made for your pet.'
            : `Choose the main health concern you want to track for your ${label}. Their tracker has room for other health conditions too.`;
        }
      }, 0);
      return;
    }

    if (target.closest('[data-filter]')) {
      window.setTimeout(() => {
        if (journeyHeading) journeyHeading.textContent = 'Browse pet health concerns';
        if (journeyCopy) journeyCopy.textContent = 'Each concern is listed once. When several tailored forms exist, choose the version made for your pet.';
      }, 0);
    }
  }

  document.addEventListener('click', event => {
    const target = event.target;
    refreshPetFirstCopy(target);

    const download = target instanceof Element ? target.closest('a.care-download') : null;
    if (!download || !supportPrompt) return;

    window.setTimeout(() => {
      supportPrompt.hidden = false;
    }, 350);
  });

  if (resultCount && resultCount.textContent?.includes('Pick your family member')) {
    resultCount.textContent = 'Choose your pet above to narrow the health trackers, or browse all health concerns.';
  }
})();
