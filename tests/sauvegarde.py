# Chargement sûr des profils « cast:<id> » (classProfil, verrou d'écriture, écran de récupération).
# Usage : python3 tests/rangesrv.py 8772 .  puis  python3 tests/sauvegarde.py [URL]   (URL par défaut http://localhost:8772/)
import sys,json
from playwright.sync_api import sync_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else "http://localhost:8772/"
R=[]
def ck(n,c,info=""):
    R.append(bool(c));print(("OK  " if c else "FAIL")+" "+n+("" if c else "  "+str(info)[:500]),flush=True)
OK2=lambda **k:json.dumps(dict({"v":2,"xp":40,"streak":0,"last":"","sc":{"hola":2},"lvl":1,"lang":"es","PL":{},"bd":{},"nt":[],"t":1793000000000},**k))
CORROMPUS={"chaîne vide":"","JSON cassé":"{corrompu","null":"null","tableau":"[]","nombre":"5","chaîne":'"abc"',"objet vide":"{}",
 "xp texte":OK2(xp="abc"),"xp négatif":OK2(xp=-5),"lvl 9":OK2(lvl=9),"lvl 2,5":OK2(lvl=2.5),"langue inconnue":OK2(lang="zz"),"langue 'constructor'":OK2(lang="constructor"),
 "sc null":OK2(sc=None),"sc tableau":OK2(sc=[]),"sr texte":OK2(sr="x"),"pth null":OK2(pth=None),"PL nombre":OK2(PL=5),"sk tableau":OK2(sk=[]),"nt objet":OK2(nt={}),
 "v texte":OK2(v="2"),"v 1":OK2(v=1),"v 2,5":OK2(v=2.5)}
ANCIEN=json.dumps({"xp":40,"streak":3,"sc":{"hola":2},"lvl":1,"lang":"es","PL":{},"nt":[],"t":1793000000000})
FUTUR=OK2(v=3,xp=55,nouveau={"x":1})
ACTUEL=OK2()
with sync_playwright() as p:
    b=p.chromium.launch()
    def page(val,init=None,user="x1"):
        ctx=b.new_context(locale="fr-FR",accept_downloads=True);pg=ctx.new_page();err=[];pg.on("pageerror",lambda e:err.append(str(e)[:150]))
        if init:pg.add_init_script(init)
        pg.goto(BASE+"index.html");pg.wait_for_timeout(1200)
        pg.evaluate("([u,v])=>{localStorage.clear();localStorage.setItem('cast_user',u);localStorage.setItem('acct:'+u,'{}');if(v!==null)localStorage.setItem('cast:'+u,v)}",[user,val])
        pg.reload();pg.wait_for_timeout(2500);return ctx,pg,err
    st=lambda pg:pg.evaluate("()=>({lock:PLOCK&&{c:PLOCK.c,r:PLOCK.r,kept:PLOCK.kept},rec:!!document.getElementById('prec'),xp:S.xp,lang:S.lang,raw:localStorage.getItem('cast:x1'),brut:Object.keys(localStorage).filter(k=>k.startsWith('cast:x1:brut:')).map(k=>[k.split(':')[3],localStorage.getItem(k)])})")
    ecrire="()=>{try{S.xp=999;save()}catch(e){}try{setLang('ca')}catch(e){}try{lsw()}catch(e){}return localStorage.getItem('cast:x1')}"
    # ---- 1. classification seule (5 catégories)
    ctx,pg,err=page(None)
    cl=pg.evaluate("(C)=>{const o={};for(const k in C)o[k]=classProfil(C[k]).c;return o}",dict(CORROMPUS,absent=None,ancien=ANCIEN,futur=FUTUR,actuel=ACTUEL))
    ck("classProfil : absent / actuel (v:2) / ancien (sans v) / futur (v:3)",cl["absent"]=="absent" and cl["actuel"]=="actuel" and cl["ancien"]=="ancien" and cl["futur"]=="futur",cl)
    ck("classProfil : JSON cassé, null, tableau, nombre, chaîne, objet vide et chaque champ critique invalide → corrompu",all(cl[k]=="corrompu" for k in CORROMPUS),{k:v for k,v in cl.items() if k in CORROMPUS and v!="corrompu"})
    ctx.close()
    # ---- 2. profils corrompus : rien d'écrasé, données brutes conservées à l'identique, écriture bloquée
    bad={}
    for n,v in CORROMPUS.items():
        ctx,pg,err=page(v);s=st(pg);after=pg.evaluate(ecrire);pg.reload();pg.wait_for_timeout(2500);s2=st(pg)
        okk=s["lock"] and s["lock"]["c"]=="corrompu" and s["rec"] and s["raw"]==v and after==v and s2["raw"]==v and [x for x in s["brut"] if x[0]=="corrompu" and x[1]==v] and len(s2["brut"])==1 and not err
        if not okk:bad[n]={"s":s,"apres_ecriture":after,"rechargement":s2,"err":err}
        ctx.close()
    ck(f"{len(CORROMPUS)} profils corrompus : écran de récupération, original intact après tentative d'écriture et rechargement, copie brute identique (une seule)",not bad,bad)
    # ---- 3. profil futur v:3 : lecture refusée, aucune écriture, ni restauration ni remise à zéro proposées
    ctx,pg,err=page(FUTUR);s=st(pg);txt=pg.evaluate("()=>document.getElementById('prec').innerText");after=pg.evaluate(ecrire)
    ck("profil futur v:3 : écriture bloquée, original intact, copie brute, « Recharger l'appli », pas de remise à zéro",s["lock"]["c"]=="futur" and after==FUTUR and s["brut"]==[["futur",FUTUR]] and "Recharger" in txt and "zéro" not in txt and not err,{"s":s,"txt":txt,"err":err})
    ctx.close()
    # ---- 4. ancien profil sans v : copie brute avant migration, puis chargement normal et migration à v:2 sans perte
    ctx,pg,err=page(ANCIEN);s=st(pg);pg.evaluate("()=>save()");n=json.loads(pg.evaluate("()=>localStorage.getItem('cast:x1')"))
    o=json.loads(ANCIEN);perdus=[k for k in o if k!="t" and n.get(k)!=o[k]]
    ck("ancien profil sans v : copie brute identique conservée avant migration, chargé (40 XP), réécrit en v:2 sans perte",s["lock"] is None and not s["rec"] and s["xp"]==40 and s["brut"]==[["ancien",ANCIEN]] and n["v"]==2 and not perdus and not err,{"s":s,"perdus":perdus,"err":err})
    ctx.close()
    # ---- 5. profil actuel v:2 : chargé, aucune copie, sauvegarde normale
    ctx,pg,err=page(ACTUEL);s=st(pg);pg.evaluate("()=>{S.xp=41;save()}");n=json.loads(pg.evaluate("()=>localStorage.getItem('cast:x1')"))
    ck("profil actuel v:2 : chargé sans écran ni copie, la sauvegarde fonctionne",s["lock"] is None and not s["rec"] and s["xp"]==40 and s["brut"]==[] and n["xp"]==41 and not err,{"s":s,"n":n.get("xp"),"err":err})
    ctx.close()
    # ---- 6. profil absent : nouveau profil, sans écran de récupération
    ctx,pg,err=page(None);s=st(pg)
    ck("profil absent : nouveau profil, pas d'écran de récupération",s["lock"] is None and not s["rec"] and s["xp"]==0 and not err,s)
    ctx.close()
    # ---- 7. restauration d'une copie valide : refus = rien ne change ; accord = copie chargée, original illisible conservé
    COPIE=OK2(xp=77,t=1793500000000)
    def restau(accept):
        ctx,pg,err=page("{corrompu");pg.evaluate("(c)=>{localStorage.setItem('cast:x1:copie-test',c);pRec()}",COPIE)
        pg.on("dialog",lambda d:d.accept() if accept else d.dismiss())
        txt=pg.evaluate("()=>document.getElementById('prec').innerText")
        pg.get_by_text("Restaurer la copie du").first.click();pg.wait_for_timeout(1500);s=st(pg);ctx.close();return txt,s,err
    txt,s,err=restau(False)
    ck("restauration refusée : rien ne change (original et copie intacts, toujours verrouillé)","77 XP" in txt and s["raw"]=="{corrompu" and s["lock"]["c"]=="corrompu" and not err,{"s":s,"txt":txt})
    txt,s,err=restau(True)
    ck("restauration acceptée : la copie (77 XP) devient le profil, l'original illisible reste conservé",s["lock"] is None and s["xp"]==77 and s["raw"]==COPIE and s["brut"]==[["corrompu","{corrompu"]] and not err,{"s":s,"err":err})
    # ---- 8. remise à zéro : deux étapes, annulation possible, original conservé
    ctx,pg,err=page("{corrompu")
    pg.get_by_text("Repartir de zéro…").click();pg.wait_for_timeout(400)
    pg.get_by_text("Annuler").click();pg.wait_for_timeout(400);s1=st(pg)
    pg.get_by_text("Repartir de zéro…").click();pg.wait_for_timeout(400);pg.get_by_text("Oui, repartir de zéro").click();pg.wait_for_timeout(1500);s2=st(pg)
    n=json.loads(s2["raw"])
    ck("remise à zéro : annulation sans effet ; confirmation explicite → profil neuf, original illisible conservé",s1["raw"]=="{corrompu" and s1["lock"] and s2["lock"] is None and n["xp"]==0 and n.get("ob")==1 and s2["brut"]==[["corrompu","{corrompu"]] and not err,{"s1":s1,"s2":s2,"err":err})
    ctx.close()
    # ---- 9. copie de sécurité impossible (stockage refusé) : remise à zéro bloquée tant que les données ne sont pas téléchargées
    QUOTA="(()=>{const f=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){if(String(k).includes(':brut:'))throw new DOMException('plein','QuotaExceededError');return f.call(this,k,v)}})()"
    ctx,pg,err=page("{corrompu",init=QUOTA);s=st(pg)
    dis=pg.evaluate("()=>[...document.querySelectorAll('#prec button')].find(b=>b.innerText.includes('zéro')).disabled")
    with pg.expect_download() as dl:pg.get_by_text("Télécharger mes données").click()
    pg.wait_for_timeout(600);fn=dl.value.suggested_filename;dis2=pg.evaluate("()=>[...document.querySelectorAll('#prec button')].find(b=>b.innerText.includes('zéro')).disabled")
    ck("copie de sécurité impossible : remise à zéro désactivée, téléchargement des données proposé puis remise à zéro autorisée, original intact",s["lock"]["kept"] is False and dis is True and fn.startswith("sobremesa-") and dis2 is False and s["raw"]=="{corrompu",{"s":s,"dis":dis,"dis2":dis2,"fn":fn})
    ctx.close()
    # ---- 10. ancien profil dont la copie est impossible : pas de migration sans accord
    ctx,pg,err=page(ANCIEN,init=QUOTA);s=st(pg);after=pg.evaluate(ecrire);pg.reload();pg.wait_for_timeout(2500)
    pg.on("dialog",lambda d:d.accept());pg.get_by_text("Continuer avec ma progression").click();pg.wait_for_timeout(1200);s2=st(pg)
    ck("ancien profil sans copie possible : verrouillé et intact ; « Continuer » (confirmé) → chargé",s["lock"]["c"]=="ancien" and after==ANCIEN and s2["lock"] is None and s2["xp"]==40 and not err,{"s":s,"s2":s2,"err":err})
    ctx.close()
    # ---- 11. déconnexion depuis l'écran de récupération : rien n'est écrit, la reconnexion repropose l'écran
    ctx,pg,err=page("{corrompu");pg.get_by_text("Se déconnecter").click();pg.wait_for_timeout(800)
    s=pg.evaluate("()=>({lock:PLOCK,raw:localStorage.getItem('cast:x1'),u:localStorage.getItem('cast_user')})")
    pg.evaluate("()=>loginL('x1')");pg.wait_for_timeout(600);s2=st(pg)
    ck("déconnexion : original intact, verrou levé ; reconnexion → écran de récupération, toujours une seule copie",s["lock"] is None and s["raw"]=="{corrompu" and s["u"] is None and s2["rec"] and len(s2["brut"])==1 and not err,{"s":s,"s2":s2,"err":err})
    ctx.close()
    b.close()
print(f"\n{sum(R)}/{len(R)} contrôles OK");sys.exit(0 if all(R) else 1)
