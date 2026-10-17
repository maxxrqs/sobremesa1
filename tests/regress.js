// Régression sur les vraies données : (1) réponse exacte, (2) réponse sans accents/majuscules/ponctuation, (3) mauvaise réponse prise ailleurs dans la base
const fs=require("fs"),vm=require("vm");
const h=fs.readFileSync(process.argv[2],"utf8"),a=h.indexOf("/*EV-BEGIN*/"),b=h.indexOf("/*EV-END*/");
const grab=n=>{const i=h.indexOf("const "+n+"=`");const j=h.indexOf("`",i+n.length+9);return h.slice(i+n.length+9,j).trim().split("\n")};
const RW=grab("RW"),RP=grab("RP");const LK=["es","va","ca","gl","eu"];
let out=[];
for(let k=0;k<5;k++){
  const lang=LK[k];
  const ALL=RW.map(l=>{const c=l.split("|");return[c[3+k],c[2],+c[1]]}),PH=RP.map(l=>{const c=l.split("|");return[c[2+k],c[1],+c[0]]});
  const ctx={lg:()=>lang,lv:()=>1,UI:"fr",tr:(s,...x)=>s.replace(/\{(\d)\}/g,(m,i)=>x[i]),ALL,PH};
  vm.createContext(ctx);vm.runInContext(h.slice(a,b)+"\nthis.EV=EV;",ctx);const EV=ctx.EV;
  const items=ALL.concat(PH).map(x=>x[0]).filter(Boolean);
  const strip=s=>s.normalize("NFD").replace(/[̀-ͯ]/g,"").toLowerCase().replace(/[¿¡?!.,;:]/g,"");
  let exact=0,loose=0,losses=[],fa=[];
  items.forEach(it=>{
    const q={ty:"type",es:it,acc:[it]};
    if(EV.grade(it,q).s===1)exact++;else losses.push(["EXACT",it]);
    const r=EV.grade(strip(it),q);if(r.s===1)loose++;else losses.push(["SANSACC("+r.s+")",it]);
  });
  // faux positifs : réponse d'un autre item (échantillon déterministe)
  let tested=0,fp=0;
  for(let i=0;i<items.length;i+=3){const j=(i*7+13)%items.length;if(strip(items[i])===strip(items[j]))continue;tested++;
    const r=EV.grade(items[j],{ty:"type",es:items[i],acc:[items[i]]});if(r.s>0){fp++;if(fa.length<12)fa.push([items[i],items[j],r.s])}}
  out.push({lang,n:items.length,exact,loose,fp,tested,losses:losses.slice(0,200),fa});
}
out.forEach(o=>{console.log(`${o.lang}: ${o.n} entrées | exact 100% : ${o.exact} | sans accents 100% : ${o.loose} | faux positifs sur ${o.tested} paires : ${o.fp}`);
 const ex=o.losses.filter(x=>x[0]==="EXACT");if(ex.length)console.log("  EXACT KO:",ex.slice(0,8).map(x=>x[1]));
 const lo=o.losses.filter(x=>x[0]!=="EXACT");console.log("  perdus sans accents:",lo.length,lo.slice(0,10).map(x=>x[0]+" "+x[1]));
 if(o.fa.length)console.log("  faux positifs:",JSON.stringify(o.fa))});
