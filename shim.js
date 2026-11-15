// Compatibilité : l'appli appelle claude.use("sample") (IA de l'artefact).
// Hors de Claude : 1) relais IA (Worker) si window.SOB_AI est défini, 2) sinon clé Gemini gratuite de l'utilisateur, enregistrée sur son appareil.
(function(){
  if(window.claude&&window.claude.use)return;
  window.SOB_KEYUI=!window.SOB_AI;
  const key=()=>{try{return localStorage.getItem("sob_gkey")||""}catch(e){return""}};
  const mk=(input)=>typeof input==="string"?[{role:"user",content:input}]:input;
  // Relais sécurisé (réserve n°4) : session courte obtenue avec un jeton Turnstile, puis chaque appel porte la session.
  // Seuls deux usages sont acceptés par le relais : conversation (« conv ») et traduction (« trad »).
  const base=()=>String(window.SOB_AI||"").replace(/\/+$/,"");
  const modeOf=p=>/^You are an expert professional translator\. /.test(p)?"trad":/^You are \w+, a cute mascot who is also the learner's conversation partner/.test(p)?"conv":"";
  let SESS=null,SESSP=null,TSP=null;
  try{const x=JSON.parse(sessionStorage.getItem("sob_ias")||"null");if(x&&x.s&&x.exp)SESS=x}catch(e){}
  const fresh=()=>SESS&&SESS.exp*1000-Date.now()>60000;
  function tsLoad(){
    if(window.turnstile)return Promise.resolve(window.turnstile);
    if(TSP)return TSP;
    TSP=new Promise((ok,ko)=>{const s=document.createElement("script");s.src="https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit";s.async=true;
      const t=setTimeout(()=>{TSP=null;ko({code:"network",message:"turnstile"})},15000);
      s.onload=()=>{clearTimeout(t);window.turnstile?ok(window.turnstile):(TSP=null,ko({code:"network",message:"turnstile"}))};
      s.onerror=()=>{clearTimeout(t);TSP=null;s.remove();ko({code:"network",message:"turnstile"})};document.head.appendChild(s)});
    return TSP;
  }
  async function tsToken(){
    if(!window.SOB_TS)throw{code:"http503",message:"turnstile non configuré"};
    const ts=await tsLoad();
    return new Promise((ok,ko)=>{
      let box=document.getElementById("sob-ts");if(!box){box=document.createElement("div");box.id="sob-ts";box.style.cssText="position:fixed;left:50%;bottom:12px;transform:translateX(-50%);z-index:99999";document.body.appendChild(box)}
      let id=null,done=0;const end=(f,v)=>{if(done)return;done=1;clearTimeout(t);try{if(id!=null)ts.remove(id)}catch(e){}f(v)};
      const t=setTimeout(()=>end(ko,{code:"timeout",message:"turnstile"}),60000);
      try{id=ts.render(box,{sitekey:window.SOB_TS,action:"sobremesa-ia",appearance:"interaction-only",callback:tok=>end(ok,tok),"error-callback":()=>end(ko,{code:"http401",message:"turnstile"}),"expired-callback":()=>end(ko,{code:"http401",message:"turnstile"})})}
      catch(e){end(ko,{code:"http401",message:"turnstile"})}
    });
  }
  async function session(force){
    if(!force&&fresh())return SESS.s;
    if(SESSP)return SESSP;
    SESSP=(async()=>{
      SESS=null;try{sessionStorage.removeItem("sob_ias")}catch(e){}
      const token=await tsToken();
      let r;try{r=await fetch(base()+"/session",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({token})})}catch(e){throw{code:"network",message:String(e)}}
      if(r.status===429)throw{code:"rate_limited",message:"rate_limited"};
      if(!r.ok)throw{code:"http"+r.status,message:"http"+r.status};
      const j=await r.json();if(!j||!j.s||!j.exp)throw{code:"http502",message:"session"};
      SESS={s:j.s,exp:j.exp};try{sessionStorage.setItem("sob_ias",JSON.stringify(SESS))}catch(e){}
      return SESS.s;
    })();
    try{return await SESSP}finally{SESSP=null}
  }
  async function relay(input,opts){
    if(typeof input!=="string")throw{code:"bad",message:"bad"};
    const mode=modeOf(input);if(!mode)throw{code:"bad",message:"bad"};
    const body=JSON.stringify({mode,prompt:input});
    const ac=new AbortController();const to=setTimeout(()=>ac.abort("timeout"),40000);if(opts.signal)opts.signal.addEventListener("abort",()=>ac.abort());
    try{
      for(let at=0;;at++){
        const s=await session(at>0);
        let r;
        try{r=await fetch(base()+"/ai",{method:"POST",headers:{"content-type":"application/json","authorization":"Bearer "+s},body,signal:ac.signal})}
        catch(e){if(opts.signal&&opts.signal.aborted)throw{code:"cancelled",message:"cancelled"};if(e&&e.name==="AbortError")throw{code:"timeout",message:"timeout"};throw{code:"network",message:String(e)}}
        if(r.status===401&&at===0){SESS=null;try{sessionStorage.removeItem("sob_ias")}catch(e){}continue}
        if(r.status===429)throw{code:"rate_limited",message:"rate_limited"};
        if(!r.ok||!r.body)throw{code:"http"+r.status,message:"http"+r.status};
        return await read(r.body,opts,false);
      }
    }finally{clearTimeout(to)}
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
