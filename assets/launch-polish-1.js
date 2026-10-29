(() => {
  'use strict';

  const supportPrompt = document.querySelector('#support-after-download');
  const journeyHeading = document.querySelector('#journey-heading');
  const journeyCopy = document.querySelector('#journey-copy');
  const trackerGrid = document.querySelector('#tracker-grid');
  const trackerSearch = document.querySelector('#tracker-search');
  const supportHome = supportPrompt?.parentElement || null;
  const supportHomeAnchor = supportPrompt?.nextElementSibling || null;

  // The support card lives at the end of the library, but it is most useful
  // directly under the tracker someone just downloaded.
  function returnSupportToLibraryEnd() {
    if (!supportPrompt || !supportHome || supportPrompt.parentElement === supportHome) return;
    supportHome.insertBefore(supportPrompt, supportHomeAnchor);
    supportPrompt.classList.remove('is-inline');
  }

  function revealSupportNear(card) {
    if (!supportPrompt) return;
    if (card && trackerGrid?.contains(card)) {
      card.after(supportPrompt);
      supportPrompt.classList.add('is-inline');
    } else {
      returnSupportToLibraryEnd();
    }
    supportPrompt.hidden = false;
  }

  function refreshPetFirstCopy(target) {
    if (!(target instanceof Element)) return;

    const familyChoice = target.closest('.family-choice');
    if (familyChoice) {
      returnSupportToLibraryEnd();
      window.setTimeout(() => {
        if (journeyHeading) journeyHeading.textContent = 'What pet health concern are you tracking?';
        if (journeyCopy) {
          const group = familyChoice.dataset.familyGroup || 'all';
          const label = familyChoice.dataset.familyLabel || 'pet';
          journeyCopy.textContent = group === 'all'
            ? 'Every card shows one animal-specific health log. Choose the issue and open its log.'
            : `Choose the health issue for your ${label}, then open the log or download a printable PDF.`;
        }
      }, 0);
      return;
    }

    if (target.closest('[data-filter]')) {
      returnSupportToLibraryEnd();
      window.setTimeout(() => {
        if (journeyHeading) journeyHeading.textContent = 'Browse pet health concerns';
        if (journeyCopy) journeyCopy.textContent = 'One animal and one health issue per card. Choose the matching log to continue.';
      }, 0);
    }
  }

  document.addEventListener('click', event => {
    const target = event.target;
    refreshPetFirstCopy(target);

    const download = target instanceof Element ? target.closest('a.care-download') : null;
    if (!download || !supportPrompt) return;

    const card = download.closest('.condition-card');
    window.setTimeout(() => revealSupportNear(card), 350);
  });

  trackerSearch?.addEventListener('input', returnSupportToLibraryEnd);
})();
