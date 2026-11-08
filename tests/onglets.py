# A1 : plusieurs onglets / fenêtres sur le même profil — aucune progression plus récente écrasée silencieusement.
# Usage : python3 tests/rangesrv.py 8772 .  puis  python3 tests/onglets.py [URL]   (URL par défaut http://localhost:8772/)
import sys,json
from playwright.sync_api import sync_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else "http://localhost:8772/"
R=[]
def ck(n,c,info=""):
    R.append(bool(c));print(("OK  " if c else "FAIL")+" "+n+("" if c else "  "+str(info)[:700]),flush=True)
P=json.dumps({"v":2,"xp":40,"streak":0,"last":"","sc":{"hola":2},"lvl":1,"lang":"es","PL":{},"bd":{},"nt":[],"t":1793000000000,"ob":1,"masSeen":1})
U="moi1";K="cast:"+U
# __freeze : l'onglet ne reçoit plus les événements « storage » (onglet suspendu) ; __stale : lecture périmée du profil (propagation entre processus)
# __fail : écritures refusées (motif) ; __rerr : lectures en erreur (motif)
INIT="""(()=>{const ae=window.addEventListener.bind(window);window.addEventListener=function(t,f,o){if(t==='storage'){return ae(t,e=>{if(!window.__freeze)f(e)},o)}return ae(t,f,o)};
  const g=Storage.prototype.getItem,s=Storage.prototype.setItem;
  Storage.prototype.getItem=function(k){k=String(k);if(window.__rerr&&window.__rerr.test(k))throw new DOMException('lecture','UnknownError');if(window.__stale&&k===window.__stale.k)return window.__stale.v;return g.call(this,k)};
  Storage.prototype.setItem=function(k,v){k=String(k);if(window.__fail&&window.__fail.test(k))throw new DOMException('plein','QuotaExceededError');return s.call(this,k,v)}})()"""
NOLOCKS="(()=>{try{Object.defineProperty(navigator,'locks',{value:undefined,configurable:true})}catch(e){}})()"
DISK=f"()=>JSON.parse(localStorage.getItem('{K}'))"
COPIES=f"()=>Object.keys(localStorage).filter(k=>k.startsWith('{K}:brut:conflit:')).map(k=>JSON.parse(localStorage.getItem(k)))"
ETAT="()=>({xp:S.xp,sc:Object.keys(S.sc||{}).sort(),streak:S.streak,ste:STE.profil,conf:STE.conf,ban:(document.getElementById('stb')||{dataset:{}}).dataset.k||null,pconf:!!PCONF,lock:PLOCK&&PLOCK.c})"
with sync_playwright() as p:
    b=p.chromium.launch()
    def deux(locks=True):
        ctx=b.new_context(locale="fr-FR");err=[]
        ctx.add_init_script(INIT)
        if not locks:ctx.add_init_script(NOLOCKS)
        a=ctx.new_page();a.on("pageerror",lambda e:err.append("A:"+str(e)[:150]))
        a.goto(BASE+"index.html");a.wait_for_timeout(700)
        a.evaluate("(P)=>{localStorage.clear();localStorage.setItem('cast_user','moi1');localStorage.setItem('acct:moi1','{\"h\":\"z\"}');localStorage.setItem('cast:moi1',P)}",P)
        a.reload();a.wait_for_timeout(2200)
        bb=ctx.new_page();bb.on("pageerror",lambda e:err.append("B:"+str(e)[:150]));bb.goto(BASE+"index.html");bb.wait_for_timeout(2200)
        return ctx,a,bb,err
    pause=lambda pg,ms=400:pg.wait_for_timeout(ms)
    # ======== 1. deux onglets ouverts avant modification
    ctx,a,bb,err=deux()
    a.evaluate("()=>{S.xp=140;S.sc.nuevo=3;save()}");pause(bb)
    eb=bb.evaluate(ETAT)
    ck("deux onglets : B (ouvert avant) reprend aussitôt la version écrite par A (140 XP, « nuevo »), sans bandeau ni copie",
       eb["xp"]==140 and "nuevo" in eb["sc"] and eb["ban"] is None and bb.evaluate(COPIES)==[] and not err,{"eb":eb,"err":err})
    bb.evaluate("()=>{S.streak=1;save()}");d=a.evaluate(DISK)
    ck("… B enregistre ensuite : le disque garde 140 XP et « nuevo » + la série de B (rien d'écrasé)",d["xp"]==140 and "nuevo" in d["sc"] and d["streak"]==1 and not err,d)
    ctx.close()
    # ======== 2. écritures successives alternées
    ctx,a,bb,err=deux()
    for i in range(4):
        pg=a if i%2==0 else bb;pg.evaluate("(i)=>{S.sc['mot'+i]=1;S.xp+=10;save()}",i);pause(a if pg is bb else bb,300)
    d=a.evaluate(DISK);ea=a.evaluate(ETAT);eb=bb.evaluate(ETAT)
    ck("écritures alternées A,B,A,B : les 4 mots et les 4 × 10 XP sont tous sur le disque, les deux onglets identiques, aucun conflit",
       all(f"mot{i}" in d["sc"] for i in range(4)) and d["xp"]==80 and ea["xp"]==eb["xp"]==80 and ea["ban"] is None and eb["ban"] is None and a.evaluate(COPIES)==[] and not err,{"d":d,"ea":ea,"eb":eb})
    ctx.close()
    # ======== 3. écritures quasi simultanées (B lit encore l'ancienne version : propagation entre processus)
    for locks in (True,False):
        ctx,a,bb,err=deux(locks)
        old=bb.evaluate(f"()=>localStorage.getItem('{K}')")
        bb.evaluate("()=>{window.__freeze=1}")
        a.evaluate("()=>{S.xp=150;S.sc.alfa=3;save()}")
        bb.evaluate("async(o)=>{window.__stale={k:'cast:moi1',v:o};S.streak=5;S.sc.beta=3;await save();window.__stale=null}",old)
        pause(a,600);ea=a.evaluate(ETAT);d=a.evaluate(DISK);cp=a.evaluate(COPIES)
        gard=any(c.get("xp")==150 and "alfa" in c["sc"] for c in cp)
        ck(f"quasi simultané ({'avec' if locks else 'sans'} navigator.locks) : la version de A écrasée par B est détectée par A, conservée dans une copie (150 XP, « alfa »), bandeau dans A",
           d["streak"]==5 and gard and ea["ban"]=="conf" and ea["streak"]==5 and not err,{"ea":ea,"d":d,"copies":cp,"err":err})
        bb.evaluate("()=>{window.__freeze=0}");ctx.close()
    # ======== 4. modification externe (autre version de l'appli, outil, autre fenêtre) d'une version qui ne descend pas de la nôtre
    ctx,a,bb,err=deux()
    a.evaluate("()=>{S.xp=60;S.sc.gamma=2;save()}");pause(bb)
    ext=json.loads(P);ext["xp"]=999;ext["t"]=1794000000000
    c=ctx.new_page();c.goto(BASE+"tests/rangesrv.py");c.evaluate("(x)=>localStorage.setItem('cast:moi1',x)",json.dumps(ext));pause(a,600);pause(bb,200)
    ea=a.evaluate(ETAT);cp=a.evaluate(COPIES)
    ck("modification externe ne contenant pas la dernière écriture de A : A conserve sa version (60 XP, « gamma ») en copie, reprend la version externe, bandeau",
       ea["xp"]==999 and any(c.get("xp")==60 and "gamma" in c["sc"] for c in cp) and ea["ban"]=="conf" and not err,{"ea":ea,"copies":cp})
    eb=bb.evaluate(ETAT)
    ck("… l'onglet B, qui n'avait rien écrit, reprend la version externe silencieusement",eb["xp"]==999 and eb["ban"] is None,eb)
    ctx.close()
    # ======== 5. onglet suspendu puis réactivé
    ctx,a,bb,err=deux()
    bb.evaluate("()=>{window.__freeze=1}")
    for i in range(3):a.evaluate("(i)=>{S.sc['susp'+i]=1;S.xp+=5;save()}",i)
    eb0=bb.evaluate(ETAT)
    bb.evaluate("()=>{window.__freeze=0;document.dispatchEvent(new Event('visibilitychange'))}");pause(bb,300);eb=bb.evaluate(ETAT)
    ck("onglet suspendu (3 écritures manquées) puis réactivé : reprise silencieuse de la version récente (55 XP, 3 mots), sans copie",
       eb0["xp"]==40 and eb["xp"]==55 and all(f"susp{i}" in eb["sc"] for i in range(3)) and eb["ban"] is None and a.evaluate(COPIES)==[] and not err,{"eb0":eb0,"eb":eb})
    ctx.close()
    ctx,a,bb,err=deux()
    bb.evaluate("()=>{window.__freeze=1}")
    for i in range(3):a.evaluate("(i)=>{S.sc['susp'+i]=1;S.xp+=5;save()}",i)
    bb.evaluate("()=>{S.sc.delta=1;S.xp+=7;save()}");pause(bb,300);eb=bb.evaluate(ETAT);d=a.evaluate(DISK);cp=a.evaluate(COPIES)
    ck("onglet suspendu qui enregistre sans avoir été réveillé : n'écrase pas (disque = 55 XP de A), sa modification (« delta ») est conservée en copie, bandeau",
       d["xp"]==55 and "delta" not in d["sc"] and any("delta" in c["sc"] for c in cp) and eb["xp"]==55 and eb["ban"]=="conf" and not err,{"d":d,"eb":eb,"copies":cp})
    ctx.close()
    # ======== 6. pendant une leçon : la reprise ne casse pas l'exercice en cours
    ctx,a,bb,err=deux()
    bb.bring_to_front();bb.evaluate("()=>{start('Mélange')}");bb.wait_for_function("()=>typeof R!=='undefined'&&R&&R.q",timeout=10000);q0=bb.evaluate("()=>{R.q.__marque='q0';return R.q.ty}")
    a.evaluate("()=>{S.xp=200;save()}");pause(bb,400)
    q1=bb.evaluate("()=>R&&R.q&&R.q.__marque==='q0'&&!R.done?R.q.ty:null");eb=bb.evaluate(ETAT)
    ck("reprise pendant une leçon : exercice en cours inchangé, progression à jour (200 XP), aucune erreur",q0 and q0==q1 and eb["xp"]==200 and not err,{"q0":q0,"q1":q1,"eb":eb,"err":err})
    ctx.close()
    # ======== 7. stockage défaillant
    ctx,a,bb,err=deux()
    a.evaluate("()=>{S.xp=70;save()}");pause(bb)
    bb.evaluate("async()=>{window.__rerr=/^cast:moi1$/;S.xp=1;await save();window.__rerr=null}");eb=bb.evaluate(ETAT);d=a.evaluate(DISK)
    ck("lecture impossible au moment d'écrire : aucune écriture (disque = 70 XP de A), échec signalé",d["xp"]==70 and eb["ste"]=="échec" and eb["ban"]=="échec" and not err,{"eb":eb,"d":d})
    ctx.close()
    ctx,a,bb,err=deux()
    bb.evaluate("()=>{window.__freeze=1;window.__fail=/:brut:/}")
    a.evaluate("()=>{S.xp=80;S.sc.uno=1;save()}")
    bb.evaluate("()=>{S.sc.dos=1;save()}");eb=bb.evaluate(ETAT);d1=a.evaluate(DISK)
    bb.evaluate("()=>{S.xp=5;save();save()}");d2=a.evaluate(DISK)
    ck("conflit dont la copie ne peut pas être écrite : l'onglet n'écrit plus rien, ne reprend rien, bandeau « n'enregistre plus » ; la version de A reste intacte",
       eb["pconf"] and eb["ste"]=="conflit" and eb["ban"]=="conflit" and d1["xp"]==80 and "uno" in d1["sc"] and d2==d1 and not err,{"eb":eb,"d1":d1,"d2":d2})
    ctx.close()
    # ======== 8. profil supprimé / rendu illisible dans une autre fenêtre : écrans B1/B4, version locale mise à l'abri
    ctx,a,bb,err=deux()
    a.evaluate("()=>{S.xp=90;save()}");pause(bb)
    a.evaluate("()=>localStorage.setItem('cast:moi1','{corrompu')");pause(bb,500);eb=bb.evaluate(ETAT)
    ck("profil rendu illisible ailleurs : l'onglet passe à l'écran de récupération B1, ne réécrit rien",eb["lock"]=="corrompu" and a.evaluate(f"()=>localStorage.getItem('{K}')")=="{corrompu" and not err,eb)
    ctx.close()
    # ======== 9. la copie de conflit est proposée par les écrans de récupération
    ctx,a,bb,err=deux()
    bb.evaluate("()=>{window.__freeze=1}");a.evaluate("()=>{S.xp=33;save()}");bb.evaluate("()=>{S.sc.copia=1;save()}")
    n=bb.evaluate("async()=>(await pCopies('moi1')).filter(c=>c.k.includes(':brut:conflit:')&&c.o.sc&&c.o.sc.copia).length")
    ck("la copie de conflit est une sauvegarde valide, proposée à la restauration (pCopies)",n==1,n)
    ctx.close()
    # ======== 10. un seul onglet : comportement inchangé
    ctx=b.new_context(locale="fr-FR");pg=ctx.new_page();err=[];pg.on("pageerror",lambda e:err.append(str(e)[:150]))
    pg.goto(BASE+"index.html");pg.wait_for_timeout(700)
    pg.evaluate("(P)=>{localStorage.clear();localStorage.setItem('cast_user','moi1');localStorage.setItem('acct:moi1','{\"h\":\"z\"}');localStorage.setItem('cast:moi1',P)}",P)
    pg.reload();pg.wait_for_timeout(2200)
    for i in range(5):pg.evaluate("(i)=>{S.xp+=1;save()}",i)
    d=pg.evaluate(DISK);e=pg.evaluate(ETAT)
    ck("un seul onglet : enregistrements normaux (45 XP), filiation _w posée, aucun bandeau, aucune copie",
       d["xp"]==45 and d.get("_w",{}).get("i") and len(d["_w"]["h"])==4 and e["ban"] is None and pg.evaluate(COPIES)==[] and not err,{"d":d.get("_w"),"e":e,"err":err})
    ctx.close()
    b.close()
print(f"\n{sum(R)}/{len(R)} contrôles OK");sys.exit(0 if all(R) else 1)
