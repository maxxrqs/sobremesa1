// Sobremesa — rappel quotidien (Cloudflare Worker, gratuit)
// Réglages Cloudflare : un espace KV lié sous le nom SUBS, et un déclencheur Cron « 0 * * * * » (toutes les heures).
// Les clés VAPID sont créées automatiquement au premier appel et gardées dans SUBS : rien d'autre à configurer.
const ORIGIN="https://maxxrqs.github.io";
const b64u=b=>btoa(String.fromCharCode(...new Uint8Array(b))).replace(/\+/g,"-").replace(/\//g,"_").replace(/=+$/,"");
const ub64=s=>Uint8Array.from(atob(s.replace(/-/g,"+").replace(/_/g,"/")+"===".slice((s.length+3)%4)),c=>c.charCodeAt(0));
async function keys(env){
  let k=await env.SUBS.get("vapid",{type:"json"});
  if(!k){const p=await crypto.subtle.generateKey({name:"ECDSA",namedCurve:"P-256"},true,["sign","verify"]);
    k={pub:b64u(await crypto.subtle.exportKey("raw",p.publicKey)),jwk:await crypto.subtle.exportKey("jwk",p.privateKey)};await env.SUBS.put("vapid",JSON.stringify(k))}
  return k}
async function jwt(aud,k){
  const enc=o=>b64u(new TextEncoder().encode(JSON.stringify(o)));
  const h=enc({typ:"JWT",alg:"ES256"}),p=enc({aud,exp:Math.floor(Date.now()/1e3)+12*3600,sub:"https://maxxrqs.github.io/sobremesa1/"});
  const key=await crypto.subtle.importKey("jwk",k.jwk,{name:"ECDSA",namedCurve:"P-256"},false,["sign"]);
  const sig=await crypto.subtle.sign({name:"ECDSA",hash:"SHA-256"},key,new TextEncoder().encode(h+"."+p));
  return h+"."+p+"."+b64u(sig)}
async function push(sub,k){
  const u=new URL(sub.endpoint),t=await jwt(u.origin,k);
  return fetch(sub.endpoint,{method:"POST",headers:{authorization:`vapid t=${t}, k=${k.pub}`,ttl:"43200",urgency:"normal","content-length":"0"}})}
const id=async s=>b64u(await crypto.subtle.digest("SHA-256",new TextEncoder().encode(s))).slice(0,32);
function local(tz){try{const f=new Intl.DateTimeFormat("en-CA",{timeZone:tz,year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",hourCycle:"h23"}).formatToParts(new Date()),g=t=>f.find(x=>x.type===t).value;return{d:`${g("year")}-${g("month")}-${g("day")}`,h:+g("hour")}}catch(e){return null}}
async function tick(env){
  const k=await keys(env);let cur;const out={sent:0,gone:0};
  do{const l=await env.SUBS.list({prefix:"s:",cursor:cur});cur=l.list_complete?null:l.cursor;
    for(const it of l.keys){const r=await env.SUBS.get(it.name,{type:"json"});if(!r)continue;const L=local(r.tz||"Europe/Madrid");if(!L)continue;
      if(L.h!==r.h||r.seen===L.d||r.sent===L.d)continue;
      try{const x=await push(r.sub,k);if(x.status===404||x.status===410){await env.SUBS.delete(it.name);out.gone++}else if(x.ok){r.sent=L.d;await env.SUBS.put(it.name,JSON.stringify(r));out.sent++}}catch(e){}}
  }while(cur);
  return out}
export default{
  async fetch(req,env){
    const o=req.headers.get("origin")||"",ok=o===ORIGIN;
    const cors={"access-control-allow-origin":ok?o:"null","access-control-allow-headers":"content-type","access-control-allow-methods":"GET,POST,OPTIONS","vary":"origin"};
    const js=(s,b)=>new Response(JSON.stringify(b),{status:s,headers:{...cors,"content-type":"application/json","cache-control":"no-store"}});
    if(req.method==="OPTIONS")return new Response(null,{headers:cors});
    const p=new URL(req.url).pathname;
    if(!env.SUBS)return js(500,{err:"KV SUBS absent"});
    if(req.method==="GET"&&p==="/key")return js(200,{key:(await keys(env)).pub});
    if(req.method!=="POST"||!ok)return js(403,{err:"forbidden"});
    let b;try{b=await req.json()}catch(e){return js(400,{err:"bad"})}
    if(!b||!b.sub||!b.sub.endpoint||!/^https:\/\//.test(b.sub.endpoint))return js(400,{err:"sub"});
    const name="s:"+await id(b.sub.endpoint);
    if(p==="/sub"){const old=await env.SUBS.get(name,{type:"json"})||{};
      await env.SUBS.put(name,JSON.stringify({sub:b.sub,h:Math.max(0,Math.min(23,+b.h|0)),tz:String(b.tz||"Europe/Madrid").slice(0,60),seen:b.seen||old.seen||"",sent:old.sent||""}));return js(200,{ok:1})}
    if(p==="/seen"){const r=await env.SUBS.get(name,{type:"json"});if(r){r.seen=String(b.d||"").slice(0,10);await env.SUBS.put(name,JSON.stringify(r))}return js(200,{ok:1})}
    if(p==="/unsub"){await env.SUBS.delete(name);return js(200,{ok:1})}
    if(p==="/test"){const r=await env.SUBS.get(name,{type:"json"});if(!r)return js(404,{err:"inconnu"});const x=await push(r.sub,await keys(env));return js(x.ok?200:502,{status:x.status})}
    return js(404,{err:"?"})},
  async scheduled(ev,env,ctx){ctx.waitUntil(tick(env))}
};
