(() => {
  'use strict';

  const STORAGE_KEY = 'steadypaws.personalization.v1';
  const familyName = document.querySelector('#family-name');
  const photoPreview = document.querySelector('#photo-preview');
  const photoRemove = document.querySelector('#photo-remove');
  const accessibleLinks = [...document.querySelectorAll('.accessible-link')];

  if (!familyName || !photoPreview) return;

  function currentPhotoDataUrl() {
    if (photoPreview.hidden) return '';
    const src = photoPreview.getAttribute('src') || '';
    return src.startsWith('data:image/jpeg;base64,') ? src : '';
  }

  function savePersonalization() {
    try {
      const payload = {
        name: familyName.value.trim(),
        photoDataUrl: currentPhotoDataUrl(),
      };
      if (!payload.name && !payload.photoDataUrl) {
        sessionStorage.removeItem(STORAGE_KEY);
        return;
      }
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
    } catch (error) {
      console.warn('Steady Paws could not keep personalization in this tab:', error);
    }
  }

  familyName.addEventListener('input', savePersonalization);
  accessibleLinks.forEach(link => link.addEventListener('click', savePersonalization));
  photoRemove?.addEventListener('click', () => window.setTimeout(savePersonalization, 0));

  const observer = new MutationObserver(savePersonalization);
  observer.observe(photoPreview, { attributes: true, attributeFilter: ['src', 'hidden'] });

  savePersonalization();
})();
