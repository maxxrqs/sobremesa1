// Compatibilité : l'appli appelle claude.use("sample") (IA de l'artefact).
// Hors de Claude, on branche le même appel sur le relais IA (Worker). Sans relais : IA non disponible.
(function(){
  if(window.claude&&window.claude.use)return;
  /* Sans relais configuré : IA gratuite sans clé (Pollinations). Moins fiable que le relais Gemini ; en cas d'échec l'appli affiche « indisponible ». */
  async function free(input,opts){
    opts=opts||{};
    const msgs=typeof input==="string"?[{role:"user",content:input}]:input.map(t=>({role:t.role==="assistant"?"assistant":"user",content:String(t.content||"")}));
    let r;
    try{r=await fetch("https://text.pollinations.ai/openai",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({model:"openai",messages:msgs,private:true}),signal:opts.signal})}
    catch(e){if(e&&e.name==="AbortError")throw{code:"cancelled",message:"cancelled"};throw{code:"network",message:String(e)}}
    if(r.status===429)throw{code:"rate_limited",message:"rate_limited"};
    if(!r.ok)throw{code:"http"+r.status,message:"http"+r.status};
    let j;try{j=await r.json()}catch(e){throw{code:"bad",message:"bad"}}
    const text=String(j&&j.choices&&j.choices[0]&&j.choices[0].message&&j.choices[0].message.content||"");
    if(!text)throw{code:"empty",message:"empty"};
    if(opts.onText)try{opts.onText({text,delta:text})}catch(e){}
    return{text,truncated:false};
  }
  async function sample(input,opts){
    if(!window.SOB_AI)return free(input,opts);
    opts=opts||{};
    const body={tier:opts.modelTier||"default"};
    if(typeof input==="string")body.prompt=input;else body.turns=input;
    let r;
    try{r=await fetch(window.SOB_AI,{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify(body),signal:opts.signal})}
    catch(e){if(e&&e.name==="AbortError")throw{code:"cancelled",message:"cancelled"};throw{code:"network",message:String(e)}}
    if(r.status===429)throw{code:"rate_limited",message:"rate_limited"};
    if(!r.ok||!r.body)throw{code:"http"+r.status,message:"http"+r.status};
    const rd=r.body.getReader(),dec=new TextDecoder();let text="";
    try{
      for(;;){
        const {done,value}=await rd.read();if(done)break;
        const d=dec.decode(value,{stream:true});if(!d)continue;
        text+=d;if(opts.onText)try{opts.onText({text,delta:d})}catch(e){}
      }
    }catch(e){if(e&&e.name==="AbortError")throw{code:"cancelled",message:"cancelled"};throw{code:"network",message:String(e),text}}
    return{text,truncated:false};
  }
  sample.json=async(i,o)=>{let t=(await sample(i,o)).text.trim().replace(/^```(?:json)?\s*/i,"").replace(/\s*```$/,"");try{return JSON.parse(t)}catch(e){const m=t.match(/[\[{][\s\S]*[\]}]/);if(m)return JSON.parse(m[0]);throw e}};
  sample.limits=async()=>({images:false});
  window.claude={use:async n=>n==="sample"?sample:null};
})();
