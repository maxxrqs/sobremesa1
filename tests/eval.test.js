// Tests de l'évaluation des réponses (node tests/eval.test.js [chemin du html])
const fs=require("fs"),vm=require("vm"),path=require("path");
const file=process.argv[2]||path.join(__dirname,"..","index.html");
const h=fs.readFileSync(file,"utf8"),a=h.indexOf("/*EV-BEGIN*/"),b=h.indexOf("/*EV-END*/");
if(a<0||b<0){console.log("module EV introuvable");process.exit(1)}
let LANG="es",LV=1;
const ctx={lg:()=>LANG,lv:()=>LV,UI:"fr",tr:(s,...x)=>s.replace(/\{(\d)\}/g,(m,i)=>x[i]),
 ALL:[["puerta","porte",1],["casa","maison",1],["caso","cas",2],["amigo","ami",1],["amiga","amie",1],["niño","garçon",1],["niña","fille",1],["pero","mais",1],["perro","chien",1],["gracias","merci",1],["gracia","grâce",2],["reunión","réunion",1],["año","an",1],["papá","papa",1],["papa","pomme de terre",2],["té","thé",1],["gato","chat",1],["gata","chatte",1],["buenos días","bonjour",1]],
 PH:[["Yo soy Marie","Je suis Marie",1],["Ella come pan","Elle mange du pain",1],["Él come pan","Il mange du pain",1],["Quiero un café con leche","Je veux un café au lait",1],["Tengo un perro","J'ai un chien",1],["Hablo español","Je parle espagnol",1],["Ayer habló con ella","Hier il a parlé avec elle",2],["Me llamo Max","Je m'appelle Max",1],["La puerta es azul","La porte est bleue",1],["Las puertas son azules","Les portes sont bleues",1]]};
vm.createContext(ctx);vm.runInContext(h.slice(a,b)+"\nthis.EV=EV;",ctx);
const EV=ctx.EV;let ok=0,ko=0;
function T(name,v,q,exp,msgRe){
  const r=EV.grade(v,q),good=r.s===exp&&(!msgRe||msgRe.test(r.m||""));
  if(good)ok++;else{ko++;console.log("ÉCHEC",name,JSON.stringify({v,exp,got:r.s,m:r.m}))}
}
const Q=(es,o)=>Object.assign({ty:"type",es,fr:"",acc:[es]},o||{});
// --- accents, majuscules, ponctuation
T("accent manquant","reunion",Q("reunión"),1,/reunión/);
T("accent en trop","reunión",Q("reunion"),1);
T("casse/ponctuation","¿DÓNDE ESTÁ LA PLAYA?",Q("¿Dónde está la playa?"),1);
T("sans signes","donde esta la playa",Q("¿Dónde está la playa?"),1);
T("exacte","reunión",Q("reunión"),1,/^$/);
T("espaces multiples","  me   llamo  max ",Q("Me llamo Max"),1);
// --- sens modifié par l'accent / ñ
T("papá/papa","papa",Q("papá"),.5,/accent/i);
T("té/te","te",Q("té"),.5);
T("año/ano","ano",Q("año"),.5);
T("él/el","el come",Q("él come"),.5);
T("esta/está sans aucun accent (habitude clavier)","donde esta la playa",Q("¿Dónde está la playa?"),1);
T("phrase tapée sans aucun accent (más)","puede hablar mas despacio",Q("¿Puede hablar más despacio?"),1);
T("mot isolé: mas/más reste signalé","mas",Q("más"),.5);
T("esta/está avec d'autres accents","¿Dónde esta la playa?",Q("¿Dónde está la playa?"),.5);
T("habló/hablo","hablo",Q("habló"),.5);
T("café/cafe (nom)","cafe",Q("café"),1);
T("qué/que (interrogatif)","que quieres",Q("¿Qué quieres?"),1);
// --- fautes de frappe
T("lettre doublée","perrro",Q("perro"),1,/faute de frappe/);
T("transposition","pueratas",Q("puertas"),1);
T("lettre oubliée long","reunon",Q("reunión"),1);
T("A1 mot long 2 fautes","comprension",Q("comprensión"),1);
T("pero≠perro","pero",Q("perro"),0);
T("casa≠caso","caso",Q("casa"),0);
T("mot trop court","gat",Q("gato"),0);
T("espace manquant","porfavor",Q("por favor"),1);
T("aucune ressemblance","mesa",Q("puerta"),0);
// --- genre / nombre / conjugaison
T("puertas pour puerta","puertas",Q("puerta",{}),.5,/pluriel de/);
T("el para la (déterminant)","el puerta",Q("la puerta"),.5,/genre/);
T("puerta pour puertas","puerta",Q("puertas"),.5);
T("casas pour casa","casas",Q("casa"),.5);
T("amiga pour amigo (même mot)","amiga",Q("amigo"),.5,/genre/);
T("gato/gata","gata",Q("gato"),.5);
T("niña pour niño = autre sens","niña",Q("niño"),0);
T("gracia pour gracias","gracia",Q("gracias"),0);
T("conjugaison: comes/come","ella comes pan",Q("Ella come pan"),.5);
T("conj. o/a: hablo/habla","yo habla",Q("yo hablo"),.5,/verbe/);
T("deux erreurs phrase courte","las puerta es azules",Q("La puerta es azul"),0);
T("mauvaise personne tengo/tienes","tienes un perro",Q("Tengo un perro"),0);
// --- pronom sujet facultatif, variantes
T("sans pronom","soy Marie",Q("Yo soy Marie"),1);
T("autre pronom","tú soy Marie",Q("Yo soy Marie"),0);
T("él≠ella (sujet différent)","él come pan",Q("Ella come pan"),0);
T("alias vale","de acuerdo",Q("vale"),1);
T("alias guay","guay",Q("genial"),1);
T("alias chao","chao",Q("adiós"),1);
T("alias qué tal","¿Qué tal?",Q("¿Cómo estás?"),1);
T("alias ordenador","computadora",Q("ordenador"),1);
T("alias refusé hors groupe","coche",Q("genial"),0);
T("dictée: pas d'alias","chao",Q("adiós",{ty:"dict"}),0);
T("dictée: accents ok","adios",Q("adiós",{ty:"dict"}),1);
T("dictée: typo ok","ayerr",Q("ayer",{ty:"dict"}),1);
T("dictée: pas de crédit partiel","puertas",Q("puerta",{ty:"dict"}),0);
T("liste de réponses (test)","tengo",{ty:"type",es:"tengo",acc:["tengo","tengo hambre"]},1);
T("test: conjugaison explicite sans crédit","tenga",{ty:"type",es:"tengo",acc:["tengo"],pr:"Conjugue : yo ___ (tener)"},0);
// --- niveaux et mode strict
LV=1;T("strict ignoré en A1","reunion",Q("reunión",{strict:1}),1);
LV=2;T("strict A2 : accent -> 50%","reunion",Q("reunión",{strict:1}),.5,/orthographe/);
T("strict A2 : exact -> 100%","reunión",Q("reunión",{strict:1}),1);
T("non strict A2","reunion",Q("reunión"),1);
LV=1;
// --- autres langues
LANG="ca";T("ca: accents","adeu",Q("adéu"),1);
T("ca: pluriel","cases",Q("casa"),.5);
T("ca: gender non géré (eu/ca)","amiga",Q("amic"),0);
LANG="eu";T("eu: accents/casse","KAIXO",Q("kaixo"),1);
LANG="gl";T("gl: typo","bos dias",Q("bos días"),1);
LANG="va";T("va: accent","visc a valencia",Q("Visc a València"),1);
LANG="es";
// --- score et robustesse
const r0=EV.grade("",Q("x"));if(r0.s===0)ok++;else{ko++;console.log("ÉCHEC vide")}
const r1=EV.grade("???",Q("hola"));if(r1.s===0)ok++;else{ko++;console.log("ÉCHEC ponctuation seule")}
console.log(`${ok} OK, ${ko} échec(s)`);process.exit(ko?1:0);
