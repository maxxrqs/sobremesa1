# Parcours CECRL : structure des unités, déblocage du niveau, évaluation finale, conservation des progrès.
# Usage : python3 tests/path.py [url_base]   (compare avec l'ancien parcours via git si disponible)
import sys,json,subprocess,os,re,urllib.request
from playwright.sync_api import sync_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else "http://localhost:8772/"
OLD="596553d"   # dernier commit avec l'ancien parcours
R=[]
def ck(n,c,info=""):
    R.append(bool(c));print(("OK  " if c else "FAIL"),n,("" if c else str(info)[:600]),flush=True)
LANGS=["es","va","ca","gl","eu"]
ORACLE="""()=>{const o={};for(const lang of %s)for(let L=1;L<=5;L++){S.lang=lang;S.lvl=L;S.pth={};S.rat={};build();PLC=null;o[lang+L]=pathPlanMain().flat.map(x=>x.id)}return o}""" % json.dumps(LANGS)
with sync_playwright() as p:
    b=p.chromium.launch();ctx=b.new_context(locale="fr-FR");pg=ctx.new_page();err=[]
    pg.on("pageerror",lambda e:err.append(str(e)))
    # ---- ancien parcours (ids)
    old=None
    try:
        h=subprocess.run(["git","show",f"{OLD}:index.html"],capture_output=True,cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),check=True).stdout
        fn=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"_old_path_tmp.html");open(fn,"wb").write(h)
        po=ctx.new_page();po.goto(BASE+"_old_path_tmp.html");po.wait_for_timeout(2500);old=po.evaluate(ORACLE);po.close();os.remove(fn)
    except Exception as e:
        print("(ancien parcours indisponible :",str(e)[:80],")")
    pg.goto(BASE+"index.html");pg.wait_for_timeout(2500)
    new=pg.evaluate(ORACLE)
    # ---- A. structure
    st=pg.evaluate("""()=>{const bad=[];const need=["BR1","BR2","BCO","BCE","BEE","BEO","BM"];
      for(const lang of %s)for(let L=1;L<=5;L++){S.lang=lang;S.lvl=L;S.pth={};S.rat={};build();PLC=null;const pl=pathPlanMain(),tag=lang+L;
        const ids=pl.flat.map(x=>x.id);if(new Set(ids).size!==ids.length)bad.push([tag,'ids dupliqués']);
        if(pl.units.length!==7)bad.push([tag,'unités',pl.units.length]);
        pl.units.slice(0,6).forEach((u,i)=>{const t=u.steps.map(x=>x.id[0]);
          if(!t.includes('W'))bad.push([tag,i,'pas de découverte']);if(t.filter(c=>c==='K').length!==1)bad.push([tag,i,'compétence']);
          if(u.steps[u.steps.length-1].id[0]!=='M')bad.push([tag,i,'bilan pas en dernier']);
          if(t.indexOf('V')>t.indexOf('K'))bad.push([tag,i,'révision avant compétence']);
          if(!u.obj||!u.title)bad.push([tag,i,'objectif manquant'])});
        const last=pl.units[6].steps.map(x=>x.id);need.forEach(n=>{if(!last.includes(n))bad.push([tag,'consolidation sans',n])});
        const tests=pl.flat.filter(x=>x.test);if(L<5){if(tests.length!==1||pl.flat[pl.flat.length-1].id!=='TEST')bad.push([tag,'TEST'])}else if(tests.length)bad.push([tag,'TEST au niveau max']);
        if(L<2&&last.includes('listenT'))bad.push([tag,'x'])}
      return bad}""" % json.dumps(LANGS))
    ck("5 langues × 5 niveaux : 7 unités, découverte → compétence → bilan, consolidation complète, évaluation finale en dernier",not st,st[:5])
    cov=pg.evaluate("""()=>{const bad=[];for(const lang of %s)for(let L=1;L<=5;L++){S.lang=lang;S.lvl=L;S.pth={};build();PLC=null;const pl=pathPlanMain();
      const inPath=new Set(pl.flat.filter(x=>x.id[0]==='W').flatMap(x=>x.ws.map(w=>w[0])));
      const th=Object.keys(D);th.forEach((t,ti)=>{const nw=D[t].filter(w=>(w[2]||1)===L);if(nw.length>=4){const miss=nw.filter(w=>!inPath.has(w[0]));if(miss.length)bad.push([lang+L,t,miss.length])}})}return bad}""" % json.dumps(LANGS))
    ck("tout le vocabulaire du niveau est introduit dans une étape de découverte",not cov,cov[:5])
    cu=pg.evaluate("""()=>{const bad=[];for(const lang of %s)for(let L=1;L<=5;L++){S.lang=lang;S.lvl=L;S.pth={};build();PLC=null;const pl=pathPlanMain();
      const ws=pl.units.slice(0,6).map(u=>new Set(u.steps.find(x=>x.id[0]==='M').ws.map(w=>w[0])));
      for(let i=1;i<6;i++){const prevV=pl.units[i-1].steps.find(x=>x.id[0]==='V');if(prevV&&!prevV.ws.every(w=>ws[i].has(w[0])))bad.push([lang+L,i])}}return bad}""" % json.dumps(LANGS))
    ck("les bilans d'unité sont cumulatifs (reprennent les mots des unités précédentes)",not cu,cu[:5])
    # ---- B. conservation des progrès
    if old:
        lost=pg.evaluate("""(old)=>{const bad=[];for(const k of Object.keys(old)){const lang=k.slice(0,2),L=+k.slice(2);S.lang=lang;S.lvl=L;S.rat={};build();
          S.pth={};old[k].forEach(id=>{S.pth[pthK(id)]=8});PLC=null;const pl=pathPlanMain(),ids=new Set(pl.flat.map(x=>x.id));
          const miss=old[k].filter(id=>!ids.has(id)&&id!=='TEST');if(miss.length)bad.push([k,miss]);
          const it=pathItems();const notdone=it.filter(x=>!x.test&&old[k].includes(x.id)&&!x.done);if(notdone.length)bad.push([k,'non validées',notdone.length]);
          if(lvReady())bad.push([k,'niveau débloqué sans consolidation'])}return bad}""",old)
        ck("progrès existants : toutes les étapes déjà validées de l'ancien parcours restent validées (5 langues × 5 niveaux)",not lost,lost[:5])
        ncons=sum(1 for k in new if True)
        added=pg.evaluate("""()=>{S.lang='es';S.lvl=1;S.pth={};S.rat={};build();PLC=null;return pathPlanMain().flat.length}""")
        print("   (A1 castillan : ancien",len(old['es1']),"étapes →",added,")")
    # ---- C. déblocage du niveau
    g=pg.evaluate("""()=>{const o={};S.lang='es';S.lvl=1;S.rat={};S.lvSnz=0;build();PLC=null;S.sh={};S.sh['es:1']=[10,10,10,10,10];
      const pl=pathPlanMain(),main=pl.flat.filter(x=>!x.test);
      S.pth={};main.slice(0,12).forEach(x=>{S.pth[pthK(x.id)]=10});o.early=lvReady();                     // bon début, scores parfaits : ne suffit plus
      S.pth={};pl.units.slice(0,6).forEach(u=>u.steps.forEach(x=>{S.pth[pthK(x.id)]=9}));o.unitsOnly=lvReady();      // 6 unités validées, consolidation non faite
      S.pth={};main.forEach(x=>{S.pth[pthK(x.id)]=6});o.all=lvReady();
      S.lvSnz=Date.now()+1e6;o.snooze=lvReady();S.lvSnz=0;
      S.pth={};main.forEach(x=>{S.pth[pthK(x.id)]=5});o.fail=lvReady();
      S.pth={};main.forEach(x=>{S.pth[pthK(x.id)]=6});const last=main[main.length-1];S.pth[pthK(last.id)]=0;o.oneMissing=lvReady();
      S.lvl=5;S.pth={};build();PLC=null;pathPlanMain().flat.forEach(x=>{S.pth[pthK(x.id)]=9});o.max=lvReady();
      return o}""")
    ck("niveau non proposé après un bon début, ni après les 6 unités sans la consolidation",g['early'] is False and g['unitsOnly'] is False,g)
    ck("niveau proposé uniquement quand TOUTES les étapes sont validées (≥ 6/10) ; pas avec 5/10 ni s'il en manque une ; « plus tard » respecté ; jamais au niveau max",g['all'] is True and g['fail'] is False and g['oneMissing'] is False and g['snooze'] is False and g['max'] is False,g)
    # ---- D. évaluation finale
    e=pg.evaluate("""()=>{const o={};
      const mk=(from,cap,pass,sc)=>{S.lang='es';S.lvl=from;S.rat={};S.lvSnz=0;build();PLC=null;R={mode:'test'};T={l:from,list:[],i:0,p:0,m:0,skip:0,skipAll:0,res:{},pass,k:{},from,cap};T.res[from]={sc,n:10};if(pass)T.pass=pass};
      // 1. évaluation finale réussie : passe d'UN niveau exactement, sans enchaîner un test du niveau suivant
      mk(1,1,1,.8);T.l=1;T.m=10;T.p=8;T.list=[];tstage();o.capOk=[S.lvl,T.l,document.body.innerText.includes('Niveau validé')];
      // 2. réussite juste (60-74 %) : le niveau est quand même validé
      mk(2,1,2,.65);T.l=2;T.m=10;T.p=6.5;T.list=[];tstage();o.capJuste=S.lvl;
      // 3. échec : le niveau reste le même
      mk(1,1,0,.4);T.l=1;T.m=10;T.p=4;T.list=[];tstage();o.capKo=S.lvl;
      // 4. test de placement (sans cap) : inchangé, peut valider plusieurs paliers
      S.lang='es';S.lvl=1;build();R={mode:'test'};T={l:3,list:[],i:0,p:0,m:0,skip:0,skipAll:0,res:{1:{sc:.9,n:5},2:{sc:.9,n:5},3:{sc:.9,n:5}},pass:3,k:{},from:0,cap:0};tend();o.place=S.lvl;
      return o}""")
    ck("évaluation finale réussie : +1 niveau exactement, écran « Niveau validé »",e['capOk'][0]==2 and e['capOk'][1]==1 and e['capOk'][2],e)
    ck("évaluation finale réussie à 65 % : niveau validé ; échec à 40 % : niveau inchangé",e['capJuste']==3 and e['capKo']==1,e)
    ck("test de placement initial inchangé (palier 3 validé à 90 % → niveau 4)",e['place']==4,e)
    src=urllib.request.urlopen(BASE+"index.html").read().decode("utf8")
    ctx_=[src[m.start()-30:m.start()+70] for m in re.finditer(r"S\.lvl=",src)]
    okc=[any(k in c for k in ("T.cap","o.lvl||0","obNext()")) for c in ctx_]
    ck(f"le niveau ne change qu'à {len(ctx_)} endroits : fin d'une évaluation, chargement du profil, « Je débute » à l'accueil",len(ctx_)==3 and all(okc),ctx_)
    # ---- E. affichage et traductions
    ui=pg.evaluate("""()=>{const bad=[];for(const lang of %s)for(let L=1;L<=5;L++){S.lang=lang;S.lvl=L;S.pth={};S.rat={};build();PLC=null;
      try{const h=pathHtml();if(!h.includes('Unité 7')||!h.includes('🎯')||!h.includes(CURR[L].g))bad.push([lang+L,'affichage'])}catch(e){bad.push([lang+L,String(e)])}}
      const miss=[];for(const L of [1,2,3,4,5]){const cu=CURR[L];if(!cu.g||cu.c.length!==3)miss.push([L,'niveau']);for(const t of Object.keys(D))if(!(cu.u[t]&&cu.u[t][0]&&cu.u[t][1]))miss.push([L,t])}
      const strs=[...Object.values(CL),...Object.values(CURR).flatMap(c=>[c.g,...c.c,...Object.values(c.u).flat()])];return{bad,miss,strs}}""" % json.dumps(LANGS))
    ck("affichage du parcours (en-tête d'objectifs, 7 unités) sans erreur pour 5 langues × 5 niveaux",not ui['bad'],ui['bad'][:3])
    ck("chaque niveau a ses objectifs, 3 compétences et un titre + objectif pour chaque unité",not ui['miss'],ui['miss'][:3])
    mt={}
    for uil in ["en","it","de","pt"]:
        tr=json.load(urllib.request.urlopen(BASE+f"tr/{uil}.json"))
        mt[uil]=[x[:40] for x in ui['strs'] if not tr.get(x) or tr.get(x)==x]
    ck(f"{len(ui['strs'])} textes du cursus traduits en en/it/de/pt",not any(mt.values()),{k:v[:3] for k,v in mt.items() if v})
    ck("aucune erreur JS",not err,err[:3])
    b.close()
print(f"\n{sum(R)}/{len(R)} contrôles OK");sys.exit(0 if all(R) else 1)
