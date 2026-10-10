// Compatibilité : l'appli appelle claude.use("sample") (IA de l'artefact).
// Hors de Claude : 1) relais IA (Worker) si window.SOB_AI est défini, 2) sinon clé Gemini gratuite de l'utilisateur, enregistrée sur son appareil.
(function(){
  if(window.claude&&window.claude.use)return;
  window.SOB_KEYUI=!window.SOB_AI;
  const key=()=>{try{return localStorage.getItem("sob_gkey")||""}catch(e){return""}};
  const mk=(input)=>typeof input==="string"?[{role:"user",content:input}]:input;
  async function relay(input,opts){
    const body={tier:opts.modelTier||"default"};
    if(typeof input==="string")body.prompt=input;else body.turns=input;
    let r;
    const ac=new AbortController();const to=setTimeout(()=>ac.abort("timeout"),40000);if(opts.signal)opts.signal.addEventListener("abort",()=>ac.abort());
    try{r=await fetch(window.SOB_AI,{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify(body),signal:ac.signal})}
    catch(e){clearTimeout(to);if(opts.signal&&opts.signal.aborted)throw{code:"cancelled",message:"cancelled"};if(e&&e.name==="AbortError")throw{code:"timeout",message:"timeout"};throw{code:"network",message:String(e)}}
    if(r.status===429){clearTimeout(to);throw{code:"rate_limited",message:"rate_limited"}}
    if(!r.ok||!r.body){clearTimeout(to);throw{code:"http"+r.status,message:"http"+r.status}}
    try{return await read(r.body,opts,false)}finally{clearTimeout(to)}
  }
  async function read(stream,opts,sse){
    const rd=stream.getReader(),dec=new TextDecoder();let text="",buf="";
    try{
      for(;;){
        const {done,value}=await rd.read();if(done)break;
        let d=dec.decode(value,{stream:true});if(!d)continue;
        if(sse){
          buf+=d;d="";let i;
          while((i=buf.indexOf("\n"))>=0){const l=buf.slice(0,i).trim();buf=buf.slice(i+1);
            if(!l.startsWith("data:"))continue;
            try{const j=JSON.parse(l.slice(5));d+=(j.candidates&&j.candidates[0]&&j.candidates[0].content&&j.candidates[0].content.parts||[]).map(p=>p.text||"").join("")}catch(e){}}
          if(!d)continue;
        }
        text+=d;if(opts.onText)try{opts.onText({text,delta:d})}catch(e){}
      }
    }catch(e){if(e&&e.name==="AbortError")throw{code:"cancelled",message:"cancelled"};throw{code:"network",message:String(e),text}}
    return{text,truncated:false};
  }
  async function gemini(input,opts){
    const model=opts.modelTier==="quick"?"gemini-2.5-flash-lite":"gemini-2.5-flash";
    const contents=mk(input).slice(-30).map(t=>({role:t.role==="assistant"?"model":"user",parts:[{text:String(t.content||"").slice(0,20000)}]}));
    let r;
    try{r=await fetch("https://generativelanguage.googleapis.com/v1beta/models/"+model+":streamGenerateContent?alt=sse",{method:"POST",headers:{"content-type":"application/json","x-goog-api-key":key()},body:JSON.stringify({contents}),signal:opts.signal})}
    catch(e){if(e&&e.name==="AbortError")throw{code:"cancelled",message:"cancelled"};throw{code:"network",message:String(e)}}
    if(r.status===429)throw{code:"rate_limited",message:"rate_limited"};
    if(r.status===400||r.status===403)throw{code:"badkey",message:"badkey"};
    if(!r.ok||!r.body)throw{code:"http"+r.status,message:"http"+r.status};
    return read(r.body,opts,true)
  }
  async function sample(input,opts){
    opts=opts||{};
    return window.SOB_AI?relay(input,opts):gemini(input,opts);
  }
  sample.json=async(i,o)=>{let t=(await sample(i,o)).text.trim().replace(/^```(?:json)?\s*/i,"").replace(/\s*```$/,"");try{return JSON.parse(t)}catch(e){const m=t.match(/[\[{][\s\S]*[\]}]/);if(m)return JSON.parse(m[0]);throw e}};
  sample.limits=async()=>({images:false});
  window.claude={use:async n=>(n==="sample"&&(window.SOB_AI||key()))?sample:null};
})();
