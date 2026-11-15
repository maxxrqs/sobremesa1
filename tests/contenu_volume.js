// Volume du contenu pédagogique par langue et par niveau (anomalie n°3 de l'audit du 7 novembre).
// Lit les blocs de données tels que build() les lit : RR (listes de vocabulaire), RW (mots des leçons), RP (phrases),
// RT (textes de lecture/écoute), RX (phrases d'exemple du vocabulaire en contexte), XD (répliques à produire à l'oral).
// Usage : node tests/contenu_volume.js [index.html] [--json sortie.json]
// Contrôle de reproduction : l'audit avait compté 936 mots de listes, 135 phrases et 33 textes par langue, dont 126 mots et 20 phrases en C1.
const fs=require("fs"),path=require("path");
const file=process.argv[2]&&!process.argv[2].startsWith("--")?process.argv[2]:path.join(__dirname,"..","index.html");
const ji=process.argv.indexOf("--json"),jout=ji>0?process.argv[ji+1]:null;
const h=fs.readFileSync(file,"utf8");
const blk=n=>{const m="const "+n+"=`",i=h.indexOf(m);if(i<0)return[];return h.slice(i+m.length,h.indexOf("`",i+m.length)).trim().split("\n").filter(Boolean).map(l=>l.split("|"))};
const RW=blk("RW"),RR=blk("RR"),RP=blk("RP"),RT=blk("RT"),RX=blk("RX");
const LK=["es","va","ca","gl","eu"],NV=["A1","A2","B1","B2","C1"];
// XD : objet JSON {langue:"niv|scène|réplique|consigne|réponse|variantes\n…"}
let XD={};{const i=h.indexOf("const XD=");if(i>=0){const a=h.indexOf("{",i);let d=0,e=a;for(let k=a;k<h.length;k++){const c=h[k];if(c==="\\"){k++;continue}if(c==='"'){k++;while(h[k]!=='"'){if(h[k]==="\\")k++;k++}continue}if(c==="{")d++;if(c==="}"){d--;if(!d){e=k+1;break}}}try{XD=JSON.parse(h.slice(a,e))}catch(x){XD={}}}}
// niveau d'un mot (clé = glose française) pour les phrases d'exemple
const lvK={};RW.forEach(c=>{lvK[c[2]]=Math.min(lvK[c[2]]||9,+c[1])});RR.forEach(c=>{lvK[c[3]]=Math.min(lvK[c[3]]||9,+c[2])});
const out={};
LK.forEach((L,k)=>{
  const z=()=>NV.map(()=>0),r={listes:z(),lecons:z(),phrases:z(),textes:z(),exemples:z(),oral:z()};
  RR.forEach(c=>{if((c[4+k]||"").trim())r.listes[+c[2]-1]++});
  RW.forEach(c=>{if((c[3+k]||"").trim())r.lecons[+c[1]-1]++});
  RP.forEach(c=>{if((c[2+k]||"").trim())r.phrases[+c[0]-1]++});
  RT.forEach(c=>{if((c[6+k]||"").trim())r.textes[+c[0]-1]++});
  RX.forEach(c=>{if((c[1+k]||"").trim()){const v=lvK[c[0]]||1;r.exemples[v-1]++}});
  String(XD[L]||"").split("\n").filter(Boolean).forEach(l=>{const v=+l.split("|")[0];if(v>=1&&v<=5)r.oral[v-1]++});
  out[L]=r;
});
const pad=(s,n)=>String(s).padStart(n);
console.log("Volume par langue et par niveau (A1 A2 B1 B2 C1 | total)");
for(const L of LK){console.log("\n"+L);for(const [t,a] of Object.entries(out[L]))console.log("  "+t.padEnd(9)+a.map(x=>pad(x,5)).join("")+" |"+pad(a.reduce((x,y)=>x+y,0),6))}
// contrôle de reproduction des chiffres de l'audit (castillan)
// l'audit comptait les lignes des blocs (une ligne = un mot pour les cinq langues, même si une case est vide)
const es=out.es,sum=a=>a.reduce((x,y)=>x+y,0);
const rep={listes:RR.length,phrases:RP.length,textes:RT.length,listesC1:RR.filter(c=>c[2]==="5").length,phrasesC1:RP.filter(c=>c[0]==="5").length};
console.log("\nChiffres de l'audit retrouvés (es) :",JSON.stringify(rep),rep.listes===936&&rep.phrases===135&&rep.textes===33&&rep.listesC1===126&&rep.phrasesC1===20?"→ identiques à l'audit du 7 novembre":"→ différents de l'audit (contenu modifié depuis)");
if(jout)fs.writeFileSync(jout,JSON.stringify(out,null,1));
