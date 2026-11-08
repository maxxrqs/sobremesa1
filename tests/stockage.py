# B4 : écritures relues et signalées, persistance du stockage, récupération quand le profil principal a disparu mais que des sauvegardes existent.
# Usage : python3 tests/rangesrv.py 8772 .  puis  python3 tests/stockage.py [URL]   (URL par défaut http://localhost:8772/)
import sys,json
from playwright.sync_api import sync_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else "http://localhost:8772/"
R=[]
def ck(n,c,info=""):
    R.append(bool(c));print(("OK  " if c else "FAIL")+" "+n+("" if c else "  "+str(info)[:700]),flush=True)
P=lambda **k:json.dumps(dict({"v":2,"xp":40,"streak":0,"last":"","sc":{"hola":2},"lvl":1,"lang":"es","PL":{},"bd":{},"nt":[],"t":1793000000000},**k))
ACT=P();BAK=P(xp=88,t=1793600000000);BAKJ=P(xp=61,t=1793300000000)
U="moi1";K=lambda s="":"cast:"+U+(":"+s if s else "")
BASEST={"cast_user":U,"acct:"+U:json.dumps({"salt":"0","a":"p","h":"z"})}
DUMP="()=>{const o={};for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);try{o[k]=localStorage.getItem(k)}catch(e){o[k]='?'}}return o}"
# pannes pilotables depuis le test : window.__fail (écriture refusée), window.__trunc (écriture tronquée), window.__all (tout refuser)
PANNES="""(()=>{const f=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){k=String(k);
  if(window.__all&&k!=='_t')throw new DOMException('plein','QuotaExceededError');
  if(window.__fail&&window.__fail.test(k))throw new DOMException('plein','QuotaExceededError');
  if(window.__trunc&&window.__trunc.test(k)&&(!window.__truncV||String(v).includes(window.__truncV)))return f.call(this,k,String(v).slice(0,40));
  return f.call(this,k,v)}})()"""
ETAT="""()=>({ste:{p:STE.profil,b:STE.bak},ban:document.querySelectorAll('#stb').length,bk:(document.getElementById('stb')||{dataset:{}}).dataset.k||null,
  txt:(document.getElementById('stb')||{}).innerText||'',lock:PLOCK&&PLOCK.c,rec:!!document.getElementById('prec'),xp:S.xp,U})"""
def valides(pg,d):
    return {v for v in d.values() if pg.evaluate("(v)=>['actuel','ancien'].includes(classProfil(v).c)",v)}
with sync_playwright() as p:
    b=p.chromium.launch()
    def page(store,init=PANNES,pre=None):
        ctx=b.new_context(locale="fr-FR",accept_downloads=True);pg=ctx.new_page();err=[];pg.on("pageerror",lambda e:err.append(str(e)[:200]))
        pg.goto(BASE+"index.html");pg.wait_for_timeout(900)
        pg.evaluate("(d)=>{localStorage.clear();for(const k in d)localStorage.setItem(k,d[k])}",store)
        if pre:pg.add_init_script(pre)
        if init:pg.add_init_script(init)
        pg.reload();pg.wait_for_timeout(2300);return ctx,pg,err
    # ======== 1. écriture du profil principal refusée
    ctx,pg,err=page(dict(BASEST,**{K():ACT}))
    e0=pg.evaluate(ETAT)
    pg.evaluate(f"()=>{{window.__fail=/^cast:{U}$/;S.xp=55;save()}}");e1=pg.evaluate(ETAT);d1=pg.evaluate(DUMP)
    ck("profil : écriture refusée → bandeau « non enregistrée », valeur précédente intacte sur l'appareil, progression gardée en mémoire (55 XP)",
       e0["ste"]=={"p":"ok","b":"ok"} and e0["ban"]==0 and e1["ste"]["p"]=="échec" and e1["ban"]==1 and e1["bk"]=="échec" and "pas pu être enregistrée" in e1["txt"] and d1[K()]==ACT and e1["xp"]==55 and not err,{"e0":e0,"e1":e1,"err":err})
    pg.evaluate("()=>{S.xp=56;save();save()}");e2=pg.evaluate(ETAT)
    ck("échecs suivants : un seul bandeau, pas de répétition",e2["ban"]==1,e2)
    mn=pg.evaluate("()=>{try{menu()}catch(e){}const m=document.getElementById('mn');const t=m?m.innerText:'';if(m)m.remove();return t}")
    ck("menu : « non enregistrée sur cet appareil », jamais « sauvegardée »","non enregistrée" in mn and "sauvegardée sur cet appareil" not in mn,mn[:300])
    pg.get_by_text("Plus tard").click();pg.wait_for_timeout(200);pg.evaluate("()=>{S.xp=57;save()}");e3=pg.evaluate(ETAT)
    ck("« Plus tard » : bandeau fermé et non réaffiché pour le même incident (état toujours en échec)",e3["ban"]==0 and e3["ste"]["p"]=="échec",e3)
    pg.evaluate("()=>{window.__fail=null;S.xp=58;save()}");e4=pg.evaluate(ETAT);m4=json.loads(pg.evaluate(f"()=>localStorage.getItem('{K()}')"))
    ck("écriture de nouveau possible : enregistrée (58 XP), état « ok », pas de bandeau",e4["ste"]["p"]=="ok" and e4["ban"]==0 and m4["xp"]==58,{"e4":e4,"xp":m4.get("xp")})
    pg.evaluate(f"()=>{{window.__fail=/^cast:{U}$/;S.xp=59;save()}}");e5=pg.evaluate(ETAT)
    ck("nouvel incident après un retour à la normale : bandeau de nouveau affiché",e5["ban"]==1 and e5["bk"]=="échec",e5)
    with pg.expect_download() as dl:pg.get_by_text("Télécharger mes données").first.click()
    ck("bandeau : « Télécharger mes données » fournit la copie",dl.value.suggested_filename.startswith("sobremesa-"),dl.value.suggested_filename)
    ctx.close()
    # ======== 2. échec de relecture (écriture tronquée) du profil principal
    ctx,pg,err=page(dict(BASEST,**{K():ACT}))
    pg.evaluate(f"()=>{{window.__truncV='\"xp\":70';window.__trunc=/^cast:{U}$/;S.xp=70;save()}}");e=pg.evaluate(ETAT);d=pg.evaluate(DUMP)
    ck("profil : écriture tronquée (relue différente) → ancienne valeur remise à l'identique, échec signalé",d[K()]==ACT and e["ste"]["p"]=="échec" and e["ban"]==1 and not err,{"e":e,"main":d[K()][:80]})
    ctx.close()
    # panne permanente : même la remise de l'ancienne valeur est tronquée → au rechargement, B1 détecte le profil illisible et propose :bak (copie de l'ouverture)
    ctx,pg,err=page(dict(BASEST,**{K():ACT}))
    pg.evaluate(f"()=>{{window.__trunc=/^cast:{U}$/;S.xp=71;save()}}");e=pg.evaluate(ETAT);pg.reload();pg.wait_for_timeout(2300)
    e2=pg.evaluate(ETAT);t=pg.evaluate("()=>(document.getElementById('prec')||{}).innerText||''")
    ck("panne d'écriture permanente : échec signalé ; au rechargement, profil illisible → écran de récupération proposant la sauvegarde de l'ouverture (40 XP)",
       e["ste"]["p"]=="échec" and e["ban"]==1 and e2["lock"]=="corrompu" and "40 XP" in t and pg.evaluate(f"()=>localStorage.getItem('{K('bak')}')")==ACT,{"e":e,"e2":e2,"t":t})
    ctx.close()
    # ======== 3. échec d'une sauvegarde automatique seule (B2), profil bien enregistré
    ctx,pg,err=page(dict(BASEST,**{K():ACT,K("bak"):BAK,K("bakJ"):BAKJ,K("bakJ:jour"):"2026-11-01"}),pre="window.__fail=/:bak/")
    e=pg.evaluate(ETAT);d=pg.evaluate(DUMP)
    ck("sauvegarde auto impossible : avis discret (« sauvegarde automatique »), profil chargé, anciennes sauvegardes intactes",
       e["ste"]=={"p":"ok","b":"échec"} and e["ban"]==1 and e["bk"]=="bak" and "sauvegarde automatique" in e["txt"] and "bien enregistrée" in e["txt"] and d[K("bak")]==BAK and d[K("bakJ")]==BAKJ and e["lock"] is None and not err,{"e":e})
    pg.get_by_text("OK",exact=True).click();pg.wait_for_timeout(200);pg.evaluate("()=>{S.xp=41;save()}");e2=pg.evaluate(ETAT)
    ck("avis de sauvegarde auto fermé : non réaffiché, la progression continue d'être enregistrée",e2["ban"]==0 and e2["ste"]["p"]=="ok" and json.loads(pg.evaluate(f"()=>localStorage.getItem('{K()}')"))["xp"]==41,e2)
    ctx.close()
    # ======== 4. stockage plein (toutes les écritures refusées), lecture possible
    st=dict(BASEST,**{K():ACT,K("bak"):BAK,K("bakJ"):BAKJ,K("bakJ:jour"):"2026-11-01"})
    ctx,pg,err=page(st,pre="window.__all=1");e=pg.evaluate(ETAT);pg.evaluate("()=>{S.xp=77;save()}");e2=pg.evaluate(ETAT);d=pg.evaluate(DUMP)
    ck("stockage plein : profil chargé ; bandeau du profil prioritaire sur l'avis de sauvegarde ; aucune donnée modifiée",
       e["ste"]["b"]=="échec" and e2["ste"]["p"]=="échec" and e2["ban"]==1 and e2["bk"]=="échec" and all(d.get(k)==v for k,v in st.items()) and not err,{"e":e,"e2":e2,"err":err})
    ctx.close()
    # ======== 5. stockage indisponible (navigation privée stricte : localStorage inutilisable)
    BLOQUE="(()=>{Storage.prototype.setItem=function(){throw new DOMException('refusé','SecurityError')}})()"
    ctx,pg,err=page({},init=BLOQUE)
    e=pg.evaluate("async()=>{const o={ok:ST.ok};U='moi1';S.xp=5;save();o.pp=await pPut('cast:moi1:bak','{}');return o}");e2=pg.evaluate(ETAT)
    ck("stockage indisponible : « gardée tant que l'appli reste ouverte », jamais « enregistrée » ; une sauvegarde en mémoire compte comme un échec",
       e["ok"] is False and e2["ste"]["p"]=="mémoire" and e2["ban"]==1 and "indisponible" in e2["txt"] and e["pp"]=="échec" and not err,{"e":e,"e2":e2,"err":err})
    ctx.close()
    # ======== 6. persistance du stockage (navigator.storage.persist), appel existant inchangé
    def pers(mock):
        init="(()=>{window.__pc=0;window.__pd=0;const m=%s;try{Object.defineProperty(navigator,'storage',{value:m,configurable:true})}catch(e){}})()"%mock
        ctx,pg,err=page(dict(BASEST,**{K():ACT}),init=init);pg.evaluate("()=>{S.xp=42;save()}");pg.wait_for_timeout(200)
        o=pg.evaluate("()=>({pc:window.__pc,pd:window.__pd,ok:STE.profil,ban:document.querySelectorAll('#stb').length,U,home:!document.getElementById('prec')})");ctx.close();return o,err
    cas={"accordée":"{persisted:()=>{__pd++;return Promise.resolve(false)},persist:()=>{__pc++;return Promise.resolve(true)}}",
         "refusée":"{persisted:()=>{__pd++;return Promise.resolve(false)},persist:()=>{__pc++;return Promise.resolve(false)}}",
         "déjà accordée":"{persisted:()=>{__pd++;return Promise.resolve(true)},persist:()=>{__pc++;return Promise.resolve(true)}}",
         "persisted() en erreur":"{persisted:()=>{__pd++;return Promise.reject(new Error('x'))},persist:()=>{__pc++;return Promise.resolve(true)}}",
         "persist() lève":"{persisted:()=>{__pd++;return Promise.resolve(false)},persist:()=>{__pc++;throw new Error('x')}}",
         "API absente (storage sans persist)":"{}","navigator.storage absent":"undefined"}
    att={"accordée":(1,1),"refusée":(1,1),"déjà accordée":(1,0),"persisted() en erreur":(1,0),"persist() lève":(1,1),"API absente (storage sans persist)":(0,0),"navigator.storage absent":(0,0)}
    res={}
    for n,m in cas.items():
        o,err=pers(m);res[n]=(o,err)
    ck("persistance : demandée une seule fois si besoin, jamais en double ; refus, erreur ou absence sans effet sur l'appli (profil enregistré, aucun bandeau, aucune erreur)",
       all((o["pd"],o["pc"])==att[n] and o["ok"]=="ok" and o["ban"]==0 and o["U"]==U and o["home"] and not er for n,(o,er) in res.items()),res)
    # ======== 7-10. profil principal absent
    def absent(extra):
        st=dict(BASEST,**extra);ctx,pg,err=page(st);d=pg.evaluate(DUMP);e=pg.evaluate(ETAT)
        txt=pg.evaluate("()=>(document.getElementById('prec')||{}).innerText||''");return st,ctx,pg,err,d,e,txt
    for nom,extra,xps in [(":bak valide",{K("bak"):BAK},["88 XP"]),(":bakJ valide",{K("bakJ"):BAKJ,K("bakJ:jour"):"2026-11-01"},["61 XP"]),
                         ("les deux sauvegardes",{K("bak"):BAK,K("bakJ"):BAKJ,K("bakJ:jour"):"2026-11-01"},["88 XP","61 XP"])]:
        st,ctx,pg,err,d,e,txt=absent(extra)
        after=pg.evaluate("()=>{try{S.xp=999;save();lsw()}catch(e){}return localStorage.getItem('cast:moi1')}")
        ordre=all(x in txt for x in xps) and (len(xps)<2 or txt.index(xps[0])<txt.index(xps[1]))
        ck(f"profil absent, {nom} : écran de récupération (« introuvable »), {len(xps)} copie(s) proposée(s), la plus récente d'abord ; rien écrit, même en tentant d'enregistrer",
           e["lock"]=="absent" and e["rec"] and "introuvable" in txt and txt.count("Restaurer la copie du")==len(xps) and ordre and d==st and after is None and pg.evaluate(DUMP)==st and not err,{"e":e,"txt":txt,"err":err})
        ctx.close()
    st,ctx,pg,err,d,e,txt=absent({K("brut:corrompu:1793000000000"):"{corrompu"})
    ck("profil absent, seulement une copie brute corrompue : jamais proposée ; nouveau profil normal, copie brute intacte",
       e["lock"] is None and not e["rec"] and e["xp"]==0 and d[K("brut:corrompu:1793000000000")]=="{corrompu" and not err,{"e":e})
    ctx.close()
    # ======== 11. restauration
    TROIS={K("bak"):BAK,K("bakJ"):BAKJ,K("bakJ:jour"):"2026-11-01"}
    st,ctx,pg,err,d,e,txt=absent(TROIS);v0=valides(pg,d)
    pg.on("dialog",lambda x:x.dismiss());pg.get_by_text("Restaurer la copie du").nth(1).click();pg.wait_for_timeout(800)
    ck("restauration annulée : rien ne change, toujours sur l'écran de récupération",pg.evaluate(DUMP)==st and pg.evaluate(ETAT)["lock"]=="absent",pg.evaluate(ETAT))
    ctx.close()
    st,ctx,pg,err,d,e,txt=absent(TROIS);v0=valides(pg,d);msgs=[]
    pg.on("dialog",lambda x:(msgs.append(x.message),x.accept()));pg.get_by_text("Restaurer la copie du").nth(1).click();pg.wait_for_timeout(1500)
    e2=pg.evaluate(ETAT);d2=pg.evaluate(DUMP);v2=set(d2.values())
    ck("restauration de la copie la plus ancienne (:bakJ, 61 XP) : profil restauré à l'identique, la copie plus récente (:bak, 88 XP) mise à l'abri, aucune donnée valide perdue",
       e2["lock"] is None and e2["xp"]==61 and d2[K()]==BAKJ and BAK in v2 and v0<=v2 and any(k.startswith(K("brut:avant-bak:")) and d2[k]==BAK for k in d2) and "autres sauvegardes restent conservées" in " ".join(msgs) and not err,
       {"e2":e2,"cles":sorted(d2),"msgs":msgs,"err":err})
    pg.evaluate("()=>localStorage.removeItem('cast:moi1')");pg.reload();pg.wait_for_timeout(2300)
    t3=pg.evaluate("()=>(document.getElementById('prec')||{}).innerText||''")
    ck("… la copie mise à l'abri est de nouveau proposée si le profil disparaît encore","88 XP" in t3 and "61 XP" in t3,t3)
    ctx.close()
    # ======== 12. remise à zéro (annulation puis confirmation)
    st,ctx,pg,err,d,e,txt=absent(TROIS);v0=valides(pg,d)
    pg.get_by_text("Repartir de zéro…").click();pg.wait_for_timeout(300);pg.get_by_text("Annuler").click();pg.wait_for_timeout(300)
    ck("remise à zéro annulée : rien ne change",pg.evaluate(DUMP)==st and pg.evaluate(ETAT)["lock"]=="absent")
    pg.get_by_text("Repartir de zéro…").click();pg.wait_for_timeout(300);t=pg.evaluate("()=>document.getElementById('prec').innerText")
    pg.get_by_text("Oui, repartir de zéro").click();pg.wait_for_timeout(1500);e2=pg.evaluate(ETAT);d2=pg.evaluate(DUMP)
    ck("remise à zéro confirmée : profil neuf (0 XP) ; :bak et :bakJ (88 et 61 XP) conservées dans des copies durables, aucune donnée valide perdue",
       "sauvegardes restent conservées" in t and e2["lock"] is None and e2["xp"]==0 and json.loads(d2[K()])["xp"]==0 and v0<=set(d2.values())
       and sum(1 for k in d2 if k.startswith(K("brut:avant-")))==2 and not err,{"e2":e2,"cles":sorted(d2),"err":err})
    ctx.close()
    # ======== 13. déconnexion depuis l'écran
    st,ctx,pg,err,d,e,txt=absent(TROIS)
    pg.get_by_text("Se déconnecter").click();pg.wait_for_timeout(600);d2=pg.evaluate(DUMP);lk=pg.evaluate("()=>PLOCK")
    pg.evaluate("()=>loginL('moi1')");pg.wait_for_timeout(500);e3=pg.evaluate(ETAT)
    ck("déconnexion : rien n'est écrit (seul cast_user retiré), verrou levé ; reconnexion → écran de récupération",
       lk is None and {k:v for k,v in st.items() if k!="cast_user"}=={k:v for k,v in d2.items()} and e3["lock"]=="absent" and e3["rec"] and not err,{"d2":sorted(d2),"e3":e3})
    ctx.close()
    # ======== 14. écritures impossibles pendant la récupération : rien n'est modifié
    st,ctx,pg,err,d,e,txt=absent(TROIS);msgs=[]
    pg.evaluate("()=>{window.__fail=/^cast:moi1$/}");pg.on("dialog",lambda x:(msgs.append(x.message),x.accept()))
    pg.get_by_text("Restaurer la copie du").first.click();pg.wait_for_timeout(1200)
    ck("restauration dont l'écriture échoue : « La restauration a échoué », profil toujours absent, toujours verrouillé, sauvegardes intactes",
       any("restauration a échoué" in m for m in msgs) and pg.evaluate("()=>localStorage.getItem('cast:moi1')") is None and pg.evaluate(ETAT)["lock"]=="absent"
       and all(pg.evaluate(DUMP).get(k)==v for k,v in TROIS.items()),{"msgs":msgs})
    ctx.close()
    st,ctx,pg,err,d,e,txt=absent(TROIS);msgs=[]
    pg.evaluate("()=>{window.__fail=/:brut:/}");pg.on("dialog",lambda x:(msgs.append(x.message),x.accept()))
    pg.get_by_text("Restaurer la copie du").nth(1).click();pg.wait_for_timeout(1200)
    ck("mise à l'abri des autres sauvegardes impossible : restauration refusée sans téléchargement préalable, rien n'est écrit",
       any("Télécharge d'abord" in m for m in msgs) and pg.evaluate(DUMP)==st and pg.evaluate(ETAT)["lock"]=="absent",{"msgs":msgs})
    ctx.close()
    # ======== 15. B1 (profil corrompu) : la restauration d'une copie plus ancienne ne fait plus perdre la plus récente
    st=dict(BASEST,**{K():"{corrompu"},**TROIS);ctx,pg,err=page(st);v0=valides(pg,pg.evaluate(DUMP))
    pg.on("dialog",lambda x:x.accept());pg.get_by_text("Restaurer la copie du").nth(1).click();pg.wait_for_timeout(1500);d2=pg.evaluate(DUMP)
    ck("profil corrompu (B1) : copie ancienne restaurée, la plus récente conservée, l'original illisible conservé",
       d2[K()]==BAKJ and v0<=set(d2.values()) and "{corrompu" in d2.values() and not err,sorted(d2))
    ctx.close()
    b.close()
print(f"\n{sum(R)}/{len(R)} contrôles OK");sys.exit(0 if all(R) else 1)
