const APP_VERSION = "2026.06.27-v11";
const CACHE_NAME = `vps-operacional-pwa-${APP_VERSION}`;
const APP_SHELL = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "./vps-pwa-icon.svg",
  "./vps-pwa-icon-180.png",
  "./vps-pwa-icon-192.png",
  "./vps-pwa-icon-512.png",
  "./default-background.png",
  "./default-client-logo.png",
  "./default-contractor-logo.png",
  "./icons/target.svg",
  "./icons/clipboard.svg",
  "./icons/alert.svg",
  "./icons/calendar.svg",
  "./icons/tower.svg",
  "./icons/network.svg",
  "./icons/wrench.svg",
  "./icons/antenna.svg"
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(APP_SHELL))
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((key) => key.startsWith("vps-operacional-pwa-") && key !== CACHE_NAME)
          .map((key) => caches.delete(key))
      )
    )
  );
  self.clients.claim();
});

self.addEventListener("message", (event) => {
  if (event.data?.type === "SKIP_WAITING") {
    self.skipWaiting();
  }
});

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;
  const request = event.request;
  if (request.mode === "navigate" || request.headers.get("accept")?.includes("text/html")) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          const copy = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put("./index.html", copy));
          return response;
        })
        .catch(() => caches.match("./index.html"))
    );
    return;
  }
  event.respondWith(
    caches.match(request).then((cached) =>
      cached || fetch(request).then((response) => {
        if (response.ok) {
          const copy = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
        }
        return response;
      })
    )
  );
});
