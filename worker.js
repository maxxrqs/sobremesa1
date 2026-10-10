// Relais IA gratuit (Cloudflare Workers) : garde la clé Gemini secrète et limite l'usage.
// Variables à définir dans Cloudflare : GEMINI_KEY (secret), ALLOWED_ORIGIN (ex: https://TONNOM.github.io)
// Facultatif : MODEL_QUICK, MODEL_DEFAULT, DAILY_LIMIT (requêtes par IP et par jour, défaut 150)
const hits=new Map();
export default{
  async fetch(req,env){
    const o=req.headers.get("origin")||"",ok=!env.ALLOWED_ORIGIN||o===env.ALLOWED_ORIGIN;
    const cors={"access-control-allow-origin":ok?o||"*":"null","access-control-allow-headers":"content-type","access-control-allow-methods":"POST,OPTIONS","vary":"origin"};
    if(req.method==="OPTIONS")return new Response(null,{headers:cors});
    if(req.method!=="POST"||!ok)return new Response("forbidden",{status:403,headers:cors});
    const ip=req.headers.get("cf-connecting-ip")||"?",day=new Date().toISOString().slice(0,10),k=ip+day;
    const n=(hits.get(k)||0)+1;hits.set(k,n);if(hits.size>5000)hits.clear();
    if(n>(+env.DAILY_LIMIT||150))return new Response("limit",{status:429,headers:cors});
    let b;try{b=await req.json()}catch(e){return new Response("bad",{status:400,headers:cors})}
    const turns=Array.isArray(b.turns)?b.turns:[{role:"user",content:String(b.prompt||"")}];
    const contents=turns.slice(-30).map(t=>({role:t.role==="assistant"?"model":"user",parts:[{text:String(t.content||"").slice(0,20000)}]}));
    const model=b.tier==="quick"?(env.MODEL_QUICK||"gemini-2.5-flash-lite"):(env.MODEL_DEFAULT||"gemini-2.5-flash");
    const up=await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${model}:streamGenerateContent?alt=sse`,{method:"POST",headers:{"content-type":"application/json","x-goog-api-key":env.GEMINI_KEY},body:JSON.stringify({contents,generationConfig:{temperature:0.4,thinkingConfig:{thinkingBudget:0}}})});
    if(!up.ok||!up.body)return new Response("upstream",{status:up.status===429?429:502,headers:cors});
    const dec=new TextDecoder(),enc=new TextEncoder();let buf="";
    const ts=new TransformStream({transform(ch,ctl){
      buf+=dec.decode(ch,{stream:true});let i;
      while((i=buf.indexOf("\n"))>=0){const l=buf.slice(0,i).trim();buf=buf.slice(i+1);
        if(!l.startsWith("data:"))continue;
        try{const j=JSON.parse(l.slice(5));const t=(j.candidates&&j.candidates[0]&&j.candidates[0].content&&j.candidates[0].content.parts||[]).map(p=>p.text||"").join("");if(t)ctl.enqueue(enc.encode(t))}catch(e){}}
    }});
    return new Response(up.body.pipeThrough(ts),{headers:{...cors,"content-type":"text/plain; charset=utf-8","cache-control":"no-store"}});
  }
};
