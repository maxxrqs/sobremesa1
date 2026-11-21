# Chantier 3, lot D : paires de notions à distinguer (XK) et astuces des 5 langues.
# Contrôles : données (tools/xk_build.py --check), niveaux, exemples et formes introduits au plus tard au niveau de la paire,
# ouverture selon la progression réellement effectuée, confusion précise en correction (priorité 1, une fois par séance),
# différence d'usage sur réponse juste (une seule fois, budget des astuces), carnet intact (aucune entrée, aucune date),
# rendu dans les 5 interfaces, écran 360 × 640 (explication ouverte bornée, « Continuer » atteignable),
# astuces : déclencheurs présents dans le parcours et introduits au plus tard au niveau de l'astuce.
# Usage : python3 tests/xk.py [URL]   (serveur : python3 tests/rangesrv.py 8774 .)
import sys,json,subprocess,os,re
from playwright.sync_api import sync_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else "http://127.0.0.1:8774/"
R=[]
def ck(n,c,i=""):R.append(bool(c));print("OK  " if c else "FAIL",n,"" if c else str(i)[:800],flush=True)
LANGS=["es","va","ca","gl","eu"];UIS=["fr","en","de","it","pt"]
H=r"""
window.SET_=(l,L)=>{S.lang=l;S.lvl=L;S.ob=0;build();XDIRTY=1;xens();XPWC=null;PLC=null;for(const k in XKC)delete XKC[k]};
window.PROG_=r=>{S.pth={};S.pa={};const pl=pathPlanMain();pl.flat.forEach(x=>{if(x.rk!=null&&x.rk<=r&&!x.opt)S.pth[pthK(x.id)]=8})};
/* tout le parcours effectué, niveaux 1 à 5 (étapes de nouveautés et tests), puis retour au niveau demandé */
window.ALLDONE_=()=>{const l=S.lang,L0=S.lvl;S.pth={};S.pa={};for(let L=1;L<=5;L++){S.lvl=L;build();XDIRTY=1;xens();PLC=null;pathPlanMain().flat.forEach(x=>{if(!x.opt)S.pth[pthK(x.id)]=8})}S.lvl=L0;build();XDIRTY=1;xens();PLC=null};
window.ENT_=(k,p)=>{const d=mkDif(k),c=[1,2,3,4].map(P=>P<=p?MKN[d][P]:0);S.sr[k]={b:1,d:dayN()+5,p,m:1,c,n:3,k:0,s:dayN()-2};if(d===3)S.sr[k].j=[0,0,0,0];return S.sr[k]};
window.SEANCE_=()=>{R={mode:"learn",n:0,ok:0,xp:0,xpi:new Set(),xpn:0,tpn:0,tc:0,tpl:null}};
0;
"""
R0=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rc=subprocess.run([sys.executable,os.path.join(R0,"tools","xk_build.py"),"--check"]).returncode
ck("castellano.html à jour avec tools/xk_data.txt",rc==0)
with sync_playwright() as p:
    b=p.chromium.launch();ERR=[]
    def page(ui="fr",w=420,h=900):
        c=b.new_context(service_workers="block",viewport={"width":w,"height":h},locale={"fr":"fr-FR","en":"en-GB","de":"de-DE","it":"it-IT","pt":"pt-PT"}[ui])
        pg=c.new_page();pg.on("pageerror",lambda e:ERR.append(str(e)));pg.goto(BASE+"index.html");pg.wait_for_timeout(2500);pg.evaluate(H);return pg
    pg=page();ev=pg.evaluate
    # 1. données : niveaux, exemples et formes introduits au plus tard au niveau de la paire
    for l in LANGS:
        d=ev("""l=>{SET_(l,5);const ks=xkP(l),bad=[];const ids=new Set();
          ks.forEach(k=>{if(ids.has(k.id))bad.push(k.id+' doublon');ids.add(k.id);if(!(k.l>=2&&k.l<=5))bad.push(k.id+' niveau');if(!k.a.length||!k.b.length)bad.push(k.id+' formes');
            const lim=k.l*1000+999;[[k.ea,k.fa],[k.eb,k.fb]].forEach(([t,fr])=>{const q=pqRank(t,fr,1);if(q.r===Infinity||q.bad.length||q.r>lim)bad.push(k.id+' exemple «'+t+'» '+q.r)});
            const E1=EV.raw(k.ea).split(' '),E2=EV.raw(k.eb).split(' ');const [a1,b1]=xkHas(E1,k),[a2,b2]=xkHas(E2,k);if(!(a1&&!b1))bad.push(k.id+' exemple A sans forme A');if(!(b2&&!a2))bad.push(k.id+' exemple B sans forme B');
            [...k.a,...k.b].forEach(f=>{const q=pqRank(f.join(' '),'',1);if(q.r===Infinity||q.r>lim)bad.push(k.id+' forme '+f.join(' ')+' '+q.r)})});
          return {n:ks.length,bad}}""",l)
        ck(f"{l} : {d['n']} paires XK, niveaux A2–C1, exemples et formes introduits au plus tard au niveau de la paire, chaque exemple illustre sa notion",d["n"]>=7 and not d["bad"],d["bad"])
    # 2. ouverture selon la progression réellement effectuée (même règle que les situations)
    for l in LANGS:
        d=ev("""l=>{SET_(l,5);S.sr={};S.sc={};S.pth={};S.pa={};const ks=xkP(l);ks.forEach(k=>delete k.rk);const f0=ks.filter(k=>xkKnown(k)).length;
          ALLDONE_();const f1=ks.filter(k=>xkKnown(k)).length;
          SET_(l,1);ALLDONE_();const lv1=ks.filter(k=>xkFind({},k.ea,'',0)).length;
          return {f0,f1,n:ks.length,lv1}}""",l)
        ck(f"{l} : paires fermées au départ ({d['f0']}/{d['n']}), toutes ouvertes une fois le parcours effectué ({d['f1']}/{d['n']}), aucune au niveau A1",d["f0"]==0 and d["f1"]==d["n"] and d["lv1"]==0,d)
    # 3. correction : confusion précise → explication de la paire (priorité 1), une fois par séance ; rien sans confusion
    for l in LANGS:
        d=ev("""l=>{SET_(l,5);ALLDONE_();const out=[];
          for(const k of xkP(l)){SEANCE_();S.sr={};S.tp={};const A=k.a.flat?k.a:[];const fa=k.a[0].join(' '),fb=k.b[0].join(' ');
            const re=new RegExp('(^|[^\\\\p{L}])('+k.a.map(f=>f.join(' ')).sort((x,y)=>y.length-x.length).map(x=>x.replace(/[.*+?^${}()|[\\]\\\\]/g,'\\\\$&')).join('|')+')(?=$|[^\\\\p{L}])','iu');
            const low=k.ea.toLowerCase(),wrong=k.ea.replace(re,(m,p1)=>p1+fb);
            const q={ty:'type',es:k.ea,sol:k.ea,key:null};
            const X=xpl(q,0,null,0,k.ea,wrong),X2=(X&&xpMark(X),xpl(q,0,null,0,k.ea,wrong)),Y=xpl(q,0,null,0,k.ea,k.ea.replace(/\\S+$/,'zzz'));
            out.push({id:k.id,wrong,X:X&&X.id,pr:X&&X.pr,X2:X2&&X2.id,Y:Y&&Y.id})}
          return out}""",l)
        bad=[x for x in d if x["X"]!="k:"+x["id"] or x["pr"]!=1 or x["X2"]==x["X"] or (x["Y"] or "").startswith("k:")]
        ck(f"{l} : confusion entre les deux notions → explication de la paire (priorité 1), pas deux fois dans la séance, rien pour une autre erreur ({len(d)} paires)",not bad,bad)
    # 4. réponse juste : différence d'usage proposée une seule fois (marque S.tp existante), dans le budget des astuces, palier ≤ 2
    d=ev("""()=>{SET_('es',5);ALLDONE_();SEANCE_();S.sr={};S.tp={};const k=xkP('es').find(z=>z.id==='porpara');const q={ty:'type',es:'Trabajo para una empresa.',key:null};
      const a=xpl(q,1,null,0,q.es,q.es);if(a)xpMark(a);R.tc=9;const b2=xpl(q,1,null,0,q.es,q.es);SEANCE_();const c=xpl(q,1,null,0,q.es,q.es);
      SEANCE_();S.tp={};const p4=xpl(q,1,null,4,q.es,q.es);SEANCE_();S.tp={};R.tpn=2;const bud=xpl(q,1,null,0,q.es,q.es);
      return {a:a&&[a.id,a.pr],b2:b2&&b2.id,c:c&&c.id,p4:p4&&p4.id,bud:bud&&bud.id,tp:Object.keys(S.tp)}}""")
    ck("réponse juste : différence d'usage une seule fois (aussi après une nouvelle séance), jamais si la notion est maîtrisée ni hors budget des astuces",d["a"]==["k:porpara",4] and d["b2"] is None and d["c"] is None and d["p4"] is None and d["bud"] is None,d)
    # 5. carnet : aucune entrée créée, aucune date modifiée par une explication de paire
    d=ev("""()=>{SET_('es',5);ALLDONE_();SEANCE_();S.sr={};S.tp={};ENT_('trabajo',1);const b0=JSON.stringify(S.sr);const q={ty:'type',es:'Trabajo para una empresa.',key:'trabajo'};
      const X=xpl(q,0,null,1,q.es,'Trabajo por una empresa.');if(X)xpMark(X);const e=S.sr.trabajo,b=JSON.parse(b0).trabajo;
      return {X:X&&X.id,keys:Object.keys(S.sr),d:e.d===b.d&&e.b===b.b&&e.s===b.s&&e.p===b.p,x:e.x===dayN()}}""")
    ck("carnet : explication de paire sans entrée créée ni date modifiée (seul le champ x de la notion existante est noté)",d["X"]=="k:porpara" and d["keys"]==["trabajo"] and d["d"] and d["x"],d)
    # 6. parcours réel : réponse tapée fausse → « Pourquoi ? » avec la paire ; choix multiple → réponse retenue transmise
    d=ev("""()=>{SET_('es',5);ALLDONE_();S.sr={};S.tp={};start('Mélange');R.xpi=new Set();R.xpn=0;R.tpn=0;R.tc=0;R.tpl=null;
      R.q={ty:'type',es:'Gracias por tu ayuda.',sol:'Gracias por tu ayuda.',fr:'Merci pour ton aide.',key:null};R.done=false;draw();const i=document.getElementById('ti');if(!i)return {noti:1};i.value='Gracias para tu ayuda.';chkT();
      const h=(document.querySelector('#fb .whyb')||{}).innerHTML||'';
      start('Mélange');R.xpi=new Set();R.xpn=0;R.q={ty:'exc',key:null,g:'para',o:['para','por','de','en'],h:'Trabajo ___ una empresa.',sol:'Trabajo para una empresa.'};R.done=false;draw();ans(1);
      const h2=(document.querySelector('#fb .whyb')||{}).innerHTML||'';return {h:h.slice(0,120),ok:h.includes('para / por'),ok2:h2.includes('para / por'),ua:R.ua}}""")
    ck("parcours : réponse tapée (« para » au lieu de « por ») et choix multiple (« por » au lieu de « para ») → explication de la paire sous « Pourquoi ? »",d.get("ok") and d.get("ok2") and d.get("ua") is None,d)
    # 7. interfaces : explication et exemples traduits ; écran 360 × 640
    for ui in UIS:
        pg2=page(ui,360,640)
        d=pg2.evaluate("""async (ui)=>{UI=ui;await trLoad(ui);const o={miss:[],fr:[]};for(const l of ["es","va","ca","gl","eu"]){SET_(l,5);for(const k of xkP(l)){[k.x,k.fa,k.fb].forEach(t=>{if(ui!=='fr'&&gl(t)===t)o.miss.push(l+':'+t.slice(0,40))})}}
          SET_('gl',5);ALLDONE_();S.sr={};S.tp={};start('Mélange');R.xpi=new Set();R.xpn=0;R.tpn=0;R.tc=0;R.tpl=null;const k=xkP('gl').find(z=>z.id==='saberconocer');
          R.q={ty:'type',es:'Coñezo o teu irmán.',sol:'Coñezo o teu irmán.',key:null};R.done=false;draw();document.getElementById('ti').value='Sei o teu irmán.';chkT();
          await new Promise(r=>setTimeout(r,400));const s=document.querySelector('#fb details.why summary');if(!s)return Object.assign(o,{nosum:1});s.click();await new Promise(r=>setTimeout(r,700));
          const bt=document.querySelector('#fb .btn').getBoundingClientRect(),w=document.querySelector('#fb .whyb').getBoundingClientRect();
          return Object.assign(o,{wb:Math.round(w.height),b:Math.round(bt.bottom),h:innerHeight,sw:document.documentElement.scrollWidth,txt:document.querySelector('#fb .whyb').innerText.slice(0,90)})}""",ui)
        pg2.context.close()
        ck(f"interface {ui} : explications et exemples des paires traduits ; 360 × 640 : explication ouverte bornée, « Continuer » atteignable, pas de débordement",not d["miss"] and not d.get("nosum") and d["wb"]<=0.36*640 and d["b"]<=d["h"]+1 and d["sw"]<=360,d)
    # 8. astuces : 5 langues, déclencheurs présents dans le parcours, introduits au plus tard au niveau de l'astuce, traduits
    d=ev("""async ()=>{const o={};for(const l of ["es","va","ca","gl","eu"]){SET_(l,5);const pd=pqData(1),idx=new Map();pd.WR.forEach(([w,r])=>{const k=tpN(w[0]);if(!idx.has(k)||idx.get(k)>r)idx.set(k,r)});pd.XR.forEach(([x,r])=>{const k=tpN(x.e);if(!idx.has(k)||idx.get(k)>r)idx.set(k,r)});
        const bad=[];(TIPS[l]||[]).forEach(t=>{const g=tpN(t[0]);let r=idx.get(g);if(r==null&&g.includes(' '))for(const [k,v] of idx)if((' '+k+' ').includes(' '+g+' ')&&(r==null||v<r))r=v;if(r==null){const q=pqRank(t[0],t[2],1);r=q.r}if(r==null||r===Infinity||Math.floor(r/1000)>t[1])bad.push(t[0]+' '+r)});
        o[l]={n:(TIPS[l]||[]).length,lv:[1,2,3,4,5].map(L=>(TIPS[l]||[]).filter(t=>t[1]===L).length),bad}}
      const miss={};for(const ui of ["en","de","it","pt"]){await trLoad(ui);UI=ui;miss[ui]=Object.values(TIPS).flat().filter(t=>gl(t[2])===t[2]).map(t=>t[0])}UI='fr';return {o,miss}}""")
    ck("astuces : "+", ".join(f"{l} {v['n']}" for l,v in d["o"].items())+" ; déclencheurs présents dans le parcours et introduits au plus tard au niveau de l'astuce",all(v["n"]>=20 and not v["bad"] for v in d["o"].values()),{l:v["bad"] for l,v in d["o"].items() if v["bad"]})
    ck("astuces : traduites dans les 4 autres interfaces",all(not m for m in d["miss"].values()),d["miss"])
    ck("aucune erreur JavaScript",not ERR,ERR[:3])
    b.close()
print(f"\n{sum(R)}/{len(R)} contrôles réussis")
sys.exit(0 if all(R) else 1)
