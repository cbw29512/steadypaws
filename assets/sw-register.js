(() => {
  "use strict";

  if (!("serviceWorker" in navigator)) return;

  window.addEventListener("load", async () => {
    try {
      const registration = await navigator.serviceWorker.register("/sw.js", { scope: "/" });
      const registrations = await navigator.serviceWorker.getRegistrations();

      await Promise.all(
        registrations
          .filter((item) => {
            const script = item.active?.scriptURL || item.waiting?.scriptURL || item.installing?.scriptURL || "";
            return script.endsWith("/app/sw.js") && item.scope.endsWith("/app/");
          })
          .map((item) => item.unregister())
      );

      if (registration.waiting) registration.waiting.postMessage({ type: "SKIP_WAITING" });
    } catch (error) {
      console.error("Your Pet’s Health Log service worker registration failed:", error);
    }
  });
})();