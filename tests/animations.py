# Animations (lot 1 : A1 B1 B2 C1 D1 H3) et orchestrateur SMAO : non-régression après la reprise de l'artefact et le chantier 2.
# Vérifie la présence des mécanismes, l'absence de déclenchements concurrents incompatibles, l'annulation des effets obsolètes
# au changement d'écran, l'absence de doublons et la tenue après des interactions rapides et répétées, y compris pendant une
# consolidation et une question de révision (chantier 2). Usage : python3 tests/animations.py URL
import sys
from playwright.sync_api import sync_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else "http://127.0.0.1:8774/"
R=[]
def ck(n,c,i=""):R.append(bool(c));print("OK  " if c else "FAIL",n,"" if c else str(i)[:600],flush=True)
H=r"""
window.LES_=()=>{S.lang='es';S.lvl=1;S.ob=0;PLC=null;build();XDIRTY=1;xens();S.sr={};S.sc={};S.cns={};S.pthAll=1;home();
  const id=pathItems().find(x=>!x.test&&pathPlan().map[x.id].nw&&pathPlan().map[x.id].ws).id;pstart(id);if(DISC)discGo();return id};
/* question à choix : on régénère jusqu'à en avoir une */
window.QCM_=()=>{for(let i=0;i<30;i++){if(R.q&&Array.isArray(R.q.o)&&R.q.o.length>1&&!R.q.void&&document.querySelectorAll('.q .opt').length)return true;R.q=mkQ(['es2fr','fr2es','listen'][i%3],0);show()}return false};
/* laisse passer les observateurs de l'écran qui vient d'être dessiné (comme entre deux gestes réels) */
window.TICK_=(ms)=>new Promise(r=>setTimeout(r,ms||30));
window.PLAYED_=()=>SMAO.played.map(x=>x[1]);
0;
"""
with sync_playwright() as p:
    b=p.chromium.launch();c=b.new_context(service_workers="block");pg=c.new_page()
    errs=[];pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.goto(BASE+"index.html");pg.wait_for_timeout(2500);ev=pg.evaluate;ev(H)
    # ---------- présence ----------
    r=ev("""()=>{const css=(document.getElementById('sm-anim')||{}).textContent||'';const cls=['.smW','.smFill','.smChk','.smKo','.smSol','.smOut','.smBarW','.smHd','.hop','.glow','.smFire','.smPt','.smBub'];
        return {css:cls.filter(k=>!css.includes(k)),js:!!document.getElementById('sm-anim-js'),smao:['say','once','clean','confRecent','holdToasts','rm'].filter(k=>typeof SMAO[k]!=='function'),
          draw:/barSetup/.test(String(window.draw)),fin:/SMAO\\.once/.test(String(window.fin)),end:/holdToasts/.test(String(window.end)),toasts:/unlOpen|hold/.test(String(window.toasts)),
          play:/celEnd|fbAt/.test(String(FX.play)),conf:/lastConf/.test(String(FX.confetti)),tr:[tr("Plus que 2 !"),tr("Tu l'as retenu ! 💪"),tr("On la reverra en révision 💪")].every(Boolean)}}""")
    ck("présence : styles du lot 1, orchestrateur SMAO, enveloppes de draw, fin, end, toasts, sons et confettis",not r["css"] and r["js"] and not r["smao"] and r["draw"] and r["fin"] and r["end"] and r["toasts"] and r["play"] and r["conf"] and r["tr"],r)
    # ---------- barre et mascotte ----------
    r=ev("""()=>{LES_();QCM_();draw();draw();return {w:document.querySelectorAll('.smBarW').length,hd:document.querySelectorAll('.smHd').length}}""")
    ck("barre : enveloppe et tête de mascotte posées une seule fois, même si l'écran est redessiné",r=={"w":1,"hd":1},r)
    # ---------- bonne réponse : effets une seule fois ----------
    r=ev("""()=>{LES_();QCM_();SMAO.played.length=0;const q=R.q;ans(q.o.indexOf(q.g));const a={chk:document.querySelectorAll('.smChk').length,fill:document.querySelectorAll('.smFill').length,pt:document.querySelectorAll('.smPt').length,good:PLAYED_().filter(k=>k==='good').length};
        fin(true,q.sol,q.key);fin(true,q.sol,q.key);const b={chk:document.querySelectorAll('.smChk').length,pt:document.querySelectorAll('.smPt').length,good:PLAYED_().filter(k=>k==='good').length};return {a,b,once:q._smfin}}""")
    ck("bonne réponse : ✓, remplissage, éclat et son joués une fois ; validation répétée sans aucun doublon",r["a"]["chk"]==1 and r["a"]["fill"]==1 and 0<r["a"]["pt"]<=12 and r["a"]["good"]==1 and r["b"]["chk"]==1 and r["b"]["pt"]==r["a"]["pt"] and r["b"]["good"]==1,r)
    # ---------- mauvaise réponse : effet différé annulé si l'écran change ----------
    r=ev("""async()=>{LES_();QCM_();await TICK_(60);const q=R.q;const bad=q.o.findIndex(x=>x!==q.g);ans(bad);const a={ko:document.querySelectorAll('.smKo').length,sol:document.querySelectorAll('.smSol').length,out:document.querySelectorAll('.smOut').length};
        await TICK_(1700);const bub=document.querySelectorAll('.smBub').length;fin(false,q.sol,q.key);fin(false,q.sol,q.key);await TICK_(1700);
        return {a,bub,out2:document.querySelectorAll('.smOut').length,ko2:document.querySelectorAll('.smKo').length,bub2:document.querySelectorAll('.smBub').length}}""")
    ck("mauvaise réponse : option pâlie, bonne réponse entourée une fois, bulle « On la reverra » une fois ; validation répétée sans doublon",r["a"]=={"ko":1,"sol":1,"out":1} and r["bub"]==1 and r["out2"]<=1 and r["ko2"]<=1 and r["bub2"]<=1,r)
    r=ev("""async()=>{LES_();QCM_();await TICK_();const q=R.q;ans(q.o.findIndex(x=>x!==q.g));adv();await new Promise(r=>setTimeout(r,1800));return {bub:document.querySelectorAll('.smBub').length,n:R.n}}""")
    ck("mauvaise réponse puis question suivante tout de suite : l'effet différé de l'ancienne question ne s'affiche pas sur la nouvelle",r["bub"]==0 and r["n"]==1,r)
    # ---------- changement d'écran ----------
    r=ev("""async()=>{LES_();QCM_();const q=R.q;ans(q.o.indexOf(q.g));const pt=document.querySelectorAll('.smPt').length;FX.confetti();const cf=document.querySelectorAll('body>.conf').length;
        R.n++;next();await TICK_();const pt2=document.querySelectorAll('.smPt').length,cf2=document.querySelectorAll('body>.conf').length;home();await new Promise(r=>setTimeout(r,50));
        return {pt,cf,pt2,cf2,ptH:document.querySelectorAll('.smPt').length,cfH:document.querySelectorAll('body>.conf').length}}""")
    ck("changement d'écran : éclats retirés à la question suivante, pluie conservée pendant la leçon puis retirée en la quittant",r["pt"]>0 and r["pt2"]==0 and r["cf"]==1 and r["cf2"]==1 and r["ptH"]==0 and r["cfH"]==0,r)
    # ---------- sons : concurrence, file, doublons ----------
    r=ev("""async()=>{home();await new Promise(r=>setTimeout(r,200));SMAO.played.length=0;FX.play('win');FX.play('win');FX.play('level');FX.play('streak');FX.play('level');
        const now=PLAYED_().slice();await new Promise(r=>setTimeout(r,3400));const all=SMAO.played.slice();
        SMAO.played.length=0;FX.play('win');FX.play('level');tools();await new Promise(r=>setTimeout(r,1600));const dropped=PLAYED_().slice();
        SMAO.played.length=0;FX.play('good');FX.play('good');FX.play('tap');await new Promise(r=>setTimeout(r,200));const fb=PLAYED_().slice();home();
        return {now,all:all.map(x=>x[1]),gap:all.length>1?all[1][0]-all[0][0]:0,dropped,fb}}""")
    ck("sons de fête : un seul à la fois, à la suite (file de 2 au plus), jamais le même deux fois",r["now"]==["win"] and r["all"]==["win","level","streak"] and r["gap"]>=1100,r)
    ck("son de fête en attente abandonné si l'écran change ; son de réponse unique, « tap » du même geste abandonné",r["dropped"]==["win"] and r["fb"]==["good"],r)
    # ---------- confettis ----------
    r=ev("""async()=>{LES_();QCM_();const n0=SMAO.nConf||0;FX.confetti();FX.confetti();FX.confetti();const n1=(SMAO.nConf||0)-n0,rain=document.querySelectorAll('body>.conf').length;
        const q=R.q;ans(q.o.indexOf(q.g));const pt=document.querySelectorAll('.smPt').length;home();return {n1,rain,pt}}""")
    ck("confettis : déclenchements rapprochés fusionnés en une seule pluie, pas d'éclat local par-dessus",r=={"n1":1,"rain":1,"pt":0},r)
    # ---------- bulle de la mascotte : priorités ----------
    r=ev("""()=>{LES_();QCM_();const box=document.querySelector('#app .lm');if(!box)return 'pas de mascotte';if(!box.querySelector('.mlb')){const s=document.createElement('span');s.className='mlb';box.appendChild(s)}
        const a=SMAO.say('A',1),b=SMAO.say('B',2),c=SMAO.say('C',1),t=box.querySelector('.mlb').textContent;
        R.n=8;R.smP2=0;draw();const cnt=()=>[...document.querySelectorAll('#app .lm .mlb')].filter(e=>e.textContent===tr("Plus que 2 !")).length;const p2=cnt();draw();const p2b=cnt();return {a,b,c,t,p2,p2b}}""")
    ck("bulle : priorité respectée (une bulle moins importante ne remplace pas la précédente), « Plus que 2 ! » une seule fois",isinstance(r,dict) and r["a"] and r["b"] and not r["c"] and r["t"]=="B" and r["p2"]==1 and r["p2b"]==0,r)
    # ---------- notifications retenues pendant « Unité débloquée » ----------
    r=ev("""async()=>{home();document.querySelectorAll('#toasts .toast').forEach(e=>e.remove());const u=document.createElement('div');u.id='unl';document.body.appendChild(u);await new Promise(r=>setTimeout(r,30));
        toasts(['x1','x2']);await new Promise(r=>setTimeout(r,700));const during=document.querySelectorAll('#toasts .toast').length;u.remove();await new Promise(r=>setTimeout(r,1300));
        return {during,after:document.querySelectorAll('#toasts .toast').length}}""")
    ck("notifications : retenues tant que « Unité débloquée » est ouverte, puis toutes affichées une fois",r=={"during":0,"after":2},r)
    # ---------- interactions rapides et répétées ----------
    r=ev("""async()=>{LES_();let maxRun=0,maxPt=0,dbl=0;const seen=[];for(let i=0;i<9;i++){QCM_();await TICK_(5);const q=R.q,n=R.n;const g=Math.random()<.7?q.o.indexOf(q.g):q.o.findIndex(x=>x!==q.g);
          ans(g);ans(g);fin(true);document.querySelectorAll('.q .opt').forEach(o=>o.click());
          const ra=document.getAnimations().filter(a=>a.playState==='running'&&!(a instanceof CSSAnimation)&&!(a instanceof CSSTransition)&&a.effect&&a.effect.target&&a.effect.target.isConnected&&a.effect.target.closest&&a.effect.target.closest('.smBarW')).map(a=>a.effect.getKeyframes()),wd=ra.filter(k=>k[0]&&k[0].width).length,hd=ra.filter(k=>k[0]&&/translateX/.test(k[0].transform||'')).length;maxRun=Math.max(maxRun,wd,hd);maxPt=Math.max(maxPt,document.querySelectorAll('.smPt').length);
          adv();adv();adv();await new Promise(r=>setTimeout(r,140));if(R.n!==n+1)dbl++;seen.push(R.n)}
        const w=parseFloat((document.querySelector('.smBarW .bar i')||{style:{}}).style.width)||0;return {maxRun,maxPt,dbl,seen,w,n:R.n,chk:document.querySelectorAll('.smChk').length}}""")
    ck("réponses et passages rapides répétés : une seule question avancée par geste, une seule animation de largeur de barre et un seul déplacement de la mascotte à la fois (les anciens annulés), éclats bornés",r["dbl"]==0 and r["n"]==9 and r["maxRun"]<=1 and r["maxPt"]<=12 and r["chk"]==0,r)
    # ---------- chantier 2 : consolidation et révision ----------
    r=ev("""async()=>{S.lang='es';S.lvl=1;PLC=null;build();XDIRTY=1;xens();S.sr={};S.sc={};S.cns={};S.pthAll=1;const ws=ALL.filter(w=>(w[2]||1)===1).slice(10,20);
        ws.forEach(w=>S.sr[w[0]]={b:1,d:dayN()+1,p:1,m:1,c:[1,0,0,0],n:2,k:0,s:dayN()});const id=pathItems().find(x=>!x.test&&pathPlan().map[x.id].nw&&pathPlan().map[x.id].ws).id;
        pstart(id);const offer=!!document.querySelector('.cns');consStart(id);const bar=document.querySelectorAll('.smBarW').length;let rv=0,ret=0;
        for(let i=0;i<10;i++){if(!R.q)break;if(R.q.rvw&&Array.isArray(R.q.o)&&document.querySelectorAll('.q .opt').length){rv++;ans(R.q.o.indexOf(R.q.g));if((document.querySelector('#app .lm .mlb')||{}).textContent===tr("Tu l'as retenu ! 💪"))ret++}
          R.done=true;R.n++;if(R.n<10)next()}await new Promise(r=>setTimeout(r,200));home();return {offer,bar,rv,ret}}""")
    ck("consolidation (chantier 2) : barre animée, bonne réponse à une révision saluée par « Tu l'as retenu ! »",r["offer"] and r["bar"]==1 and (r["rv"]==0 or r["ret"]>=1),r)
    ck("aucune erreur JavaScript",not errs,errs[:3])
    b.close()
print(sum(R),"/",len(R),"OK");sys.exit(0 if all(R) else 1)
