'use strict';

const CACHE = 'yourpetshealthlog-v1';
const CORE = [
  '/',
  '/app/',
  '/assets/paw.svg',
  '/assets/site.js',
  '/assets/mobile-app.js',
  '/assets/care-personalization-print1.js',
  '/assets/care-autosave.js',
  '/assets/offline.js',
  '/styles/base.css',
  '/styles/components.css',
  '/styles/care.css',
  '/styles/mobile-app.css'
];

self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(CORE)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(key => key !== CACHE).map(key => caches.delete(key))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  const request = event.request;
  if (request.method !== 'GET') return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  const isWorksheet = url.pathname.startsWith('/care/');
  const isAppRoute = url.pathname === '/app/' || url.pathname.startsWith('/app/');
  const isStatic = url.pathname.startsWith('/assets/') || url.pathname.startsWith('/styles/');
  if (!isWorksheet && !isAppRoute && !isStatic && request.mode !== 'navigate') return;

  if (isStatic) {
    event.respondWith(
      caches.match(request).then(cached => cached || fetch(request).then(response => {
        if (response.ok) caches.open(CACHE).then(cache => cache.put(request, response.clone()));
        return response;
      }))
    );
    return;
  }

  event.respondWith(
    fetch(request)
      .then(response => {
        if (response.ok) caches.open(CACHE).then(cache => cache.put(request, response.clone()));
        return response;
      })
      .catch(() => caches.match(request).then(cached => cached || (isAppRoute ? caches.match('/app/') : caches.match('/'))))
  );
});