const CACHE_NAME = "pusulamnet-shell-v3";
const APP_SHELL = [
    "/",
    "/static/css/styles.css?v=4.1.0",
    "/static/js/api.js?v=4.2.0",
    "/static/js/charts.js?v=4.2.0",
    "/static/js/app.js?v=4.2.0",
    "/static/favicon.svg",
    "/static/manifest.json"
];

self.addEventListener("install", (event) => {
    event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(APP_SHELL)));
    self.skipWaiting();
});

self.addEventListener("activate", (event) => {
    event.waitUntil(
        caches.keys().then((keys) => Promise.all(
            keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
        ))
    );
    self.clients.claim();
});

self.addEventListener("fetch", (event) => {
    if (event.request.method !== "GET" || new URL(event.request.url).origin !== self.location.origin) {
        return;
    }

    // API responses must always come from the server; stale progress data would be misleading.
    if (new URL(event.request.url).pathname.startsWith("/api/")) {
        event.respondWith(fetch(event.request));
        return;
    }

    event.respondWith(
        fetch(event.request)
            .then((response) => {
                const copy = response.clone();
                caches.open(CACHE_NAME).then((cache) => cache.put(event.request, copy));
                return response;
            })
            .catch(() => caches.match(event.request))
    );
});
