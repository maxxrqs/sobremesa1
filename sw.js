const V="sobremesa-1792926919",SHELL=["./","index.html","config.js","shim.js","manifest.webmanifest","icon-192.png","icon-512.png"],STA="sobstatic-v1";
self.addEventListener("install",e=>{e.waitUntil(caches.open(V).then(c=>c.addAll(SHELL.map(u=>new Request(u,{cache:"reload"})))).then(()=>self.skipWaiting()))});
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
    /* cache:"no-cache" : on redemande toujours au serveur (sinon le navigateur garde l'ancienne page jusqu'à 10 min) */
    const net=fetch(r.mode==="navigate"?new Request(r.url,{cache:"no-cache",credentials:"same-origin"}):new Request(r,{cache:"no-cache"})).then(x=>{if(x.ok){const c=x.clone();caches.open(V).then(ch=>ch.put(r,c))}return x});
    const cached=()=>caches.match(r).then(m=>m||caches.match("index.html"));
    /* si la copie enregistrée a été affichée, on prévient la page dès que la nouvelle version est arrivée : elle se recharge seule */
    e.respondWith(new Promise(ok=>{let done=0,stale=0;const t=setTimeout(()=>cached().then(m=>{if(m&&!done){done=1;stale=1;ok(m)}}),8000);
      net.then(x=>{if(!done){done=1;clearTimeout(t);ok(x)}else if(stale&&x.ok&&r.mode==="navigate")setTimeout(()=>self.clients.matchAll({type:"window"}).then(cs=>cs.forEach(c=>c.postMessage("sob-new"))),600)}).catch(()=>cached().then(m=>{if(!done){done=1;clearTimeout(t);ok(m||Response.error())}}))}));return}
  if(u.pathname.indexOf("/a/tv/")>=0||durable(u)){e.respondWith(caches.open(STA).then(c=>c.match(r).then(m=>m||fetch(r).then(x=>{if(x.ok)putDurable(r,x.clone());return x}))));return}
  e.respondWith(caches.match(r).then(m=>m||fetch(r).then(x=>{if(x.ok){const c=x.clone();caches.open(V).then(ch=>ch.put(r,c))}return x})));
});
/* rappel quotidien : notification du compagnon (message préparé par l'appli dans le cache « sobprefs ») */
self.addEventListener("push",e=>{e.waitUntil(caches.open("sobprefs").then(c=>c.match("rp.json")).then(r=>r?r.json():null).catch(()=>null).then(p=>{const L=p&&p.msgs&&p.msgs.length?p.msgs:["Ta série du jour t'attend ! 🔥"];return self.registration.showNotification(p&&p.title||"Sobremesa",{body:L[Math.floor(Math.random()*L.length)],icon:"icon-192.png",badge:"icon-192.png",tag:"sob-rappel",renotify:true})}))});
self.addEventListener("notificationclick",e=>{e.notification.close();e.waitUntil(self.clients.matchAll({type:"window",includeUncontrolled:true}).then(cs=>{const c=cs.find(x=>x.url.indexOf(self.registration.scope)===0);return c?c.focus():self.clients.openWindow("./")}))});
