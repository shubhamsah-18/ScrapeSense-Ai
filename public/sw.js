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

// Fetch: Network-only for API and mutations, cache-first only for static assets
self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);

  const isApiRoute =
    url.port === "8000" ||
    url.pathname.startsWith("/api") ||
    url.pathname.startsWith("/auth") ||
    url.pathname.startsWith("/listings") ||
    url.pathname.startsWith("/orders") ||
    url.pathname.startsWith("/dealers") ||
    url.pathname.startsWith("/categories") ||
    url.pathname.startsWith("/analytics") ||
    url.pathname.startsWith("/predict") ||
    url.pathname.startsWith("/approval-requests");

  // Non-GET requests or dynamic API endpoints must never be served from or stored in cache
  if (event.request.method !== "GET" || isApiRoute) {
    event.respondWith(
      fetch(event.request).catch(() => {
        return new Response(
          JSON.stringify({ error: "Offline - Service not reachable" }),
          { headers: { "Content-Type": "application/json" }, status: 503 }
        );
      })
    );
    return;
  }

  // Cache-first only for static frontend assets
  event.respondWith(
    caches.match(event.request).then((cached) => {
      if (cached) return cached;
      return fetch(event.request).then((response) => {
        // Cache successful responses for static GET requests only
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
