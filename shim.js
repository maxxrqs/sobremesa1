// Compatibilité : l'appli appelle claude.use("sample") (IA de l'artefact).
// Hors de Claude, on branche le même appel sur le relais IA (Worker). Sans relais : IA non disponible.
(function(){
  if(window.claude&&window.claude.use)return;
  async function sample(input,opts){
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
  sample.json=async(i,o)=>JSON.parse((await sample(i,o)).text);
  sample.limits=async()=>({images:false});
  window.claude={use:async n=>(n==="sample"&&window.SOB_AI)?sample:null};
})();
