# L1 (correction de sbq) : écriture immédiate quand la file est vide, ordre FIFO sinon, aucune écriture sous le mauvais utilisateur.
# Usage : python3 tests/rangesrv.py 8772 .  puis  python3 tests/ecriture.py [URL]   (URL par défaut http://localhost:8772/)
import sys,json,os,signal,time,asyncio
from playwright.sync_api import sync_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else "http://localhost:8772/"
R=[]
def ck(n,c,info=""):
    R.append(bool(c));print(("OK  " if c else "FAIL")+" "+n+("" if c else "  "+str(info)[:600]),flush=True)
P=lambda xp:json.dumps({"v":2,"xp":xp,"streak":0,"last":"","sc":{"hola":2},"lvl":1,"lang":"es","PL":{},"bd":{},"nt":[],"t":1793000000000,"ob":1,"masSeen":1})
SET="([a,b])=>{localStorage.clear();localStorage.setItem('cast_user','moi1');for(const u of ['moi1','moi2'])localStorage.setItem('acct:'+u,'{\"h\":\"z\"}');localStorage.setItem('cast:moi1',a);localStorage.setItem('cast:moi2',b)}"
XP="(u)=>{const r=localStorage.getItem('cast:'+u);return r?JSON.parse(r).xp:null}"
NEUTRE=BASE+"manifest.webmanifest"   # document de la même origine, sans l'appli
with sync_playwright() as p:
    b=p.chromium.launch();cdp=b.new_browser_cdp_session()
    rend=lambda:{x["id"] for x in cdp.send("SystemInfo.getProcessInfo")["processInfo"] if x["type"]=="renderer"}
    def page():
        ctx=b.new_context(locale="fr-FR");pg=ctx.new_page();err=[];pg.on("pageerror",lambda e:err.append(str(e)[:150]))
        pg.goto(BASE+"index.html");pg.wait_for_timeout(600);pg.evaluate(SET,[P(40),P(70)]);pg.reload();pg.wait_for_timeout(2000);return ctx,pg,err
    # ---- 1. arrêt brutal juste après save() (processus de l'onglet tué pendant le calcul qui suit, dans la même tâche)
    for essai in range(3):
        ctx,pg,err=page();avant=rend();q=ctx.new_page();q.goto(NEUTRE);q.wait_for_timeout(300);appli=[x for x in rend() if x not in (rend()-avant)]
        pg.evaluate("()=>{setTimeout(()=>{S.xp=555;save();const t=Date.now();while(Date.now()-t<1500){}},50)}");time.sleep(0.7)
        for pid in appli:
            try:os.kill(pid,signal.SIGKILL)
            except Exception:pass
        time.sleep(0.8);v=q.evaluate(XP,"moi1")
        ck(f"arrêt brutal juste après save() (essai {essai+1}) : l'écriture est sur le disque (555), comme avant L1",v==555,v)
        ctx.close()
    # ---- 2. lecture dans le même bloc
    ctx,pg,err=page()
    r=pg.evaluate("()=>{S.xp=101;save();return JSON.parse(localStorage.getItem('cast:moi1')).xp}")
    ck("save() puis lecture dans le même bloc : nouvelle valeur (101), comme avant L1",r==101,r)
    r=pg.evaluate("()=>{S.xp=102;const p=save();return{type:typeof p.then,sync:SB.sync,file:SBN}}")
    ck("save() renvoie toujours une promesse ; file vide après l'écriture immédiate",r["type"]=="function" and r["sync"] is True and r["file"]==0,r)
    ctx.close()
    # ---- 3. ordre FIFO quand une tâche est déjà en attente
    ctx,pg,err=page()
    r=pg.evaluate("""async()=>{const log=[];const e0=SBS.ecrire,l0=SBS.lire;SBS.ecrire=function(k,v){log.push('écrit '+k+' xp='+JSON.parse(v).xp);return e0.apply(this,arguments)};
      const ps=window.pSyncRun;window.pSyncRun=async function(){log.push('reprise A1');return ps.apply(this,arguments)};
      pSync(0);const enAttente=SBN;S.xp=301;save();log.push('après save() : disque xp='+JSON.parse(localStorage.getItem('cast:moi1')).xp);S.xp=302;save();
      await SBQ;await new Promise(r=>setTimeout(r,0));SBS.ecrire=e0;window.pSyncRun=ps;return{enAttente,log,fin:JSON.parse(localStorage.getItem('cast:moi1')).xp,file:SBN}}""")
    i=lambda s:next((k for k,x in enumerate(r["log"]) if s in x),99)
    ecr=[k for k,x in enumerate(r["log"]) if x.startswith("écrit")]
    ck("file non vide (reprise A1 en attente) : rien n'est écrit avant la reprise, les 2 écritures suivent dans l'ordre et enregistrent l'état le plus récent (302)",
       r["enAttente"]==1 and "xp=40" in r["log"][0] and len(ecr)==2 and all(k>i("reprise A1") for k in ecr) and all("xp=302" in r["log"][k] for k in ecr) and r["fin"]==302 and r["file"]==0 and not err,r)
    ctx.close()
    # ---- 4. écritures successives (même bloc) et données conservées
    ctx,pg,err=page()
    r=pg.evaluate("""()=>{const vus=[];for(let i=1;i<=50;i++){S.sc['m'+i]=1;S.xp=40+i;save();vus.push(JSON.parse(localStorage.getItem('cast:moi1')).xp)}const d=JSON.parse(localStorage.getItem('cast:moi1'));
      return{monotone:vus.every((v,k)=>v===41+k),xp:d.xp,mots:Object.keys(d.sc).length,h:d._w.h.length,ste:STE.profil}}""")
    ck("50 enregistrements successifs : chacun écrit aussitôt, dans l'ordre, filiation A1 posée, aucun échec",r["monotone"] and r["xp"]==90 and r["mots"]==51 and r["h"]==30 and r["ste"]=="ok" and not err,r)
    ctx.close()
    # ---- 5. changement d'utilisateur
    for cas,js,att in [("save() puis logout()","()=>{S.xp=111;save();logout()}",{"moi1":111,"moi2":70,"U":None}),
                       ("save() puis loginL('moi2')","()=>{S.xp=222;save();loginL('moi2')}",{"moi1":222,"moi2":70,"U":"moi2"})]:
        ctx,pg,err=page();pg.evaluate(js);pg.wait_for_timeout(400)
        d={"moi1":pg.evaluate(XP,"moi1"),"moi2":pg.evaluate(XP,"moi2"),"U":pg.evaluate("()=>U")}
        ck(f"{cas} : écrit sous le bon utilisateur, l'autre profil intact",d==att and not err,d)
        ctx.close()
    ctx,pg,err=page()
    r=pg.evaluate("()=>{loginL('moi2');S.xp=333;const p=save();return{file:SBN,disque1:JSON.parse(localStorage.getItem('cast:moi1')).xp}}");pg.wait_for_timeout(400)
    d={"moi1":pg.evaluate(XP,"moi1"),"moi2":pg.evaluate(XP,"moi2")}
    ck("save() appelé pendant qu'une connexion attend : mis en file (pas d'écriture immédiate), jamais écrit dans l'ancien profil",r["file"]>=2 and r["disque1"]==40 and d["moi1"]==40 and d["moi2"]==70,{"r":r,"d":d})
    ctx.close()
    # ---- 6. pagehide : fermeture d'onglet et navigation
    for mode in ("fermeture d'onglet","navigation"):
        ctx,pg,err=page();pg.evaluate("()=>addEventListener('pagehide',()=>{S.xp=777;save()})")
        if mode.startswith("fermeture"):pg.close(run_before_unload=True)
        else:pg.goto(NEUTRE)
        q=ctx.new_page();q.goto(NEUTRE);time.sleep(0.3);v=q.evaluate(XP,"moi1")
        ck(f"save() dans pagehide ({mode}) : écrit (777)",v==777,v);ctx.close()
    b.close()
# ---- 7. rafale réellement concurrente entre deux onglets (deux processus) : aucun mot perdu sans trace (API asynchrone, hors du bloc précédent)
async def rafale():
    from playwright.async_api import async_playwright
    async with async_playwright() as ap:
        bb=await ap.chromium.launch();c=await bb.new_context();x=await c.new_page();await x.goto(BASE+"index.html");await x.wait_for_timeout(600)
        await x.evaluate(SET,[P(40),P(70)]);await x.reload();await x.wait_for_timeout(2000);y=await c.new_page();await y.goto(BASE+"index.html");await y.wait_for_timeout(2000)
        T=await x.evaluate("()=>Date.now()+600")
        JS="""async([t,n,T])=>{while(Date.now()<T){}const e=[];for(let i=0;i<n;i++){const w=t+i;S.sc[w]=1;save();e.push(w);await new Promise(r=>setTimeout(r,Math.random()*2))}return e}"""
        ea,eb=await asyncio.gather(x.evaluate(JS,["a",60,T]),y.evaluate(JS,["b",60,T]));await x.wait_for_timeout(1200)
        st=await x.evaluate("()=>{const o={};for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);o[k]=localStorage.getItem(k)}return o}")
        await bb.close()
        tout=set()
        for k,v in st.items():
            if k=="cast:moi1" or ":brut:conflit:" in k:
                try:tout|=set(json.loads(v)["sc"])
                except Exception:pass
        return set(ea)|set(eb),tout
ecrits,tout=asyncio.run(rafale())
perdus=sorted(ecrits-tout)
ck(f"rafale concurrente réelle (2 onglets × 60 enregistrements) : aucun mot perdu sans trace (profil ou copie de conflit)",not perdus,perdus[:10])
print(f"\n{sum(R)}/{len(R)} contrôles OK");sys.exit(0 if all(R) else 1)
