# Anomalie n°1 de l'audit du 7 novembre : « Je n'arrive pas à écouter ».
# La question d'écoute révélée est annulée (aucun point, rien dans le profil), remplacée par une question sans écoute,
# et ne peut plus être validée par aucun chemin de notation. Le fonctionnement normal des écoutes est préservé.
# Usage : python3 tests/nolisten.py [URL] [page]
import sys
from playwright.sync_api import sync_playwright
URL=sys.argv[1] if len(sys.argv)>1 else "http://127.0.0.1:8772/";PAGE=sys.argv[2] if len(sys.argv)>2 else "castellano.html"
res=[]
def ck(n,ok,d=""):res.append(ok);print(("OK   " if ok else "FAIL ")+n+("" if ok else f"  {d}"))
NLA=["pic","tfL","listen","listenP","listenT","exL","dict"]
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page();err=[]
    pg.on("pageerror",lambda e:err.append(str(e)))
    pg.goto(URL+PAGE);pg.wait_for_timeout(2500)
    pg.evaluate("()=>{S.lang='es';S.lvl=1;build();xens()}")
    SNAP="""()=>JSON.stringify({ok:R.ok,xp:R.xp,n:R.n,sk:S.sk,sc:S.sc,sr:S.sr,md:(S.md||{})[lg()],mi:S.mi,adp:S.adp})"""
    def setup(ty,mode="lesson",t="CO"):
        return pg.evaluate("""([ty,mode,t])=>{R={mode,t,n:3,ok:2,xp:20,hist:[]};if(mode==='test')T={i:0,list:[{}],l:1,k:{},m:0,p:0,skip:0,skipAll:0,res:{}};let q=null;for(let i=0;i<20&&(!q||q.ty!==ty);i++){try{q=mkQ0(ty,0)}catch(e){q=null}}if(!q)return null;R.q=q;show();return {ty:q.ty,say:q.say,key:q.key,btn:!!document.getElementById('nol')}}""",[ty,mode,t])
    # 1. chaque type d'écoute : remplacement immédiat, non noté, sans écoute, texte montré
    for ty in NLA:
        q=setup(ty)
        if not q:ck(f"{ty} : question d'écoute générée",False,"aucune question");continue
        avant=pg.evaluate(SNAP)
        pg.evaluate("()=>{window.__old=R.q}");pg.click("#nol");pg.wait_for_timeout(150)
        r=pg.evaluate("""()=>({void:!!(__old&&__old.void),same:R.q===__old,ty:R.q.ty,done:R.done,
            note:(document.querySelector('.nlr')||{}).textContent||'',nol:!!document.getElementById('nol')})""")
        apres=pg.evaluate(SNAP)
        ck(f"{ty} : « Je n'arrive pas à écouter » remplace la question tout de suite par une question sans écoute ({r['ty']})",
           r["void"] and not r["same"] and r["ty"] not in NLA and not r["done"] and not r["nol"],r)
        ck(f"{ty} : aucun point, aucune question comptée, profil inchangé (compétences, mots, révisions, modalités, profil adaptatif)",avant==apres,[avant,apres])
        ck(f"{ty} : le texte du clip n'est montré qu'avec l'avis « remplacée, non notée »",bool(q["say"]) and q["say"] in r["note"] and ("non not" in r["note"] or "not marked" in r["note"]),r["note"])
    # 2. aucun autre chemin ne peut valider l'ancienne question
    q=setup("dict");pg.evaluate("()=>{window.__old=R.q}");pg.click("#nol");pg.wait_for_timeout(150)
    avant=pg.evaluate(SNAP)
    r=pg.evaluate("""()=>{const out={};const cur=R.q;
        // a) fin() appelé avec l'ancienne question remise en place (rappel tardif, double clic…)
        R.q=__old;R.done=false;try{fin(true,__old.sol,__old.key)}catch(e){out.e1=String(e)}out.doneOld=R.done;R.q=cur;R.done=false;
        // b) ans()/chkT() sur l'ancienne question
        R.q=__old;R.done=false;try{if(__old.o)ans(__old.o.indexOf(__old.g));else{const i=document.getElementById('ti');if(i){i.disabled=false;i.value=__old.say;chkT()}}}catch(e){out.e2=String(e)}R.q=cur;R.done=false;
        // c) deuxième clic sur « Je n'arrive pas à écouter » après remplacement
        try{noListen()}catch(e){out.e3=String(e)}out.same=R.q===cur;
        return out}""")
    apres=pg.evaluate(SNAP)
    ck("ancienne question : fin(), ans()/chkT() et un nouvel appel à noListen() n'attribuent rien",avant==apres and r.get("same") and not r.get("e1") and not r.get("e2"),[r,avant,apres])
    # 3. la question de remplacement est notée normalement
    q=setup("listen");pg.click("#nol");pg.wait_for_timeout(150)
    r=pg.evaluate("""()=>{const q=R.q,o0=R.ok,x0=R.xp;if(q.o&&q.g!=null){ans(q.o.indexOf(q.g))}else{fin(true,q.sol,q.key)}return{ty:q.ty,dOk:R.ok-o0,dXp:R.xp-x0,done:R.done}}""")
    ck(f"la question de remplacement ({r['ty']}) est notée normalement (bonne réponse comptée)",r["done"] and r["dOk"]==1 and r["dXp"]>0,r)
    # 4. comportement normal des écoutes préservé (sans le bouton)
    for ty in ["listen","dict"]:
        q=setup(ty)
        r=pg.evaluate("""()=>{const q=R.q,o0=R.ok,x0=R.xp;if(q.ty==='dict'){const i=document.getElementById('ti');i.value=q.say;chkT()}else ans(q.o.indexOf(q.g));return{dOk:R.ok-o0,dXp:R.xp-x0,done:R.done}}""")
        ck(f"{ty} sans le bouton : bonne réponse toujours comptée",r["done"] and r["dOk"]==1 and r["dXp"]>0,r)
    # 5. test de niveau : le bouton reste « question ignorée » (tskip), noListen() ne fait rien
    q=setup("listen",mode="test",t="CO")
    r=pg.evaluate("""()=>{const b=document.getElementById('nol');const q=R.q;noListen();return{onclick:b&&b.getAttribute('onclick'),same:R.q===q,void:!!q.void}}""")
    ck("test de niveau : bouton « question ignorée » inchangé, noListen() sans effet",r["onclick"]=="tskip()" and r["same"] and not r["void"],r)
    # 6. étape réservée à l'écoute : pas de boucle sur une autre écoute
    q=setup("dict",t="CO");pg.click("#nol");pg.wait_for_timeout(150)
    ty=pg.evaluate("R.q.ty");ck(f"étape « Écouter » : remplacement sans écoute quand même ({ty})",ty not in NLA,ty)
    ck("aucune erreur JavaScript",not err,err)
    b.close()
print(f"{sum(res)}/{len(res)} contrôles OK")
sys.exit(0 if all(res) else 1)
