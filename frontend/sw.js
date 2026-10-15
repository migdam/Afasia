/**
 * Retired service worker (backlog P1-7).
 *
 * The app used to install a worker here that served its files from a cache
 * forever (so fixes never arrived) and cached API responses, personal data
 * included. Every exercise needs the server, so the cache gave no real
 * offline use. Browsers that still have that worker fetch this file when
 * they check for updates; this version deletes every cache, unregisters
 * itself and reloads open pages, so they come straight from the server.
 * The app no longer registers a worker. Keep this file until no old
 * installs can be left.
 */
self.addEventListener('install', () => self.skipWaiting());

self.addEventListener('activate', (event) => {
    event.waitUntil((async () => {
        const names = await caches.keys();
        await Promise.all(names.map((name) => caches.delete(name)));
        await self.registration.unregister();
        const pages = await self.clients.matchAll({ type: 'window' });
        pages.forEach((page) => page.navigate(page.url));
    })());
});
