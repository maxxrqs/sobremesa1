# Version PWA (index.html + service worker, comme sur GitHub Pages) : installation du service worker, fonctionnement
# hors ligne, carnet de maîtrise et séance « Réviser » sur la version servie par le service worker, en français et en anglais.
# Usage : python3 tests/pwa_carnet.py URL
import sys
from playwright.sync_api import sync_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else "http://127.0.0.1:8774/"
R=[]
def ck(n,c,i=""):R.append(bool(c));print("OK  " if c else "FAIL",n,"" if c else str(i)[:500],flush=True)
with sync_playwright() as p:
    b=p.chromium.launch()
    for loc in ["fr-FR","en-US"]:
        c=b.new_context(service_workers="allow",locale=loc,viewport={'width':390,'height':844},is_mobile=True,has_touch=True);pg=c.new_page()
        errs=[];pg.on("pageerror",lambda e:errs.append(str(e)));ev=pg.evaluate
        pg.goto(BASE+"index.html");pg.wait_for_timeout(2500)
        ev("async()=>{await navigator.serviceWorker.ready}");pg.reload();pg.wait_for_timeout(2500)
        st=ev("async()=>{const r=await navigator.serviceWorker.getRegistration();return {ctl:!!navigator.serviceWorker.controller,sw:r&&r.active&&r.active.scriptURL,mk:typeof mkRec,ad:typeof adLoad,ver:(await fetch('sw.js').then(r=>r.text())).match(/V=\"([^\"]+)/)[1]}}")
        ck(f"[{loc}] PWA : service worker actif et contrôlant la page, carnet et adaptation présents dans la version servie",st["ctl"] and st["sw"] and st["sw"].endswith("sw.js") and st["mk"]=="function" and st["ad"]=="function",st)
        c.set_offline(True);pg.reload();pg.wait_for_timeout(3000)
        ok=ev("()=>typeof S==='object'&&!!document.getElementById('app')&&document.getElementById('app').children.length>0")
        ck(f"[{loc}] PWA hors ligne : l'appli se recharge depuis le cache",ok)
        r=ev("""()=>{S.lang='es';S.lvl=2;S.ob=0;build();XDIRTY=1;xens();S.sr={};S.sc={};home();start('Mélange');const out={};
            for(const ty of ['exM','exc','conj','es2fr']){let q=null;for(let i=0;i<10&&!q;i++)q=mkQ(ty,0);if(!q||!q.key){out[ty]='-';continue}R.q=q;show();if(q.o)ans(q.o.indexOf(q.g));else fin(true,q.g,q.key);out[ty]=(S.sr[q.key]||{}).p;R.done=true;R.n++;next()}
            const ks=Object.keys(S.sr);ks.forEach(k=>S.sr[k].d=dayN()-1);const n=mkDueN();tools();const btn=[...document.querySelectorAll('button')].find(b=>/start\\('Révision'\\)/.test(b.getAttribute('onclick')||''));
            start('Révision');const got=[];for(let i=0;i<10&&R.q;i++){if(R.q.rvw)got.push(R.q.key.split(':')[0].length<3&&R.q.key.includes(':')?R.q.key.slice(0,2):'mot');R.done=true;R.n++;if(R.n>=10)break;next()}home();
            return {out,n,att:ks.length,btn:btn&&btn.textContent,got}}""")
        ck(f"[{loc}] PWA hors ligne : réponses enregistrées dans le carnet (expression, grammaire, conjugaison, mot)",all(isinstance(v,int) and v>=1 for v in r["out"].values()),r["out"])
        ck(f"[{loc}] PWA hors ligne : compteur « À revoir » et séance « Réviser » couvrent les 4 catégories",r["n"]==r["att"] and str(r["n"]) in (r["btn"] or "") and len(r["got"])==r["att"],r)
        # chantier 2 : consolidation proposée sur la version servie, hors ligne, dans la langue de l'interface
        r=ev("""()=>{S.lang='es';S.lvl=1;PLC=null;build();XDIRTY=1;xens();S.sr={};S.sc={};S.cns={};S.pth={};S.pthAll=0;
            const it=pathItems().find(x=>!x.done&&!x.lock&&!x.test),st=pathPlan().map[it.id];if(!st.nw)return {skip:it.id};
            ALL.filter(w=>(w[2]||1)===1).slice(0,10).forEach(w=>S.sr[w[0]]={b:0,d:dayN()+1,p:1,m:1,c:[1,0,0,0],n:1,k:0,s:dayN()});
            pstart(it.id);const t=document.querySelector('.cns h2'),bs=[...document.querySelectorAll('.cns .btn')].map(b=>b.textContent);consStart(it.id);const q=R.q&&R.q.rvw;
            return {h:t&&t.textContent,bs,cons:R.t,rv:!!q}}""")
        att="Let's consolidate first" if loc=="en-US" else "On consolide d'abord"
        ck(f"[{loc}] PWA hors ligne : consolidation proposée avant les nouveautés, traduite, et lancée",r.get("skip") or (r["h"]==att and len(r["bs"])==2 and r["cons"]=="Consolidation" and r["rv"]),r)
        ev("()=>{S.cns={};S.sr={};save()}");pg.wait_for_timeout(600);c.set_offline(False)
        ck(f"[{loc}] aucune erreur JavaScript",not errs,errs[:3])
        c.close()
    b.close()
print(sum(R),"/",len(R),"OK");sys.exit(0 if all(R) else 1)
