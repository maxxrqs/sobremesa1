# Parcours CECRL (v2) : unités dimensionnées sur le contenu du niveau, 3-4 nouveautés par étape, prérequis réellement
# enseignés avant toute évaluation (vocabulaire, temps, phrases, textes, dialogues), révisions espacées, évaluation finale à 70 %,
# report de la progression de l'ancien parcours.
# Usage : python3 tests/path.py [url_base]
import sys,json,re,urllib.request
from playwright.sync_api import sync_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else "http://localhost:8772/"
R=[]
def ck(n,c,info=""):
    R.append(bool(c));print(("OK  " if c else "FAIL"),n,("" if c else str(info)[:700]),flush=True)
LANGS=["es","va","ca","gl","eu"]
SIM=r"""(a)=>{const out={n:0,bad:[],types:{},steps:0};
 for(const lang of a.langs)for(let L=1;L<=5;L++){S.lang=lang;S.lvl=L;S.pth={};S.pmv={};S.rat={};S.rq={};S.md={};build();PLC=null;
  const pl=pathPlanMain(),pd=pqData(),phS=new Set(PH.map(x=>x[0])),txS=new Map(TX.map(x=>[x[0],x])),wr=new Map(pd.WR.map(x=>[x[0][0],x[1]])),xr=new Map(pd.XR.map(x=>[x[0].e,x[1]]));
  const scM=new Map(xdP(lang).map(z=>[z.m,z]));
  for(const st of pl.flat){if(st.test)continue;out.steps++;const rk=st.rk,kn=st.kn,tag=lang+L+":"+st.id;
   R={mode:"lesson",t:st.t||"Chunk",n:0,ok:0,xp:0,cat:null,pid:st.id,pt:st.pt||null,ws:st.ws||null,dp:st.dp||null,gp:st.gp||null,go:st.go||null,xs:st.xs||null,qs:st.qs||null,vs:st.vs||null,pp:st.pp||null,kn:st.kn||null,tn:st.tn||null};
   const own=new Set((st.ws||[]).map(w=>w[0])),wok=w=>own.has(w)||(wr.has(w)?wr.get(w)<=rk:true);
   const tnames=new Set();const ks=st.tn||kn.tk;Object.values(VD[lang]).slice(0,40).forEach(d=>vlist(lang,d).forEach(t=>{if(ks.includes(t.imv?"imv":t.k))tnames.add(gl(t.fr))}));
   for(let i=0;i<12;i++){R.n=i;let q;try{q=mkQ(pickType(),0)}catch(e){out.bad.push([tag,"EXC",String(e).slice(0,80)]);continue}
    out.n++;out.types[q.ty]=(out.types[q.ty]||0)+1;const txt=q.es||q.say||q.txt;
    const chkP=(p,why)=>{if(phS.has(p)){const x=PH.find(z=>z[0]===p);if(pqPH(x)>rk)out.bad.push([tag,why,q.ty,p])}else if(!wok(p)&&!(st.ws||[]).some(w=>w[0]===p))out.bad.push([tag,why+"-mot",q.ty,p])};
    if(["listenP","readP","fr2P","build","cloze","speak","speakC","rep","speakF","type","dict"].includes(q.ty)&&txt)chkP(q.ty==="cloze"&&q.say?q.say:txt,"phrase");
    if(q.ty==="fr2P")q.o.forEach(o=>{if(phS.has(o))chkP(o,"option")});
    if(q.ty==="listenT"||q.ty==="read"){const x=txS.get(q.say||q.txt);if(x&&pqTX(x)>rk)out.bad.push([tag,"texte",q.ty,(q.say||q.txt).slice(0,40)])}
    if(q.ty==="speakQ"||q.ty==="replyQ"){const z=scM.get(q.es);if(z&&pqSC(z)>rk)out.bad.push([tag,"dialogue",q.es])}
    if(q.ty==="conj"){if(!tnames.has(q.tn))out.bad.push([tag,"temps",q.tn]);if(kn&&!kn.vb.includes(q.verb)&&!(st.vs||[]).includes(q.verb))out.bad.push([tag,"verbe",q.verb])}
    if(["exM","exE","exL"].includes(q.ty)){const e=q.key.slice(2);if(!(st.xs&&st.xs.has(e))&&!(xr.get(e)<=rk))out.bad.push([tag,"expression",e])}
    if(q.ty==="exc"&&st.qs&&!st.qs.has(q.key.slice(2)))out.bad.push([tag,"grammaire",q.key.slice(0,40)]);
    if(["es2fr","fr2es","listen","tf"].includes(q.ty)&&q.w&&!wok(q.w[0]))out.bad.push([tag,"mot",q.ty,q.w[0]]);
   }}}
 return out}"""
with sync_playwright() as p:
    b=p.chromium.launch();ctx=b.new_context(locale="fr-FR");pg=ctx.new_page();err=[]
    pg.on("pageerror",lambda e:err.append(str(e)))
    pg.goto(BASE+"index.html");pg.wait_for_timeout(2500)
    # ---- A. structure
    st=pg.evaluate("""(langs)=>{const bad=[],U={};
      for(const lang of langs)for(let L=1;L<=5;L++){S.lang=lang;S.lvl=L;S.pth={};S.pmv={};S.rat={};build();PLC=null;const pl=pathPlanMain(),tag=lang+L;U[tag]=pl.units.length-1;
        const ids=pl.flat.map(x=>x.id);if(new Set(ids).size!==ids.length)bad.push([tag,'ids dupliqués']);
        pl.units.slice(0,-1).forEach((u,i)=>{const t=u.steps.map(x=>x.id[0]);
          if(!u.steps.some(x=>x.nw))bad.push([tag,i,'pas de nouveauté']);if(t.filter(c=>c==='k').length!==1)bad.push([tag,i,'compétence']);
          if(t[t.length-1]!=='m')bad.push([tag,i,'bilan pas en dernier']);if(!u.obj||!u.title)bad.push([tag,i,'objectif manquant']);
          if(u.steps.filter(x=>x.nw).length>7)bad.push([tag,i,'unité trop longue'])});
        pl.flat.filter(x=>x.nw).forEach(x=>{if(x.id[0]==='v'&&x.ws.length>4)bad.push([tag,x.id,'mots',x.ws.length]);if(x.xs&&x.xs.size>4)bad.push([tag,x.id,'expressions',x.xs.size]);if(x.ru&&x.ru.length>3)bad.push([tag,x.id,'règles',x.ru.length])});
        const last=pl.units[pl.units.length-1].steps.map(x=>x.id);["BR1","BR2","BCO","BCE","BEE","BEO","BM"].forEach(n=>{if(!last.includes(n))bad.push([tag,'consolidation sans',n])});
        const tests=pl.flat.filter(x=>x.test);if(L<5){if(tests.length!==1||pl.flat[pl.flat.length-1].id!=='TEST')bad.push([tag,'TEST'])}else if(tests.length)bad.push([tag,'TEST au niveau max'])}
      return{bad,U}}""",LANGS)
    print("   unités par niveau (hors bilan) :",json.dumps(st['U']))
    ck("5 langues × 5 niveaux : unités = nouveautés → compétence → bilan, ≤ 4 mots / 4 expressions / 3 règles par étape, consolidation et évaluation finale",not st['bad'],st['bad'][:5])
    ck("nombre d'unités adapté au contenu (A1 > C1, au moins 10 unités par niveau)",all(v>=10 for v in st['U'].values()) and all(st['U'][l+'1']>st['U'][l+'5'] for l in LANGS),st['U'])
    cov=pg.evaluate("""(langs)=>{const bad=[];for(const lang of langs)for(let L=1;L<=5;L++){S.lang=lang;S.lvl=L;S.pth={};build();PLC=null;const pl=pathPlanMain();
      const inW=new Set(pl.flat.filter(x=>x.nw&&x.ws).flatMap(x=>x.ws.map(w=>w[0]))),inX=new Set(pl.flat.filter(x=>x.xs&&x.nw).flatMap(x=>[...x.xs])),inQ=new Set(pl.flat.filter(x=>x.qs&&x.nw).flatMap(x=>[...x.qs]));
      const prev=new Set([...ALL,...LP].filter(w=>(w[2]||1)<L).map(w=>w[0]));
      const mw=[...ALL,...LP].filter(w=>(w[2]||1)===L&&!prev.has(w[0])&&!inW.has(w[0])),mx=XP.filter(x=>x.l===L&&!inX.has(x.e)),mq=EQ.filter(x=>x.l===L&&!inQ.has(x.k));
      if(mw.length||mx.length||mq.length)bad.push([lang+L,mw.length,mx.length,mq.length,mw.slice(0,3).map(w=>w[0])])}return bad}""",LANGS)
    ck("tout le contenu du niveau (mots, listes, expressions, questions de grammaire) est enseigné dans une étape",not cov,cov[:5])
    rul=pg.evaluate("""(langs)=>{const bad=[];for(const lang of langs)for(let L=1;L<=5;L++){S.lang=lang;S.lvl=L;S.pth={};build();PLC=null;const pl=pathPlanMain();
      pl.flat.filter(x=>x.tn).forEach(x=>{S.ds={};const d=discItems(x);if(d.length<2||!d.intro)bad.push([lang+L,x.id,'temps sans explication'])});
      pl.flat.filter(x=>x.ru&&x.ru.length).forEach(x=>{S.ds={};const d=discItems(x);if(!d.length||!d[0].fr)bad.push([lang+L,x.id,'règle sans explication'])})}return bad}""",LANGS)
    ck("chaque nouveau temps et chaque règle de grammaire sont expliqués (fiche de découverte) avant l'entraînement",not rul,rul[:5])
    sp=pg.evaluate("""(langs)=>{const bad=[];for(const lang of langs)for(let L=1;L<=5;L++){S.lang=lang;S.lvl=L;S.pth={};build();PLC=null;const pl=pathPlanMain(),us=pl.units.slice(0,-1);
      us.forEach((u,i)=>{const m=new Set(u.steps.find(x=>x.id[0]==='m').ws.map(w=>w[0]));[1,3].forEach(d=>{if(i-d>=0&&us[i-d].uw.length&&!us[i-d].uw.slice(0,3).some(w=>m.has(w[0])))bad.push([lang+L,i,'u-'+d])})})}return bad}""",LANGS)
    ck("révisions espacées : chaque bilan d'unité reprend des mots des unités u-1 et u-3",not sp,sp[:5])
    # ---- B. prérequis : simulation de toutes les étapes (12 questions par étape)
    for grp in (["es","va"],["ca","gl","eu"]):
        r=pg.evaluate(SIM,{"langs":grp})
        print("   ",grp,r['steps'],"étapes,",r['n'],"questions ; types :",dict(sorted(r['types'].items(),key=lambda x:-x[1])[:12]))
        ck(f"{'/'.join(grp)} : aucune phrase, aucun texte, dialogue, temps, verbe, expression ou point de grammaire évalué avant d'avoir été enseigné",not r['bad'],r['bad'][:8])
    ex=pg.evaluate("""()=>{S.lang='es';build();xens();const ok=s=>{const x=PH.find(z=>z[0]===s);return Math.floor(pqPH(x)/1000)};
      return{reveil:ok('Me levanté tarde porque no sonó el despertador.'),fui:ok('Ayer fui a la playa con mis amigos'),tense:pqData().TR.pret,a2:pqEnd(1)}}""")
    ck("exemple : « Me levanté tarde porque no sonó el despertador » n'arrive qu'après l'introduction du passé simple et du mot despertador (en A2, pas au début)",ex['reveil']>=2 and ex['tense']>ex['a2'],ex)
    # ---- C. conservation des progrès (ancien parcours → nouveau)
    mg=pg.evaluate("""()=>{const o={};for(const [lang,L] of [['es',1],['es',2],['gl',3]]){S.lang=lang;S.lvl=L;S.rat={};build();PLC=null;S.pth={};S.pmv={};
        const old=pathPlanV1(),done=old.flat.filter(x=>!x.test).slice(0,20);done.forEach(x=>{S.pth[pthK(x.id)]=8});const W=new Set(done.flatMap(x=>x.ws||[]).map(w=>w[0]));
        const pl=pathPlanMain(),nd=pl.flat.filter(x=>x.nw&&x.ws&&(S.pth[pthK(x.id)]||0)>=6);
        o[lang+L]={n:nd.length,wrong:nd.filter(x=>!x.ws.every(w=>W.has(w[0]))).length};
        S.pth={};S.pmv={};old.flat.filter(x=>!x.test).forEach(x=>{S.pth[pthK(x.id)]=7});PLC=null;pathPlanMain();o[lang+L].all=pl.flat.filter(x=>!x.test).every(x=>(S.pth[pthK(x.id)]||0)>=6);o[lang+L].ready=lvReady()}
      return o}""")
    ck("progression de l'ancien parcours reportée : mots déjà validés → étapes validées, ancien niveau terminé → nouveau niveau terminé",all(v['n']>0 and v['wrong']==0 and v['all'] and v['ready'] for v in mg.values()),mg)
    # ---- D. déblocage du niveau
    g=pg.evaluate("""()=>{const o={};S.lang='es';S.lvl=1;S.rat={};S.lvSnz=0;S.pmv={'es:1':2};build();PLC=null;
      const pl=pathPlanMain(),main=pl.flat.filter(x=>!x.test);
      S.pth={};main.slice(0,40).forEach(x=>{S.pth[pthK(x.id)]=10});o.early=lvReady();
      S.pth={};main.forEach(x=>{S.pth[pthK(x.id)]=6});o.all=lvReady();
      S.lvSnz=Date.now()+1e6;o.snooze=lvReady();S.lvSnz=0;
      S.pth={};main.forEach(x=>{S.pth[pthK(x.id)]=5});o.fail=lvReady();
      S.pth={};main.forEach(x=>{S.pth[pthK(x.id)]=6});S.pth[pthK(main[main.length-1].id)]=0;o.oneMissing=lvReady();
      S.lvl=5;S.pth={};S.pmv={'es:5':2};build();PLC=null;pathPlanMain().flat.forEach(x=>{S.pth[pthK(x.id)]=9});o.max=lvReady();
      return o}""")
    ck("niveau proposé uniquement quand TOUTES les étapes sont validées ; pas après un bon début, ni avec 5/10, ni s'il en manque une ; jamais au niveau max",g['early'] is False and g['all'] is True and g['fail'] is False and g['oneMissing'] is False and g['snooze'] is False and g['max'] is False,g)
    # ---- E. évaluation finale : 70 % dans la logique de validation ; test de placement inchangé (60 %)
    e=pg.evaluate("""()=>{const o={};
      const mk=(from,cap,p)=>{S.lang='es';S.lvl=from;S.rat={};S.lvSnz=0;build();PLC=null;R={mode:'test'};T={l:from,list:[],i:0,p,m:10,skip:0,skipAll:0,res:{},pass:0,k:{},from,cap};tstage();return S.lvl};
      o.cap80=mk(1,1,8);o.cap70=mk(2,1,7);o.cap69=mk(2,1,6.9);o.cap65=mk(1,1,6.5);
      S.lang='es';S.lvl=1;build();R={mode:'test'};T={l:1,list:[],i:0,p:6.5,m:10,skip:0,skipAll:0,res:{},pass:0,k:{},from:0,cap:0};
      const sv=window.ptList;window.ptList=()=>[];tstage();window.ptList=sv;o.place65=T.pass;
      // arrêt anticipé : 7/10 au bout de 6 questions ne suffit pas à conclure en dessous du seuil de 70 %
      S.lvl=1;R={mode:'test'};T={l:1,list:Array(10).fill({wt:1}),i:6,p:4,m:6,skip:0,skipAll:0,res:{},pass:0,k:{},from:1,cap:1};let st=0;const sv2=window.tstage;window.tstage=()=>{st=1};try{tnext()}catch(x){}window.tstage=sv2;o.early=st;
      o.lab=[CL.how,CL.bb].every(s=>s.includes('70 %'));
      // l'évaluation finale ne contient que ce qui a été enseigné dans le niveau
      S.lang='es';S.lvl=2;build();xens();const li=ptList(2,1),e2=pqEnd(2);o.fin=li.length;o.finBad=li.filter(q=>{const t=q.ty==='cloze'?q.say:q.ty==='read'?q.txt:q.es||q.say;return t&&pqRank(t,q.ty==='read'?q.p+' '+q.o.join(' '):'').r>e2}).map(q=>q.ty+':'+(q.say||q.txt||q.es).slice(0,40));
      return o}""")
    ck("évaluation finale : 80 % et 70 % → niveau validé ; 69 % et 65 % → refusé (logique de validation, pas seulement l'affichage)",e['cap80']==2 and e['cap70']==3 and e['cap69']==2 and e['cap65']==1,e)
    ck("test de placement inchangé (un palier se valide toujours à 60 %)",e['place65']==1,e)
    ck("textes « 70 % minimum » affichés ; évaluation finale composée uniquement de contenus enseignés",e['lab'] and e['fin']>=8 and not e['finBad'],e)
    src=urllib.request.urlopen(BASE+"index.html").read().decode("utf8")
    ctx_=[src[m.start()-30:m.start()+70] for m in re.finditer(r"S\.lvl=",src)]
    okc=[any(k in c for k in ("T.cap","o.lvl||0","obNext()")) for c in ctx_]
    ck(f"le niveau ne change qu'à {len(ctx_)} endroits : fin d'une évaluation, chargement du profil, « Je débute » à l'accueil",len(ctx_)==3 and all(okc),ctx_)
    # ---- F. affichage et traductions
    ui=pg.evaluate("""(langs)=>{const bad=[];for(const lang of langs)for(let L=1;L<=5;L++){S.lang=lang;S.lvl=L;S.pth={};S.rat={};build();PLC=null;
      try{const pl=pathPlanMain(),h=pathHtml();if(!h.includes('Unité '+pl.units.length)||!h.includes(CURR[L].g))bad.push([lang+L,'affichage'])}catch(e){bad.push([lang+L,String(e)])}}
      const strs=[...Object.values(CL),...Object.values(CURR).flatMap(c=>[c.g,...c.c,...Object.values(c.u).flat()])];return{bad,strs}}""",LANGS)
    ck("affichage du parcours (en-tête d'objectifs, toutes les unités) sans erreur pour 5 langues × 5 niveaux",not ui['bad'],ui['bad'][:3])
    mt={}
    for uil in ["en","it","de","pt"]:
        tr=json.load(urllib.request.urlopen(BASE+f"tr/{uil}.json"))
        mt[uil]=[x[:40] for x in ui['strs'] if not tr.get(x) or tr.get(x)==x]
    ck(f"{len(ui['strs'])} textes du cursus traduits en en/it/de/pt",not any(mt.values()),{k:v[:3] for k,v in mt.items() if v})
    ck("aucune erreur JS",not err,err[:3])
    b.close()
print(f"\n{sum(R)}/{len(R)} contrôles OK");sys.exit(0 if all(R) else 1)
