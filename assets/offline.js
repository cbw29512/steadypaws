(() => {
  'use strict';
  if (!('serviceWorker' in navigator)) return;
  window.addEventListener('load', async () => {
    try {
      const registrations = await navigator.serviceWorker.getRegistrations();
      await Promise.all(
        registrations
          .filter(registration => {
            const script = registration.active?.scriptURL || registration.waiting?.scriptURL || registration.installing?.scriptURL || '';
            return script.endsWith('/app/sw.js');
          })
          .map(registration => registration.unregister())
      );
      await navigator.serviceWorker.register('/sw.js', { scope: '/' });
    } catch (error) {
      console.warn('Your Pet’s Health Log offline support could not start:', error);
    }
  });
})();