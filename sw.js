// Revalidate pages and code on every visit so returning visitors get the latest version.
// Scope stays inside this site, including /trenesis/ on GitHub Pages.
'use strict';
self.addEventListener('install', event => event.waitUntil(self.skipWaiting()));
self.addEventListener('activate', event => event.waitUntil(self.clients.claim()));
self.addEventListener('fetch', event => {
  const request = event.request;
  const url = new URL(request.url);
  const scope = new URL(self.registration.scope);
  if (request.method !== 'GET' || url.origin !== scope.origin ||
      !url.pathname.startsWith(scope.pathname)) return;
  const relativePath = url.pathname.slice(scope.pathname.length);
  const isPage = request.mode === 'navigate' &&
    (relativePath === '' || relativePath.endsWith('.html'));
  const isCodeOrData = relativePath.startsWith('assets/') && /\.(?:js|css|json)$/.test(relativePath);
  if (!isPage && !isCodeOrData) return;
  // Conditional requests reuse unchanged files but check with the server first.
  // Images, fonts and PDFs keep the browser's normal caching behavior.
  event.respondWith(fetch(request, { cache: 'no-cache' }).catch(() =>
    fetch(request, { cache: 'force-cache' })
  ));
});
