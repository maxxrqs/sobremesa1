// Relais IA (Cloudflare Workers) — version avec diagnostic
const GEMINI_KEY="COLLE_TA_CLE_ICI";
const ORIGIN="https://maxxrqs.github.io";
const hits=new Map();
export default{
  async fetch(req,env){
    const o=req.headers.get("origin")||"",ok=!ORIGIN||o===ORIGIN;
    const cors={"access-control-allow-origin":ok?o||"*":"null","access-control-allow-headers":"content-type","access-control-allow-methods":"POST,OPTIONS","vary":"origin"};
    const txt=(s,t)=>new Response(t,{status:s,headers:{...cors,"content-type":"text/plain; charset=utf-8","cache-control":"no-store"}});
    if(req.method==="OPTIONS")return new Response(null,{headers:cors});
    if(req.method!=="POST"||!ok)return txt(403,"forbidden");
    if(!GEMINI_KEY||GEMINI_KEY==="COLLE_TA_CLE_ICI")return txt(500,"clé absente dans le code");
    const ip=req.headers.get("cf-connecting-ip")||"?",day=new Date().toISOString().slice(0,10),k=ip+day;
    const n=(hits.get(k)||0)+1;hits.set(k,n);if(hits.size>5000)hits.clear();
    if(n>150)return txt(429,"limit");
    let b;try{b=await req.json()}catch(e){return txt(400,"bad")}
    const turns=Array.isArray(b.turns)?b.turns:[{role:"user",content:String(b.prompt||"")}];
    const contents=turns.slice(-30).map(t=>({role:t.role==="assistant"?"model":"user",parts:[{text:String(t.content||"").slice(0,20000)}]}));
    const models=b.tier==="quick"?["gemini-3.5-flash-lite","gemini-flash-lite-latest","gemini-3.5-flash"]:["gemini-3.5-flash","gemini-flash-latest","gemini-3.5-flash-lite"];
    let up,j;
    for(const model of models){
      const ac=new AbortController(),to=setTimeout(()=>ac.abort(),25000);
      try{
        up=await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`,{method:"POST",signal:ac.signal,headers:{"content-type":"application/json","x-goog-api-key":GEMINI_KEY},body:JSON.stringify({contents,generationConfig:{temperature:0.4}})});
        j=await up.text();
      }catch(e){clearTimeout(to);return txt(504,"Gemini ne répond pas : "+String(e))}
      clearTimeout(to);
      if(up.status!==404)break;
    }
    if(!up.ok)return txt(up.status===429?429:502,"Gemini "+up.status+" : "+j.slice(0,300));
    let t="";
    try{const d=JSON.parse(j);t=(d.candidates&&d.candidates[0]&&d.candidates[0].content&&d.candidates[0].content.parts||[]).map(p=>p.text||"").join("")}catch(e){return txt(502,"réponse illisible")}
    if(!t)return txt(502,"réponse vide : "+j.slice(0,300));
    return txt(200,t);
  }
};
