// Tests du profil adaptatif (module ADP) : node tests/adaptatif.test.js [chemin du html]
// Simule des réponses sur plusieurs jours avec une horloge contrôlée, sans navigateur.
const fs=require("fs"),vm=require("vm"),path=require("path");
const file=process.argv[2]||path.join(__dirname,"..","castellano.html");
const h=fs.readFileSync(file,"utf8"),a=h.indexOf("/*ADP-BEGIN"),b=h.indexOf("/*ADP-END*/");
if(a<0||b<0){console.log("module ADP introuvable");process.exit(1)}
let ok=0,ko=0;const T=(n,c,info)=>{if(c){ok++;console.log("OK  ",n)}else{ko++;console.log("FAIL",n,info===undefined?"":JSON.stringify(info))}};
function mk(lvl,sr){
  let now=Date.UTC(2026,9,1,9);
  const ctx={S:{lvl,sc:{},sk:{}},LANG:"es",lg:()=>ctx.LANG,lv:()=>ctx.S.lvl,SR:sr===false?null:function(){},
    tr:(s,...x)=>s.replace(/\{(\d)\}/g,(m,i)=>x[i]),gl:s=>s,NL:{1:"A1 · Débutant",2:"A2 · Élémentaire",3:"B1 · Intermédiaire",4:"B2 · Avancé",5:"C1 · Autonome"},
    ALL:[],PH:[],TX:[],pick:x=>x[0],Math};
  vm.createContext(ctx);vm.runInContext(h.slice(a,b)+"\nthis.A={ADP,adpRec,adpEst,adpF,adpT,adpDiff,adpStr,adpHtml,adpQB,adpWeakNot,adpSt};",ctx);
  ctx.A.ADP.now=()=>now;ctx.day=n=>{now+=n*864e5};ctx.hour=()=>{now+=36e5};
  return ctx;
}
// formats représentatifs de chaque compétence
const Q={
  co:[l=>({ty:"listenP",o:["a","b","c","d"],lv:l}),l=>({ty:"dict",lv:l}),l=>({ty:"listen",o:["a","b","c","d"],lv:l})],
  ce:[l=>({ty:"read",o:["a","b","c","d"],lv:l}),l=>({ty:"cloze",o:["a","b","c","d"],lv:l}),l=>({ty:"readP",lv:l})],
  ee:[l=>({ty:"type",lv:l}),l=>({ty:"build",lv:l}),l=>({ty:"conjT",tn:"Pretérito indefinido",lv:l})],
  eo:[l=>({ty:"speakF",lv:l}),l=>({ty:"speakQ",lv:l}),l=>({ty:"rep",lv:l})]};
// joue n réponses par jour pendant d jours ; p(L) = probabilité de réussite au niveau L (déterministe via compteur)
// réussites réparties régulièrement (suite à faible discrépance) pour atteindre exactement le taux p(L)
function play(c,k,d,n,p,levels){let i=0;const cnt={};for(let j=0;j<d;j++){for(let t=0;t<n;t++){const L=levels[i%levels.length],f=Q[k][i%Q[k].length];cnt[L]=(cnt[L]||0)+1;const v=((cnt[L]*0.6180339887)%1)<p(L)?1:0;c.A.adpRec(f(L),v);i++}c.day(1)}}
// plusieurs compétences pratiquées les mêmes jours, comme dans de vraies séries
function playDays(c,d,spec){for(let j=0;j<d;j++){spec.forEach(([k,n,p,lv])=>{const s=c["_"+k]=c["_"+k]||{i:0,cnt:{}};for(let t=0;t<n;t++){const L=lv[s.i%lv.length],f=Q[k][s.i%Q[k].length];s.cnt[L]=(s.cnt[L]||0)+1;c.A.adpRec(f(L),((s.cnt[L]*0.6180339887)%1)<p(L)?1:0);s.i++;c.hour()}});c.day(1)}}
const CEFR=["<A1","A1","A2","B1","B2","C1"];
const lab=e=>e.lvl===null?"?":CEFR[e.lvl];

// ---------- 1. Fort en compréhension orale, faible en expression écrite (parcours B1 = niveau 3)
{const c=mk(3);
  playDays(c,6,[["co",8,L=>L<=3?.95:L===4?.55:.3,[1,2,3,3,4]],["ce",6,L=>L<=2?.9:L===3?.75:.4,[1,2,3,3]],
    ["ee",8,L=>L===1?.85:L===2?.45:.2,[1,2,2,3]],["eo",5,L=>L<=2?.8:.6,[1,2,3]]]);
  const A=c.A,co=A.adpEst("co"),ee=A.adpEst("ee"),ce=A.adpEst("ce");
  console.log("   estimations :",{co:lab(co),ce:lab(ce),ee:lab(ee),eo:lab(A.adpEst("eo"))});
  T("compréhension orale estimée B1 (indépendamment des autres)",co.lvl===3,co);
  T("expression écrite estimée A1, sans être tirée vers le haut par l'oral",ee.lvl===1,ee);
  T("aucun niveau unique : chaque compétence a sa propre estimation",new Set(["co","ce","ee"].map(k=>A.adpEst(k).lvl)).size>=2);
  const f={co:A.adpF("co"),ee:A.adpF("ee")},t=A.adpT();
  console.log("   facteurs",f,"parts visées",Object.fromEntries(Object.entries(t).map(([k,v])=>[k,Math.round(v*100)])));
  T("expression écrite renforcée (facteur > 1,25)",f.ee>1.25,f);
  T("compréhension orale allégée (facteur < 0,85) mais pas supprimée",f.co<.85&&t.co>=.12,{f,t});
  T("part visée EE nettement supérieure à CO",t.ee>t.co*1.6,t);
  T("pratique minimale ≥ 12 % pour chacune des 4 compétences",Object.values(t).every(v=>v>=.119)&&Object.keys(t).length===4,t);
  const dc=A.adpDiff("co"),de=A.adpDiff("ee");
  T("difficulté : CO tirée vers le niveau du parcours, EE vers les niveaux déjà vus",dc>1.2&&de<.8,{dc,de});
  T("notion de grammaire fragile (prétérit) favorisée au tirage",A.adpQB({ty:"conjT",tn:"Pretérito indefinido"})>0&&A.adpWeakNot().includes("Pretérito indefinido"));
  const html=A.adpHtml();T("la carte affiche les 4 compétences séparément et le niveau de parcours à part",["co","ce","ee","eo"].every(k=>html.includes('data-sk="'+k+'"'))&&/niveau de parcours \(B1\)/.test(html),html.slice(0,300));
  // ---------- 2. Pas de sur-réaction : 4 erreurs d'affilée sur une compétence solide
  console.log("   CO avant :",JSON.stringify(A.adpEst("co")));const before=A.adpF("co"),e0=A.adpEst("co").lvl;for(let i=0;i<4;i++)A.adpRec({ty:"dict",lv:3},0);
  const after=A.adpF("co");
  T("4 erreurs isolées ne font pas chuter l'estimation CO",A.adpEst("co").lvl===e0,A.adpEst("co"));
  T("4 erreurs isolées ne changent le facteur CO que modérément (< +0,35)",after-before<.35,{before,after});
}
// ---------- 3. Débutant : quelques réponses ne prouvent rien
{const c=mk(1),A=c.A;
  A.adpRec({ty:"listenP",o:["a","b","c","d"],lv:4},1);A.adpRec({ty:"read",o:["a","b","c","d"],lv:4},1);A.adpRec({ty:"listen",o:["a","b"],lv:3},1);
  T("3 bonnes réponses QCM au B2 : compétence toujours « pas encore évaluée »",A.adpEst("co").lvl===null&&A.adpEst("ce").lvl===null);
  T("adaptation quasi neutre sans preuves (facteurs entre 0,9 et 1,1)",["co","ce","ee","eo"].every(k=>Math.abs(A.adpF(k)-1)<.1),["co","ce","ee","eo"].map(k=>A.adpF(k)));
  for(let i=0;i<3;i++)A.adpRec({ty:"type",lv:1},0);
  T("3 erreurs d'écriture ne déclenchent pas un renforcement massif (facteur < 1,25)",A.adpF("ee")<1.25,A.adpF("ee"));
}
// ---------- 4. QCM seuls : ni maîtrise sur une seule journée, ni B1 sans production
{const c=mk(3),A=c.A;
  for(let i=0;i<20;i++)A.adpRec({ty:"cloze",o:["a","b","c","d"],lv:3},1);
  T("20 QCM réussis le même jour : niveau non reconnu (≥ 2 jours exigés)",!(A.adpEst("ce").lvl>=3),A.adpEst("ce"));
  c.day(1);for(let i=0;i<20;i++)A.adpRec({ty:"cloze",o:["a","b","c","d"],lv:3},1);
  T("QCM seuls sur 2 jours : B1 refusé (production exigée à partir du B1)",A.adpEst("ce").lvl!==3,A.adpEst("ce"));
  const r=A.adpEst("ce");T("…et l'incertitude est signalée (provisoire, palier supérieur possible)",r.st==="prov",r);
}
// ---------- 5. Correction du hasard : répondre au hasard en QCM ne fait pas un niveau
{const c=mk(2),A=c.A;
  for(let d=0;d<4;d++){for(let i=0;i<12;i++)A.adpRec({ty:"listen",o:["a","b","c","d"],lv:1},i%4===0?1:0);c.day(1)}
  const e=A.adpEst("co");T("25 % de réussite sur QCM à 4 choix (hasard) : A1 non acquis",e.lvl===0,e);
}
// ---------- 6. Oubli : compétence solide non pratiquée depuis 3 semaines → réactivée ; récence
{const c=mk(2),A=c.A;
  play(c,"ce",5,8,()=>.95,[1,2,2]);const f0=A.adpF("ce");c.day(21);const f1=A.adpF("ce");
  T("acquis non pratiqué depuis 3 semaines : réintroduit (facteur ≥ 1,35)",f0<.85&&f1>=1.35,{f0,f1});
  T("l'estimation reste connue après une pause (pas d'effacement)",A.adpEst("ce").lvl>=2,A.adpEst("ce"));
}
// ---------- 7. Décrochage récent sur un acquis : fragile
{const c=mk(2),A=c.A;
  play(c,"ee",5,8,()=>.9,[1,2,2]);const f0=A.adpF("ee");for(let i=0;i<6;i++){A.adpRec({ty:"type",lv:2},0);c.hour()}
  T("acquis qui décroche (6 échecs récents) : renforcé, sans effondrer l'estimation",A.adpF("ee")>=1.35&&A.adpEst("ee").lvl>=1,{f0,f:A.adpF("ee"),e:A.adpEst("ee")});
}
// ---------- 8. Langues séparées, micro absent, C2 jamais estimé
{const c=mk(5,false),A=c.A;
  play(c,"co",8,10,()=>.98,[5,5,4]);
  T("excellent au C1 : estimation plafonnée à C1 (pas de contenu C2)",A.adpEst("co").lvl===5,A.adpEst("co"));
  c.LANG="eu";T("profil distinct par langue étudiée (basque vierge)",A.adpEst("co").lvl===null);
  T("sans micro : l'expression orale sort des parts visées, les 3 autres gardent ≥ 12 %",!("eo" in A.adpT())&&Object.values(A.adpT()).every(v=>v>=.119));
}
console.log(`\n${ok} OK, ${ko} échec(s)`);process.exit(ko?1:0);
