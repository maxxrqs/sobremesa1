# Sauvegardes automatiques des profils valides : cast:<id>:bak (chaque ouverture) et cast:<id>:bakJ (une fois par jour local).
# Usage : python3 tests/rangesrv.py 8772 .  puis  python3 tests/sauvegarde_auto.py [URL]   (URL par défaut http://localhost:8772/)
import sys,json,datetime
from playwright.sync_api import sync_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else "http://localhost:8772/"
R=[]
def ck(n,c,info=""):
    R.append(bool(c));print(("OK  " if c else "FAIL")+" "+n+("" if c else "  "+str(info)[:600]),flush=True)
TZ=datetime.timezone(datetime.timedelta(hours=1))
J1=datetime.datetime(2026,11,8,10,0,tzinfo=TZ);J1b=datetime.datetime(2026,11,8,22,30,tzinfo=TZ);J2=datetime.datetime(2026,11,9,0,15,tzinfo=TZ)
prof=lambda **k:json.dumps(dict({"v":2,"xp":40,"streak":0,"last":"","sc":{"hola":2},"lvl":1,"lang":"es","PL":{},"bd":{},"nt":[],"t":1793000000000},**k))
ACTUEL=prof();ANCIEN=json.dumps({"xp":40,"streak":3,"sc":{"hola":2},"lvl":1,"lang":"es","PL":{},"nt":[],"t":1793000000000})
VIEUX=prof(xp=12,t=1792000000000)   # sauvegardes antérieures valides
K=lambda s:"cast:x1:"+s
with sync_playwright() as p:
    b=p.chromium.launch()
    class Session:
        """un navigateur dont le stockage persiste entre les ouvertures (comme l'appli installée)"""
        def __init__(s,store,init=None):
            s.ctx=b.new_context(locale="fr-FR",timezone_id="Europe/Madrid");s.err=[];s.init=init;s.pg=None
            pg=s.ctx.new_page();pg.goto(BASE+"index.html");pg.wait_for_timeout(1000)
            pg.evaluate("(d)=>{localStorage.clear();localStorage.setItem('cast_user','x1');localStorage.setItem('acct:x1','{}');for(const k in d)localStorage.setItem(k,d[k])}",store);pg.close()
        def ouvrir(s,quand,init=None):
            if s.pg:s.pg.close()
            pg=s.ctx.new_page();pg.on("pageerror",lambda e:s.err.append(str(e)[:150]))
            if init or s.init:pg.add_init_script(init or s.init)
            pg.clock.set_fixed_time(quand);pg.goto(BASE+"index.html");pg.wait_for_timeout(2500);s.pg=pg
            return pg.evaluate("()=>({lock:PLOCK&&PLOCK.c,PBAK,xp:S.xp,main:localStorage.getItem('cast:x1'),bak:localStorage.getItem('cast:x1:bak'),bakJ:localStorage.getItem('cast:x1:bakJ'),jour:localStorage.getItem('cast:x1:bakJ:jour'),cles:Object.keys(localStorage).filter(k=>k.startsWith('cast:x1:')).sort()})")
        def progres(s,xp):s.pg.evaluate("(x)=>{S.xp=x;save()}",xp);return s.pg.evaluate("()=>localStorage.getItem('cast:x1')")
        def close(s):s.ctx.close()
    # ---- 1. première ouverture d'un profil valide
    se=Session({"cast:x1":ACTUEL});o=se.ouvrir(J1)
    ck("1re ouverture : :bak et :bakJ = copie exacte du profil, jour local enregistré, profil chargé normalement",
       o["bak"]==ACTUEL and o["bakJ"]==ACTUEL and o["jour"]=="2026-11-08" and o["PBAK"]=={"bak":"ok","bakJ":"ok"} and o["lock"] is None and o["xp"]==40 and not se.err,o)
    # ---- 2. ouvertures successives le même jour
    m1=se.progres(55);o=se.ouvrir(J1b)
    ck("même jour, après progression : :bak suit le profil ouvert (55 XP), :bakJ garde la copie du matin (40 XP), non réécrite",
       o["bak"]==m1 and o["bakJ"]==ACTUEL and o["jour"]=="2026-11-08" and o["PBAK"]=={"bak":"ok","bakJ":"déjà faite aujourd'hui"} and not se.err,o)
    o=se.ouvrir(J1b)
    ck("même jour, sans changement : rien n'est réécrit (:bak « inchangé »)",o["bak"]==m1 and o["PBAK"]["bak"]=="inchangé" and o["bakJ"]==ACTUEL,o)
    # ---- 3. nouvelle ouverture un autre jour (minuit passé, heure locale)
    m2=se.progres(70);o=se.ouvrir(J2)
    ck("autre jour (9 nov. 00:15 heure locale) : :bakJ remplacée par le profil du jour (70 XP), jour mis à jour",
       o["bakJ"]==m2 and o["bak"]==m2 and o["jour"]=="2026-11-09" and o["PBAK"]=={"bak":"ok","bakJ":"ok"} and not se.err,o)
    se.close()
    # ---- 4. ancien profil sans version
    se=Session({"cast:x1":ANCIEN});o=se.ouvrir(J1)
    brut=[k for k in o["cles"] if ":brut:ancien:" in k];n=json.loads(se.progres(41))
    ck("ancien profil sans v : copie brute (B1) + :bak et :bakJ = profil d'origine exact, puis migration v:2 normale",
       len(brut)==1 and o["bak"]==ANCIEN and o["bakJ"]==ANCIEN and o["lock"] is None and n["v"]==2 and n["xp"]==41 and not se.err,o)
    o=se.ouvrir(J1b)
    ck("ancien profil, réouverture : :bak devient le profil migré (v:2), :bakJ garde l'original du jour",json.loads(o["bak"])["v"]==2 and o["bakJ"]==ANCIEN,o)
    se.close()
    # ---- 5. profils corrompu et futur : sauvegardes antérieures intactes, jamais remplacées
    for nom,val in [("corrompu","{corrompu"),("futur",prof(v=3,xp=99))]:
        se=Session({"cast:x1":val,K("bak"):VIEUX,K("bakJ"):VIEUX,K("bakJ:jour"):"2026-11-01"});o=se.ouvrir(J1)
        ck(f"profil {nom} : :bak et :bakJ antérieures intactes (aucune écriture), profil verrouillé",
           o["lock"]==nom and o["bak"]==VIEUX and o["bakJ"]==VIEUX and o["jour"]=="2026-11-01" and o["main"]==val and o["PBAK"] in (None,{"bak":"","bakJ":""}),o)
        se.close()
    # ---- 6. restauration de bout en bout depuis les sauvegardes après une corruption
    se=Session({"cast:x1":ACTUEL});se.ouvrir(J1);se.pg.evaluate("()=>localStorage.setItem('cast:x1','{corrompu')");o=se.ouvrir(J1)
    txt=se.pg.evaluate("()=>document.getElementById('prec').innerText")
    ck("corruption juste après la 1re ouverture : :bak et :bakJ identiques → une seule copie proposée",o["lock"]=="corrompu" and txt.count("Restaurer la copie du")==1 and "40 XP" in txt,txt)
    se.close()
    se=Session({"cast:x1":ACTUEL});se.ouvrir(J1);m=se.progres(88);se.ouvrir(J1b)
    se.pg.evaluate("()=>localStorage.setItem('cast:x1','{corrompu')");o=se.ouvrir(J1b)
    txt=se.pg.evaluate("()=>document.getElementById('prec').innerText")
    se.pg.on("dialog",lambda d:d.accept());se.pg.get_by_text("Restaurer la copie du").first.click();se.pg.wait_for_timeout(1500)
    xp=se.pg.evaluate("()=>S.xp");main=se.pg.evaluate("()=>localStorage.getItem('cast:x1')")
    ck("corruption après plusieurs ouvertures : :bak (88 XP) puis :bakJ (40 XP) proposées ; la plus récente restaurée à l'identique",
       o["lock"]=="corrompu" and txt.count("Restaurer la copie du")==2 and txt.index("88 XP")<txt.index("40 XP") and xp==88 and main==m and not se.err,{"txt":txt,"xp":xp})
    se.close()
    # ---- 7. échec d'écriture (stockage plein sur les sauvegardes) : anciennes sauvegardes intactes, appli utilisable
    PLEIN="(()=>{const f=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){if(/:bak/.test(k))throw new DOMException('plein','QuotaExceededError');return f.call(this,k,v)}})()"
    se=Session({"cast:x1":ACTUEL,K("bak"):VIEUX,K("bakJ"):VIEUX,K("bakJ:jour"):"2026-11-01"});o=se.ouvrir(J1,init=PLEIN)
    ck("échec d'écriture : :bak et :bakJ antérieures intactes, échec signalé dans PBAK, profil chargé normalement",
       o["bak"]==VIEUX and o["bakJ"]==VIEUX and o["jour"]=="2026-11-01" and o["PBAK"]=={"bak":"échec","bakJ":"échec"} and o["lock"] is None and o["xp"]==40 and not se.err,o)
    o=se.ouvrir(J1b,init="0")
    ck("après l'échec, ouverture suivante sans problème de stockage : sauvegardes faites (le jour n'avait pas été marqué)",o["bak"]==ACTUEL and o["bakJ"]==ACTUEL and o["jour"]=="2026-11-08",o)
    se.close()
    # ---- 8. échec de relecture (copie incomplète écrite) : l'ancienne valeur est remise
    TRONQUE='(()=>{const q=String.fromCharCode(34),f=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){if(/:bak(J)?$/.test(k)&&String(v).includes(q+"xp"+q+": 40"))return f.call(this,k,String(v).slice(0,60));return f.call(this,k,v)}})()'
    se=Session({"cast:x1":ACTUEL,K("bak"):VIEUX,K("bakJ"):VIEUX,K("bakJ:jour"):"2026-11-01"});o=se.ouvrir(J1,init=TRONQUE)
    ck("copie incomplète à la relecture : ancienne :bak et :bakJ remises à l'identique, jour non marqué",
       o["bak"]==VIEUX and o["bakJ"]==VIEUX and o["jour"]=="2026-11-01" and o["PBAK"]=={"bak":"échec","bakJ":"échec"} and o["lock"] is None and not se.err,o)
    se.close()
    se=Session({"cast:x1":ACTUEL});o=se.ouvrir(J1,init=TRONQUE)
    ck("copie incomplète sans sauvegarde antérieure : la copie tronquée est retirée (aucune :bak / :bakJ)",
       o["PBAK"]=={"bak":"échec","bakJ":"échec"} and o["bak"] is None and o["bakJ"] is None and o["lock"] is None,o)
    vals=se.pg.evaluate("async()=>(await pCopies('x1')).length")
    ck("… et elle n'est jamais proposée à la restauration",vals==0,vals)
    se.close()
    # ---- 9. échec de l'enregistrement du jour : :bakJ correcte, nouvelle tentative à l'ouverture suivante
    JOUR="(()=>{const f=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){if(/:jour$/.test(k))throw new DOMException('plein','QuotaExceededError');return f.call(this,k,v)}})()"
    se=Session({"cast:x1":ACTUEL});o=se.ouvrir(J1,init=JOUR)
    ck("échec de l'enregistrement du jour : :bakJ écrite et valide, échec signalé, pas de jour enregistré",o["bakJ"]==ACTUEL and o["jour"] is None and o["PBAK"]["bakJ"]=="échec (jour)",o)
    se.close()
    # ---- 10. profil absent : aucune sauvegarde
    se=Session({});o=se.ouvrir(J1)
    ck("profil absent : aucune sauvegarde créée",o["bak"] is None and o["bakJ"] is None and o["lock"] is None,o)
    se.close()
    b.close()
print(f"\n{sum(R)}/{len(R)} contrôles OK");sys.exit(0 if all(R) else 1)
