/* Service worker: libreria Firebase in cache + pagine disponibili anche offline.
   Metti questo file nella stessa cartella delle pagine (index, gare, pdg, premiazioni). */
const FB = 'fb-cache', AP = 'app-cache', U = 'https://www.gstatic.com/firebasejs/10.12.2/';
self.addEventListener('install', e => {
  e.waitUntil(caches.open(FB)
    .then(c => Promise.allSettled(['firebase-app.js', 'firebase-auth.js', 'firebase-firestore.js'].map(f => c.add(U + f))))
    .then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => e.waitUntil(self.clients.claim()));
self.addEventListener('fetch', e => {
  const r = e.request;
  if (r.method !== 'GET') return;
  const u = new URL(r.url);
  if (u.pathname.startsWith('/api/')) return; // server locale: mai in cache (tempo reale)
  // Firebase JS: prima la copia salvata, altrimenti rete (e la salva)
  if (u.hostname === 'www.gstatic.com' && u.pathname.startsWith('/firebasejs/')) {
    e.respondWith(caches.open(FB).then(async c => {
      const hit = await c.match(r);
      if (hit) return hit;
      const n = await fetch(r);
      if (n.ok) c.put(r, n.clone());
      return n;
    }));
    return;
  }
  // Pagine del sito e bandiere: prima la rete (sempre aggiornato), se offline la copia salvata
  if (u.origin === location.origin || r.destination === 'image') {
    e.respondWith(fetch(r).then(n => {
      if (n.ok || n.type === 'opaque') { const k = n.clone(); caches.open(AP).then(c => c.put(r, k)); }
      return n;
    }).catch(() => caches.match(r, { ignoreSearch: true })));
  }
});
