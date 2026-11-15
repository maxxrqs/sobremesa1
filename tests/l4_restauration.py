# L4 : une restauration explicite (écran « Copies de sécurité » ou écran B1) n'est jamais annulée par le rejeu d'un journal.
# Usage : python3 tests/rangesrv.py 8772 .  puis  python3 tests/l4_restauration.py [URL] [page]   (défauts : http://localhost:8772/ index.html)
import sys,json,time
from playwright.sync_api import sync_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else "http://localhost:8772/"
PAGE=sys.argv[2] if len(sys.argv)>2 else "index.html"
R=[]
def ck(n,c,info=""):
    R.append(bool(c));print(("OK  " if c else "FAIL")+" ["+PAGE+"] "+n+("" if c else "  "+str(info)[:800]),flush=True)
P=lambda xp,**k:json.dumps(dict({"v":2,"xp":xp,"streak":0,"last":"","sc":{"hola":2},"lvl":1,"lang":"es","PL":{},"bd":{},"nt":[],"t":1793000000000,"ob":1,"masSeen":1},**k))
SEED="(P)=>{localStorage.clear();localStorage.setItem('acct:moi1','{\"h\":\"z\"}');localStorage.setItem('cast:moi1',P);localStorage.setItem('cast_user','moi1')}"
TOUT="()=>{const o={};for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);if(k.startsWith('cast:moi1'))o[k]=localStorage.getItem(k)}return o}"
def SANSW(r):
    try:o=json.loads(r)
    except Exception:return r
    return json.dumps({k:v for k,v in o.items() if k!="_w"},sort_keys=True) if isinstance(o,dict) else r
with sync_playwright() as p:
    b=p.chromium.launch()
    def ouvrir():
        ctx=b.new_context(locale="fr-FR");pg=ctx.new_page();err=[];dl=[]
        pg.on("pageerror",lambda e:err.append(str(e)[:200]));pg.on("dialog",lambda d:(dl.append(d.message),d.accept()))
        pg.goto(BASE+PAGE);pg.wait_for_timeout(700);pg.evaluate(SEED,P(40));pg.reload();pg.wait_for_timeout(2200);return ctx,pg,err,dl
    def preparer(pg,typ):
        """profil à 50 XP (filiation posée), copie `typ` = ce profil, puis un enregistrement à 60 XP : journal dont le point de départ est la copie"""
        pg.evaluate("()=>{S.xp=50;S.sc.cinquante=1;save()}")
        if typ=="bak":pg.reload();pg.wait_for_timeout(2200)          # sauvegarde d'ouverture :bak = profil 50 XP (chemin réel)
        else:   # état construit : :bakJ (premier chargement du jour) = profil 50 XP, :bak différent (30 XP, autre filiation)
            pg.evaluate("()=>{localStorage.setItem('cast:moi1:bakJ',localStorage.getItem('cast:moi1'));localStorage.setItem('cast:moi1:bak',JSON.stringify(Object.assign(JSON.parse(localStorage.getItem('cast:moi1')),{xp:30,_w:{i:'autre',h:[]}})))}")
        cible=pg.evaluate(f"()=>localStorage.getItem('cast:moi1:{typ}')")
        pg.evaluate("()=>{S.xp=60;S.sc.soixante=1;save()}")
        st=pg.evaluate(TOUT);j=[v for k,v in st.items() if ":jrnl:" in k]
        base=json.loads(cible).get("_w",{}).get("i")
        return cible,j,base
    # ======== 1. écran « Copies de sécurité » : restaurer :bak puis :bakJ
    for typ in ("bak","bakJ"):
        ctx,pg,err,dl=ouvrir();cible,j,base=preparer(pg,typ)
        ok_prep=json.loads(cible)["xp"]==50 and len(j)==1 and json.loads(j[0])["_w"]["h"][0]==base
        pg.evaluate("()=>cpScr()");pg.wait_for_timeout(700)
        i=pg.evaluate(f"()=>CPL.findIndex(c=>/:{typ}$/.test(c.k))")
        pg.locator("#cop .cpi").nth(i).get_by_text("Restaurer").click();pg.wait_for_timeout(1800)
        st=pg.evaluate(TOUT);ui=pg.evaluate("()=>({xp:S.xp,cinquante:!!S.sc.cinquante,soixante:!!S.sc.soixante,ecran:SCR})")
        garde=[k for k,v in st.items() if ":jrnl:" not in k and k!="cast:moi1" and SANSW(v)==SANSW(j[0])]
        ck(f"« Copies de sécurité » : restaurer :{typ} (point de départ du journal) → contenu exact (stockage = copie à l'octet près, interface 50 XP), pas de rejeu du journal (60 XP)",
           ok_prep and i>=0 and st["cast:moi1"]==cible and ui["xp"]==50 and ui["cinquante"] and not ui["soixante"] and not err,{"prep":ok_prep,"i":i,"ui":ui,"disque":json.loads(st["cast:moi1"])["xp"]})
        ck(f"« Copies de sécurité » ({typ}) : le journal (60 XP) reste récupérable comme copie durable ; plus aucun journal en attente de rejeu",
           len(garde)>=1 and not [k for k in st if ":jrnl:" in k] ,{"copies":garde,"cles":sorted(st)})
        # nouvelle reconnexion ordinaire : la restauration tient
        pg.reload();pg.wait_for_timeout(2200);x=pg.evaluate("()=>({xp:S.xp,disque:JSON.parse(localStorage.getItem('cast:moi1')).xp})")
        ck(f"« Copies de sécurité » ({typ}) : après rechargement, la version restaurée tient (50 XP)",x=={"xp":50,"disque":50},x)
        ctx.close()
    # ======== 2. écran B1 après corruption : restaurer :bak puis :bakJ
    for typ in ("bak","bakJ"):
        ctx,pg,err,dl=ouvrir();cible,j,base=preparer(pg,typ)
        pg.evaluate("()=>localStorage.setItem('cast:moi1','{corrompu')");pg.reload();pg.wait_for_timeout(2500)
        cps=pg.evaluate("async()=>(await pCopies('moi1')).map(c=>({k:c.k,raw:c.raw}))")
        i=next((n for n,c in enumerate(cps) if c["k"].endswith(":"+typ) and c["raw"]==cible),-1)
        if i>=0:pg.locator("#prec button").filter(has_text="Restaurer la copie du").nth(i).click();pg.wait_for_timeout(2000)
        st=pg.evaluate(TOUT);ui=pg.evaluate("()=>({xp:S.xp,cinquante:!!S.sc.cinquante,soixante:!!S.sc.soixante,lock:PLOCK&&PLOCK.c})")
        garde=[k for k,v in st.items() if ":jrnl:" not in k and k!="cast:moi1" and v==j[0]]
        kept=[v for k,v in st.items() if ":brut:corrompu:" in k]
        ck(f"écran B1 : restaurer :{typ} (point de départ du journal) → contenu exact (stockage = copie à l'octet près, interface 50 XP), illisible conservé",
           i>=0 and st["cast:moi1"]==cible and ui["xp"]==50 and ui["cinquante"] and not ui["soixante"] and ui["lock"] is None and kept==["{corrompu"] and not err,{"i":i,"ui":ui,"disque":st.get("cast:moi1","")[:40]})
        ck(f"écran B1 ({typ}) : le journal (60 XP, dernière progression) reste récupérable comme copie, à l'identique",len(garde)>=1 and not [k for k in st if ":jrnl:" in k],{"copies":garde,"cles":sorted(st)})
        ctx.close()
    # ======== 3. échec de mise à l'abri d'un journal : rien n'est retiré ni restauré
    ECHEC="()=>{const e0=SB.ecrireNeuf;SB.ecrireNeuf=async function(k,raw){if(k.includes(':brut:journal:'))return 'échec';return e0.call(this,k,raw)}}"
    for ecran in ("copies","B1"):
        ctx,pg,err,dl=ouvrir();cible,j,base=preparer(pg,"bak")
        # journal d'un autre onglet, différent de toute copie (sa mise à l'abri devra créer une copie, qui échouera)
        autre=json.dumps(dict(json.loads(j[0]),xp=70,sc={"hola":2,"cinquante":1,"autre":1}))
        pg.evaluate("(v)=>localStorage.setItem('cast:moi1:jrnl:autreonglet',v)",autre)
        if ecran=="B1":pg.evaluate("()=>localStorage.setItem('cast:moi1','{corrompu')");pg.reload();pg.wait_for_timeout(2500)
        avant=pg.evaluate(TOUT);pg.evaluate(ECHEC);dl.clear()
        if ecran=="copies":
            pg.evaluate("()=>cpScr()");pg.wait_for_timeout(700);i=pg.evaluate("()=>CPL.findIndex(c=>/:bak$/.test(c.k))")
            pg.locator("#cop .cpi").nth(i).get_by_text("Restaurer").click()
        else:
            cps=pg.evaluate("async()=>(await pCopies('moi1')).map(c=>c.k)");i=next(n for n,k in enumerate(cps) if k.endswith(":bak"))
            pg.locator("#prec button").filter(has_text="Restaurer la copie du").nth(i).click()
        pg.wait_for_timeout(1800);apres=pg.evaluate(TOUT)
        supprime=[k for k in avant if k not in apres];jr=[k for k in avant if ":jrnl:" in k]
        ui=pg.evaluate("()=>({xp:S.xp,lock:PLOCK&&PLOCK.c})")
        ck(f"échec de mise à l'abri d'un journal ({'écran des copies' if ecran=='copies' else 'écran B1'}) : restauration annulée et signalée, profil inchangé, aucune clé supprimée, journaux intacts",
           any("échou" in m or "mise à l'abri" in m for m in dl[1:]) and apres["cast:moi1"]==avant["cast:moi1"] and not supprime and all(apres.get(k)==avant[k] for k in jr) and len(jr)==2
           and (ui["xp"]==60 if ecran=="copies" else ui["lock"]=="corrompu") and not err,{"alertes":dl,"supprimé":supprime,"ui":ui})
        ctx.close()
    # ======== 4. hors restauration explicite : un journal réellement interrompu est toujours rejoué
    ctx,pg,err,dl=ouvrir();pg.evaluate("()=>{S.xp=50;save()}")
    m=pg.evaluate("()=>localStorage.getItem('cast:moi1')");mi=json.loads(m)["_w"]["i"]
    jv=json.dumps(dict(json.loads(m),xp=77,sc={"hola":2,"interrompu":1},_w={"i":"interrompu1","h":[mi]}))
    pg.evaluate("(v)=>localStorage.setItem('cast:moi1:jrnl:ongletinterrompu',v)",jv);pg.reload();pg.wait_for_timeout(2200)
    x=pg.evaluate("()=>({xp:S.xp,i:!!S.sc.interrompu,disque:localStorage.getItem('cast:moi1'),j:Object.keys(localStorage).filter(k=>k.includes(':jrnl:'))})")
    ck("hors restauration : journal interrompu prolongeant directement le profil → rejoué au démarrage (77 XP, profil = journal à l'octet près), journal retiré",
       x["xp"]==77 and x["i"] and x["disque"]==jv and x["j"]==[] and not err,{"xp":x["xp"],"j":x["j"]})
    ctx.close()
    # ======== 5. suppression des journaux : jamais une valeur réécrite entre la relecture et la suppression
    IDB="window.SOB_MOTEUR='idb'"
    def appli_idb():
        ctx=b.new_context(locale="fr-FR");ctx.add_init_script(IDB);pg=ctx.new_page();err=[];pg.on("pageerror",lambda e:err.append(str(e)[:200]));pg.on("dialog",lambda d:d.accept())
        pg.goto(BASE+PAGE);pg.wait_for_timeout(700)
        pg.evaluate("async(P)=>{localStorage.clear();await SB.ecrireBrut('acct:moi1','{\"h\":\"z\"}');await SB.ecrireBrut('cast:moi1',P);localStorage.setItem('cast_user','moi1')}",P(40))
        pg.reload();pg.wait_for_timeout(2200);pg.evaluate("()=>{S.xp=50;save()}");pg.wait_for_timeout(300);return ctx,pg,err
    for moteur in ("idb","localStorage"):
        ctx,pg,err=(appli_idb() if moteur=="idb" else ouvrir()[:3])
        r=pg.evaluate("""async()=>{await SB.ecrireBrut('cast:moi1:jrnl:x','A');const a=await SB.supprSi('cast:moi1:jrnl:x','B'),va=await SB.lire('cast:moi1:jrnl:x');
          const b2=await SB.supprSi('cast:moi1:jrnl:x','A'),vb=await SB.lire('cast:moi1:jrnl:x');return{a,va,b:b2,vb}}""")
        ck(f"supprSi ({moteur}) : valeur différente → « différent », rien supprimé ; valeur attendue → supprimée",r=={"a":"différent","va":"A","b":"ok","vb":None} and not err,r)
        ctx.close()
    # entrelacement forcé (IndexedDB) : un autre onglet réécrit le journal juste avant la suppression, dans chaque chemin de suppression
    J=lambda xp,mot,**w:json.dumps(dict(json.loads(P(xp)),sc={"hola":2,mot:1},**w))
    CAS={"jAbriTous":"async()=>jAbriTous('moi1')",
         "jRepr (journal déjà intégré)":"async()=>{const m=await SB.lire('cast:moi1'),w=JSON.parse(m)._w;await SB.ecrireBrut('cast:moi1:jrnl:autre',JSON.stringify(Object.assign(JSON.parse(m),{_w:{i:w.i,h:w.h}})));return jRepr('moi1',m)}",
         "jRepr (journal gardé en copie)":"async()=>{const m=await SB.lire('cast:moi1');return jRepr('moi1',m,1)}",
         "jRepr (journal rejoué)":"async()=>{const m=await SB.lire('cast:moi1'),w=JSON.parse(m)._w;await SB.ecrireBrut('cast:moi1:jrnl:autre',JSON.stringify(Object.assign(JSON.parse(m),{xp:66,_w:{i:'rejeu1',h:[w.i]}})));return jRepr('moi1',m)}"}
    for nom,js in CAS.items():
        ctx,pg,err=appli_idb()
        pg.evaluate("async(v)=>SB.ecrireBrut('cast:moi1:jrnl:autre',v)",J(61,"ancien"))
        pg.evaluate("""(v2)=>{const s0=SB.supprSi;let f=0;SB.supprSi=async function(k,att){if(k==='cast:moi1:jrnl:autre'&&!f){f=1;SBI.ecrireSync(k,v2);await new Promise(r=>setTimeout(r,50))}return s0.call(this,k,att)}}""",J(62,"nouveau"))
        pg.evaluate(js);pg.wait_for_timeout(200);v=pg.evaluate("async()=>SB.lire('cast:moi1:jrnl:autre')")
        ck(f"IndexedDB, {nom} : journal réécrit par un autre onglet juste avant la suppression → la nouvelle valeur n'est pas supprimée",
           v is not None and "nouveau" in json.loads(v)["sc"] and not err,{"reste":(v or "")[:80],"err":err})
        ctx.close()
    # concurrence réelle entre deux processus (IndexedDB) : A relit puis supprime en boucle, B réécrit en continu
    import asyncio,threading
    async def course():
        from playwright.async_api import async_playwright
        async with async_playwright() as ap:
            bb=await ap.chromium.launch();c=await bb.new_context();await c.add_init_script(IDB)
            x=await c.new_page();y=await c.new_page()
            for q in (x,y):await q.goto(BASE+PAGE)
            await x.wait_for_timeout(1500);bilan=[]
            for essai in range(5):
                await x.evaluate("async()=>SB.supprSi('cast:z:jrnl:c',await SB.lire('cast:z:jrnl:c'))");T=await x.evaluate("()=>Date.now()+300")
                A="""async(T)=>{while(Date.now()<T){}const ok=[];const t0=Date.now();while(Date.now()-t0<1500){const v=await SB.lire('cast:z:jrnl:c');if(v&&(await SB.supprSi('cast:z:jrnl:c',v))==='ok')ok.push(v)}return ok}"""
                Bj="""async(T)=>{while(Date.now()<T){}let i=0,der=null;const t0=Date.now();while(Date.now()-t0<1500){der='b'+(i++);await SB.ecrireBrut('cast:z:jrnl:c',der)}return der}"""
                ok,der=await asyncio.gather(x.evaluate(A,T),y.evaluate(Bj,T));await x.wait_for_timeout(200)
                fin=await x.evaluate("async()=>SB.lire('cast:z:jrnl:c')")
                bilan.append((fin==der) or (fin is None and der in ok))
            await bb.close();return bilan
    res=[];th=threading.Thread(target=lambda:res.append(asyncio.run(course())));th.start();th.join()
    ck(f"IndexedDB, deux processus réels (B réécrit en continu, A relit puis supprime) : la dernière valeur de B n'est jamais supprimée sans avoir été celle relue ({sum(res[0])}/5)",all(res[0]),res[0])
    b.close()
print(f"\n{sum(R)}/{len(R)} contrôles OK");sys.exit(0 if all(R) else 1)
