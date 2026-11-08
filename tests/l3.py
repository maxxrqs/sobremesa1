# L3 : concurrence sûre (ecrireSi, pSyncRun) et migration localStorage → IndexedDB (jamais automatique).
# Usage : python3 tests/rangesrv.py 8772 .  puis  python3 tests/l3.py [URL]   (URL par défaut http://localhost:8772/)
import sys,json,re,time,asyncio,threading
from playwright.sync_api import sync_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else "http://localhost:8772/"
R=[]
def ck(n,c,info=""):
    R.append(bool(c));print(("OK  " if c else "FAIL")+" "+n+("" if c else "  "+str(info)[:700]),flush=True)
P=lambda xp,**k:json.dumps(dict({"v":2,"xp":xp,"streak":0,"last":"","sc":{"hola":2},"lvl":1,"lang":"es","PL":{},"bd":{},"nt":[],"t":1793000000000,"ob":1,"masSeen":1},**k))
IDB="window.SOB_MOTEUR='idb'"
MIG="window.SOB_MOTEUR='idb';window.SOB_MIGRER=1"
TOUT_LS="()=>{const o={};for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);o[k]=localStorage.getItem(k)}return o}"
BASE_IDB="""async()=>new Promise(ok=>{const r=indexedDB.open('sobremesa');r.onupgradeneeded=()=>{};r.onsuccess=()=>{const d=r.result,o={};const st=[...d.objectStoreNames];if(!st.length){d.close();return ok(o)}
  const t=d.transaction(st);for(const s of st){const c=t.objectStore(s).openCursor();c.onsuccess=()=>{const x=c.result;if(!x)return;o[s+'|'+x.key]=x.value;x.continue()}}t.oncomplete=()=>{d.close();ok(o)}}})"""
# ---- 0. contrôle statique : ni activation ni migration automatiques
src=re.sub(r"/\*.*?\*/","",open("castellano.html",encoding="utf-8").read(),flags=re.S)
appels=[m.group(0) for m in re.finditer(r'(SB|SBI)\.migrer\(\)|moteur\(\s*["\']idb["\']\s*\)|SOB_(MOTEUR|MIGRER)\s*=(?!=)',src)]
lecture_drapeau=src.count("window.SOB_MIGRER===1")
ck("code de l'appli : aucune activation ni migration automatique (migrer() appelée seulement sous le drapeau de test SOB_MIGRER, jamais défini par l'appli)",
   [a for a in appels if a!="SBI.migrer()"]==[] and lecture_drapeau==2 and src.count("SBI.migrer()")==3 and src.count("async migrer(){return SBI.migrer()}")==1
   and len(re.findall(r'window\.SOB_MIGRER===1&&SBM===SBI[^\n]{0,80}SBI\.migrer\(\)',src))==2,{"appels":appels,"drapeau":lecture_drapeau})
# ---- 1. rafales concurrentes réelles de l'appli (deux processus, deux onglets)
async def rafale(moteur,n=50):
    from playwright.async_api import async_playwright
    async with async_playwright() as ap:
        b=await ap.chromium.launch();c=await b.new_context()
        if moteur=="idb":await c.add_init_script(IDB)
        x=await c.new_page();await x.goto(BASE+"index.html");await x.wait_for_timeout(1500)
        await x.evaluate("async(P)=>{localStorage.clear();await SB.ecrireBrut('acct:moi1','{\"h\":\"z\"}');await SB.ecrireBrut('cast:moi1',P);localStorage.setItem('cast_user','moi1')}",P(40))
        await x.reload();await x.wait_for_timeout(2500);y=await c.new_page();await y.goto(BASE+"index.html");await y.wait_for_timeout(2500)
        T=await x.evaluate("()=>Date.now()+700")
        JS="""async([t,n,T])=>{while(Date.now()<T){}const e=[];for(let i=0;i<n;i++){const w=t+i;S.sc[w]=1;save();e.push(w);await new Promise(r=>setTimeout(r,Math.random()*3))}await SBQ;return e}"""
        ea,eb=await asyncio.gather(x.evaluate(JS,["a",n,T]),y.evaluate(JS,["b",n,T]))
        await x.wait_for_timeout(1500)
        st=await x.evaluate("async()=>{const o={main:await SB.lire('cast:moi1'),cp:[]};for(const k of await SB.cles('cast:moi1:brut:conflit'))o.cp.push(await SB.lire(k));return o}")
        await b.close()
    disque=set(json.loads(st["main"])["sc"]);tout=set(disque)
    for v in st["cp"]:
        try:tout|=set(json.loads(v)["sc"])
        except Exception:pass
    ecrits=set(ea)|set(eb);return len(ecrits),len(ecrits&disque),len(st["cp"]),sorted(ecrits-tout)
def fil(coro):
    r=[];t=threading.Thread(target=lambda:r.append(asyncio.run(coro)));t.start();t.join();return r[0]
for moteur in ("idb","localStorage"):
    for essai in range(3 if moteur=="idb" else 2):
        tot,disque,ncp,perdus=fil(rafale(moteur))
        ck(f"rafale concurrente réelle ({moteur}, essai {essai+1}) : 2 onglets × 50 enregistrements — {disque}/{tot} sur le profil, {ncp} copies, aucun mot perdu sans trace",not perdus,perdus[:10])
with sync_playwright() as p:
    b=p.chromium.launch()
    def page(init=None):
        ctx=b.new_context(locale="fr-FR");err=[]
        if init:ctx.add_init_script(init)
        pg=ctx.new_page();pg.on("pageerror",lambda e:err.append(str(e)[:150]));return ctx,pg,err
    def seed_ls(pg,d):pg.evaluate("(d)=>{localStorage.clear();for(const k in d)localStorage.setItem(k,d[k])}",d)
    # ---- 2. écriture périmée et fermeture d'onglet (IndexedDB)
    ctx,pg,err=page(IDB);pg.goto(BASE+"index.html");pg.wait_for_timeout(1500)
    pg.evaluate("async(P)=>{localStorage.clear();await SB.ecrireBrut('acct:moi1','{\"h\":\"z\"}');await SB.ecrireBrut('cast:moi1',P);localStorage.setItem('cast_user','moi1')}",P(40))
    pg.reload();pg.wait_for_timeout(2500);q=ctx.new_page();q.goto(BASE+"index.html");q.wait_for_timeout(2500)
    pg.evaluate("async()=>{S.xp=140;S.sc.adieu=1;await save()}");pg.close()
    q.evaluate("async()=>{S.sc.tard=1;await save()}");q.wait_for_timeout(500)
    r=q.evaluate("async()=>{const m=JSON.parse(await SB.lire('cast:moi1'));const cp=[];for(const k of await SB.cles('cast:moi1:brut:conflit'))cp.push(Object.keys(JSON.parse(await SB.lire(k)).sc));return{xp:m.xp,sc:Object.keys(m.sc),cp,ban:(document.getElementById('stb')||{dataset:{}}).dataset.k||null}}")
    ck("IndexedDB : A écrit puis se ferme ; B (périmé) n'écrase pas (140 XP, « adieu » gardés), sa modification (« tard ») est en copie, bandeau",
       r["xp"]==140 and "adieu" in r["sc"] and any("tard" in c for c in r["cp"]) and r["ban"]=="conf" and not err,r)
    ctx.close()
    # ---- 3. migration : données exactes, comptes, copies, corrompu
    LS={"cast_user":"moi1","cast_ui":"es","acct:moi1":'{"salt":"0","a":"p","h":"z"}',"cast:moi1":P(250),"cast:moi1:bak":P(240),"cast:moi1:bakJ":P(230),"cast:moi1:bakJ:jour":"2026-11-07",
        "cast:moi1:brut:corrompu:1793000000000":"{corrompu","acct:moi2":'{"h":"y"}',"cast:moi2":"{corrompu","cast":P(5),"sobv_es":"x"}
    ctx,pg,err=page();pg.goto(BASE+"index.html");pg.wait_for_timeout(800);seed_ls(pg,LS)
    r=pg.evaluate("async()=>{const a=await SB.migrer();return{a,moteur:SB.moteur()}}");idb=pg.evaluate(BASE_IDB);ls=pg.evaluate(TOUT_LS)
    routees={k:v for k,v in LS.items() if k=="cast" or k.startswith(("cast:","acct:"))}
    exact=all(next((e["raw"] for kk,e in idb.items() if kk.split("|",1)[1]==k),None)==v for k,v in routees.items())
    ck("migration : 9 clés de progression copiées À L'OCTET PRÈS (profils, copies, :jour, copie brute corrompue, profil corrompu, comptes, profil invité), dans les bons stores",
       r["a"]["migre"]==9==len(routees) and exact and idb.get("profils|cast:moi1",{}).get("raw")==LS["cast:moi1"] and "copies|cast:moi1:bak" in idb and "meta|acct:moi1" in idb and "profils|cast" in idb,{"r":r,"cles":sorted(idb)})
    ck("migration : rien n'est supprimé ni modifié dans localStorage (seule la marque sob_migration est ajoutée) ; préférences non migrées ; moteur actif inchangé",
       all(ls.get(k)==v for k,v in LS.items()) and set(ls)-set(LS)=={"sob_migration"} and not any(k.split("|",1)[1] in("cast_user","cast_ui","sobv_es") for k in idb) and r["moteur"]=="localStorage",{"en_plus":sorted(set(ls)-set(LS))})
    r2=pg.evaluate("async()=>SB.migrer()");idb2=pg.evaluate(BASE_IDB)
    ck("migration relancée : idempotente (9 « déjà migré », aucune écriture de données)",r2["deja"]==9 and r2["migre"]==0 and {k:v for k,v in idb2.items() if not k.startswith("meta|migration")}=={k:v for k,v in idb.items() if not k.startswith("meta|migration")},r2)
    ctx.close()
    # ---- 4. migration simultanée depuis trois onglets (trois processus)
    async def trois():
        from playwright.async_api import async_playwright
        async with async_playwright() as ap:
            bb=await ap.chromium.launch();c=await bb.new_context();pages=[await c.new_page() for _ in range(3)]
            for q in pages:await q.goto(BASE+"index.html")
            await pages[0].wait_for_timeout(1500);await pages[0].evaluate("(d)=>{localStorage.clear();for(const k in d)localStorage.setItem(k,d[k])}",LS)
            T=await pages[0].evaluate("()=>Date.now()+600")
            res=await asyncio.gather(*[q.evaluate("async(T)=>{while(Date.now()<T){}return await SB.migrer()}",T) for q in pages])
            idb=await pages[0].evaluate(BASE_IDB);await bb.close();return res,idb
    res,idb=fil(trois())
    ck("migration lancée au même instant par 3 onglets : chaque clé migrée exactement une fois (9 au total), les autres onglets voient « déjà migré », données exactes",
       sum(r["migre"] for r in res)==9 and sorted(r["migre"] for r in res)==[0,0,9] and sum(r["deja"] for r in res)==18 and idb.get("profils|cast:moi1",{}).get("raw")==LS["cast:moi1"],res)
    # ---- 5. migration interrompue (processus de l'onglet tué en pleine transaction) puis reprise
    import os,signal
    cdp=b.new_browser_cdp_session();rend=lambda:{x["id"] for x in cdp.send("SystemInfo.getProcessInfo")["processInfo"] if x["type"]=="renderer"}
    DONNEES=lambda d:{k:v for k,v in d.items() if not k.startswith(("meta|mig:","meta|migration"))}
    for essai in range(2):
        ctx,pg,err=page();pg.goto(BASE+"index.html");pg.wait_for_timeout(800);seed_ls(pg,LS)
        avant_p=rend();q=ctx.new_page();q.goto(BASE+"manifest.webmanifest");q.wait_for_timeout(300);appli=[x for x in rend() if x not in (rend()-avant_p)]
        pg.evaluate("""()=>{let n=0;const p0=IDBObjectStore.prototype.put;IDBObjectStore.prototype.put=function(){const r=p0.apply(this,arguments);
          if(++n===6+%d*5){window.EN=n;setTimeout(()=>{},0);const t=Date.now();while(Date.now()-t<20000){}}return r};SB.migrer()}"""%essai)
        time.sleep(1.0)
        for pid in appli:
            try:os.kill(pid,signal.SIGKILL)
            except Exception:pass
        time.sleep(0.8);avant=q.evaluate(BASE_IDB);n_avant=len(DONNEES(avant))
        q.goto(BASE+"index.html");q.wait_for_timeout(1500);x=q.evaluate("async()=>{const ls=("+TOUT_LS+")();return{ls,r:await SB.migrer()}}");r=x["r"];apres=q.evaluate(BASE_IDB)   # l'appli rechargée a pu réécrire le profil : la source est l'état au moment de la reprise
        exact=all(next((e["raw"] for kk,e in apres.items() if kk.split("|",1)[1]==k),None)==v for k,v in x["ls"].items() if k=="cast" or k.startswith(("cast:","acct:")))
        ck(f"migration interrompue (essai {essai+1} : processus tué après {6+essai*5} écritures, transaction non validée) : rien d'écrit à moitié (0 clé), reprise complète (9 migrées) et exacte",
           len(appli)>=1 and n_avant==0 and "meta|migration" not in avant and r["migre"]==9 and len(DONNEES(apres))==9 and exact,{"appli":appli,"avant":n_avant,"r":r,"n":len(DONNEES(apres)),"exact":exact,"cles":sorted(DONNEES(apres))})
    ctx.close()
    # ---- 6. données présentes dans les deux moteurs, écritures tardives, conflit de compte
    ctx,pg,err=page();pg.goto(BASE+"index.html");pg.wait_for_timeout(1200)
    seed_ls(pg,{"acct:moi1":'{"h":"ls"}',"cast:moi1":P(250),"cast:moi1:bak":P(240),"cast:moi3":P(9)})
    pg.evaluate("async([a,b])=>{SB.moteur('idb');await SB.ecrireBrut('cast:moi1',a);await SB.ecrireBrut('acct:moi1','{\"h\":\"idb\"}');await SB.ecrireBrut('cast:moi3',b);SB.moteur('localStorage')}",[P(300),P(9)])
    r=pg.evaluate("async()=>SB.migrer()");idb=pg.evaluate(BASE_IDB)
    cp=[(k,v["raw"]) for k,v in idb.items() if ":brut:conflit" in k];acp=[(k,v["raw"]) for k,v in idb.items() if k.startswith("meta|acct:moi1:conflit")]
    ck("deux moteurs : profil différent → la base est gardée (300 XP), la version localStorage (250 XP) part en copie « conflit » ; profil identique → rien ; :bak migrée",
       idb["profils|cast:moi1"]["raw"]==P(300) and any(v==P(250) for k,v in cp) and r["conflit"]==2 and r["egal"]==1 and r["migre"]==1,{"r":r,"copies":[k for k,_ in cp]})
    ck("deux moteurs : compte différent → compte de la base gardé, compte localStorage conservé sous acct:moi1:conflit:…",
       idb["meta|acct:moi1"]["raw"]=='{"h":"idb"}' and any(v=='{"h":"ls"}' for _,v in acp),acp)
    pg.evaluate("(P)=>localStorage.setItem('cast:moi1',P)",P(260))   # ancienne version encore ouverte : écriture tardive
    r=pg.evaluate("async()=>SB.migrer()");idb=pg.evaluate(BASE_IDB)
    tard=[v["raw"] for k,v in idb.items() if ":brut:tardif" in k]
    ck("écriture tardive dans localStorage après migration : jamais écrasante (base = 300 XP), conservée en copie « tardif » (260 XP), détectée une seule fois",
       idb["profils|cast:moi1"]["raw"]==P(300) and P(260) in tard and r["tardif"]==1 and pg.evaluate("async()=>(await SB.migrer()).tardif")==0,{"r":r})
    ctx.close()
    # écriture tardive détectée en direct (mode expérimental, événement storage venant d'un autre onglet)
    ctx,pg,err=page(MIG);pg.goto(BASE+"index.html");pg.wait_for_timeout(800)
    seed_ls(pg,{"cast_user":"moi1","acct:moi1":'{"h":"z"}',"cast:moi1":P(40)});pg.reload();pg.wait_for_timeout(2500)
    vieux=ctx.new_page();vieux.goto(BASE+"manifest.webmanifest");vieux.evaluate("(P)=>localStorage.setItem('cast:moi1',P)",P(77));pg.wait_for_timeout(800)
    idb=pg.evaluate(BASE_IDB);e=pg.evaluate("()=>({xp:S.xp,moteur:SB.moteur()})")
    ck("mode expérimental : profil migré au démarrage puis chargé depuis la base ; écriture d'une ancienne version dans un autre onglet détectée en direct (copie « tardif », base intacte)",
       e["moteur"]=="indexedDB" and e["xp"]==40 and idb["profils|cast:moi1"]["raw"]==P(40) and any(v["raw"]==P(77) for k,v in idb.items() if ":brut:tardif" in k) and not err,{"e":e,"cles":sorted(idb)})
    ctx.close()
    # ---- 7. comptes, inscription et export pendant la transition
    ctx,pg,err=page();pg.goto(BASE+"index.html");pg.wait_for_timeout(1500);pg.evaluate("()=>localStorage.clear()");pg.reload();pg.wait_for_timeout(1500)
    REG="""async([m,u,pw])=>{auth(m);await new Promise(r=>setTimeout(r,200));document.getElementById('u').value=u;document.getElementById('p').value=pw;await sub(m);await new Promise(r=>setTimeout(r,900));const x=document.getElementById('m');return{msg:x&&x.style.display!=='none'?x.textContent:'',U}}"""
    r=pg.evaluate(REG,["reg","ancien1","motdepasse1"]);pg.evaluate("async()=>{S.xp=123;await save()}");pg.evaluate("()=>logout()");pg.wait_for_timeout(300)
    ls=pg.evaluate(TOUT_LS);ctx.close()
    ctx,pg,err=page(IDB);pg.goto(BASE+"index.html");pg.wait_for_timeout(800);seed_ls(pg,{k:v for k,v in ls.items() if k!="cast_user"});pg.reload();pg.wait_for_timeout(1500)
    r1=pg.evaluate(REG,["reg","ancien1","autremdp1"])
    ex=pg.evaluate("async()=>{const d=await SB.entrees(BKK);return{prefixes:Object.keys(d).filter(k=>k.startsWith('localStorage:')).sort(),tr:d.sob_transition?JSON.parse(d.sob_transition):null}}")
    ck("transition (IndexedDB, données encore dans localStorage) : inscription d'un identifiant existant dans localStorage REFUSÉE ; export signale les données de localStorage",
       "existe déjà" in r1["msg"] and r1["U"] is None and "localStorage:cast:ancien1" in ex["prefixes"] and "localStorage:acct:ancien1" in ex["prefixes"] and ex["tr"] and ex["tr"]["differentes"]>=2,{"r1":r1,"ex":ex})
    pg.evaluate("async()=>SB.migrer()")
    r2=pg.evaluate(REG,["login","ancien1","motdepasse1"]);xp=pg.evaluate("()=>S.xp")
    ex2=pg.evaluate("async()=>{const d=await SB.entrees(BKK);return{prefixes:Object.keys(d).filter(k=>k.startsWith('localStorage:')),tr:d.sob_transition?JSON.parse(d.sob_transition):null,acct:!!d['acct:ancien1']}}")
    ck("après migration : connexion avec le mot de passe d'origine réussie depuis la base (123 XP) ; export : plus de différence avec localStorage, signalé dans sob_transition",
       r2["U"]=="ancien1" and xp==123 and ex2["prefixes"]==[] and ex2["tr"]["differentes"]==0 and ex2["acct"] and not err,{"r2":r2,"xp":xp,"ex2":ex2})
    ctx.close()
    # ---- 8. profils corrompus, copies et sauvegardes après migration (appli sur IndexedDB)
    ctx,pg,err=page(MIG);pg.goto(BASE+"index.html");pg.wait_for_timeout(800)
    seed_ls(pg,{"cast_user":"moi1","acct:moi1":'{"h":"z"}',"cast:moi1":"{corrompu","cast:moi1:bak":P(66),"cast:moi1:bakJ":P(55),"cast:moi1:bakJ:jour":"2026-11-01"});pg.reload();pg.wait_for_timeout(2500)
    t=pg.evaluate("()=>(document.getElementById('prec')||{}).innerText||''");lock=pg.evaluate("()=>PLOCK&&PLOCK.c")
    pg.on("dialog",lambda d:d.accept());pg.get_by_text("Restaurer la copie du").nth(1).click();pg.wait_for_timeout(1500)
    r=pg.evaluate("async()=>({xp:S.xp,main:await SB.lire('cast:moi1'),bak:await SB.lire('cast:moi1:bak'),avant:(await SB.cles('cast:moi1:brut:avant')).length,orig:(await SB.cles('cast:moi1:brut:corrompu')).length,ls:localStorage.getItem('cast:moi1')})")
    ck("migré puis corrompu : écran B1 avec les 2 copies ; restauration de la plus ancienne (55 XP) ; la plus récente mise à l'abri ; original illisible gardé ; localStorage intact",
       lock=="corrompu" and "66 XP" in t and "55 XP" in t and r["xp"]==55 and r["main"]==P(55) and r["avant"]>=1 and r["orig"]==1 and r["ls"]=="{corrompu" and not err,{"lock":lock,"r":r})
    ctx.close()
    # ---- 9. disponibilité du moteur actif (plus de confusion avec localStorage)
    ctx,pg,err=page(IDB+";(()=>{Storage.prototype.setItem=function(){throw new DOMException('refusé','SecurityError')}})()");pg.goto(BASE+"index.html");pg.wait_for_timeout(1500)
    r=pg.evaluate("""async(P)=>{await SB.ecrireBrut('acct:moi1','{"h":"z"}');await SB.ecrireBrut('cast:moi1',P);await loginL('moi1');S.xp=41;await save();
      auth('reg');await new Promise(r=>setTimeout(r,200));const avert=document.body.innerText.includes('stockage');
      return{stok:ST.ok,dispo:SB.dispo,ste:STE.profil,ban:(document.getElementById('stb')||{dataset:{}}).dataset.k||null,idb:JSON.parse(await SB.lire('cast:moi1')).xp,avert}}""",P(40))
    ck("localStorage bloqué, IndexedDB actif et fonctionnel : moteur disponible, progression enregistrée (41 XP), AUCUN bandeau « mémoire », pas d'avertissement à l'inscription",
       r["stok"] is False and r["dispo"] is True and r["ste"]=="ok" and r["ban"] is None and r["idb"]==41 and r["avert"] is False,r)
    ctx.close()
    ctx,pg,err=page(IDB+";(()=>{IDBFactory.prototype.open=function(){throw new DOMException('x','InvalidStateError')}})()");pg.goto(BASE+"index.html");pg.wait_for_timeout(1500)
    r=pg.evaluate("async()=>{await SB.lire('cast:x');return{stok:ST.ok,dispo:SB.dispo}}")
    ck("IndexedDB actif mais indisponible (localStorage disponible) : SB.dispo = false (le moteur actif est évalué, pas localStorage)",r=={"stok":True,"dispo":False},r)
    ctx.close()
    # ---- 10. mode par défaut : aucune base, aucune migration
    ctx,pg,err=page();pg.goto(BASE+"index.html");pg.wait_for_timeout(800);seed_ls(pg,{"cast_user":"moi1","acct:moi1":'{"h":"z"}',"cast:moi1":P(40)});pg.reload();pg.wait_for_timeout(2500)
    pg.evaluate("()=>{S.xp=44;save()}");r=pg.evaluate("async()=>({moteur:SB.moteur(),dispo:SB.dispo,bases:indexedDB.databases?(await indexedDB.databases()).map(d=>d.name):'?',mig:localStorage.getItem('sob_migration')})")
    ck("mode par défaut : localStorage, aucune base IndexedDB, aucune migration (pas de marque sob_migration)",r["moteur"]=="localStorage" and r["dispo"] is True and "sobremesa" not in r["bases"] and r["mig"] is None,r)
    ctx.close()
    b.close()
print(f"\n{sum(R)}/{len(R)} contrôles OK");sys.exit(0 if all(R) else 1)
