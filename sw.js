/* Riuman PWA service worker — network-first for navigation, cached fallback offline. */
"use strict";

const CACHE_NAME = "riuman-pwa-shell-v1";
const BASE_ASSETS = [
  "./",
  "./index.html",
  "./version.json",
  "./manifest.webmanifest",
  "./riuman-icon.svg"
];

async function cacheKeyFor(request) {
  const url = new URL(request.url);
  url.search = "";
  url.hash = "";
  return new Request(url.href, { method: "GET" });
}

async function networkFirst(request) {
  const cache = await caches.open(CACHE_NAME);
  const cacheKey = await cacheKeyFor(request);
  try {
    const fresh = await fetch(request, { cache: "no-store" });
    if (fresh && fresh.ok) {
      try { await cache.put(cacheKey, fresh.clone()); } catch (_) {}
    }
    return fresh;
  } catch (_) {
    const cached = await cache.match(request) || await cache.match(cacheKey);
    if (cached) return cached;
    return new Response("Riuman no está disponible sin conexión todavía.", {
      status: 503,
      headers: { "Content-Type": "text/plain; charset=utf-8" }
    });
  }
}

self.addEventListener("install", function (event) {
  event.waitUntil((async function () {
    const scope = self.registration.scope;
    const response = await fetch(new URL("version.json", scope).href, { cache: "no-store" });
    if (!response.ok) throw new Error("No se pudo cargar version.json para la caché inicial.");
    const release = await response.json();
    if (!release || typeof release.entry !== "string") throw new Error("Entrada de versión inválida.");

    const entry = new URL(release.entry, scope);
    if (entry.origin !== self.location.origin ||
        !entry.pathname.startsWith(new URL(scope).pathname) ||
        !entry.pathname.toLowerCase().endsWith(".html")) {
      throw new Error("La entrada de Riuman está fuera del ámbito permitido.");
    }

    const cache = await caches.open(CACHE_NAME);
    await cache.addAll(BASE_ASSETS.concat([entry.href]));
    await self.skipWaiting();
  })());
});

self.addEventListener("activate", function (event) {
  event.waitUntil((async function () {
    const names = await caches.keys();
    await Promise.all(names.map(function (name) {
      return name.startsWith("riuman-pwa-") && name !== CACHE_NAME
        ? caches.delete(name)
        : Promise.resolve(false);
    }));
    await self.clients.claim();
  })());
});

self.addEventListener("fetch", function (event) {
  const request = event.request;
  if (request.method !== "GET") return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  if (url.pathname.endsWith("/version.json") || request.mode === "navigate") {
    event.respondWith(networkFirst(request));
    return;
  }

  if (["style", "script", "image", "font"].includes(request.destination)) {
    event.respondWith((async function () {
      const cache = await caches.open(CACHE_NAME);
      const key = await cacheKeyFor(request);
      const cached = await cache.match(request) || await cache.match(key);
      const refresh = fetch(request).then(function (response) {
        if (response && response.ok) cache.put(key, response.clone()).catch(function () {});
        return response;
      }).catch(function () { return null; });
      return cached || await refresh || new Response("", { status: 504 });
    })());
  }
});
