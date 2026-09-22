// ============================================================
// ScrapSense AI - Service Worker (PWA Offline Support)
// ============================================================
const CACHE_NAME = "scrapsense-v2";
const STATIC_ASSETS = [
  "/",
  "/index.html",
  "/style.css",
  "/script.js",
  "/manifest.json"
];

// Install: Cache static assets
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log("[SW] Caching static assets");
      return cache.addAll(STATIC_ASSETS);
    })
  );
  self.skipWaiting();
});

// Activate: Clean old caches
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      );
    })
  );
  self.clients.claim();
});

// Fetch: Network-first for API, cache-first for static
self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);

  // Network-first for API calls
  if (url.port === "8000" || url.pathname.startsWith("/api")) {
    event.respondWith(
      fetch(event.request).catch(() => {
        return new Response(
          JSON.stringify({ error: "Offline - Backend not reachable" }),
          { headers: { "Content-Type": "application/json" }, status: 503 }
        );
      })
    );
    return;
  }

  // Cache-first for static assets
  event.respondWith(
    caches.match(event.request).then((cached) => {
      if (cached) return cached;
      return fetch(event.request).then((response) => {
        // Cache successful responses
        if (response.ok && event.request.method === "GET") {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
        }
        return response;
      }).catch(() => {
        // Offline fallback for HTML pages
        if (event.request.headers.get("accept")?.includes("text/html")) {
          return caches.match("/index.html");
        }
      });
    })
  );
});
