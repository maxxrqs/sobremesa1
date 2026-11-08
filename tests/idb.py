# L2 : moteur IndexedDB (non actif par défaut) derrière l'interface SB.
# Usage : python3 tests/rangesrv.py 8772 .  puis  python3 tests/idb.py [URL]   (URL par défaut http://localhost:8772/)
import sys,json,re,time,asyncio,statistics
from playwright.sync_api import sync_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else "http://localhost:8772/"
R=[]
def ck(n,c,info=""):
    R.append(bool(c));print(("OK  " if c else "FAIL")+" "+n+("" if c else "  "+str(info)[:600]),flush=True)
P=lambda xp,**k:json.dumps(dict({"v":2,"xp":xp,"streak":0,"last":"","sc":{"hola":2},"lvl":1,"lang":"es","PL":{},"bd":{},"nt":[],"t":1793000000000,"ob":1,"masSeen":1},**k))
IDB="window.SOB_MOTEUR='idb'"
LIRE_IDB="""async([st,k])=>new Promise(ok=>{const r=indexedDB.open('sobremesa');r.onsuccess=()=>{const d=r.result;if(!d.objectStoreNames.contains(st)){d.close();return ok('pas de store')}const q=d.transaction(st).objectStore(st).get(k);q.onsuccess=()=>{d.close();ok(q.result===undefined?null:q.result)}}})"""
BASES="async()=>(indexedDB.databases?(await indexedDB.databases()).map(d=>d.name):'?')"
# ---- 0. contrôle statique : rien dans l'appli ne sélectionne IndexedDB
src=re.sub(r"/\*.*?\*/","",open("castellano.html",encoding="utf-8").read(),flags=re.S)   # commentaires exclus
sel=[m.group(0) for m in re.finditer(r'moteur\(\s*["\']idb["\']\s*\)|SOB_MOTEUR\s*=(?!=)',src)]
ck("code de l'appli : aucun appel à SB.moteur(\"idb\") ni affectation de SOB_MOTEUR (seule une lecture du drapeau de test existe)",sel==[] and src.count("SOB_MOTEUR")==1,sel)
with sync_playwright() as p:
    b=p.chromium.launch()
    def ctxpage(init=None,quota=None):
        ctx=b.new_context(locale="fr-FR");err=[]
        if init:ctx.add_init_script(init)
        pg=ctx.new_page();pg.on("pageerror",lambda e:err.append(str(e)[:150]));return ctx,pg,err
    # ======== A. mode par défaut : strictement localStorage
    ctx,pg,err=ctxpage();pg.goto(BASE+"index.html");pg.wait_for_timeout(700)
    pg.evaluate("(P)=>{localStorage.clear();localStorage.setItem('cast_user','moi1');localStorage.setItem('acct:moi1','{\"h\":\"z\"}');localStorage.setItem('cast:moi1',P)}",P(40))
    pg.reload();pg.wait_for_timeout(2200)
    pg.evaluate("()=>{for(let i=0;i<3;i++){S.xp++;save()}}");pg.evaluate("()=>{start('Mélange')}");pg.wait_for_timeout(600)
    r=pg.evaluate("async()=>({moteur:SB.moteur(),sync:SB.sync,xp:JSON.parse(localStorage.getItem('cast:moi1')).xp,bak:!!localStorage.getItem('cast:moi1:bak')})");bases=pg.evaluate(BASES)
    ck("mode par défaut : moteur localStorage (écriture immédiate), profil et sauvegardes dans localStorage, AUCUNE base IndexedDB créée",
       r["moteur"]=="localStorage" and r["sync"] is True and r["xp"]==43 and r["bak"] and "sobremesa" not in bases and not err,{"r":r,"bases":bases,"err":err})
    ctx.close()
    # ======== B. moteur IndexedDB (sélection explicite de test)
    ctx,pg,err=ctxpage();pg.goto(BASE+"index.html");pg.wait_for_timeout(1500)
    r=pg.evaluate("""async()=>{const o={};o.sel=SB.moteur('idb');o.sync=SB.sync;
      o.absent=await SB.lire('cast:t1');o.e1=await SB.ecrire('cast:t1','{"a":1}');o.e2=await SB.ecrire('cast:t1','{"a":1}');o.e3=await SB.ecrire('cast:t1','{"a":2}');
      o.lu=await SB.lire('cast:t1');o.ver=await SBI.version('cast:t1');
      await SB.ecrireBrut('cast:t1:bak','B');await SB.ecrireBrut('acct:t1','{"h":"x"}');o.souple=await SB.lireSouple('cast:t1:bak');
      o.cles=await SB.cles('cast:t1:');await SB.ecrireBrut('cast:t1:brut:x:1','C');o.cles2=(await SB.cles('cast:t1:')).sort();o.lisibles=await SB.lisibles('cast:t1:');
      await SB.suppr('cast:t1:brut:x:1');o.cles3=await SB.cles('cast:t1:');
      localStorage.setItem('cast_ui','en');const e=await SB.entrees(k=>/^(cast|acct:)/.test(k));o.entrees=Object.keys(e).sort();
      o.lsTouche=['cast:t1','cast:t1:bak','acct:t1'].some(k=>localStorage.getItem(k)!==null);return o}""")
    ck("IndexedDB : absent → null ; écriture « ok », réécriture identique « inchangé », nouvelle valeur « ok » ; lecture exacte ; version 2",
       r["sel"]=="indexedDB" and r["sync"] is False and r["absent"] is None and [r["e1"],r["e2"],r["e3"]]==["ok","inchangé","ok"] and r["lu"]=='{"a":2}' and r["ver"]==2,r)
    ck("IndexedDB : ecrireBrut / lireSouple / cles (préfixe) / suppr / lisibles ; export = progression de la base + préférences de localStorage ; rien écrit dans localStorage",
       r["souple"]=="B" and r["cles"]==["cast:t1:bak"] and r["cles2"]==["cast:t1:bak","cast:t1:brut:x:1"] and r["cles3"]==["cast:t1:bak"] and r["lisibles"] is True
       and r["entrees"]==["acct:t1","cast:t1","cast:t1:bak","cast_ui"] and r["lsTouche"] is False,r)
    st={(s_,k):pg.evaluate(LIRE_IDB,[s_,k]) for s_,k in [("profils","cast:t1"),("copies","cast:t1:bak"),("meta","acct:t1")]}
    ck("stores : profil → « profils », copie → « copies », compte → « meta » ; entrée = {raw (texte exact), ver, t}",
       st[("profils","cast:t1")]["raw"]=='{"a":2}' and st[("profils","cast:t1")]["ver"]==2 and st[("copies","cast:t1:bak")]["raw"]=="B" and st[("meta","acct:t1")]["raw"]=='{"h":"x"}',st)
    r=pg.evaluate("""async()=>{const o={};o.ok=await SB.ecrireSi('cast:t1','{"a":3}','{"a":2}');o.v1=await SBI.version('cast:t1');
      o.perime=await SB.ecrireSi('cast:t1','{"a":99}','{"a":2}');o.lu=await SB.lire('cast:t1');o.v2=await SBI.version('cast:t1');
      o.creation=await SB.ecrireSi('cast:t2','{"n":1}',null);o.recreation=await SB.ecrireSi('cast:t2','{"n":2}',null);return o}""")
    ck("écriture conditionnelle : version attendue → « ok » ; version périmée → « conflit », valeur et version inchangées ; création seulement si absent",
       r["ok"]=="ok" and r["v1"]==3 and r["perime"]=="conflit" and r["lu"]=='{"a":3}' and r["v2"]==3 and r["creation"]=="ok" and r["recreation"]=="conflit" and not err,r)
    # reconnexion après fermeture de la connexion
    r=pg.evaluate("async()=>{const d=await SBI.ouvrir();d.close();const a=await SB.lire('cast:t1');const b=await SB.ecrire('cast:t1','{\"a\":4}');return{a,b,c:await SB.lire('cast:t1')}}")
    ck("connexion fermée entre deux opérations : rouverte automatiquement, lecture et écriture réussies",r=={"a":'{"a":3}',"b":"ok","c":'{"a":4}'},r)
    ctx.close()
    # ======== C. concurrence réelle entre deux onglets (deux processus)
    async def concur():
        from playwright.async_api import async_playwright
        async with async_playwright() as ap:
            bb=await ap.chromium.launch();c=await bb.new_context();x=await c.new_page();y=await c.new_page()
            for q in (x,y):await q.goto(BASE+"index.html")
            await x.wait_for_timeout(1500);await y.wait_for_timeout(300)
            await x.evaluate("async()=>{SB.moteur('idb');await SB.ecrire('cast:cpt','0')}");await y.evaluate("()=>SB.moteur('idb')")
            T=await x.evaluate("()=>Date.now()+600")
            CAS="""async(T)=>{while(Date.now()<T){}let essais=0;for(let i=0;i<150;i++){for(;;){const v=await SB.lire('cast:cpt');const r=await SB.ecrireSi('cast:cpt',String(+v+1),v);essais++;if(r==='ok')break;if(r==='échec')return 'échec'}}return essais}"""
            ea,eb=await asyncio.gather(x.evaluate(CAS,T),y.evaluate(CAS,T))
            fin=await x.evaluate("()=>SB.lire('cast:cpt')")
            T=await x.evaluate("()=>Date.now()+600")
            NAIF="""async(T)=>{while(Date.now()<T){}for(let i=0;i<150;i++){const v=await SB.lire('cast:naif');await SB.ecrire('cast:naif',String(+(v||0)+1))}}"""
            await x.evaluate("()=>SB.ecrire('cast:naif','0')");await asyncio.gather(x.evaluate(NAIF,T),y.evaluate(NAIF,T));naif=await x.evaluate("()=>SB.lire('cast:naif')")
            # écriture périmée refusée même si l'autre onglet est fermé juste après avoir écrit
            await x.evaluate("()=>SB.ecrire('cast:p','v1')");attendu=await y.evaluate("()=>SB.lire('cast:p')")
            ra=await x.evaluate("()=>SB.ecrireSi('cast:p','v2-A','v1')");await x.close()
            rb=await y.evaluate("(a)=>SB.ecrireSi('cast:p','v2-B',a)",attendu);pf=await y.evaluate("()=>SB.lire('cast:p')")
            await bb.close();return ea,eb,fin,naif,ra,rb,pf
    import threading;_res=[];_t=threading.Thread(target=lambda:_res.append(asyncio.run(concur())));_t.start();_t.join()   # API asynchrone : dans un fil séparé
    ea,eb,fin,naif,ra,rb,pf=_res[0]
    ck(f"2 onglets × 150 incréments conditionnels simultanés : 300 exactement (aucune mise à jour perdue ; {ea+eb-300} conflits détectés et rejoués)",fin=="300",{"fin":fin,"essais":(ea,eb)})
    print(f"   (pour comparaison, lire puis écrire sans condition : {naif} / 300 — c'est ce que l'écriture conditionnelle évite)")
    ck("écriture périmée : A écrit puis se ferme aussitôt ; B (version périmée) est refusé ; la valeur de A reste",ra=="ok" and rb=="conflit" and pf=="v2-A",{"A":ra,"B":rb,"final":pf})
    # ======== D. fermeture pendant une transaction : tout ou rien
    res=[]
    for delai in (0,3,15,60):
        ctx,pg,err=ctxpage();pg.goto(BASE+"index.html");pg.wait_for_timeout(1200)
        pg.evaluate("async()=>{SB.moteur('idb');await SB.ecrire('cast:gros','ANCIEN')}")
        pg.evaluate("()=>{SB.ecrire('cast:gros','N'.repeat(8e6))}")
        if delai:pg.wait_for_timeout(delai)
        q=ctx.new_page();pg.close();q.goto(BASE+"manifest.webmanifest");time.sleep(0.4)
        v=q.evaluate("""async()=>new Promise(ok=>{const r=indexedDB.open('sobremesa');r.onsuccess=()=>{const q=r.result.transaction('profils').objectStore('profils').get('cast:gros');q.onsuccess=()=>ok(q.result?(q.result.raw==='ANCIEN'?'ancien':q.result.raw.length===8e6&&/^N+$/.test(q.result.raw)?'nouveau':'PARTIEL'):'absent')}})""")
        res.append((delai,v));ctx.close()
    ck("onglet fermé pendant l'écriture de 8 Mo (0/3/15/60 ms) : toujours l'ancienne ou la nouvelle valeur complète, jamais partielle",all(v in("ancien","nouveau") for _,v in res),res)
    # ======== E. quota dépassé : échec, valeur précédente intacte, reprise ensuite
    ctx,pg,err=ctxpage();pg.goto(BASE+"index.html");pg.wait_for_timeout(1200)
    cdp=ctx.new_cdp_session(pg)
    try:
        use=pg.evaluate("async()=>(await navigator.storage.estimate()).usage")   # avant toute ouverture de la base par le moteur
        print(f"   (usage actuel de l'origine : {use} octets ; quota simulé = usage + 500 000, fixé avant l'ouverture de la base)")
        cdp.send("Storage.overrideQuotaForOrigin",{"origin":BASE.rstrip("/"),"quotaSize":use+500000})
        r=pg.evaluate("""async()=>{SB.moteur('idb');const o={};o.a=await SB.ecrire('cast:q','petit');const alea=n=>{const a=new Uint8Array(n);for(let i=0;i<n;i+=65536)crypto.getRandomValues(a.subarray(i,Math.min(n,i+65536)));let s='';for(let i=0;i<n;i+=8192)s+=String.fromCharCode.apply(null,a.subarray(i,i+8192));return btoa(s)};
          const gros=alea(3e6);o.b=await SB.ecrire('cast:q',gros);o.lu=await SB.lire('cast:q');
          o.c=await SB.ecrireSi('cast:q',alea(3e6),'petit');o.d=await SB.ecrire('cast:q','petit2');o.lu2=await SB.lire('cast:q');return o}""")
        ck("quota dépassé (données incompressibles de 4 Mo) : écriture « échec » (simple et conditionnelle), valeur précédente intacte ; écriture suivante réussie ou refusée proprement, jamais abîmée",
           r["a"]=="ok" and r["b"]=="échec" and r["lu"]=="petit" and r["c"]=="échec" and r["d"] in("ok","échec") and r["lu2"] in("petit","petit2"),r)
        print(f"   (juste après l'échec, petite écriture : « {r['d']} » — l'espace d'une transaction annulée n'est pas rendu immédiatement par Chromium)")
        cdp.send("Storage.overrideQuotaForOrigin",{"origin":BASE.rstrip("/")})
        r2=pg.evaluate("async()=>({e:await SB.ecrire('cast:q','petit3'),lu:await SB.lire('cast:q')})")
        ck("espace de nouveau disponible : l'écriture reprend normalement",r2=={"e":"ok","lu":"petit3"},r2)
    except Exception as e:ck("quota dépassé (simulation CDP disponible)",False,str(e)[:200])
    ctx.close()
    # ======== F. base indisponible puis rétablie
    PANNE="(()=>{const o=IDBFactory.prototype.open;IDBFactory.prototype.open=function(){if(window.__panne)throw new DOMException('indisponible','InvalidStateError');return o.apply(this,arguments)}})()"
    ctx,pg,err=ctxpage(PANNE);pg.goto(BASE+"index.html");pg.wait_for_timeout(1200)
    r=pg.evaluate("""async()=>{window.__panne=1;SB.moteur('idb');const o={};const l=await SB.lire('cast:z');o.lire=l===undefined?null:'valeur:'+l;o.ecrire=await SB.ecrire('cast:z','x');o.si=await SB.ecrireSi('cast:z','x',null);
      await SB.ecrireBrut('cast:z:bak','memoire');o.souple=await SB.lireSouple('cast:z:bak');o.cles=await SB.cles('cast:z');o.lisibles=await SB.lisibles('cast:z');
      window.__panne=0;o.ecrire2=await SB.ecrire('cast:z','y');o.lire2=await SB.lire('cast:z');o.ls=localStorage.getItem('cast:z');return o}""")
    ck("base indisponible : lecture impossible (undefined), écritures « échec », ecrireBrut gardé en mémoire, aucune clé, non lisible ; rien dans localStorage",
       r.get("lire") is None and r["ecrire"]=="échec" and r["si"]=="échec" and r["souple"]=="memoire" and r["cles"]==[] and r["lisibles"] is False and r["ls"] is None,r)
    ck("base rétablie : la connexion est retentée, l'écriture et la lecture réussissent",r["ecrire2"]=="ok" and r["lire2"]=="y",r)
    ctx.close()
    # ======== G. parcours de l'appli avec IndexedDB sélectionné (window.SOB_MOTEUR avant le chargement)
    def appli(seed,init_extra=None):
        ctx,pg,err=ctxpage(IDB+(";"+init_extra if init_extra else ""));pg.goto(BASE+"index.html");pg.wait_for_timeout(1500)
        pg.evaluate("async(d)=>{localStorage.clear();for(const k in d)await SB.ecrireBrut(k,d[k]);localStorage.setItem('cast_user','moi1')}",seed)
        pg.reload();pg.wait_for_timeout(2500);return ctx,pg,err
    ETAT="()=>({moteur:SB.moteur(),lock:PLOCK&&PLOCK.c,rec:!!document.getElementById('prec'),xp:S.xp,U,ste:STE.profil,txt:(document.getElementById('prec')||{}).innerText||''})"
    ctx,pg,err=appli({"acct:moi1":'{"h":"z"}',"cast:moi1":P(40)})
    e=pg.evaluate(ETAT);pg.evaluate("async()=>{S.xp=41;await save()}")
    r=pg.evaluate("async()=>({main:JSON.parse(await SB.lire('cast:moi1')).xp,ver:await SBI.version('cast:moi1'),bak:await SB.lire('cast:moi1:bak'),ls:Object.keys(localStorage).filter(k=>/^(cast:|acct:)/.test(k))})")
    ck("appli sur IndexedDB : profil chargé depuis la base (40 XP), sauvegarde écrite dans la base (41 XP, version augmentée), :bak créée dans « copies », rien dans localStorage",
       e["moteur"]=="indexedDB" and e["lock"] is None and e["xp"]==40 and r["main"]==41 and r["ver"]>=2 and r["bak"]==P(40) and r["ls"]==[] and not err,{"e":e,"r":r,"err":err})
    ctx.close()
    ctx,pg,err=appli({"acct:moi1":'{"h":"z"}',"cast:moi1":"{corrompu","cast:moi1:bak":P(77)})
    e=pg.evaluate(ETAT);pg.on("dialog",lambda d:d.accept());pg.get_by_text("Restaurer la copie du").first.click();pg.wait_for_timeout(1500)
    r=pg.evaluate("async()=>({e:{lock:PLOCK&&PLOCK.c,xp:S.xp},main:await SB.lire('cast:moi1'),brut:(await SB.cles('cast:moi1:brut:corrompu')).length})")
    ck("appli sur IndexedDB, profil corrompu : écran de récupération B1, copie restaurée à l'identique, original illisible conservé dans la base",
       e["lock"]=="corrompu" and "77 XP" in e["txt"] and r["e"]["lock"] is None and r["e"]["xp"]==77 and r["main"]==P(77) and r["brut"]==1 and not err,{"e":e,"r":r})
    ctx.close()
    ctx,pg,err=ctxpage(IDB+";(()=>{const o=IDBFactory.prototype.open;IDBFactory.prototype.open=function(){if(!window.__ok)throw new DOMException('x','InvalidStateError');return o.apply(this,arguments)}})()")
    pg.goto(BASE+"index.html");pg.wait_for_timeout(800);pg.evaluate("()=>{localStorage.clear();localStorage.setItem('cast_user','moi1')}");pg.reload();pg.wait_for_timeout(2500)
    e=pg.evaluate(ETAT)
    ck("appli sur IndexedDB, base indisponible au démarrage : écran « lecture impossible » (B4-C), aucun profil neuf, rien écrit dans localStorage",
       e["lock"]=="lecture" and "Réessayer" in e["txt"] and pg.evaluate("()=>Object.keys(localStorage).filter(k=>k.startsWith('cast:')).length")==0,e)
    ctx.close()
    # deux onglets sur IndexedDB : pas d'événement « storage », mais l'écriture d'un onglet périmé est détectée avant d'écrire (A1)
    ctx,pg,err=appli({"acct:moi1":'{"h":"z"}',"cast:moi1":P(40)})
    q=ctx.new_page();q.goto(BASE+"index.html");q.wait_for_timeout(2500)
    pg.evaluate("async()=>{S.xp=140;S.sc.nuevo=3;await save()}")
    q.evaluate("async()=>{S.sc.otro=1;await save()}");q.wait_for_timeout(500)
    r=q.evaluate("async()=>{const m=JSON.parse(await SB.lire('cast:moi1'));const c=await SB.cles('cast:moi1:brut:conflit');const cp=[];for(const k of c)cp.push(JSON.parse(await SB.lire(k)));return{xp:m.xp,mots:Object.keys(m.sc).sort(),copies:cp.map(x=>Object.keys(x.sc).sort()),ban:(document.getElementById('stb')||{dataset:{}}).dataset.k||null}}")
    ck("deux onglets sur IndexedDB : l'onglet périmé n'écrase pas (140 XP et « nuevo » gardés), sa modification (« otro ») est conservée en copie, bandeau",
       r["xp"]==140 and "nuevo" in r["mots"] and any("otro" in c for c in r["copies"]) and r["ban"]=="conf",r)
    ctx.close()
    # inscription sur IndexedDB (B3)
    ctx,pg,err=ctxpage(IDB);pg.goto(BASE+"index.html");pg.wait_for_timeout(1500)
    pg.evaluate("async()=>{localStorage.clear();await SB.ecrireBrut('cast:pris1','{\"v\":2}')}")
    REG="""async([u,pw])=>{auth('reg');await new Promise(r=>setTimeout(r,200));document.getElementById('u').value=u;document.getElementById('p').value=pw;await sub('reg');await new Promise(r=>setTimeout(r,800));const m=document.getElementById('m');return{msg:m&&m.style.display!=='none'?m.textContent:'',U}}"""
    r1=pg.evaluate(REG,["pris1","motdepasse1"]);r2=pg.evaluate(REG,["neuf1","motdepasse1"])
    r3=pg.evaluate("async()=>({acct:!!(await SB.lire('acct:neuf1')),prof:JSON.parse(await SB.lire('cast:neuf1')).v,ls:Object.keys(localStorage).filter(k=>/^(cast:|acct:)/.test(k))})")
    ck("inscription sur IndexedDB : identifiant pris (profil dans la base) refusé ; identifiant neuf créé dans la base, rien dans localStorage",
       "existe déjà" in r1["msg"] and r1["U"] is None and r2["U"]=="neuf1" and r3["acct"] and r3["prof"]==2 and r3["ls"]==[] and not err,{"r1":r1,"r2":r2,"r3":r3})
    ctx.close()
    # ======== H. performances : localStorage (défaut) vs IndexedDB
    MES="""async(n)=>{S.sc={};S.sr={};for(let i=0;i<n;i++){S.sc['mot'+i]=3;S.sr['mot'+i]={b:3,d:20000+i}}await save();await SBQ;
      const tot=[];for(let i=0;i<20;i++){S.xp++;const t0=performance.now();await save();await SBQ;tot.push(performance.now()-t0)}
      const t1=performance.now();await loginL('moi1');const lg=performance.now()-t1;tot.sort((a,b)=>a-b);
      return{ko:Math.round(JSON.stringify(S).length/1024),save:+tot[10].toFixed(2),login:+lg.toFixed(1),ok:JSON.parse(await SB.lire('cast:moi1')).xp===S.xp}}"""
    print("   performances (médiane de 3 contextes ; save = enregistrement complet, connexion = loginL) :")
    for n in (500,3000,8000):
        lig=[]
        for mode in ("localStorage","indexedDB"):
            vals=[]
            for k in range(3):
                if mode=="indexedDB":ctx,pg,err=appli({"acct:moi1":'{"h":"z"}',"cast:moi1":P(40)})
                else:
                    ctx,pg,err=ctxpage();pg.goto(BASE+"index.html");pg.wait_for_timeout(700)
                    pg.evaluate("(P)=>{localStorage.clear();localStorage.setItem('cast_user','moi1');localStorage.setItem('acct:moi1','{\"h\":\"z\"}');localStorage.setItem('cast:moi1',P)}",P(40));pg.reload();pg.wait_for_timeout(2200)
                vals.append(pg.evaluate(MES,n));ctx.close()
            m=lambda key:round(statistics.median(v[key] for v in vals),2)
            lig.append((mode,vals[0]["ko"],m("save"),m("login"),all(v["ok"] for v in vals)))
        for mode,ko,sv,lg,ok in lig:print(f"     {n:>5} mots ({ko} Ko) | {mode:<12} | save {sv:>6} ms | connexion {lg:>6} ms | disque à jour {ok}")
        ck(f"performances {n} mots : enregistrements corrects avec les deux moteurs",all(x[4] for x in lig))
    b.close()
print(f"\n{sum(R)}/{len(R)} contrôles OK");sys.exit(0 if all(R) else 1)
