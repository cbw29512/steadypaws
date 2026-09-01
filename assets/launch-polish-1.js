(() => {
  'use strict';

  const supportPrompt = document.querySelector('#support-after-download');
  if (!supportPrompt) return;

  document.addEventListener('click', event => {
    const target = event.target instanceof Element ? event.target.closest('a.care-download') : null;
    if (!target) return;

    window.setTimeout(() => {
      supportPrompt.hidden = false;
    }, 350);
  });
})();
