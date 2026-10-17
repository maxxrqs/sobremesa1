// Toutes les réponses attendues du test de niveau (production écrite « y » et dictée « d ») doivent rester à 100 %, avec ou sans accents.
const fs=require("fs"),vm=require("vm");const h=fs.readFileSync(process.argv[2],"utf8");
const a=h.indexOf("/*EV-BEGIN*/"),b=h.indexOf("/*EV-END*/");
const i=h.indexOf("const PTB={"),j=h.indexOf("\n];",h.indexOf("]}",i)>0?i:i);
// PTB = objet {langue:[...]} : on l'évalue tel quel
let end=i;let depth=0,started=false;for(let k=h.indexOf("{",i);k<h.length;k++){const c=h[k];if(c==="{")depth++;if(c==="}"){depth--;if(depth===0){end=k+1;break}}}
const ctx={lg:()=>"es",lv:()=>1,UI:"fr",tr:(s,...x)=>s.replace(/\{(\d)\}/g,(m,i)=>x[i]),ALL:[],PH:[]};vm.createContext(ctx);
vm.runInContext(h.slice(i,end).replace("const PTB=","this.PTB=")+";"+h.slice(a,b)+"\nthis.EV=EV;",ctx);
const strip=s=>s.normalize("NFD").replace(/[̀-ͯ]/g,"").toLowerCase().replace(/[¿¡?!.,;:]/g,"");
let n=0,ko=0;
for(const [lang,items] of Object.entries(ctx.PTB)){ctx.lg=()=>lang;
  items.forEach(it=>{const k=it[1];let accs=null;if(k==="y")accs=it[3];else if(k==="d")accs=[it[2]];if(!accs)return;
    accs.forEach(x=>{[x,strip(x)].forEach(v=>{n++;const r=ctx.EV.grade(v,{ty:k==="d"?"dict":"type",es:accs[0],acc:accs});if(r.s!==1){ko++;console.log("KO",lang,JSON.stringify(v),r.s)}})})})}
console.log(`réponses du test de niveau vérifiées : ${n}, hors 100 % : ${ko}`);process.exit(ko?1:0);
