// Tests de la notation orale (reconnaissance vocale) : node tests/asr.test.js [chemin du html]
// Simule ce que renvoie le micro (texte + alternatives + confiance) ; ne teste PAS la qualité du micro lui-même.
const fs=require("fs"),vm=require("vm"),path=require("path");
const file=process.argv[2]||path.join(__dirname,"..","index.html");
const h=fs.readFileSync(file,"utf8"),a=h.indexOf("/*ASR-BEGIN"),b=h.indexOf("/*ASR-END*/");
if(a<0||b<0){console.log("module ASR introuvable");process.exit(1)}
let LANG="es";
const VOC={es:[["playa"],["perro"],["pero"],["año"],["ano"],["habla"],["hablo"],["café"],["agua"],["gracias"],["casa"],["plaza"]],
 ca:[["l'aigua"],["plaça"],["placa"],["bon dia"],["anys"],["tinc"],["el"],["que"],["es"]],va:[["huit"],["anys"],["tinc"]],
 gl:[["teño"],["irmáns"],["vivo"],["no centro"]],eu:[["kaixo"],["urte"],["ditut"],["ulertzen"]]};
const ctx={lg:()=>LANG,lv:()=>1,EOTH:[0,.6,.66,.72,.78,.8],LFR:{es:"castillan",va:"valencien",ca:"catalan",gl:"galicien",eu:"basque"},
 tr:(s,...x)=>s.replace(/\{(\d)\}/g,(m,i)=>x[i]),esc:s=>String(s),ALL:[],PH:[]};
vm.createContext(ctx);vm.runInContext(h.slice(a,b)+"\nthis.eoGrade=eoGrade;this.eoTok=eoTok;",ctx);
let ok=0,ko=0;
function T(name,lang,target,alts,exp,o){
  LANG=lang;ctx.ALL=VOC[lang]||[];const g=ctx.eoGrade(Array.isArray(alts)?alts:[alts],target,1,o||{});
  const bad=Object.entries(exp).filter(([k,v])=>k==="u"?(g.u||"")!==v:k==="minS"?g.s<v:k==="maxS"?g.s>v:g[k]!==v);
  if(!bad.length)ok++;else{ko++;console.log("ÉCHEC",name,JSON.stringify({alts,exp,got:{full:g.full,s:+g.s.toFixed(2),u:g.u,msg:g.msg}}))}
}
const OK={full:true,u:""},NO={full:false,u:""};
// --- bonnes réponses, écritures du micro différentes de la cible
T("exacte + ponctuation","es","¿Dónde está la playa?","Dónde está la playa",OK);
T("sans accents","es","¿Dónde está la playa?","donde esta la playa",OK);
T("chiffre 9","es","Empiezo a las nueve.","empiezo a las 9",OK);
T("chiffre 2","es","Necesito dos habitaciones.","necesito 2 habitaciones",OK);
T("chiffre 1 = un","es","Un café, por favor.","1 café por favor",OK);
T("chiffre 31","es","Tengo treinta y un años.","tengo 31 años",OK);
T("heure 9:30","es","A las nueve treinta.","a las 9:30",OK);
T("mots en trop (hésitation)","es","Quiero un café, por favor.","eh quiero un café por favor",OK);
T("mots collés","es","¿A dónde vas?","adónde vas",OK);
T("mot coupé","es","Yo también.","yo tan bien",OK);
T("seseo/ceceo toléré","es","Me gustan los zapatos.","me gustan los sapatos",OK);
T("yeísmo toléré","es","Quiero pollo.","quiero poyo",OK);
T("b/v toléré","es","Vamos a la playa.","bamos a la playa",OK);
// --- vraies erreurs : sens ou prononciation différents
T("año/ano","es","Tengo un año.","tengo un ano",{full:false});
T("perro/pero","es","Tengo un perro.","tengo un pero",{full:false});
T("plaza/playa","es","¿Dónde está la plaza?","dónde está la playa",{full:false});
T("forme verbale","es","Hablo español.","habla español",{full:false});
T("négation ajoutée","es","Me gusta el café.","no me gusta el café",{full:false,u:""});
T("négation oubliée","es","No, nada más, gracias.","nada más gracias",{full:false,u:""});
T("réponse fausse","es","¿Dónde está la playa?","hola",{full:false,u:""});
T("réponse fausse qui commence pareil","es","Quiero un café.","quiero agua",{full:false,u:""});
T("validation partielle impossible","es","¿Dónde está la playa?","dónde está la",{full:false});
// --- incertitudes : répéter, sans valider ni pénaliser
T("début seulement","es","¿Dónde está la playa?","dónde está",{full:false,u:"cut"});
T("résultat partiel incomplet","es","Quiero un café con leche.","quiero un café",{full:false,u:"cut"},{part:1});
T("résultat partiel complet = accepté","es","Quiero un café.","quiero un café",OK,{part:1});
T("français entendu (mot)","es","Gracias.","merci",{full:false,u:"lang"});
T("français entendu (phrase)","es","Quiero un café.","je voudrais un café",{full:false,u:"lang"});
T("seule l'alternative 2 colle","es","Tengo un perro.",["tengo un pero","tengo un perro"],{full:true,u:"alt"});
T("alternative 1 correcte","es","Tengo un perro.",["tengo un perro","tengo un pero"],OK);
T("confiance très basse","es","Quiero un café.","quiero un café",{u:"conf"},{conf:.15});
T("confiance basse + écart","es","Quiero un café.","quiero un cafe que",{u:""},{conf:.9});
T("confiance basse, réponse fausse","es","Quiero un café.","quiero agua",{full:false,u:"conf"},{conf:.3});
T("un mot manquant dans une longue phrase","es","Mañana voy a visitar el museo con mis amigos.","mañana voy a visitar el con mis amigos",{full:false,u:"miss"});
T("petit mot de 3 lettres oublié (A1)","es","Una paella, por favor.","una paella favor",OK);
T("« sin » oublié","es","Un café sin azúcar.","un café azúcar",{full:false});
T("vide","es","Hola.","",{full:false});
// --- catalan / valencien
T("ca apostrophe collée","ca","L'aigua, si us plau.","laigua si us plau",OK);
T("ca apostrophe","ca","L'aigua, si us plau.","l'aigua si us plau",OK);
T("ca plaça/placa","ca","On és la plaça?","on és la placa",{full:false});
T("ca 21","ca","Tinc vint-i-un anys.","tinc 21 anys",OK);
T("ca : castillan renvoyé","ca","Bon dia.","buenos días",{full:false,u:"lang"});
T("va huit/vuit","va","Tinc huit anys.","tinc vuit anys",OK);
T("va chiffre 8","va","Tinc huit anys.","tinc 8 anys",OK);
// --- galicien
T("gl chiffre 2 = dous","gl","Teño dous irmáns.","teño 2 irmáns",OK);
T("gl « no » n'est pas une négation","gl","Vivo no centro.","vivo no centro",OK);
T("gl négation ajoutée","gl","Vivo no centro.","non vivo no centro",{full:false});
T("gl : castillan renvoyé","gl","Moitas grazas.","muchas gracias",{full:false,u:"lang"});
// --- euskara
T("eu 21","eu","Hogeita bat urte ditut.","21 urte ditut",OK);
T("eu négation oubliée","eu","Ez dut ulertzen.","dut ulertzen",{full:false});
T("eu : castillan renvoyé","eu","Kaixo.","hola",{full:false,u:"lang"});
console.log(ok,"OK,",ko,"échec(s)");process.exit(ko?1:0);
