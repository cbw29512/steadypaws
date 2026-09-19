"use strict";

const VERSION = "20260919-a11y-seo-offline1";
const STATIC_CACHE = `yourpetshealthlog-static-${VERSION}`;
const PAGE_CACHE = `yourpetshealthlog-pages-${VERSION}`;

const CORE = [
  "/",
  "/app/",
  "/app/index.html",
  "/app/manifest.webmanifest",
  "/styles/base.css",
  "/styles/components.css",
  "/styles/care.css",
  "/styles/family.css",
  "/styles/launch-polish-1.css",
  "/styles/mobile-app.css",
  "/assets/paw.svg",
  "/assets/site.js",
  "/assets/launch-polish-1.js",
  "/assets/personalization-bridge-print1.js",
  "/assets/mobile-app.js",
  "/assets/care-personalization-print1.js",
  "/assets/care-form-state.js",
  "/assets/sw-register.js",
];

async function precacheCarePages() {
  const cache = await caches.open(PAGE_CACHE);
  try {
    const response = await fetch("/sitemap.xml", { cache: "no-store" });
    if (!response.ok) return;
    const xml = await response.text();
    const urls = [...xml.matchAll(/<loc>(https?:\/\/[^<]+)<\/loc>/g)]
      .map((match) => new URL(match[1]))
      .filter((url) => url.origin === self.location.origin && url.pathname.startsWith("/care/"))
      .map((url) => url.pathname + url.search);

    await Promise.allSettled(
      urls.map(async (url) => {
        const page = await fetch(url, { cache: "no-store" });
        if (page.ok) await cache.put(url, page);
      })
    );
  } catch (error) {
    console.warn("Care-page precache skipped:", error);
  }
}

self.addEventListener("install", (event) => {
  event.waitUntil(
    Promise.all([
      caches.open(STATIC_CACHE).then((cache) => cache.addAll(CORE)),
      precacheCarePages(),
    ]).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(
        keys
          .filter((key) =>
            (key.startsWith("yourpetshealthlog-") && ![STATIC_CACHE, PAGE_CACHE].includes(key))
            || key.startsWith("steadypaws-app-")
          )
          .map((key) => caches.delete(key))
      ))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("message", (event) => {
  if (event.data?.type === "SKIP_WAITING") self.skipWaiting();
});

async function matchIgnoringSearch(request) {
  const staticCache = await caches.open(STATIC_CACHE);
  const staticHit = await staticCache.match(request, { ignoreSearch: true });
  if (staticHit) return staticHit;

  const pageCache = await caches.open(PAGE_CACHE);
  return pageCache.match(request, { ignoreSearch: true });
}

async function networkFirst(request, cacheName) {
  const cache = await caches.open(cacheName);
  try {
    const response = await fetch(request);
    if (response.ok) await cache.put(request, response.clone());
    return response;
  } catch (error) {
    const cached = await cache.match(request, { ignoreSearch: true }) || await matchIgnoringSearch(request);
    if (cached) return cached;
    if (request.mode === "navigate") {
      const home = await caches.match("/", { ignoreSearch: true });
      if (home) return home;
    }
    throw error;
  }
}

self.addEventListener("fetch", (event) => {
  const request = event.request;
  if (request.method !== "GET") return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  if (request.mode === "navigate") {
    const isOfflineRoute = url.pathname === "/"
      || url.pathname.startsWith("/app/")
      || url.pathname.startsWith("/care/");
    if (isOfflineRoute) {
      event.respondWith(networkFirst(request, PAGE_CACHE));
    }
    return;
  }

  if (url.pathname.startsWith("/assets/") || url.pathname.startsWith("/styles/")) {
    event.respondWith(
      matchIgnoringSearch(request).then((cached) => {
        if (cached) return cached;
        return fetch(request).then(async (response) => {
          if (response.ok) {
            const cache = await caches.open(STATIC_CACHE);
            await cache.put(request, response.clone());
          }
          return response;
        });
      })
    );
  }
});