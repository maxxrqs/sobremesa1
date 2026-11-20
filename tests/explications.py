# Chantier 3, lot A : notions d'une question (cible + appuis), rattachement question → règle (QR),
# erreurs EV → règle, explications contextuelles (« Pourquoi ? »), champ « x » du carnet.
# 5 langues étudiées × niveaux A1–C1, 5 langues d'interface, écran 360 × 640, profils existants.
# Usage : python3 tests/explications.py URL
import sys,json,re
from playwright.sync_api import sync_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else "http://127.0.0.1:8774/"
R=[]
def ck(n,c,i=""):R.append(bool(c));print("OK  " if c else "FAIL",n,"" if c else str(i)[:700],flush=True)
LANGS=["es","va","ca","gl","eu"];UIS=["fr","en","de","it","pt"]
H=r"""
window.SET_=(l,L)=>{S.lang=l;S.lvl=L;S.ob=0;build();XDIRTY=1;xens();XPWC=null;MKDC.clear()};
window.FRESH_=()=>{S.sr={};S.sc={};S.mi={};S.tp={};MKDC.clear()};
window.LESSON_=()=>{start('Mélange');R.n=0;R.ok=0;R.xp=0;R.xpi=new Set();R.xpn=0;R.tpn=0;R.tc=0;R.tpl=null};
window.ENT_=(k,p)=>{const d=mkDif(k),c=[1,2,3,4].map(P=>P<=p?MKN[d][P]:0);S.sr[k]={b:1,d:dayN()+5,p,m:1,c,n:3,k:0,s:dayN()-2};if(d===3)S.sr[k].j=[0,0,0,0];return S.sr[k]};
0;
"""
with sync_playwright() as p:
    b=p.chromium.launch();errs=[]
    def page(ui="fr",w=420,h=900):
        c=b.new_context(service_workers="block",locale={"fr":"fr-FR","en":"en-GB","de":"de-DE","it":"it-IT","pt":"pt-PT"}[ui],viewport={"width":w,"height":h})
        pg=c.new_page();pg.on("pageerror",lambda e:errs.append(str(e)))
        pg.goto(BASE+"index.html");pg.wait_for_timeout(2500)
        if ui!="fr":pg.evaluate("(u)=>{if(typeof setUI==='function')setUI(u)}",ui);pg.wait_for_timeout(600)
        pg.evaluate(H);return pg
    pg=page();ev=pg.evaluate
    import subprocess,os
    rc=subprocess.run([sys.executable,os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","tools","qr_rattachements.py"),"verifier"],capture_output=True,text=True)
    ck("QR : castellano.html conforme à tools/qr_rattachements.tsv (rattachements relus à la main)",rc.returncode==0,rc.stdout+rc.stderr)
    # ---------- 1. QR : chaque question de grammaire a un rattachement vérifié (règle ou aucune), dans les 5 langues ----------
    r=ev("""()=>{const o={};for(const l of LK){SET_(l,5);let n=0,ok=0,none=0,miss=[],bad=[];for(const x of EQ){n++;const h=qrMap(l).get(xpH(x.k+'|'+x.as));if(h==null){miss.push(x.k);continue}if(h==='-'){none++;continue}const r=qrRule(x);if(r)ok++;else bad.push(x.k)}
      o[l]={n,ok,none,miss:miss.slice(0,3),bad:bad.slice(0,3),regles:new Set(EX.map(r=>xpH(r.ts))).size===EX.length}}return o}""")
    ck("QR : chaque question de grammaire a une entrée vérifiée, toutes les règles citées existent, aucune collision (5 langues)",
       all(v["miss"]==[] and v["bad"]==[] and v["regles"] and v["ok"]+v["none"]==v["n"] for v in r.values()),r)
    ck("QR : au moins 97 % des questions rattachées à une règle (le reste : « aucune règle », jamais deviné)",all(v["ok"]>=.97*v["n"] for v in r.values()),{l:(v["ok"],v["n"]) for l,v in r.items()})
    # rattachements vérifiés à la main (échantillon de contrôle, y compris des cas que le rapprochement automatique ratait)
    S=[("es","Complète : ___ viene de Francia (il vient de France).","él avec accent ou el sans accent"),
       ("es","Complète : El nuevo hospital ___ inaugurado el año pasado.","passif avec ser : ser + participe accordé"),
       ("es","Complète : ___ difícil es empezar (le plus dur c'est de commencer).","lo + adjectif"),
       ("es","Complète : Tengo ___ foto de mi familia (une photo).","noms féminins en -o"),
       ("va","Complète : Jo ___ la resposta (je sais la réponse).","sé / se, té / te, és / es"),
       ("ca","Quel article convient : ___ calor (la chaleur) ?","Genre différent du castillan"),
       ("gl","Complétez : Non ___ sei (Je ne le sais pas).","Proclise après une négation"),
       ("eu","Le livre d'Ane : ___ liburua","Génitif -(r)en et -ko")]
    r=ev("""(S)=>S.map(([l,k,t])=>{SET_(l,5);const x=EQ.find(z=>z.k===k||z.k.startsWith(k.replace(/ \\?$/,'')));const r=x&&qrRule(x);return [l,k.slice(0,30),r?r.ts:null,t]})""",[list(x) for x in S])
    ck("QR : rattachements de contrôle conformes à la vérification manuelle",all(x[2]==x[3] for x in r),[x for x in r if x[2]!=x[3]])
    # ---------- 2. EV : forme attendue fautive → règle, seulement si le rattachement est unique ----------
    r=ev("""()=>{SET_('es',2);const g=EV.grade('un foto de mi casa',{ty:'type',es:'una foto de mi casa'}),p=EV.grade('los sofás grande',{ty:'type',es:'los sofás grandes'}),c=EV.grade('yo pensa mucho',{ty:'type',es:'yo pienso mucho'});
      return {g:[g.s,g.k,g.t,g.tn],gr:(xpEvRule(g)||{}).ts,typo:EV.grade('una fotto',{ty:'type',es:'una foto'}).t||null,ok:EV.grade('una foto',{ty:'type',es:'una foto'}).t||null}}""")
    ck("EV : erreur de genre sur l'article → forme attendue et voisins renvoyés, règle « noms féminins en -o »",r["g"][0]==.5 and r["g"][1]=="g" and r["g"][2]=="una" and r["gr"]=="noms féminins en -o",r)
    ck("EV : pas de forme désignée pour une simple faute de frappe ni pour une bonne réponse",r["typo"] is None and r["ok"] is None,r)
    r=ev("""()=>{const o={};for(const l of LK){SET_(l,5);XPEC[l]=null;const I=xpEvIdx();o[l]={g:[...I.g.values()].filter(s=>s.size===1).length,n:[...I.n.values()].filter(s=>s.size===1).length,amb:xpEvRule({k:'g',t:'zzzz'})}}return o}""")
    ck("EV : index des formes construit dans les 5 langues, forme inconnue → aucune règle",all(v["amb"] is None and v["g"]+v["n"]>0 for v in r.values()),r)
    # ---------- 3. qNotions : cible inchangée, appuis = mots et expressions déjà suivis, 3 au plus ----------
    r=ev("""()=>{SET_('es',2);FRESH_();const ph=PH.find(f=>f[0].split(' ').length>=5&&EV.raw(f[0]).split(' ').filter(t=>xpWIdx().one.get(t)).length>=3);
      const ks=EV.raw(ph[0]).split(' ').map(t=>xpWIdx().one.get(t)).filter(Boolean);const q={ty:'readP',es:ph[0],key:null};
      const a0=qNotions(q).appuis.length;ks.forEach(k=>ENT_(k,0));const a=qNotions(q);
      const kq=qNotions({ty:'type',es:'hola amigo bueno',key:'hola'}),mc=qNotions({ty:'es2fr',es:ph[0],key:null});
      return {ph:ph[0],ks,a0,a:a.appuis.map(x=>x.key),cible:a.cible,kq:[kq.cible,kq.appuis.length],mc:mc.appuis.length}}""")
    ck("qNotions : aucune notion d'appui tant que le carnet ne suit pas les mots (aucune création)",r["a0"]==0,r)
    ck("qNotions : appuis pris parmi les mots de la phrase suivis par le carnet, 3 au plus",0<len(r["a"])<=3 and set(r["a"])<=set(r["ks"]),r)
    ck("qNotions : question à notion cible → cible = q.key, sans appui ; format sans phrase à comprendre → pas d'appui",r["kq"]==["hola",0] and r["mc"]==0,r)
    r=ev("""()=>{SET_('es',3);FRESH_();const x=XP.find(z=>z.e.split(' ').length>=2&&z.l<=3&&xpWIdx().multi.some(m=>m[1]==='e:'+z.e)&&z.e.split(' ').some(t=>xpWIdx().one.get(EV.raw(t))));ENT_('e:'+x.e,0);const w=x.e.split(' ').find(t=>xpWIdx().one.get(EV.raw(t)));if(w)ENT_(xpWIdx().one.get(EV.raw(w)),0);
      const a=qNotions({ty:'dict',es:x.e+' hoy',key:null}).appuis.map(z=>z.key);return {e:x.e,a}}""")
    ck("qNotions : une expression reconnue couvre ses mots (pas de double compte)",r["a"]==["e:"+r["e"]],r)
    # ---------- 4. mkApp : plafond palier 2, une preuve par réussite, ni création, ni date, recul seulement si EV situe l'erreur ----------
    r=ev("""()=>{SET_('es',2);FRESH_();const k='gracias',e0=ENT_(k,0),f=o=>JSON.stringify([o.b,o.d,o.m,o.n,o.s,o.k]),z0=f(e0),P=[];
      for(let i=0;i<6;i++){mkApp(k,{ty:'build'},1,false);P.push(S.sr[k].p)}const e=S.sr[k];
      const none=mkApp('palabrainexistente',{ty:'build'},1,false),crea=!!S.sr['palabrainexistente'];
      return {P,dates:f(e)===z0,c:e.c,none,crea}}""")
    ck("appui : une seule preuve par réussite (pas de saut), palier 2 au plus même après 6 réussites",r["P"][:2]==[1,2] and max(r["P"])==2,r)
    ck("appui : boîte, date de révision, facilité, compteurs et dernier jour vu inchangés",r["dates"],r)
    ck("appui : aucune entrée créée pour une notion absente du carnet",r["none"] is None and not r["crea"],r)
    r=ev("""()=>{SET_('es',2);FRESH_();const k='gracias';ENT_(k,1);S.sr[k].c=[1,1,0,0];S.sr[k].p=1;const s0=JSON.stringify(S.sr[k]);
      const a=mkApp(k,{ty:'build'},0,false),same=JSON.stringify(S.sr[k])===s0;const b=mkApp(k,{ty:'build'},0,true),e=S.sr[k];
      ENT_('hola',4);const h0=JSON.stringify(S.sr.hola);mkApp('hola',{ty:'build'},0,true);mkApp('hola',{ty:'build'},1,false);
      return {a,same,p:e.p,c:e.c,d:e.d,hola:JSON.stringify(S.sr.hola)===h0}}""")
    ck("appui : échec sans erreur localisée → aucun changement",r["a"] is None and r["same"],r)
    ck("appui : échec localisé par EV → preuve partielle perdue, jamais de recul de palier ni de date",r["p"]==1 and r["c"][1]==0 and r["c"][0]==1,r)
    ck("appui : notion déjà au palier 4 → ni gain ni perte",r["hola"],r)
    # ---------- 5. vraie réponse (fin) : cible inchangée, appuis enregistrés, erreur EV située sur un appui ----------
    r=ev("""()=>{SET_('es',2);FRESH_();LESSON_();const ph=PH.find(f=>f[0].split(' ').length>=4&&EV.raw(f[0]).split(' ').filter(t=>xpWIdx().one.get(t)).length>=2);
      const ks=[...new Set(EV.raw(ph[0]).split(' ').map(t=>xpWIdx().one.get(t)).filter(Boolean))];ks.forEach(k=>ENT_(k,0));const b0=ks.map(k=>JSON.stringify([S.sr[k].b,S.sr[k].d,S.sr[k].s]));
      R.q={ty:'readP',txt:ph[0],es:ph[0],say:ph[0],key:null,g:ph[1],o:[ph[1],'a','b','c'],sol:ph[0]};R.done=false;draw();fin(1,R.q.sol,null);
      return {ph:ph[0],p:ks.map(k=>S.sr[k].p),dates:ks.every((k,i)=>JSON.stringify([S.sr[k].b,S.sr[k].d,S.sr[k].s])===b0[i])}}""")
    ck("réponse réelle (lecture d'une phrase) : notions d'appui prouvées au palier 1, dates inchangées",min(r["p"])>=1 and max(r["p"])<=2 and r["dates"],r)
    r=ev("""()=>{SET_('es',2);FRESH_();LESSON_();const s='La casa es grande';const kc=xpWIdx().one.get('casa'),kg=xpWIdx().one.get('grande');ENT_(kc,0);ENT_(kg,0);
      [kc,kg].forEach(k=>{S.sr[k].c=[1,1,0,0];S.sr[k].p=1});R.q={ty:'type',fr:'La maison est grande',es:s,say:s,acc:[s],key:null,sol:s};R.done=false;draw();
      document.getElementById('ti').value='El casa es grande';chkT();return {kc,kg,s:R.ok,casa:S.sr[kc].c,grande:S.sr[kg].c,pc:S.sr[kc].p}}""")
    ck("réponse réelle écrite « presque » (genre de l'article) : seule la notion visée par EV perd sa preuve partielle, sans recul de palier ; l'autre appui ne gagne rien",
       r["kc"] and r["kg"] and r["s"]==.5 and r["casa"]==[1,0,0,0] and r["pc"]==1 and r["grande"]==[1,1,0,0],r)
    r=ev("""()=>{SET_('es',2);FRESH_();LESSON_();const s='La casa es grande';const kc=xpWIdx().one.get('casa');ENT_(kc,0);S.sr[kc].c=[1,1,0,0];S.sr[kc].p=2;S.sr[kc].c=[1,0,0,0];S.sr[kc].p=1;
      const b0=JSON.stringify([S.sr[kc].b,S.sr[kc].d]);R.q={ty:'type',fr:'La maison est grande',es:s,say:s,acc:[s],key:null,sol:s};R.done=false;draw();
      document.getElementById('ti').value='La casa es grande';chkT();return {c:S.sr[kc].c,p:S.sr[kc].p,dates:JSON.stringify([S.sr[kc].b,S.sr[kc].d])===b0}}""")
    ck("réponse réelle écrite juste : notion d'appui prouvée au palier suivant (2), dates inchangées",r["p"]==2 and r["dates"],r)
    # ---------- 6. xpl : priorités, une explication au plus, champ x, aucune explication inutile ----------
    r=ev("""()=>{SET_('es',2);FRESH_();LESSON_();const x=EQ.find(z=>z.k.startsWith('Complète : Tengo ___ foto'));const key='q:'+x.k;
      R.q={ty:'exc',key,g:x.a,o:[x.a,...x.w],h:x.q,sol:x.a+'. '+x.x};R.done=false;draw();fin(0,R.q.sol,key);
      const e=S.sr[key],h1=(document.querySelector('#fb details.why')||{}).outerHTML||'',op=!!document.querySelector('#fb details.why[open]');
      LESSON_();R.q=Object.assign({},R.q);R.done=false;draw();fin(0,R.q.sol,key);const h2=!!document.querySelector('#fb details.why');
      return {x:e.x===dayN(),h1:h1.includes('noms féminins en -o'),op,h2}}""")
    ck("priorité 2 : erreur sur une notion fragile → règle rattachée, repliée sous « Pourquoi ? »",r["h1"] and not r["op"],r)
    ck("champ x : jour de l'explication noté dans l'entrée existante ; pas de seconde explication le même jour",r["x"] and not r["h2"],r)
    r=ev("""()=>{SET_('es',2);FRESH_();LESSON_();const x=EQ.find(z=>z.k.startsWith('Complète : Tengo ___ foto'));const key='q:'+x.k;ENT_(key,4);
      R.q={ty:'exc',key,g:x.a,o:[x.a,...x.w],h:x.q,sol:x.a};R.done=false;draw();fin(1,R.q.sol,key);const a=!!document.querySelector('#fb details.why');
      LESSON_();R.q=Object.assign({},R.q);R.done=false;draw();fin(0,R.q.sol,key);const b=!!document.querySelector('#fb details.why');return {a,b}}""")
    ck("notion maîtrisée (palier 4) : rien après une bonne réponse, rien non plus après un simple écart",not r["a"] and not r["b"],r)
    r=ev("""()=>{SET_('es',2);FRESH_();LESSON_();const x=EQ.find(z=>z.l<=2&&qrRule(z));const key='q:'+x.k;
      R.tc=5;R.q={ty:'exc',key,g:x.a,o:[x.a,...x.w],h:x.q,sol:x.a};R.done=false;draw();fin(1,R.q.sol,key);const a=!!document.querySelector('#fb details.why'),btn=!!document.querySelector('#fb .btn');
      const xx=S.sr[key].x;S.sr[key].p=1;S.sr[key].c=[1,0,0,0];LESSON_();R.tc=5;R.q=Object.assign({},R.q);R.done=false;draw();fin(1,R.q.sol,key);const b=!!document.querySelector('#fb details.why');
      return {a,btn,xx:xx===dayN(),b}}""")
    ck("priorité 3 : premier réemploi réussi d'une notion de grammaire récente → règle repliée + bouton Continuer",r["a"] and r["btn"] and r["xx"],r)
    ck("priorité 3 : une seule fois par notion (champ x déjà rempli)",not r["b"],r)
    r=ev("""()=>{SET_('es',2);FRESH_();LESSON_();ENT_('una foto',0);const s='Tengo una foto bonita';
      R.q={ty:'type',fr:"J'ai une jolie photo",es:s,say:s,acc:[s],key:null,sol:s};R.done=false;draw();document.getElementById('ti').value='Tengo un foto bonita';chkT();
      const w=document.querySelector('#fb details.why .whyb');return {w:w&&w.textContent,n:document.querySelectorAll('#fb details.why').length,tip:document.querySelectorAll('#fb .tip').length}}""")
    ck("priorité 1 : erreur de genre repérée par EV → règle correspondante ; une seule explication, pas d'astuce en plus",r["w"] and "-o" in r["w"] and r["n"]==1 and r["tip"]==0,r)
    r=ev("""()=>{SET_('es',1);FRESH_();LESSON_();let n=0,mx=0;for(let i=0;i<10;i++){const x=EQ.filter(z=>z.l<=2&&qrRule(z))[i];const key='q:'+x.k;R.q={ty:'exc',key,g:x.a,o:[x.a,...x.w],h:x.q,sol:x.a};R.done=false;R.n=i;draw();fin(0,R.q.sol,key);
      const k=document.querySelectorAll('#fb details.why').length;n+=k;mx=Math.max(mx,k+document.querySelectorAll('#fb .tip').length)}return {n,mx}}""")
    ck("séance : au plus 4 explications d'erreur, jamais plus d'une par correction",r["n"]<=4 and r["mx"]<=1,r)
    r=ev("""()=>{SET_('es',3);FRESH_();LESSON_();const x=XP.find(z=>z.g&&z.g!==gl('neutre')&&z.l<=3);const key='e:'+x.e;R.q={ty:'exM',key,say:x.e,g:x.m,o:[x.m,'a','b','c'],e:x.e,sol:x.e};R.done=false;draw();fin(0,R.q.sol,key);
      const h=(document.querySelector('#fb .whyb')||{}).innerHTML||'';FRESH_();LESSON_();const q=mkConj();R.q=q;R.done=false;draw();fin(0,q.sol,q.key);const v=(document.querySelector('#fb .whyb')||{}).innerHTML||'';
      return {e:x.e,g:x.g,h,tu:q.tu,v}}""")
    ck("expression : registre et exemple proposés après une erreur",r["g"] in r["h"] and len(r["h"])>20,r)
    ck("conjugaison : emploi du temps travaillé proposé après une erreur",r["tu"] and r["tu"] in r["v"],r)
    # ---------- 7. 5 langues × niveaux A1–C1 : génération réelle de questions, aucune erreur, au plus une explication ----------
    r=ev("""()=>{const out={},TY=['exc','conj','exM','readP','build','dict','es2fr','fr2es','type','cloze','listenP','fr2P'];
      for(const l of LK)for(let L=1;L<=5;L++){SET_(l,L);FRESH_();let n=0,ex=0,app=0,err=[];
        for(const ty of TY)for(let i=0;i<4;i++){LESSON_();let q=null;try{q=ty==='exc'?mkExc():ty==='conj'?mkConj():ty==='exM'?mkExp('exM'):mkQ0(ty)}catch(e){err.push(ty+':'+e.message)}if(!q)continue;n++;
          if(q.key&&!S.sr[q.key])ENT_(q.key,i%2?0:3);try{const N=qNotions(q);N.appuis.forEach(a=>{});app+=N.appuis.length;R.q=q;R.done=false;draw();fin(i%2?0:1,q.sol,q.key);ex+=document.querySelectorAll('#fb details.why').length>1?100:document.querySelectorAll('#fb details.why').length}catch(e){err.push(ty+':'+e.message)}}
        out[l+L]={n,ex,err:err.slice(0,2)}}return out}""")
    ck("5 langues × A1–C1 : questions réelles corrigées sans erreur, jamais plus d'une explication",all(v["err"]==[] and v["n"]>=20 and v["ex"]<100 for v in r.values()),{k:v for k,v in r.items() if v["err"] or v["n"]<20 or v["ex"]>=100})
    ck("5 langues × A1–C1 : des explications apparaissent réellement dans chaque langue",all(sum(r[l+str(L)]["ex"] for L in range(1,6))>0 for l in LANGS),{k:v["ex"] for k,v in r.items()})
    pg.context.close()
    # ---------- 8. langue d'interface : explication et bouton dans la langue de l'apprenant ----------
    for ui in UIS:
        pg=page(ui);pg.wait_for_timeout(300)
        r=pg.evaluate("""(ui)=>{const out={};for(const l of LK){SET_(l,2);FRESH_();LESSON_();const x=EQ.find(z=>z.l<=2&&qrRule(z));const key='q:'+x.k;
          R.q={ty:'exc',key,g:x.a,o:[x.a,...x.w],h:x.q,sol:x.a};R.done=false;draw();fin(0,R.q.sol,key);const d=document.querySelector('#fb details.why');
          out[l]={s:d&&d.querySelector('summary').innerText,t:d&&d.querySelector('.whyb').textContent,rt:qrRule(x).t,UI}}return out}""",ui)
        want={"fr":"Pourquoi ?","en":"Why?","de":"Warum?","it":"Perché?","pt":"Porquê?"}[ui]
        ck(f"interface {ui} : « Pourquoi ? » traduit et règle affichée dans la langue d'interface (5 langues étudiées)",
           all(v["s"]==want and v["t"] and v["rt"] in v["t"] and v["UI"]==ui for v in r.values()),r)
        if ui!="fr":
            fr=pg.evaluate("""()=>{const out=[];for(const l of LK){SET_(l,2);const x=EQ.find(z=>z.l<=2&&qrRule(z));out.push([l,qrRule(x).t,qrRule(x).ts])}return out}""")
            ck(f"interface {ui} : titres de règle traduits (pas le texte source français)",all(t!=ts for _,t,ts in fr),fr)
        pg.context.close()
    # ---------- 9. mobile 360 × 640 : correction et « Continuer » visibles, explication repliée puis ouverte ----------
    pg=page("fr",360,640)
    r=pg.evaluate("""()=>{SET_('es',2);FRESH_();LESSON_();const x=EQ.find(z=>z.k.startsWith('Complète : Tengo ___ foto'));const key='q:'+x.k;
      R.q={ty:'exc',key,g:x.a,o:[x.a,...x.w],h:x.q,sol:x.a+'. '+x.x};R.done=false;draw();fin(0,R.q.sol,key);return 1}""")
    pg.wait_for_timeout(900)
    a=pg.evaluate("()=>{const b=document.querySelector('#fb .btn').getBoundingClientRect(),s=document.querySelector('#fb details.why summary').getBoundingClientRect();return {b:b.bottom,s:s.bottom,h:innerHeight,w:document.documentElement.scrollWidth}}")
    ck("360 × 640 : « Pourquoi ? » et « Continuer » visibles sans débordement horizontal",a["b"]<=a["h"] and a["s"]<=a["h"] and a["w"]<=360,a)
    pg.click("#fb details.why summary");pg.wait_for_timeout(900)
    a=pg.evaluate("()=>{const b=document.querySelector('#fb .btn').getBoundingClientRect(),w=document.querySelector('#fb .whyb').getBoundingClientRect();return {open:!!document.querySelector('#fb details.why[open]'),b:b.bottom,wb:w.height,h:innerHeight,xpo:R.xpo}}")
    ck("360 × 640 : explication ouverte (hauteur bornée), « Continuer » toujours atteignable, avance automatique suspendue",a["open"] and a["wb"]<=0.36*640 and a["b"]<=a["h"]+1 and a["xpo"]==1,a)
    # ---------- 10. profils existants : champ x conservé, anciennes entrées intactes, sauvegarde et rechargement ----------
    PRO=json.dumps({"v":2,"xp":40,"streak":0,"last":"","sc":{"hola":2,"viejo":2},"lvl":2,"lang":"es","PL":{},"bd":{},"nt":[],"t":1793000000000,"ob":1,"masSeen":1,
                    "sr":{"viejo":{"b":2,"d":1},"hola":{"b":1,"d":20000,"p":1,"m":1,"c":[1,0,0,0],"n":2,"k":0,"s":19990,"x":19995}}})
    pg.evaluate("(P)=>{localStorage.clear();localStorage.setItem('cast_user','moi3');localStorage.setItem('acct:moi3',JSON.stringify({h:'z'}));localStorage.setItem('cast:moi3',P)}",PRO)
    pg.reload();pg.wait_for_timeout(2500);pg.evaluate(H)
    r=pg.evaluate("""()=>{const o0=JSON.stringify(S.sr.viejo),h=JSON.stringify(S.sr.hola);mkApp('viejo',{ty:'build'},0,false);const intact=JSON.stringify(S.sr.viejo)===o0;
      mkRec('hola',{ty:'type'},1);const kx=S.sr.hola.x===19995;mkApp('hola',{ty:'build'},1,false);const kx2=S.sr.hola.x===19995;return save().then(()=>({h,intact,kx,kx2}))}""")
    ck("profil existant : chargé tel quel (champ x compris) ; ancienne entrée non réécrite ; x conservé par mkRec et mkApp",'"x":19995' in r["h"] and r["intact"] and r["kx"] and r["kx2"],r)
    pg.wait_for_timeout(600);pg.reload();pg.wait_for_timeout(2500)
    r=pg.evaluate("()=>({x:((S.sr||{}).hola||{}).x,v:JSON.stringify((S.sr||{}).viejo)})")
    ck("sauvegarde et rechargement : champ x et anciennes entrées conservés",r["x"]==19995 and r["v"]=='{"b":2,"d":1}',r)
    pg.context.close()
    ck("aucune erreur JavaScript",not errs,errs[:5])
    b.close()
print(f"{sum(R)} / {len(R)} OK")
sys.exit(0 if all(R) else 1)
