const V="sobremesa-1792866475",SHELL=["./","index.html","config.js","shim.js","manifest.webmanifest","icon-192.png","icon-512.png"],STA="sobstatic-v1";
self.addEventListener("install",e=>{e.waitUntil(caches.open(V).then(c=>c.addAll(SHELL)).then(()=>self.skipWaiting()))});
/* supprime toutes les anciennes versions de l'appli (avant : elles s'empilaient à chaque mise à jour) ; les caches durables (voix, clips) sont gardés */
self.addEventListener("activate",e=>{e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x.startsWith("sobremesa-")&&x!==V).map(x=>caches.delete(x)))).then(()=>self.clients.claim()))});
/* fichiers dont l'URL porte ?v= (traductions, index des voix, moteur de secours, voix du traducteur) : cache durable, gardé entre les mises à jour */
const durable=u=>u.search.indexOf("v=")>=0&&/\/(tr|a|v)\//.test(u.pathname);
function putDurable(r,x){return caches.open(STA).then(c=>c.keys().then(ks=>Promise.all(ks.filter(k=>{const o=new URL(k.url);return o.pathname===new URL(r.url).pathname&&o.search!==new URL(r.url).search}).map(k=>c.delete(k)))).then(()=>c.put(r,x)))}
self.addEventListener("fetch",e=>{
  const r=e.request,u=new URL(r.url);
  if(r.method!=="GET"||u.origin!==location.origin||r.headers.has("range"))return; // Range : directement au réseau (clips audio) ; le relais IA et les autres sites ne sont jamais mis en cache
  if(r.mode==="navigate"||u.pathname.endsWith("/index.html")||u.pathname.endsWith("config.js")){
    /* réseau d'abord, mais si la connexion traîne (métro, 4G faible) on ouvre la version enregistrée au bout de 3,5 s */
    const net=fetch(r).then(x=>{if(x.ok){const c=x.clone();caches.open(V).then(ch=>ch.put(r,c))}return x});
    const cached=()=>caches.match(r).then(m=>m||caches.match("index.html"));
    e.respondWith(new Promise(ok=>{let done=0;const t=setTimeout(()=>cached().then(m=>{if(m&&!done){done=1;ok(m)}}),3500);
      net.then(x=>{if(!done){done=1;clearTimeout(t);ok(x)}}).catch(()=>cached().then(m=>{if(!done){done=1;clearTimeout(t);ok(m||Response.error())}}))}));return}
  if(u.pathname.indexOf("/a/tv/")>=0||durable(u)){e.respondWith(caches.open(STA).then(c=>c.match(r).then(m=>m||fetch(r).then(x=>{if(x.ok)putDurable(r,x.clone());return x}))));return}
  e.respondWith(caches.match(r).then(m=>m||fetch(r).then(x=>{if(x.ok){const c=x.clone();caches.open(V).then(ch=>ch.put(r,c))}return x})));
});
