// Mutations : un mot de la base remplacé par un AUTRE mot réel de la base à 1 lettre près ne doit jamais obtenir 100 %.
const fs=require("fs"),vm=require("vm");
const h=fs.readFileSync(process.argv[2],"utf8"),a=h.indexOf("/*EV-BEGIN*/"),b=h.indexOf("/*EV-END*/");
const grab=n=>{const i=h.indexOf("const "+n+"=`");const j=h.indexOf("`",i+n.length+9);return h.slice(i+n.length+9,j).trim().split("\n")};
const RW=grab("RW"),RP=grab("RP"),LK=["es","va","ca","gl","eu"];let bad=0,tot=0,part=0;
for(let k=0;k<5;k++){const lang=LK[k];
  const ALL=RW.map(l=>{const c=l.split("|");return[c[3+k],c[2],+c[1]]}),PH=RP.map(l=>{const c=l.split("|");return[c[2+k],c[1],+c[0]]});
  const ctx={lg:()=>lang,lv:()=>1,UI:"fr",tr:(s,...x)=>s.replace(/\{(\d)\}/g,(m,i)=>x[i]),ALL,PH};vm.createContext(ctx);vm.runInContext(h.slice(a,b)+"\nthis.EV=EV;",ctx);const EV=ctx.EV;
  const toks=[...new Set(ALL.concat(PH).flatMap(x=>EV.raw(x[0]).split(" ")).filter(w=>w.length>=4))];
  const F=w=>EV.fold(w);
  toks.forEach(w=>toks.forEach(u=>{if(w===u||F(w)===F(u))return;if(Math.abs(w.length-u.length)>1)return;if(EV.dl(F(w),F(u))>1)return;
    tot++;const r=EV.grade(u,{ty:"type",es:w,acc:[w]});if(r.s===1){bad++;console.log(lang,"100% à tort:",u,"pour",w)}else if(r.s>0){part++;if(part%4==0&&process.env.SHOW)console.log("50%",lang,u,"/",w,"=>",r.m.slice(0,70))}}));
}
console.log(`paires de vrais mots à 1 lettre près: ${tot} | 100% à tort: ${bad} | 50%: ${part}`);process.exit(bad?1:0);
