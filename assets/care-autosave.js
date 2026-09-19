(() => {
  'use strict';

  const ROOT = document.querySelector('.care-form');
  const CLEAR = document.querySelector('#clear-care-form-data');
  if (!ROOT) return;

  const STORAGE_PREFIX = 'yourpetshealthlog.care-form.v1:';
  const key = STORAGE_PREFIX + location.pathname;
  const editable = () => [...ROOT.querySelectorAll('input, textarea')]
    .filter(control => !control.disabled && !control.readOnly && control.type !== 'file');

  function fieldKey(control, index) {
    return control.id || control.name || `field-${index}`;
  }

  function snapshot() {
    const data = {};
    editable().forEach((control, index) => {
      data[fieldKey(control, index)] = control.type === 'checkbox' || control.type === 'radio'
        ? control.checked
        : control.value;
    });
    return data;
  }

  function save() {
    try {
      localStorage.setItem(key, JSON.stringify(snapshot()));
    } catch (error) {
      console.warn('Your Pet’s Health Log could not save this worksheet locally:', error);
    }
  }

  function restore() {
    try {
      const raw = localStorage.getItem(key);
      if (!raw) return;
      const data = JSON.parse(raw);
      editable().forEach((control, index) => {
        const stored = data[fieldKey(control, index)];
        if (stored === undefined) return;
        if (control.type === 'checkbox' || control.type === 'radio') control.checked = Boolean(stored);
        else control.value = String(stored);
      });
    } catch (error) {
      console.warn('Your Pet’s Health Log could not restore this worksheet:', error);
    }
  }

  function clearFormData() {
    const confirmed = window.confirm('Clear the saved entries from this worksheet on this device? This cannot be undone.');
    if (!confirmed) return false;
    try {
      localStorage.removeItem(key);
      editable().forEach(control => {
        if (control.type === 'checkbox' || control.type === 'radio') control.checked = false;
        else control.value = '';
      });
      document.querySelector('#care-autosave-status')?.replaceChildren(document.createTextNode('Saved worksheet data cleared from this device.'));
      return true;
    } catch (error) {
      console.error('Your Pet’s Health Log could not clear this worksheet:', error);
      return false;
    }
  }

  ROOT.addEventListener('input', save);
  ROOT.addEventListener('change', save);
  CLEAR?.addEventListener('click', clearFormData);
  window.clearPetHealthFormData = clearFormData;
  restore();
})();