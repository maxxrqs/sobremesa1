# Refonte des exercices : répartition des 4 compétences, formats dominants réduits, expression orale réelle (notation, formats,
# secours), apprendre avant tester, progression cohérente par niveau/unité.
import sys,json,re
from playwright.sync_api import sync_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else "http://localhost:8772/"
R=[]
def ck(n,c,i=""):
    R.append(bool(c));print("OK  " if c else "FAIL",n,"" if c else str(i)[:500],flush=True)
FAKE="""window.__srRes=null;window.__srErr=null;window.__ev={a:1,s:1,sp:1};window.__gum='ok';
navigator.mediaDevices.getUserMedia=async()=>({getTracks:()=>[{stop(){}}]});
class FSR{start(){const t=this;setTimeout(()=>{t.onaudiostart&&t.onaudiostart();t.onsoundstart&&t.onsoundstart();t.onspeechstart&&t.onspeechstart();
 if(window.__srErr)t.onerror&&t.onerror({error:window.__srErr});else if(window.__srRes!==null)t.onresult&&t.onresult({results:[Object.assign([{transcript:window.__srRes}],{isFinal:true})]});t.onend&&t.onend()},15)}abort(){}stop(){}}
window.SpeechRecognition=FSR;window.webkitSpeechRecognition=FSR;"""
NOSR="delete window.SpeechRecognition;delete window.webkitSpeechRecognition;"
DIST="""(a)=>{const out={};for(const lang of a.langs){for(let L=1;L<=5;L++){S.lang=lang;S.lvl=L;S.pth={};S.rat={};S.rq={};S.md={};build();PLC=null;const T={};let n=0,er=0;
 for(const st of pathPlanMain().flat){if(st.test)continue;
  R={mode:'lesson',t:st.t||'Chunk',n:0,ok:0,xp:0,cat:null,pid:st.id,pt:st.pt||null,ws:st.ws||null,dp:st.dp||null,gp:st.gp||null,go:st.go||null,xs:st.xs||null,qs:st.qs||null,vs:st.vs||null,pp:st.pp||null,kn:st.kn||null,tn:st.tn||null};
  for(let i=0;i<10;i++){R.n=i;try{const q=mkQ(pickType(),0);T[q.ty]=(T[q.ty]||0)+1;n++;const m=MODL[q.ty];if(m){S.md[lang]=S.md[lang]||[];S.md[lang].push(m);if(S.md[lang].length>80)S.md[lang].shift()}}catch(e){er++}}}
 out[lang+L]={n,T,er}}}return out}"""
def shares(res,sr):
    tot={};err=0
    for v in res.values():
        err+=v["er"]
        for a,c in v["T"].items():tot[a]=tot.get(a,0)+c
    N=sum(tot.values());MOD={"co":["listen","listenP","listenT","exL","dict"],"eo":["speak","rep","speakF","speakC","speakQ"],"ce":["read","readP","es2fr","tf","odd","cloze","exM","exc"],"ee":["build","type","fr2P","fr2es","conj","exE","replyQ"]}
    return {m:100*sum(tot.get(t,0) for t in ts)/N for m,ts in MOD.items()},{a:100*c/N for a,c in tot.items()},err,N
with sync_playwright() as p:
    b=p.chromium.launch()
    # ---------- A. répartition (reconnaissance vocale disponible)
    c=b.new_context(locale="fr-FR");pg=c.new_page();er=[];pg.on("pageerror",lambda e:er.append(str(e)));pg.add_init_script(FAKE);pg.goto(BASE+"index.html");pg.wait_for_timeout(2000)
    res=pg.evaluate(DIST,{"langs":["es","va","ca","gl","eu"]});m,t,e,N=shares(res,True)
    print("   parts (%):",{k:round(v,1) for k,v in m.items()},"| odd",round(t.get("odd",0),1),"es2fr",round(t.get("es2fr",0),1),"listen",round(t.get("listen",0),1),"| N =",N)
    ck("4 compétences : chacune entre 18 % et 33 % (5 langues × 5 niveaux)",all(18<=v<=33 for v in m.values()),m)
    ck("« Quel mot n'appartient pas » nettement réduit (avant 8,9 % → ≤ 2 %)",t.get("odd",0)<=2,t.get("odd"))
    ck("écoute d'un mot puis choix (es2fr) réduit (avant 10,5 % → ≤ 7 %)",t.get("es2fr",0)<=7,t.get("es2fr"))
    ck("écoute d'un mot puis choix du mot réduit (avant 10,9 % → ≤ 8 %)",t.get("listen",0)<=8,t.get("listen"))
    ck("expression orale = productions de l'élève (répéter, dire, compléter, répondre) ≥ 15 %",sum(t.get(x,0) for x in ["rep","speakF","speakC","speakQ","speak"])>=15)
    ck("aucune erreur de génération",e==0 and not er,[e,er]);c.close()
    # ---------- B. sans reconnaissance vocale : aucun format oral, équivalents écrits, pas de simulation
    c=b.new_context(locale="fr-FR");pg=c.new_page();er=[];pg.on("pageerror",lambda e:er.append(str(e)));pg.add_init_script(NOSR);pg.goto(BASE+"index.html");pg.wait_for_timeout(2000)
    res=pg.evaluate(DIST,{"langs":["es","gl"]});m,t,e,N=shares(res,False)
    ck("sans reconnaissance vocale : aucun format oral généré",all(t.get(x,0)==0 for x in ["speak","rep","speakF","speakC","speakQ"]),t)
    ck("sans reconnaissance vocale : remplacé par de l'écrit/écoute (EE+CO+CE = 100 %), sans erreur",e==0 and not er and abs(sum(m.values())-100)<.01,[m,e,er])
    pg.evaluate("S.lang='es';S.lvl=2;S.pth={};S.pthAll=1;build();PLC=null;const st=pathPlanMain().flat.find(x=>x.t==='EO');pstart(st.id);")
    pg.wait_for_timeout(300)
    ck("sans reconnaissance vocale : l'étape d'expression orale l'indique clairement",pg.evaluate("document.body.innerText.includes('Reconnaissance vocale indisponible')") or pg.evaluate("!!document.querySelector('.disc')"),pg.evaluate("document.body.innerText.slice(0,300)"));c.close()
    # ---------- C. notation de l'oral
    c=b.new_context(locale="fr-FR");pg=c.new_page();pg.add_init_script(FAKE);pg.goto(BASE+"index.html");pg.wait_for_timeout(2000)
    G=lambda alts,t,L=1,need=None:pg.evaluate("([a,t,L,n])=>{S.lang='es';const g=eoGrade(a,t,L,n?{need:n}:{});return{s:g.s,full:g.full,score:g.score,msg:g.msg}}",[alts,t,L,need])
    g=G(["donde esta la playa"],"¿Dónde está la playa?");ck("sans accents ni ponctuation : accepté",g["full"] and g["score"]==1,g)
    g=G(["grasias"],"gracias");ck("seseo (c/z → s) accepté, accent régional non pénalisé",g["full"],g)
    g=G(["bamos a la bentana"],"vamos a la ventana");ck("b/v confondus (variante régionale) acceptés",g["full"],g)
    g=G(["donde esta playa"],"¿Dónde está la playa?");ck("petit mot oublié (article) : accepté",g["full"],g)
    g=G(["yo habla español"],"yo hablo español",1);ck("mauvaise terminaison verbale détectée comme mot différent (grammaire)",("Mot différent" in g["msg"]),g)
    g=G(["grasyas por faboh"],"gracias por favor");ck("mot inconnu proche : signalé comme prononciation",("Prononciation" in g["msg"]),g)
    g=G(["banana computadora azul"],"¿Dónde está la playa?");ck("réponse sans rapport : 0",g["score"]==0 and not g["full"],g)
    g=G(["quiero un por favor"],"Quiero un café por favor",1,"café");ck("complétion orale : mot manquant obligatoire",not g["full"],g)
    g1=G(["una paella favor"],"una paella por favor",1);g3=G(["una paella favor"],"una paella por favor",5);ck("exigence adaptée au niveau (A1 plus tolérant que C1)",g1["full"] and not g3["full"],[g1,g3])
    g=G(["hola buenos dias","hola buenas dias","ola buenos dias"],"Hola, buenos días");ck("plusieurs hypothèses du moteur : la meilleure est retenue",g["full"])
    c.close()
    # ---------- D. formats oraux : génération valide, UI complète avec reconnaissance simulée par le navigateur de test
    c=b.new_context(locale="fr-FR",viewport={"width":390,"height":844});pg=c.new_page();er=[];pg.on("pageerror",lambda e:er.append(str(e)));pg.add_init_script(FAKE);pg.goto(BASE+"index.html");pg.wait_for_timeout(2000)
    bad=pg.evaluate("""()=>{const bad=[];for(const lang of ['es','va','ca','gl','eu'])for(let L=1;L<=5;L++){S.lang=lang;S.lvl=L;build();for(const ty of ['rep','speakF','speakC','speakQ','replyQ']){for(let i=0;i<25;i++){
      R={mode:'lesson',t:'Mélange',n:0,ok:0,xp:0,pt:null};let q;try{q=mkQ0(ty,0)}catch(e){bad.push([lang,L,ty,String(e)]);break}
      if(!q||!q.ty||!(q.es||q.models)||!(q.say||q.models)){bad.push([lang,L,ty,'incomplet']);break}
      if(q.ty==='speakC'&&(!q.txt.includes('_____')||!q.g)){bad.push([lang,L,ty,'trou']);break}
      if((q.ty==='speakQ'||q.ty==='replyQ')&&(!q.npc||!q.models.length)){bad.push([lang,L,ty,'dialogue']);break}
      if(q.ty==='rep'||q.ty==='speakF'){const w=q.es.split(' ').length,cap=CAPW[q.ty==='rep'?'c':'p'][L];if(w>Math.max(cap,2)&&!q.word){bad.push([lang,L,ty,'trop long '+w+'>'+cap]);break}}}}}return bad.slice(0,5)}""")
    ck("rep/speakF/speakC/speakQ/replyQ : questions valides (5 langues × 5 niveaux), longueurs plafonnées par niveau",not bad,bad)
    def lesson(ty,lang="es",L=2):
        pg.evaluate("([ty,lang,L])=>{S.lang=lang;S.lvl=L;S.mute=true;build();R={mode:'lesson',t:'Mélange',n:0,ok:0,xp:0,pt:[ty]};R.q=mkQ0(ty,0);show()}",[ty,lang,L]);pg.wait_for_timeout(250)
    for ty,expect in [("rep","Écoute et répète"),("speakF","Dis en"),("speakC","Complète à voix haute"),("speakQ","Réponds à voix haute")]:
        lesson(ty);ck(f"{ty} : consigne affichée, bouton Parler",expect in pg.evaluate("document.body.innerText") and pg.query_selector("button[onclick='rec()']"),pg.evaluate("document.body.innerText.slice(0,200)"))
        ans=pg.evaluate("R.q.models?R.q.models[0]:R.q.es");pg.evaluate("(a)=>{window.__srErr=null;window.__srRes=a}",ans);pg.click("button[onclick='rec()']");pg.wait_for_timeout(500)
        ck(f"{ty} : bonne réponse orale → point gagné, retour affiché",pg.evaluate("R.ok")>0 and pg.evaluate("document.querySelector('.fbm.ok')!==null"),pg.evaluate("document.getElementById('fb').innerText"))
        lesson(ty);pg.evaluate("window.__srRes='banana computadora azul'");pg.click("button[onclick='rec()']");pg.wait_for_timeout(500)
        ck(f"{ty} : réponse fausse → pas de point, correction + explication",pg.evaluate("R.ok")==0 and ("entendu" in pg.evaluate("document.getElementById('fb').innerText")),pg.evaluate("document.getElementById('fb').innerText"))
    # refus de micro → « Écrire à la place » (rep→dictée, speakQ→réponse écrite) fonctionnel
    lesson("speakQ");pg.evaluate("window.__srRes=null;window.__srErr='service-not-allowed'");pg.click("button[onclick='rec()']");pg.wait_for_timeout(400)
    pg.click("button:has-text('Écrire à la place')");pg.wait_for_timeout(300)
    ok=pg.evaluate("R.q.ty")=="replyQ";mod=pg.evaluate("R.q.models[0]");pg.fill("#ti",mod);pg.click("#chk");pg.wait_for_timeout(300)
    ck("speakQ sans micro : repli écrit (replyQ) noté correctement",ok and pg.evaluate("R.ok")>0,pg.evaluate("document.getElementById('fb').innerText"))
    lesson("rep");pg.evaluate("window.__srErr='service-not-allowed'");pg.click("button[onclick='rec()']");pg.wait_for_timeout(400);pg.click("button:has-text('Écrire à la place')");pg.wait_for_timeout(300)
    ck("rep sans micro : repli en dictée",pg.evaluate("R.q.ty")=="dict")
    ck("aucune erreur JS (formats oraux)",not er,er);c.close()
    # ---------- E. apprendre avant de tester
    c=b.new_context(locale="fr-FR",viewport={"width":390,"height":844});pg=c.new_page();er=[];pg.on("pageerror",lambda e:er.append(str(e)));pg.add_init_script(FAKE);pg.goto(BASE+"index.html");pg.wait_for_timeout(2000)
    r=pg.evaluate("""()=>{S.lang='es';S.lvl=1;S.pth={};S.sc={};S.ds={};build();PLC=null;const st=pathPlanMain().flat.find(x=>x.id.startsWith('v'));pstart(st.id);
      const o={disc:!!DISC,n:DISC?DISC.items.length:0,txt:document.body.innerText,q:R.q?R.q.ty:null,ws:st.ws.map(w=>w[0]),items:DISC?DISC.items.map(x=>x.es):[],ex:DISC?DISC.items.filter(x=>x.ex).length:0};return o}""")
    ck("nouvelle étape de vocabulaire : écran de découverte AVANT toute question",r["disc"] and r["q"] is None and r["n"]>=3,r)
    ck("découverte : tous les mots de l'étape présentés (sens + exemple pour la plupart)",set(r["ws"])<=set(r["items"]) and r["ex"]>=1,[r["ws"],r["items"],r["ex"]])
    ck("découverte : orthographe, audio, sens affichés",("Découvre" in r["txt"]) and pg.query_selector(".dsc .dc button.spk") and pg.evaluate("getComputedStyle(document.querySelector('.dw')).textDecorationLine")=='none')
    q=pg.evaluate("""()=>{discGo();const ty=R.q.ty;const seen=[];for(let i=0;i<40;i++){R.n=i%10;const q=mkQ(pickType(),0);seen.push([q.ty,q.key||q.wk||null])}
       return{ty,ds:Object.keys(S.ds).length,seen}}""")
    ck("après « C'est parti » : l'exercice démarre, mots marqués vus",q["ds"]>=3 and q["ty"],q["ty"])
    r2=pg.evaluate("""()=>{const st=pathPlanMain().flat.find(x=>x.id.startsWith('v'));pstart(st.id);return{disc:!!DISC,q:R.q?R.q.ty:null}}""")
    ck("même étape rejouée : pas de redite de la découverte",not r2["disc"] and r2["q"])
    r3=pg.evaluate("""()=>{S.ds={};const st=pathPlanMain().flat.find(x=>x.id.startsWith('v'));st.ws.forEach(w=>S.sc[w[0]]=3);pstart(st.id);return{disc:!!DISC}}""")
    ck("mots déjà acquis : pas de découverte inutile",not r3["disc"])
    r4=pg.evaluate("""()=>{S.ds={};S.sc={};const st=pathPlanMain().flat.find(x=>x.id.startsWith('m'));pstart(st.id);return{disc:!!DISC}}""")
    ck("bilan/révision : pas de découverte (on évalue du déjà vu)",not r4["disc"])
    # progression des formats selon l'acquisition du mot : reconnaissance → rappel → production
    d=pg.evaluate("""()=>{const o={};for(const sc of [0,5]){S.lang='es';S.lvl=1;build();const ws=ALL.filter(w=>(w[2]||1)===1).slice(0,6);ws.forEach(w=>S.sc[w[0]]=sc);const T={};let n=0;
      for(let k=0;k<60;k++){S.rq={};R={mode:'lesson',t:'Chunk',n:0,ok:0,xp:0,pt:['es2fr','fr2es','listen','tf','dict','rep','speakF','type'],ws,dp:ws,hist:[],seen:{},ph:{}};for(let i=0;i<10;i++){R.n=i;const q=mkQ(pickType(),0);if(q.key||q.wk){T[q.ty]=(T[q.ty]||0)+1;n++}}}
      o[sc]={n,prod:((T.type||0)+(T.speakF||0))/n,rec:((T.es2fr||0)+(T.listen||0)+(T.tf||0))/n}}return o}""")
    ck("mot nouveau : surtout reconnaissance ; mot acquis : surtout production (type/speakF)",d["0"]["rec"]>d["0"]["prod"] and d["5"]["prod"]>d["5"]["rec"],d)
    ck("aucune erreur JS (découverte)",not er,er);c.close()
    # ---------- F. progression CECRL : difficulté croissante, 4 compétences au programme de chaque niveau
    c=b.new_context(locale="fr-FR");pg=c.new_page();er=[];pg.on("pageerror",lambda e:er.append(str(e)));pg.add_init_script(FAKE);pg.goto(BASE+"index.html");pg.wait_for_timeout(2000)
    dff=pg.evaluate("""()=>{const o={};for(let L=1;L<=5;L++){S.lang='es';S.lvl=L;build();let n=0,w=0,m=0,c=0;for(let i=0;i<300;i++){R={mode:'lesson',t:'Mélange',n:0,ok:0,xp:0,pt:null};for(const ty of ['rep','speakF','build','type']){const q=mkQ0(ty,0);const s=(q.es||'').split(' ').length;w+=s;n++}}
      o[L]=w/n}return o}""")
    ck("longueur des productions demandées croissante A1 < B1 < C1",dff["1"]<dff["3"]<dff["5"],dff)
    sk=pg.evaluate("""()=>{const o={};for(let L=1;L<=5;L++){S.lang='es';S.lvl=L;S.pth={};build();PLC=null;const f=pathPlanMain().flat;o[L]={co:f.some(x=>x.t==='CO'),ce:f.some(x=>x.t==='CE'),ee:f.some(x=>x.t==='EE'),eo:f.some(x=>x.t==='EO'),eoSR:f.filter(x=>x.t==='EO').every(x=>x.pt.some(t=>['speak','rep','speakF','speakC','speakQ'].includes(t))),units:pathPlanMain().units.length}}return o}""")
    ck("chaque niveau A1→C1 contient une étape dédiée aux 4 compétences (CO, CE, EE, EO) et l'EO est vocal",all(v["co"] and v["ce"] and v["ee"] and v["eo"] and v["eoSR"] for v in sk.values()),sk)
    # parcours complet : à CHAQUE niveau, les 4 compétences sont travaillées ; bilans d'unité de plus en plus larges (cumul), vocabulaire du niveau d'abord
    lv=pg.evaluate("""()=>{const o={};for(let L=1;L<=5;L++){S.lang='es';S.lvl=L;S.pth={};S.rat={};S.rq={};S.md={};build();PLC=null;const T={};let n=0;const pl=pathPlanMain();
      for(const st of pl.flat){if(st.test)continue;R={mode:'lesson',t:st.t||'Chunk',n:0,ok:0,xp:0,pid:st.id,pt:st.pt||null,ws:st.ws||null,dp:st.dp||null,gp:st.gp||null,go:st.go||null,xs:st.xs||null,qs:st.qs||null,vs:st.vs||null,pp:st.pp||null,kn:st.kn||null,tn:st.tn||null};
        for(let i=0;i<10;i++){R.n=i;const q=mkQ(pickType(),0);const m=MODL[q.ty];if(m){T[m]=(T[m]||0)+1;n++}}}
      const us=pl.units.slice(0,-1),inc=us.every((u,i)=>{const m=new Set(u.steps.find(x=>x.id.startsWith('m')).ws.map(w=>w[0]));return u.uw.every(w=>m.has(w[0]))&&(i===0||us[i-1].uw.length===0||us[i-1].uw.some(w=>m.has(w[0])))});
      o[L]={sh:Object.fromEntries(Object.entries(T).map(([k,v])=>[k,Math.round(100*v/n)])),inc}}return o}""")
    ck("chaque niveau A1→C1 : les 4 compétences ≥ 12 % du travail (parcours complet)",all(all(v["sh"].get(k,0)>=12 for k in ["co","eo","ce","ee"]) for v in lv.values()),lv)
    ck("bilans d'unité : tous les mots de l'unité + rappels espacés des unités précédentes, à chaque niveau",all(v["inc"] for v in lv.values()),lv)
    ck("aucune erreur JS (progression)",not er,er);c.close()
    b.close()
print(sum(R),"/",len(R),"OK");sys.exit(0 if all(R) else 1)
