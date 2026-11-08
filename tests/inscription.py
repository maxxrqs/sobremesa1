# B3 : une inscription ne remplace jamais un compte ou un profil existant.
# Usage : python3 tests/rangesrv.py 8772 .  puis  python3 tests/inscription.py [URL]   (URL par défaut http://localhost:8772/)
import sys,json
from playwright.sync_api import sync_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else "http://localhost:8772/"
R=[]
def ck(n,c,info=""):
    R.append(bool(c));print(("OK  " if c else "FAIL")+" "+n+("" if c else "  "+str(info)[:600]),flush=True)
PROF=json.dumps({"v":2,"xp":40,"streak":0,"last":"","sc":{"hola":2},"lvl":1,"lang":"es","PL":{},"bd":{},"nt":[],"t":1793000000000})
ACCT=json.dumps({"salt":"00","a":"p","h":"abc","t":1793000000000})
DUMP="()=>{const o={};for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);try{o[k]=localStorage.getItem(k)}catch(e){o[k]='<illisible>'}}return o}"
REG="""async([u,p])=>{auth('reg');await new Promise(r=>setTimeout(r,200));document.getElementById('u').value=u;document.getElementById('p').value=p;
  await sub('reg');await new Promise(r=>setTimeout(r,600));const m=document.getElementById('m');
  return{msg:m&&m.style.display!=='none'?m.textContent:'',U,form:!!document.getElementById('u'),lock:PLOCK&&PLOCK.c,xp:S.xp}}"""
with sync_playwright() as p:
    b=p.chromium.launch()
    def page(store,init=None):
        ctx=b.new_context(locale="fr-FR");pg=ctx.new_page();err=[];pg.on("pageerror",lambda e:err.append(str(e)[:150]))
        if init:pg.add_init_script(init)
        pg.goto(BASE+"index.html");pg.wait_for_timeout(1000)
        pg.evaluate("(d)=>{localStorage.clear();for(const k in d)localStorage.setItem(k,d[k])}",store)
        pg.reload();pg.wait_for_timeout(2000);return ctx,pg,err
    def refus(nom,store,u="moi1",init=None):
        ctx,pg,err=page(store,init);avant=pg.evaluate(DUMP);r=pg.evaluate(REG,[u,"nouveaumdp"]);apres=pg.evaluate(DUMP)
        ck(f"{nom} : inscription refusée (« existe déjà »), aucune connexion, stockage identique octet pour octet",
           "existe déjà" in r["msg"] and r["U"] is None and r["form"] and avant==apres and not err,
           {"r":r,"ajouté/modifié":{k:apres.get(k) for k in apres if avant.get(k)!=apres.get(k)},"retiré":[k for k in avant if k not in apres],"err":err})
        return ctx,pg,err
    # ---- 1. identifiant entièrement nouveau
    ctx,pg,err=page({})
    r=pg.evaluate(REG,["neuf1","motdepasse1"]);d=pg.evaluate(DUMP)
    a=json.loads(d.get("acct:neuf1") or "null");c=json.loads(d.get("cast:neuf1") or "null")
    ck("identifiant neuf : compte créé (mot de passe haché), profil v:2 neuf, connecté, sauvegardes B2 créées",
       not r["msg"] and r["U"]=="neuf1" and a and a.get("h") and a.get("salt") and c and c["v"]==2 and c["xp"]==0
       and d.get("cast:neuf1:bak") and d.get("cast:neuf1:bakJ") and r["lock"] is None and not err,{"r":r,"cles":sorted(d),"err":err})
    # même page : déconnexion puis réinscription du même identifiant → refus ; l'ancien mot de passe fonctionne toujours
    pg.evaluate("()=>{S.xp=33;save()}");pg.evaluate("()=>logout()");pg.wait_for_timeout(300)
    avant=pg.evaluate(DUMP);r=pg.evaluate(REG,["neuf1","autremdp99"]);apres=pg.evaluate(DUMP)
    ck("identifiant créé juste avant, réinscription avec un autre mot de passe : refusée, compte et profil (33 XP) intacts",
       "existe déjà" in r["msg"] and r["U"] is None and avant==apres and json.loads(apres["cast:neuf1"])["xp"]==33,{"r":r})
    r=pg.evaluate("""async()=>{auth('login');await new Promise(r=>setTimeout(r,200));document.getElementById('u').value='neuf1';document.getElementById('p').value='motdepasse1';
      await sub('login');await new Promise(r=>setTimeout(r,600));return{U,xp:S.xp}}""")
    ck("… connexion avec le mot de passe d'origine : réussie, progression retrouvée (33 XP)",r["U"]=="neuf1" and r["xp"]==33 and not err,r)
    ctx.close()
    # ---- 2. compte existant (avec profil)
    refus("compte + profil existants",{"acct:moi1":ACCT,"cast:moi1":PROF})[0].close()
    # ---- 3. profil existant sans compte
    refus("profil existant sans compte",{"cast:moi1":PROF})[0].close()
    # ---- 4. compte existant, profil absent
    refus("compte existant, profil absent",{"acct:moi1":ACCT})[0].close()
    # ---- 5. comptes et profils corrompus
    for nom,st in [("compte JSON cassé",{"acct:moi1":"{corrompu"}),("compte vide {}",{"acct:moi1":"{}"}),("compte « null »",{"acct:moi1":"null"}),
                   ("compte chaîne vide",{"acct:moi1":""}),("compte sans mot de passe",{"acct:moi1":json.dumps({"salt":"00","t":1})}),
                   ("profil JSON cassé sans compte",{"cast:moi1":"{corrompu"}),("profil chaîne vide sans compte",{"cast:moi1":""}),
                   ("profil futur v:3 sans compte",{"cast:moi1":json.dumps({"v":3,"xp":5})}),("compte et profil corrompus",{"acct:moi1":"{x","cast:moi1":"{y"})]:
        refus(nom,st)[0].close()
    # ---- 6. profil principal absent, copies présentes (B1/B2) : refus (sinon :bak serait remplacée par un profil vide)
    for nom,st in [(":bak seule",{"cast:moi1:bak":PROF}),(":bakJ seule",{"cast:moi1:bakJ":PROF,"cast:moi1:bakJ:jour":"2026-11-01"}),
                   ("copie brute B1 seule",{"cast:moi1:brut:corrompu:1793000000000":"{corrompu"})]:
        refus("profil absent, "+nom,st)[0].close()
    # ---- 7. un identifiant proche n'est pas confondu (préfixe)
    ctx,pg,err=page({"cast:moi1:bak":PROF,"acct:moi1":ACCT,"cast:moi1":PROF})
    avant=pg.evaluate(DUMP);r=pg.evaluate(REG,["moi12","motdepasse1"]);apres=pg.evaluate(DUMP)
    ck("identifiant voisin (moi12 à côté de moi1) : inscription acceptée, données de moi1 intactes",
       not r["msg"] and r["U"]=="moi12" and all(apres.get(k)==v for k,v in avant.items()),{"r":r})
    ctx.close()
    # ---- 8. stockage illisible (lecture qui échoue) : refus par prudence, rien d'écrit
    PANNE="(()=>{const g=Storage.prototype.getItem;Storage.prototype.getItem=function(k){if(String(k).startsWith('acct:moi1'))throw new Error('lecture');return g.call(this,k)}})()"
    refus("lecture du compte impossible (compte présent)",{"acct:moi1":ACCT},init=PANNE)[0].close()
    # ---- 9. base en ligne (DB simulée) : compte distant existant, même sans mot de passe → refus ; profil local existant → refus sans écrire en ligne
    MOCK="""(docs)=>{window.__w=[];DB={doc:p=>({get:async()=>({exists:p in docs,data:()=>docs[p]}),set:async d=>{window.__w.push(p);docs[p]=d},acquire:async()=>({acquired:true})})}}"""
    for nom,docs,st in [("compte en ligne existant",{"accounts/moi1":{"salt":"0","a":"p","h":"z"}},{}),
                        ("compte en ligne sans mot de passe",{"accounts/moi1":{"t":1}},{}),
                        ("profil local existant, aucun compte en ligne",{},{"cast:moi1":PROF})]:
        ctx,pg,err=page(st);pg.evaluate(MOCK,docs);avant=pg.evaluate(DUMP);r=pg.evaluate(REG,["moi1","nouveaumdp"]);apres=pg.evaluate(DUMP);w=pg.evaluate("()=>window.__w")
        ck(f"en ligne — {nom} : refus, rien d'écrit (ni en ligne ni sur l'appareil)","existe déjà" in r["msg"] and r["U"] is None and avant==apres and w==[] and not err,{"r":r,"w":w})
        ctx.close()
    ctx,pg,err=page({});pg.evaluate(MOCK,{});r=pg.evaluate(REG,["moi1","motdepasse1"]);w=pg.evaluate("()=>window.__w");d=pg.evaluate(DUMP)
    ck("en ligne — identifiant neuf : compte créé en ligne, profil local neuf, connecté",w==["accounts/moi1"] and r["U"]=="moi1" and json.loads(d["cast:moi1"])["v"]==2 and not err,{"r":r,"w":w})
    ctx.close()
    # ---- 10. profil apparu entre la vérification et l'écriture (autre onglet) : jamais écrasé
    ctx,pg,err=page({})
    pg.evaluate("""()=>{const f=hp;hp=async(...a)=>{localStorage.setItem('cast:moi1',%s);return f(...a)}}"""%json.dumps(PROF))
    r=pg.evaluate(REG,["moi1","motdepasse1"]);c=pg.evaluate("()=>localStorage.getItem('cast:moi1')")
    ck("profil écrit par un autre onglet pendant l'inscription : pas écrasé (40 XP conservés)",c==PROF and not err,{"r":r,"c":c})
    ctx.close()
    b.close()
print(f"\n{sum(R)}/{len(R)} contrôles OK");sys.exit(0 if all(R) else 1)
