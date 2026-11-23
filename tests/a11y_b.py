# Accessibilité et interface (audit du 7 novembre, n°17, 21, 22), sur les deux pages :
#  n°17 : étiquette du champ de réponse #ti (test de niveau, exercices, scènes), rôle de la barre d'étapes .obs, étiquette de l'heure du rappel ;
#  n°21 : polices hébergées dans fonts/ (aucune requête Google Fonts), chargées localement, et hors ligne via le service worker (index.html) ;
#  n°22 : présentation du test de niveau (estimation indicative, nombre réel de questions, examen officiel propre à chaque langue, traductions).
# Usage : python3 tests/rangesrv.py 8820 .  puis  python3 tests/a11y_b.py [URL]   (URL par défaut http://localhost:8772/)
# Option : SOB_AXE=/chemin/vers/axe.min.js ajoute un contrôle axe-core (règles label, select-name, aria-prohibited-attr).
import sys,os,json
from playwright.sync_api import sync_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else "http://localhost:8772/"
AXE=open(os.environ["SOB_AXE"]).read() if os.environ.get("SOB_AXE") else None
R=[]
def ck(n,c,i=""):
    R.append(bool(c));print("OK  " if c else "FAIL",n,"" if c else str(i)[:500],flush=True)
FACES=[("600 30px Fraunces","Fraunces"),("italic 600 30px Fraunces","Fraunces italique"),("500 16px Figtree","Figtree"),("800 16px Figtree","Figtree 800"),
       ("400 16px Nunito","Nunito"),("700 16px Nunito","Nunito 700"),("800 16px \"Baloo 2\"","Baloo 2"),("700 20px DynaPuff","DynaPuff")]
JSF="""async L=>{const o={};for(const f of L){try{const r=await document.fonts.load(f,"Hola ñ ç l·l");o[f]=r.length>0&&r.every(x=>x.status==="loaded")}catch(e){o[f]=false}}return o}"""
def axe(pg):
    if not AXE:return None
    if not pg.evaluate("!!window.axe"):pg.evaluate(AXE)
    return pg.evaluate("async()=>{const r=await axe.run(document,{runOnly:{type:'rule',values:['label','select-name','aria-prohibited-attr']}});return r.violations.map(v=>v.id+': '+v.nodes.map(x=>x.target.join(' ')).join(', '))}")
EX={"es":"DELE","va":"JQCV","ca":"Generalitat de Catalunya","gl":"CELGA","eu":"HABE, EGA"}
with sync_playwright() as p:
    b=p.chromium.launch()
    for page in ["castellano.html","index.html"]:
        print("==",page)
        c=b.new_context(locale="fr-FR",viewport={"width":390,"height":844});pg=c.new_page();ext=[];loc=[];er=[]
        pg.on("request",lambda r:ext.append(r.url) if ("fonts.googleapis" in r.url or "fonts.gstatic" in r.url) else (loc.append(r.url) if "/fonts/" in r.url else None))
        pg.on("pageerror",lambda e:er.append(str(e)))
        pg.goto(BASE+page);pg.wait_for_timeout(1500)
        # ---------- n°21
        ck("aucun lien ni requête vers fonts.googleapis.com / fonts.gstatic.com",not ext and pg.evaluate("!document.querySelector('link[href*=\"fonts.g\"]')"),ext)
        f=pg.evaluate(JSF,[x[0] for x in FACES])
        ck("polices chargées depuis fonts/ : "+", ".join(n for _,n in FACES),all(f.values()),f)
        ck("fichiers woff2 servis par le site (fonts/)",len(loc)>=6 and all(u.startswith(BASE) for u in loc),loc[:3])
        # ---------- n°17
        pg.evaluate("()=>{S.lang='es';S.lvl=1;S.ob=1;build();welcomeOb()}");pg.wait_for_timeout(250)
        ob=pg.locator(".obs");ck(".obs : rôle img avec nom « Étape 2 sur 4 » (aria-label autorisé)",ob.get_attribute("role")=="img" and pg.get_by_role("img",name="Étape 2 sur 4").count()==1,ob.get_attribute("role"))
        a=axe(pg);a is None or ck("axe : aucune violation sur l'écran d'accueil du parcours",not a,a)
        # ---------- n°22 (français, 5 langues)
        txt=pg.evaluate("[...document.querySelectorAll('.q p')].map(x=>x.textContent).find(t=>/test de niveau/i.test(t))||''")
        ck("texte du test : estimation indicative, 4 à 50 questions, oral non évalué, pas une certification",all(s in txt for s in ["indicatif","de 4 à 50 questions","l'oral n'est pas évalué","pas une certification","aux questions à choix"]),txt)
        ck("texte du test : plus de « 6 à 25 » ni de « modèle des épreuves officielles (DELE) »","6 à 25" not in txt and "modèle des épreuves" not in txt,txt)
        got={}
        for l,e in EX.items():
            got[l]=pg.evaluate("l=>{S.lang=l;S.lvl=0;build();welcomeOb();return [...document.querySelectorAll('.q p')].map(x=>x.textContent).find(t=>/test de niveau/i.test(t))||''}",l)
        ck("examen officiel cité selon la langue (DELE, JQCV, Generalitat de Catalunya, CELGA, HABE/EGA)",all("("+EX[l]+")" in got[l] for l in EX) and "DELE" not in got["va"]+got["ca"]+got["gl"]+got["eu"],{l:got[l][120:200] for l in got})
        # ---------- n°17 : champ #ti (test de niveau : écrire, dictée)
        pg.evaluate("()=>{S.lang='es';S.lvl=1;build();test()}");pg.wait_for_timeout(250)
        for i,ty in [(7,"type"),(9,"dict")]:
            pg.evaluate("i=>{T.i=i;R.q=T.list[i];R.done=false;show()}",i);pg.wait_for_timeout(250)
            q=pg.evaluate("R.q.ty")
            ck("test de niveau (%s) : #ti a un nom accessible « Écris ta réponse… »"%q,pg.get_by_role("textbox",name="Écris ta réponse…").count()==1 and pg.locator("#ti").count()==1,pg.evaluate("(document.getElementById('ti')||{}).outerHTML"))
            a=axe(pg);a is None or ck("axe : aucune violation (test, %s)"%q,not a,a)
        # exercice de leçon qui écrit (type) et scène guidée (immersion) avec #ti
        pg.evaluate("()=>{S.lang='es';S.lvl=1;build();R={mode:'lesson',t:'Mélange',n:0,ok:0,xp:0};R.q=mkQ0('type',0);R.done=false;show()}");pg.wait_for_timeout(250)
        ck("exercice « écris » : #ti étiqueté",pg.get_by_role("textbox",name="Écris ta réponse…").count()==1,pg.evaluate("(document.getElementById('ti')||{}).outerHTML"))
        # vraie étape écrite : une étape adaptative « T » dont les notions sont mises au palier 2 s'affiche au format écrit (W) ;
        # les notions ajoutées pour l'occasion sont ensuite retirées (et les valeurs déjà présentes restaurées)
        n=pg.evaluate("()=>{S.sr=S.sr||{};const l=lg(),L=immP(l);for(const s of L){const i=s.st.findIndex(x=>{if(x.k!=='T')return false;if(!x.ks){x.ks=sitNo(l,x.m||x.g);x.kn=sitNo(l,x.n)}return x.ks.length>0});if(i>=0){const sv={};for(const k of s.st[i].ks){sv[k]=k in S.sr?JSON.stringify(S.sr[k]):null;S.sr[k]=Object.assign({},S.sr[k]||{},{p:2})}window.__a11ySr=sv;imStart(s.id);IM.i=i;imShow();return IM.cur.k}}return ''}")
        if not n:print("     (scènes d'immersion non chargées sur cette page : contrôle de leur champ #ti sauté)")
        if n:
            ck("scène (étape écrite, palier 2) : #ti étiqueté",n=="W" and pg.get_by_role("textbox",name="Écris ta réponse…").count()==1,(n,pg.evaluate("(document.getElementById('ti')||{}).outerHTML")))
            pg.evaluate("()=>{const sv=window.__a11ySr||{};for(const k in sv){if(sv[k]===null)delete S.sr[k];else S.sr[k]=JSON.parse(sv[k])}delete window.__a11ySr}")
        # heure du rappel
        pg.evaluate("()=>{window.SOB_PUSH=1;S.rp={h:19};$.innerHTML=rpUI()}")
        ck("rappel : la liste des heures a un nom accessible",pg.get_by_role("combobox",name="Heure du rappel").count()==1)
        a=axe(pg);a is None or ck("axe : aucune violation (rappel)",not a,a)
        # ---------- traductions (anglais) : texte du test, étiquettes
        pg.evaluate("()=>{S.lang='es';S.lvl=0;build()}")
        pg.evaluate("()=>setUI('en')");pg.wait_for_timeout(1200)
        en=pg.evaluate("()=>{welcomeOb();return [...document.querySelectorAll('.q p')].map(x=>x.textContent).find(t=>/level test/i.test(t))||''}")
        ck("anglais : texte du test traduit (indicative, 4 to 50, DELE)","indicative level test: 4 to 50 questions" in en and "(DELE)" in en,en)
        pg.evaluate("()=>{test();T.i=7;R.q=T.list[7];R.done=false;show()}");pg.wait_for_timeout(250)
        ck("anglais : #ti étiqueté « Type your reply… »",pg.get_by_role("textbox",name="Type your reply…").count()==1,pg.evaluate("(document.getElementById('ti')||{}).getAttribute('aria-label')"))
        ck("aucune erreur JavaScript",not er,er);c.close()
    # ---------- n°21 hors ligne (PWA : index.html + service worker)
    print("== hors ligne (index.html, service worker)")
    c=b.new_context(locale="fr-FR",service_workers="allow");pg=c.new_page();ext=[]
    pg.on("request",lambda r:ext.append(r.url) if "fonts.g" in r.url else None)
    pg.goto(BASE+"index.html");pg.wait_for_timeout(1500)
    pg.evaluate("navigator.serviceWorker.ready.then(()=>1)")
    ok=False
    for _ in range(40):
        n=pg.evaluate("caches.open('sobstatic-v1').then(c=>c.keys()).then(k=>k.filter(r=>r.url.indexOf('/fonts/')>=0).length)")
        if n>=30:ok=True;break
        pg.wait_for_timeout(250)
    ck("service worker : les 30 fichiers de polices sont dans le cache durable",ok,n)
    pg.reload();pg.wait_for_timeout(1000)
    ck("page contrôlée par le service worker",pg.evaluate("!!navigator.serviceWorker.controller"))
    c.set_offline(True);pg.reload();pg.wait_for_timeout(1500)
    f=pg.evaluate(JSF,[x[0] for x in FACES])
    ck("hors ligne : l'appli s'ouvre et les polices locales se chargent",pg.evaluate("!!document.querySelector('#app,body')") and all(f.values()),f)
    ck("hors ligne : aucune requête vers Google Fonts",not ext,ext);c.close()
    b.close()
print("\n%d/%d OK"%(sum(R),len(R)));sys.exit(0 if all(R) else 1)
