# Compatibilité des profils « cast:<id> » écrits par d'anciennes versions de la PWA, relus par la version actuelle.
# Les anciennes versions sont reconstruites depuis l'historique git dans un dossier temporaire (le dépôt n'est pas modifié),
# servies sur la même origine que la version actuelle (/new/), donc avec le même stockage.
# Usage : python3 tests/compat_profils.py [commit ...]      (depuis la racine du dépôt ; historique git complet nécessaire)
import sys,os,json,subprocess,tempfile,time,socket
from playwright.sync_api import sync_playwright
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERS=sys.argv[1:] or ["15a773a","fb1accd","88ce4c0"]   # 1re PWA (10/10) ; parcours v2 ; profil adaptatif (25/10)
R=[]
def ck(n,c,info=""):
    R.append(bool(c));print(("OK  " if c else "FAIL")+" "+n+("" if c else "  "+str(info)[:600]),flush=True)
tmp=tempfile.mkdtemp(prefix="sob-compat-")
os.symlink(ROOT,os.path.join(tmp,"new"))
for c in VERS:
    d=os.path.join(tmp,c);os.makedirs(d)
    for f in ["index.html","config.js","shim.js","manifest.webmanifest"]:
        try:open(os.path.join(d,f),"wb").write(subprocess.check_output(["git","-C",ROOT,"show",c+":"+f],stderr=subprocess.DEVNULL))
        except subprocess.CalledProcessError:pass
    cf=os.path.join(d,"config.js")
    if os.path.exists(cf):open(cf,"w").write("window.SOB_AI=\"\";window.SOB_PUSH=\"\";\n")
    for x in ["tr","a","v"]:os.symlink(os.path.join(ROOT,x),os.path.join(d,x))
s=socket.socket();s.bind(("127.0.0.1",0));PORT=s.getsockname()[1];s.close()
srv=subprocess.Popen([sys.executable,os.path.join(ROOT,"tests","rangesrv.py"),str(PORT),tmp],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);time.sleep(1)
B=f"http://127.0.0.1:{PORT}/"
SIM="""async()=>{auth('reg');await new Promise(r=>setTimeout(r,300));document.getElementById('u').value='ancien';document.getElementById('p').value='motdepasse1';await sub('reg');await new Promise(r=>setTimeout(r,800));
 S.lvl=1;try{build()}catch(e){}
 const one=async()=>{let pid=null;try{const pl=(typeof pathPlanMain==='function'?pathPlanMain():pathPlan());const f=(pl.flat||pl.units.flatMap(u=>u.steps)).find(x=>!x.test);pid=f&&f.id}catch(e){}
   start('Mélange',null,pid);for(let i=0;i<12;i++){await new Promise(r=>setTimeout(r,250));if(document.querySelector('.end'))break;try{if(!R.done)fin(true,'',R.q&&R.q.key)}catch(e){}try{adv()}catch(e){}}};
 await one();try{setLang('ca')}catch(e){}await one();try{setLang('es')}catch(e){}save();return S.xp}"""
LIRE="()=>({lock:PLOCK&&PLOCK.c,rec:!!document.getElementById('prec'),U,xp:S.xp,lang:S.lang,lvl:S.lvl,pth:Object.keys(S.pth||{}).length,PL:Object.keys(S.PL||{}).sort(),sc:Object.keys(S.sc||{}).length})"
try:
    with sync_playwright() as p:
        b=p.chromium.launch()
        for c in VERS:
            # 1. profil écrit par l'ancienne version
            ctx=b.new_context(locale="fr-FR");pg=ctx.new_page();pg.goto(B+c+"/index.html");pg.wait_for_timeout(3500)
            pg.evaluate(SIM);pg.wait_for_timeout(500)
            raw=pg.evaluate("()=>localStorage.getItem('cast:ancien')");o=json.loads(raw)
            stt=ctx.storage_state();ctx.close()
            # 2. relu par la version actuelle, dans un contexte neuf (même origine, même stockage)
            ctx=b.new_context(locale="fr-FR",storage_state=stt);pg=ctx.new_page();err=[];pg.on("pageerror",lambda e:err.append(str(e)[:150]))
            pg.goto(B+"new/index.html");pg.wait_for_timeout(4000)
            k=pg.evaluate("(r)=>classProfil(r).c",raw);st=pg.evaluate(LIRE)
            same=st["xp"]==o.get("xp") and st["lang"]==o.get("lang") and st["lvl"]==o.get("lvl") and st["pth"]==len(o.get("pth") or {}) and st["PL"]==sorted((o.get("PL") or {}).keys()) and st["sc"]==len(o.get("sc") or {})
            ck(f"{c} : profil classé « {k} », chargé sans verrou ni écran de récupération, XP / langue / niveau / étapes / langues / mots identiques",
               k=="actuel" and st["lock"] is None and not st["rec"] and st["U"]=="ancien" and same and not err,{"k":k,"st":st,"o":{x:o.get(x) for x in("xp","lang","lvl","v")},"err":err})
            pg.evaluate("()=>save()");n=json.loads(pg.evaluate("()=>localStorage.getItem('cast:ancien')"))
            perdus=sorted(set(o)-set(n));chg=[x for x in o if x not in("t","pmv","pth") and n.get(x)!=o[x]]
            brut=pg.evaluate("()=>Object.keys(localStorage).filter(k=>k.startsWith('cast:ancien:brut:'))")
            bk=pg.evaluate("()=>[localStorage.getItem('cast:ancien:bak'),localStorage.getItem('cast:ancien:bakJ')]")
            ck(f"{c} : réécrit par la version actuelle sans champ perdu ni modifié ; aucune copie brute (profil actuel) ; :bak et :bakJ = profil de l'ancienne version, à l'identique",
               not perdus and not chg and brut==[] and bk==[raw,raw] and not err,{"perdus":perdus,"modifiés":chg,"copies brutes":brut,"bak identiques":[x==raw for x in bk],"err":err})
            # 3. restauration : le même profil, gardé en copie, restauré après une corruption
            pg.evaluate("(r)=>{localStorage.setItem('cast:ancien','{corrompu');localStorage.setItem('cast:ancien:copie-test',r)}",raw)
            pg.reload();pg.wait_for_timeout(3000);rec=pg.evaluate("()=>!!document.getElementById('prec')")
            pg.on("dialog",lambda d:d.accept());pg.get_by_text("Restaurer la copie du").first.click();pg.wait_for_timeout(1500)
            st2=pg.evaluate(LIRE);cur=pg.evaluate("()=>localStorage.getItem('cast:ancien')")
            kept=pg.evaluate("()=>Object.keys(localStorage).filter(k=>k.startsWith('cast:ancien:brut:corrompu:')).map(k=>localStorage.getItem(k))")
            ck(f"{c} : profil corrompu → écran de récupération ; la copie de ce profil est restaurée à l'identique, l'original illisible est conservé",
               rec and st2["lock"] is None and st2["xp"]==o.get("xp") and st2["PL"]==st["PL"] and cur==raw and kept==["{corrompu"] and not err,{"rec":rec,"st2":st2,"kept":kept,"err":err})
            ctx.close()
        b.close()
finally:
    srv.terminate()
    for c in VERS:
        for x in os.listdir(os.path.join(tmp,c)):os.remove(os.path.join(tmp,c,x))
        os.rmdir(os.path.join(tmp,c))
    os.remove(os.path.join(tmp,"new"));os.rmdir(tmp)
print(f"\n{sum(R)}/{len(R)} contrôles OK");sys.exit(0 if all(R) else 1)
