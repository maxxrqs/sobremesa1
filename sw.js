const V="sobremesa-1792271226",SHELL=["./","index.html","config.js","shim.js","manifest.webmanifest","icon-192.png","icon-512.png"];
self.addEventListener("install",e=>{e.waitUntil(caches.open(V).then(c=>c.addAll(SHELL)).then(()=>self.skipWaiting()))});
self.addEventListener("activate",e=>{e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x.startsWith("sobremesa-1792271226")&&x!==V).map(x=>caches.delete(x)))).then(()=>self.clients.claim()))});
self.addEventListener("fetch",e=>{
  const r=e.request,u=new URL(r.url);
  if(r.method!=="GET"||u.origin!==location.origin||r.headers.has("range"))return; // Range : directement au réseau (clips audio) ; // le relais IA et les autres sites ne sont jamais mis en cache
  if(r.mode==="navigate"||u.pathname.endsWith("/index.html")||u.pathname.endsWith("config.js")){
    e.respondWith(fetch(r).then(x=>{const c=x.clone();caches.open(V).then(ch=>ch.put(r,c));return x}).catch(()=>caches.match(r).then(m=>m||caches.match("index.html"))));return}
  /* voix de la conversation/traducteur (≈ 30 Mo) : cache durable, non effacé à chaque mise à jour de l'appli (l'URL porte déjà ?v=) */
  if(u.pathname.indexOf("/a/tv/")>=0){e.respondWith(caches.open("sobstatic-v1").then(c=>c.match(r).then(m=>m||fetch(r).then(x=>{if(x.ok)c.put(r,x.clone());return x}))));return}
  e.respondWith(caches.match(r).then(m=>m||fetch(r).then(x=>{if(x.ok){const c=x.clone();caches.open(V).then(ch=>ch.put(r,c))}return x})));
});
