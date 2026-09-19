(() => {
  "use strict";

  const VERSION = 1;
  const STORAGE_PREFIX = "yourpetshealthlog.care-form.v1:";
  const form = document.querySelector(".care-form");
  const clearButton = document.querySelector("#care-clear-form-data");
  const status = document.querySelector("#care-form-state-status");
  if (!form) return;

  const storageKey = STORAGE_PREFIX + window.location.pathname;
  const controls = [...form.querySelectorAll("input, textarea, select")].filter((control) => {
    const type = (control.getAttribute("type") || "").toLowerCase();
    return !control.disabled
      && !control.readOnly
      && !["button", "submit", "reset", "file", "hidden"].includes(type);
  });

  function controlKey(control, index) {
    return control.dataset.autosaveKey
      || control.id
      || control.getAttribute("name")
      || control.getAttribute("aria-label")
      || `field-${index + 1}`;
  }

  const fields = new Map(controls.map((control, index) => [controlKey(control, index), control]));

  function setStatus(message) {
    if (status) status.textContent = message;
  }

  function readState() {
    try {
      const raw = localStorage.getItem(storageKey);
      if (!raw) return null;
      const parsed = JSON.parse(raw);
      if (!parsed || parsed.version !== VERSION || typeof parsed.fields !== "object") return null;
      return parsed;
    } catch (error) {
      console.error("Your Pet’s Health Log form restore failed:", error);
      return null;
    }
  }

  function serialize() {
    const values = {};
    for (const [key, control] of fields) {
      if (control instanceof HTMLInputElement && (control.type === "checkbox" || control.type === "radio")) {
        values[key] = control.checked;
      } else {
        values[key] = control.value;
      }
    }
    return {
      version: VERSION,
      path: window.location.pathname,
      saved_at: new Date().toISOString(),
      fields: values,
    };
  }

  let saveTimer = 0;
  function saveNow() {
    window.clearTimeout(saveTimer);
    try {
      localStorage.setItem(storageKey, JSON.stringify(serialize()));
      setStatus("Saved on this device.");
    } catch (error) {
      console.error("Your Pet’s Health Log form auto-save failed:", error);
      setStatus("This browser could not save the form locally.");
    }
  }

  function scheduleSave() {
    window.clearTimeout(saveTimer);
    saveTimer = window.setTimeout(saveNow, 120);
  }

  function restore() {
    const saved = readState();
    if (!saved) return;
    for (const [key, value] of Object.entries(saved.fields)) {
      const control = fields.get(key);
      if (!control) continue;
      if (control instanceof HTMLInputElement && (control.type === "checkbox" || control.type === "radio")) {
        control.checked = Boolean(value);
      } else if (typeof value === "string") {
        control.value = value;
      }
    }
    setStatus("Saved form data restored from this device.");
  }

  function clearSavedFormData() {
    const confirmed = window.confirm(
      "Clear the saved entries for this tracker on this device? This cannot be undone."
    );
    if (!confirmed) return false;

    window.clearTimeout(saveTimer);
    try {
      localStorage.removeItem(storageKey);
      for (const control of controls) {
        if (control instanceof HTMLInputElement && (control.type === "checkbox" || control.type === "radio")) {
          control.checked = false;
        } else {
          control.value = "";
        }
      }
      setStatus("Saved form data cleared from this device.");
      return true;
    } catch (error) {
      console.error("Your Pet’s Health Log form clear failed:", error);
      setStatus("This browser could not clear the saved form data.");
      return false;
    }
  }

  form.addEventListener("input", scheduleSave);
  form.addEventListener("change", scheduleSave);
  clearButton?.addEventListener("click", clearSavedFormData);

  window.YourPetsHealthLogCareForm = Object.freeze({
    save: saveNow,
    clear: clearSavedFormData,
    storageKey,
  });

  restore();
})();