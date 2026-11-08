# B4-C : à la connexion, une erreur de lecture du stockage n'est jamais prise pour un profil absent.
# Usage : python3 tests/rangesrv.py 8772 .  puis  python3 tests/lecture.py [URL]   (URL par défaut http://localhost:8772/)
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
COPIES={K("bak"):BAK,K("bakJ"):BAKJ,K("bakJ:jour"):"2026-11-01"}
# window.__rerr : les lectures (getItem) des clés correspondantes échouent ; window.__w : journal de toutes les écritures
PANNE="""(()=>{window.__w=[];const g=Storage.prototype.getItem,s=Storage.prototype.setItem,r=Storage.prototype.removeItem;
  Storage.prototype.getItem=function(k){if(window.__rerr&&window.__rerr.test(String(k)))throw new DOMException('lecture impossible','UnknownError');return g.call(this,k)};
  Storage.prototype.setItem=function(k,v){if(String(k)!=='_t')window.__w.push(String(k));return s.call(this,k,v)};
  Storage.prototype.removeItem=function(k){if(String(k)!=='_t')window.__w.push('-'+k);return r.call(this,k)}})()"""
RAW="()=>{const o={},g=Object.getPrototypeOf(localStorage);for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);o[k]=Storage.prototype.getItem.call(localStorage,k)}return o}"
# lecture sans passer par la panne (pour contrôler le contenu réel du stockage)
DUMP="()=>{const e=window.__rerr;window.__rerr=null;const o={};for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);o[k]=localStorage.getItem(k)}window.__rerr=e;return o}"
ETAT="()=>({lock:PLOCK&&PLOCK.c,r:PLOCK&&PLOCK.r,rec:!!document.getElementById('prec'),txt:(document.getElementById('prec')||{}).innerText||'',xp:S.xp,U,ste:STE.bak,w:window.__w.slice()})"
with sync_playwright() as p:
    b=p.chromium.launch()
    def page(store,rerr=None):
        ctx=b.new_context(locale="fr-FR");pg=ctx.new_page();err=[];pg.on("pageerror",lambda e:err.append(str(e)[:200]))
        pg.goto(BASE+"index.html");pg.wait_for_timeout(900)
        pg.evaluate("(d)=>{localStorage.clear();for(const k in d)localStorage.setItem(k,d[k])}",store)
        if rerr:pg.add_init_script("window.__rerr=new RegExp(%s)"%json.dumps(rerr))
        pg.add_init_script(PANNE);pg.reload();pg.wait_for_timeout(2300);return ctx,pg,err
    ecrire="()=>{try{S.xp=999;save()}catch(e){}try{lsw()}catch(e){}try{setLang('ca')}catch(e){}try{pRec()}catch(e){}}"
    # ---- 1. lecture normale d'un profil existant (avec :bak et :bakJ)
    st=dict(BASEST,**{K():ACT},**COPIES);ctx,pg,err=page(st);e=pg.evaluate(ETAT);d=pg.evaluate(DUMP)
    ck("lecture normale : profil chargé (40 XP), pas d'écran ; :bak et :bakJ mises à jour comme en B2",
       e["lock"] is None and not e["rec"] and e["xp"]==40 and d[K("bak")]==ACT and d[K("bakJ")]==ACT and d[K()]==ACT and not err,{"e":e,"err":err})
    ctx.close()
    # ---- 2. profil réellement absent (aucune copie) : comportement normal inchangé
    ctx,pg,err=page(dict(BASEST));e=pg.evaluate(ETAT)
    ck("profil réellement absent : nouveau profil (0 XP), pas d'écran",e["lock"] is None and not e["rec"] and e["xp"]==0 and not err,e)
    ctx.close()
    ctx,pg,err=page(dict(BASEST,**COPIES));e=pg.evaluate(ETAT)
    ck("profil réellement absent avec sauvegardes : écran « introuvable » de B4 inchangé",e["lock"]=="absent" and "introuvable" in e["txt"],e)
    ctx.close()
    # ---- 3. erreur de lecture ponctuelle du profil, puis récupération
    st=dict(BASEST,**{K():ACT},**COPIES);ctx,pg,err=page(st,rerr="^cast:moi1$")
    e=pg.evaluate(ETAT);pg.evaluate(ecrire);w=pg.evaluate("()=>window.__w.slice()");d=pg.evaluate(DUMP)
    ck("erreur de lecture : écran « n'a pas pu être lue », aucun profil neuf, aucune restauration proposée, aucun bouton de remise à zéro",
       e["lock"]=="lecture" and e["r"]=="profil" and "pas pu être lue" in e["txt"] and "Réessayer" in e["txt"] and "Restaurer" not in e["txt"] and "zéro" not in e["txt"] and e["xp"]==0 and not err,{"e":e,"err":err})
    ck("pendant l'erreur : aucune écriture de données (seul cast_user, identique), même en tentant d'enregistrer ; profil et sauvegardes intacts",
       [x for x in w if x!="cast_user"]==[] and d==st,{"w":w,"diff":{k:d.get(k) for k in set(d)|set(st) if d.get(k)!=st.get(k)}})
    pg.evaluate("()=>{window.__rerr=null}");pg.get_by_text("Réessayer").click();pg.wait_for_timeout(1200);e2=pg.evaluate(ETAT);d2=pg.evaluate(DUMP)
    ck("lecture de nouveau possible → « Réessayer » : profil chargé à l'identique (40 XP), sauvegardes B2 normales",
       e2["lock"] is None and not e2["rec"] and e2["xp"]==40 and d2[K()]==ACT and d2[K("bak")]==ACT and not err,{"e2":e2})
    ctx.close()
    # ---- 4. erreur de lecture persistante
    ctx,pg,err=page(st,rerr="^cast:moi1$")
    for _ in range(3):pg.get_by_text("Réessayer").click();pg.wait_for_timeout(500)
    e=pg.evaluate(ETAT);d=pg.evaluate(DUMP)
    ck("erreur persistante : « Réessayer » ×3 → toujours l'écran d'erreur, aucune écriture, données intactes",
       e["lock"]=="lecture" and e["rec"] and [x for x in e["w"] if x!="cast_user"]==[] and d==st and not err,{"e":e,"err":err})
    pg.get_by_text("Se déconnecter").click();pg.wait_for_timeout(500);d=pg.evaluate(DUMP);w=pg.evaluate("()=>window.__w.slice()")
    ck("erreur persistante, déconnexion : seul cast_user retiré, profil et sauvegardes intacts",
       {k:v for k,v in st.items() if k!="cast_user"}==d and [x for x in w if x not in("cast_user","-cast_user")]==[],{"w":w})
    pg.evaluate("()=>loginL('moi1')");pg.wait_for_timeout(500);e=pg.evaluate(ETAT)
    ck("… reconnexion pendant l'erreur : de nouveau l'écran d'erreur",e["lock"]=="lecture",e)
    ctx.close()
    # ---- 5. lecture totalement impossible (toutes les clés)
    ctx,pg,err=page(st,rerr=".");e=pg.evaluate(ETAT)
    REG="""async([m,u,pw])=>{auth(m);await new Promise(r=>setTimeout(r,200));document.getElementById('u').value=u;document.getElementById('p').value=pw;
      await sub(m);await new Promise(r=>setTimeout(r,600));const x=document.getElementById('m');return{msg:x&&x.style.display!=='none'?x.textContent:'',U}}"""
    lg=pg.evaluate(REG,["login",U,"motdepasse1"]);rg=pg.evaluate(REG,["reg",U,"motdepasse1"]);d=pg.evaluate(DUMP);w=pg.evaluate("()=>window.__w.slice()")
    ck("stockage illisible en entier (même cast_user) : accueil sans connexion ; connexion échouée et inscription refusée ; aucune écriture, données intactes",
       e["U"] is None and e["lock"] is None and lg["U"] is None and lg["msg"] and rg["U"] is None and "existe déjà" in rg["msg"] and w==[] and d==st and not err,{"e":e,"lg":lg,"rg":rg,"w":w,"err":err})
    ctx.close()
    # ---- 6. profil absent mais copies illisibles : jamais un profil neuf
    st2=dict(BASEST,**COPIES);ctx,pg,err=page(st2,rerr=":bak")
    e=pg.evaluate(ETAT);pg.evaluate(ecrire);d=pg.evaluate(DUMP);w=pg.evaluate("()=>window.__w.slice()")
    ck("profil absent, copies illisibles : écran d'erreur (copies), aucun profil créé, copies intactes",
       e["lock"]=="lecture" and e["r"]=="copies" and K() not in d and d==st2 and [x for x in w if x!="cast_user"]==[] and not err,{"e":e,"w":w})
    pg.evaluate("()=>{window.__rerr=null}");pg.get_by_text("Réessayer").click();pg.wait_for_timeout(1200);e2=pg.evaluate(ETAT)
    ck("… copies de nouveau lisibles → « Réessayer » : écran « introuvable » avec les 2 sauvegardes",e2["lock"]=="absent" and e2["txt"].count("Restaurer la copie du")==2,e2)
    ctx.close()
    # ---- 7. profil lisible, :bakJ illisible : profil chargé, aucune sauvegarde auto écrite, échec signalé
    st=dict(BASEST,**{K():ACT},**COPIES);ctx,pg,err=page(st,rerr=":bakJ$");e=pg.evaluate(ETAT);d=pg.evaluate(DUMP)
    ck("profil lisible, :bakJ illisible : profil chargé (40 XP) ; :bak et :bakJ non réécrites ; avis « sauvegarde automatique »",
       e["lock"] is None and e["xp"]==40 and d[K("bak")]==BAK and d[K("bakJ")]==BAKJ and e["ste"]=="échec"
       and pg.evaluate("()=>(document.getElementById('stb')||{dataset:{}}).dataset.k")=="bak" and not err,{"e":e,"err":err})
    ctx.close()
    # ---- 8. profils corrompu et futur : comportement B1 inchangé
    for nom,v in [("corrompu","{corrompu"),("futur",P(v=3))]:
        ctx,pg,err=page(dict(BASEST,**{K():v}));e=pg.evaluate(ETAT)
        ck(f"profil {nom} : écran de récupération B1 inchangé",e["lock"]==nom and "pas pu être lue pour l'instant" not in e["txt"] and not err,e)
        ctx.close()
    b.close()
print(f"\n{sum(R)}/{len(R)} contrôles OK");sys.exit(0 if all(R) else 1)
