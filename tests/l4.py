# L4 : journal d'écriture (H1, M1), copies uniques (M3), copies consultables et restaurables, stockage surveillé (M2).
# Usage : python3 tests/rangesrv.py 8772 .  puis  python3 tests/l4.py [URL]   (URL par défaut http://localhost:8772/)
import sys,json,os,signal,time,re,asyncio,threading
from playwright.sync_api import sync_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else "http://localhost:8772/"
NEUTRE=BASE+"manifest.webmanifest"
R=[]
def ck(n,c,info=""):
    R.append(bool(c));print(("OK  " if c else "FAIL")+" "+n+("" if c else "  "+str(info)[:800]),flush=True)
P=lambda xp,**k:json.dumps(dict({"v":2,"xp":xp,"streak":0,"last":"","sc":{"hola":2},"lvl":1,"lang":"es","PL":{},"bd":{},"nt":[],"t":1793000000000,"ob":1,"masSeen":1},**k))
IDB="window.SOB_MOTEUR='idb'"
LIRE_IDB="""async()=>new Promise(ok=>{const r=indexedDB.open('sobremesa');r.onupgradeneeded=()=>{};r.onsuccess=()=>{const d=r.result,o={};const st=[...d.objectStoreNames];if(!st.length){d.close();return ok(o)}
  const t=d.transaction(st);for(const s of st){const c=t.objectStore(s).openCursor();c.onsuccess=()=>{const x=c.result;if(!x)return;o[x.key]=x.value.raw;x.continue()}}t.oncomplete=()=>{d.close();ok(o)}}})"""
TOUT_LS="()=>{const o={};for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);o[k]=localStorage.getItem(k)}return o}"
SEED_LS="(P)=>{localStorage.clear();localStorage.setItem('acct:moi1','{\"h\":\"z\"}');localStorage.setItem('cast:moi1',P);localStorage.setItem('cast_user','moi1')}"
SEED_IDB="async(P)=>{localStorage.clear();await SB.ecrireBrut('acct:moi1','{\"h\":\"z\"}');await SB.ecrireBrut('cast:moi1',P);localStorage.setItem('cast_user','moi1')}"
ETAT="async()=>{const o={main:await SB.lire('cast:moi1'),cp:{},j:[]};for(const k of await SB.cles('cast:moi1:'))if(/:jrnl:/.test(k))o.j.push(k);else if(/:brut:/.test(k))o.cp[k]=await SB.lire(k);return o}"
def mots(st):
    m=set(json.loads(st["main"])["sc"]);c=set()
    for v in st["cp"].values():
        try:c|=set(json.loads(v)["sc"])
        except Exception:pass
    return m,c
def fil(coro):
    r=[];t=threading.Thread(target=lambda:r.append(asyncio.run(coro)));t.start();t.join();return r[0]
with sync_playwright() as p:
    b=p.chromium.launch();cdp=b.new_browser_cdp_session()
    rend=lambda:{x["id"] for x in cdp.send("SystemInfo.getProcessInfo")["processInfo"] if x["type"]=="renderer"}
    def tuer(pids):
        for pid in pids:
            try:os.kill(pid,signal.SIGKILL)
            except Exception:pass
    def appli(init=None,seed=None,mode="ls"):
        ctx=b.new_context(locale="fr-FR",accept_downloads=True)
        if init:ctx.add_init_script(init)
        pg=ctx.new_page();err=[];pg.on("pageerror",lambda e:err.append(str(e)[:200]));pg.on("dialog",lambda d:d.accept())
        pg.goto(BASE+"index.html");pg.wait_for_timeout(700)
        if seed:pg.evaluate(SEED_IDB if mode=="idb" else SEED_LS,seed);pg.reload();pg.wait_for_timeout(2200)
        return ctx,pg,err
    def processus_de(ctx,pg):
        """pid du processus de l'onglet pg : processus présents avant l'ouverture d'une page témoin de la même origine"""
        avant=rend();q=ctx.new_page();q.goto(NEUTRE);q.wait_for_timeout(300);return q,[x for x in avant if x in rend()]
    # ======== 0. moteur par défaut et journal
    ctx,pg,err=appli(seed=P(40))
    r=pg.evaluate("async()=>{S.sc.j0=1;save();const ks=await SB.cles('cast:moi1:jrnl:');return{moteur:SB.moteur(),ks,j:ks.length?localStorage.getItem(ks[0]):null,main:localStorage.getItem('cast:moi1'),bases:indexedDB.databases?(await indexedDB.databases()).map(d=>d.name):'?',mig:localStorage.getItem('sob_migration')}}")
    ck("moteur par défaut localStorage : journal de l'onglet posé (cast:moi1:jrnl:<onglet>), identique au profil écrit ; aucune base IndexedDB, aucune migration",
       r["moteur"]=="localStorage" and len(r["ks"])==1 and r["j"]==r["main"] and "j0" in json.loads(r["main"])["sc"] and "sobremesa" not in r["bases"] and r["mig"] is None and not err,r)
    # hygiène : 30 enregistrements puis rechargement → aucune copie, journal intégré retiré
    pg.evaluate("()=>{for(let i=0;i<30;i++){S.sc['h'+i]=1;save()}}");pg.reload();pg.wait_for_timeout(2000)
    st=pg.evaluate(ETAT)
    ck("30 enregistrements puis rechargement : aucune copie créée, le journal déjà intégré au profil est retiré au démarrage",st["cp"]=={} and st["j"]==[] and "h29" in json.loads(st["main"])["sc"] and not err,st["j"])
    ctx.close()
    # ======== 1. H1 : IndexedDB, onglet tué dans la même tâche que save()
    perdus=0;rejoues=0;N=6
    for essai in range(N):
        ctx,pg,err=appli(IDB,P(40),"idb");q,pa=processus_de(ctx,pg)
        pg.evaluate("()=>{setTimeout(()=>{S.sc['h1_'+%d]=1;save();const t=Date.now();while(Date.now()-t<5000){}},0)}"%essai);time.sleep(0.8);tuer(pa);time.sleep(0.8)
        brut=q.evaluate(LIRE_IDB);avant="h1_%d"%essai in json.loads(brut["cast:moi1"])["sc"]
        q.goto(BASE+"index.html");q.wait_for_timeout(2500);st=q.evaluate(ETAT);m,c=mots(st)
        rejoues+=(not avant and "h1_%d"%essai in m);perdus+=("h1_%d"%essai not in m|c)
        ctx.close()
    ck(f"H1 (IndexedDB) : onglet tué dans la même tâche que save() ({N} essais) — l'écriture du profil n'avait pas eu lieu, le journal immédiat (commit) l'a rejouée au démarrage suivant : {rejoues}/{N}, perdu {perdus}",perdus==0 and rejoues==N,{"rejoues":rejoues,"perdus":perdus})
    # pagehide : fermeture et navigation (IndexedDB)
    for mode in ("fermeture d'onglet","navigation"):
        ctx,pg,err=appli(IDB,P(40),"idb");pg.evaluate("()=>addEventListener('pagehide',()=>{S.sc.ph=1;S.xp=777;save()})")
        if mode.startswith("fermeture"):pg.close(run_before_unload=True)
        else:pg.goto(NEUTRE)
        q=ctx.new_page();q.goto(BASE+"index.html");q.wait_for_timeout(2500);x=q.evaluate("()=>({xp:S.xp,ph:!!S.sc.ph})")
        ck(f"H1 (IndexedDB) : save() dans pagehide ({mode}) retrouvé au démarrage suivant (777 XP)",x=={"xp":777,"ph":True},x);ctx.close()
    # ======== 2. M1 : localStorage, deux processus, l'onglet perdant meurt / gèle juste après son écriture
    def course(fin,N):
        res=[]
        for essai in range(N):
            ctx,a,err=appli(seed=P(40));q,pa=processus_de(ctx,a);bb=ctx.new_page();bb.on("dialog",lambda d:d.accept());bb.goto(BASE+"index.html");bb.wait_for_timeout(1800)
            T=a.evaluate("()=>Date.now()+400")
            a.evaluate("(T)=>{setTimeout(()=>{while(Date.now()<T){}S.sc.motA=1;save();const t=Date.now();while(Date.now()-t<1200){}},0)}",T)
            bb.evaluate("(T)=>{setTimeout(()=>{while(Date.now()<T){}S.sc.motB=1;save()},0)}",T)
            if fin=="gel":
                ca=ctx.new_cdp_session(a);time.sleep(0.45);ca.send("Page.setWebLifecycleState",{"state":"frozen"});time.sleep(3.2)
                st=bb.evaluate(ETAT);m,c=mots(st);ban=bb.evaluate("()=>(document.getElementById('stb')||{dataset:{}}).dataset.k||null")
                ca.send("Page.setWebLifecycleState",{"state":"active"});time.sleep(2.5);st2=bb.evaluate(ETAT);m2,c2=mots(st2)
                res.append(("motA" in m|c,"motB" in m|c,"motA" in m2|c2 and "motB" in m2|c2,ban,len(st2["cp"])))
            else:
                time.sleep(1.0);tuer(pa)
                if fin=="mort":
                    time.sleep(3.0);st=bb.evaluate(ETAT);m,c=mots(st);ban=bb.evaluate("()=>(document.getElementById('stb')||{dataset:{}}).dataset.k||null")
                    res.append(("motA" in m|c,"motB" in m|c,True,ban,len(st["cp"]),"motA" in m,"motB" in m))
                else:   # les deux meurent : B tué aussi, puis nouvel onglet
                    q2,pb=processus_de(ctx,bb);tuer(pb);time.sleep(0.8)
                    n=ctx.new_page();n.goto(BASE+"index.html");n.wait_for_timeout(2600);st=n.evaluate(ETAT);m,c=mots(st)
                    res.append(("motA" in m|c,"motB" in m|c,True,None,len(st["cp"])))
            ctx.close()
        return res
    r=course("mort",10)
    ck(f"M1 (localStorage) : A écrit en même temps que B puis est tué — mot de A conservé {sum(x[0] for x in r)}/10, mot de B {sum(x[1] for x in r)}/10 (profil ou copie) ; copies par essai {[x[4] for x in r]}",
       all(x[0] and x[1] for x in r),r)
    ck("M1 : version de A remplacée → B le signale (« modification d'une autre fenêtre … conservée », lien vers les copies) ; version de B remplacée → bandeau A1 habituel",
       all((x[3]=="jc" if not x[5] else x[3]=="conf" if not x[6] else True) for x in r),[(x[3],x[5],x[6],x[4]) for x in r])
    # même situation, rendue certaine : journal d'un autre onglet non intégré au profil, écrit depuis un autre document (vrai événement storage)
    ctx,pg,err=appli(seed=P(40));pg.evaluate("()=>{S.sc.ici=1;save()}");mi=pg.evaluate("()=>JSON.parse(localStorage.getItem('cast:moi1'))._w.i")
    q=ctx.new_page();q.goto(NEUTRE)
    q.evaluate("(a)=>{localStorage.setItem('cast:moi1:jrnl:ongletmort',a[0]);localStorage.setItem('cast:moi1:jrnl:ongletvivant',a[1])}",
               [P(45,sc={"hola":2,"etranger":1},_w={"i":"zzzz","h":["inconnu"]}),P(46,sc={"hola":2,"ici":1},_w={"i":mi,"h":[]})])
    time.sleep(2.8);st=pg.evaluate(ETAT);ban=pg.evaluate("()=>(document.getElementById('stb')||{dataset:{}}).dataset.k||null")
    cps=[json.loads(v)["sc"] for v in st["cp"].values()]
    ck("journal d'un autre onglet jamais intégré au profil (événement storage réel) : conservé en copie après 1,5 s et signalé ; journal déjà intégré : aucune copie",
       len(cps)==1 and "etranger" in cps[0] and ban=="jc" and json.loads(st["main"])["xp"]==40 and not err,{"cp":list(st["cp"]),"ban":ban})
    ctx.close()
    r=course("deux",6)
    ck(f"M1 : les deux onglets tués juste après leurs écritures simultanées, nouvel onglet ouvert — les deux mots retrouvés (profil ou copie) {sum(x[0] and x[1] for x in r)}/6",all(x[0] and x[1] for x in r),r)
    r=course("gel",6)
    ck(f"M1 : A gelé (CDP Page.setWebLifecycleState frozen) juste après son écriture — pendant le gel les deux mots sont conservés {sum(x[0] and x[1] for x in r)}/6 ; après réveil {sum(x[2] for x in r)}/6",all(x[0] and x[1] and x[2] for x in r),r)
    # usage normal à deux fenêtres (alternance) : aucune fausse copie
    ctx,a,err=appli(seed=P(40));bb=ctx.new_page();bb.goto(BASE+"index.html");bb.wait_for_timeout(1800)
    for i in range(8):
        (a if i%2==0 else bb).evaluate("(i)=>{S.sc['alt'+i]=1;save()}",i);time.sleep(0.4);(bb if i%2==0 else a).evaluate("()=>dispatchEvent(new Event('focus'))");time.sleep(0.4)
    time.sleep(2.0);st=a.evaluate(ETAT);m,c=mots(st)
    ck("deux fenêtres utilisées tour à tour (8 enregistrements alternés) : tout est dans le profil, aucune copie inutile",all(f"alt{i}" in m for i in range(8)) and st["cp"]=={} and not err,{"cp":list(st["cp"]),"m":sorted(x for x in m if x.startswith("alt"))})
    ctx.close()
    # ======== 3. M3 : noms de copies uniques, création seule
    async def collisions(mode,tours):
        from playwright.async_api import async_playwright
        async with async_playwright() as ap:
            bb=await ap.chromium.launch();c=await bb.new_context()
            if mode=="idb":await c.add_init_script(IDB)
            x=await c.new_page();await x.goto(BASE+"index.html");await x.wait_for_timeout(1200)
            await x.evaluate(SEED_IDB if mode=="idb" else SEED_LS,P(40));await x.reload();await x.wait_for_timeout(2000)
            y=await c.new_page();await y.goto(BASE+"index.html");await y.wait_for_timeout(2000)
            JS="""async([moi,T,n,tour])=>{while(Date.now()<T){}const d0=Date.now;Date.now=()=>1790000000000;const ok=[];
              try{for(let i=0;i<n;i++)ok.push(await pAbri('moi1',JSON.stringify(Object.assign(FRESH(),{v:2,xp:1000+i,sc:{[moi+tour+'_'+i]:1}}))))}finally{Date.now=d0}return ok}"""
            tot=0;att=0
            for tour in range(tours):
                T=await x.evaluate("()=>Date.now()+300")
                ra,rb=await asyncio.gather(x.evaluate(JS,["a",T,5,tour]),y.evaluate(JS,["b",T,5,tour]));att+=10
            st=await x.evaluate("async()=>{const o={};for(const k of await SB.cles('cast:moi1:brut:conflit'))o[k]=await SB.lire(k);return o}")
            await bb.close()
        noms=[k for k in st];contenus=set()
        for v in st.values():contenus|=set(json.loads(v)["sc"])
        return att,len(noms),len(contenus),sum(1 for k in noms if ":1790000000000:" in k)
    for mode in ("localStorage","idb"):
        att,nk,nc,meme=fil(collisions(mode,6))
        ck(f"M3 ({mode}) : 2 processus créent chacun 5 copies dans la MÊME milliseconde (horloge figée), 6 tours — {nk} copies distinctes pour {att} demandes, {nc} contenus retrouvés, aucune écrasée",nk==att and nc==att and meme==att,{"att":att,"nk":nk,"nc":nc})
    for mode,init in (("localStorage",None),("idb",IDB)):
        ctx,pg,err=appli(init,P(40),"idb" if init else "ls")
        r=pg.evaluate("""async()=>{const d0=Date.now;Date.now=()=>1790000000000;const ok=[];try{for(let i=0;i<200;i++)ok.push(await pAbri('moi1',JSON.stringify(Object.assign(FRESH(),{v:2,xp:i,sc:{['m'+i]:1}}))))}finally{Date.now=d0}
          const k0='cast:moi1:brut:test:1';await SB.ecrireBrut(k0,'original');const e=await SB.ecrireNeuf(k0,'autre');
          return{ok:ok.filter(Boolean).length,n:(await SB.cles('cast:moi1:brut:conflit')).length,e,v:await SB.lire(k0)}}""")
        ck(f"M3 ({mode}) : 200 copies dans la même milliseconde depuis un onglet → 200 clés ; ecrireNeuf refuse une clé existante (« existe », contenu intact)",r=={"ok":200,"n":200,"e":"existe","v":"original"} and not err,r)
        ctx.close()
    # création seule sur la MÊME clé depuis deux processus : atomique avec IndexedDB, pas avec localStorage (d'où la partie aléatoire des noms)
    async def meme_cle(mode):
        from playwright.async_api import async_playwright
        async with async_playwright() as ap:
            bb=await ap.chromium.launch();c=await bb.new_context()
            if mode=="idb":await c.add_init_script(IDB)
            x=await c.new_page();y=await c.new_page()
            for q in (x,y):await q.goto(BASE+"index.html")
            await x.wait_for_timeout(1500);dbl=0
            for i in range(20):
                k="cast:z:brut:t:%d"%i;T=await x.evaluate("()=>Date.now()+250")
                JS="async([k,v,T])=>{await SB.lire('cast:z');while(Date.now()<T){}return await SB.ecrireNeuf(k,v)}"
                ra,rb=await asyncio.gather(x.evaluate(JS,[k,"A",T]),y.evaluate(JS,[k,"B",T]));dbl+=(ra=="ok" and rb=="ok")
            await bb.close();return dbl
    d_idb=fil(meme_cle("idb"));d_ls=fil(meme_cle("localStorage"))
    ck(f"M3 : même clé créée au même instant par 2 processus (20 essais) — IndexedDB : double création {d_idb}/20 (atomique) ; localStorage : {d_ls}/20 (non atomique, mesuré et documenté : l'unicité repose sur la partie aléatoire)",d_idb==0,{"idb":d_idb,"ls":d_ls})
    # ======== 4. M2 : copies consultables, restauration, suppression gardée, quota
    ctx,pg,err=appli(seed=P(300,sc={"hola":2,"actuel":1}))
    pg.evaluate("""(a)=>{localStorage.setItem('cast:moi1:brut:conflit:1793000000001:aaaa',a[0]);localStorage.setItem('cast:moi1:brut:tardif:1793000000002:0bbbb',a[1]);localStorage.setItem('cast:moi1:brut:corrompu:1793000000003','{illisible')}""",
                [P(250,sc={"hola":2,"perdu":1},t=1793000000001),P(120,t=1793000000002)])
    pg.evaluate("()=>menu()");pg.wait_for_timeout(200);pg.get_by_text("Copies de sécurité").first.click();pg.wait_for_timeout(800)
    t=pg.evaluate("()=>(document.getElementById('cop')||{}).innerText||''");dis=pg.evaluate("()=>[...document.querySelectorAll('#cop button')].filter(b=>b.textContent==='Supprimer').map(b=>b.disabled)")
    ck("écran « Copies de sécurité » depuis le menu (profil valide) : copies listées avec type, XP et mots (250 et 120 XP), la copie identique au profil et la copie illisible exclues ; suppression désactivée avant téléchargement",
       "Autre fenêtre (conflit)" in t and "250 XP" in t and "120 XP" in t and "Écriture tardive" in t and "300 XP" not in t and dis==[True,True] and not err,{"t":t[:400],"dis":dis})
    pg.locator("#cop .cpi").filter(has_text="250 XP").get_by_text("Restaurer").click();pg.wait_for_timeout(1500)
    st=pg.evaluate(ETAT);x=pg.evaluate("()=>({xp:S.xp,perdu:!!S.sc.perdu})")
    av=[v for k,v in st["cp"].items() if ":brut:avant-restauration:" in k]
    ck("restauration (confirmation acceptée) : progression = copie (250 XP) ; la progression remplacée (300 XP) est d'abord conservée ; la copie restaurée reste disponible",
       x=={"xp":250,"perdu":True} and len(av)==1 and json.loads(av[0])["xp"]==300 and any(":brut:conflit:" in k for k in st["cp"]) and not err,{"x":x,"cp":list(st["cp"])})
    pg.evaluate("()=>cpScr()");pg.wait_for_timeout(600);n0=len(pg.evaluate(ETAT)["cp"])
    pg.evaluate("()=>cpDel(0)");pg.wait_for_timeout(300);n1=len(pg.evaluate(ETAT)["cp"])
    with pg.expect_download() as dlw:pg.get_by_text("Télécharger mes données").first.click()
    dl=dlw.value;dat=json.loads(open(dl.path(),encoding="utf-8").read())["data"];pg.wait_for_timeout(600)
    dis=pg.evaluate("()=>[...document.querySelectorAll('#cop button')].filter(b=>b.textContent==='Supprimer').map(b=>b.disabled)")
    cible=pg.evaluate("()=>CPL[0].k");pg.locator("#cop .cpi").first.get_by_text("Supprimer").click();pg.wait_for_timeout(800);st2=pg.evaluate(ETAT)
    ck("suppression : impossible avant téléchargement ; après, uniquement pour une copie présente à l'identique dans le fichier ; confirmée, elle ne retire que cette copie (profil et autres copies intacts)",
       n1==n0 and dis and all(d is False for d in dis) and cible in dat and cible not in st2["cp"] and len(st2["cp"])==n0-1 and json.loads(st2["main"])["xp"]==250 and not err,{"n0":n0,"n1":n1,"dis":dis,"cible":cible})
    ctx.close()
    # quota : stockage presque plein, écriture refusée, avis à l'ouverture
    ctx,pg,err=appli(seed=P(40))
    pg.evaluate("""()=>{const s='x'.repeat(100000);let n=0;try{for(;;n++)localStorage.setItem('zz_rempli_'+n,s)}catch(e){}const t='y'.repeat(2000);try{for(let m=0;;m++)localStorage.setItem('zz_r2_'+m,t)}catch(e){}}""")
    pg.evaluate("()=>{S.sc.gros='w'.repeat(30000);save()}");pg.wait_for_timeout(300)
    ban=pg.evaluate("()=>{const b=document.getElementById('stb');return b?{k:b.dataset.k,t:b.innerText}:null}")
    ck("stockage plein : enregistrement refusé signalé (« pas pu être enregistrée … stockage plein ? »), avec accès aux copies ; jamais présenté comme enregistré",
       ban and ban["k"]=="échec" and "Voir les copies" in ban["t"] and "stockage plein" in ban["t"],ban)
    pg.evaluate("()=>cpScr()");pg.wait_for_timeout(600);t=pg.evaluate("()=>(document.getElementById('cop')||{}).innerText||''")
    ck("écran des copies : place utilisée affichée et avertissement « presque plein »","presque plein" in t and re.search(r"environ (9\d|100) %",t) is not None,t[:300])
    pg.evaluate("()=>{for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);if(k.startsWith('zz_r2_')){localStorage.removeItem(k);i--}}for(let i=0;i<12;i++)localStorage.removeItem('zz_rempli_'+i)}")
    pg.reload();pg.wait_for_timeout(2500);ban=pg.evaluate("()=>{const b=document.getElementById('stb');return b?{k:b.dataset.k,t:b.innerText}:null}")
    ck("à l'ouverture, stockage au-delà de 70 % : avis discret avec le nombre de copies et la place occupée (une fois par session), sans rien supprimer",
       ban and ban["k"]=="cop" and "%" in ban["t"] and "Voir les copies" in ban["t"],ban)
    ctx.close()
    # ======== 5. rien d'activé
    ctx,pg,err=appli(seed=P(40));pg.evaluate("()=>{S.xp=41;save()}")
    r=pg.evaluate("async()=>({moteur:SB.moteur(),bases:indexedDB.databases?(await indexedDB.databases()).map(d=>d.name):'?',mig:localStorage.getItem('sob_migration')})")
    ck("après tout cela, mode par défaut : localStorage, aucune base IndexedDB, aucune migration",r["moteur"]=="localStorage" and "sobremesa" not in r["bases"] and r["mig"] is None,r)
    ctx.close();b.close()
print(f"\n{sum(R)}/{len(R)} contrôles OK");sys.exit(0 if all(R) else 1)
