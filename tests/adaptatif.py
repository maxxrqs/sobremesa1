# Profil adaptatif dans la vraie appli : réponses passées par fin() (comme un utilisateur), tirages réels de pickType/mkQ.
# Usage : python3 tests/rangesrv.py 8776 .  puis  python3 tests/adaptatif.py http://127.0.0.1:8776/
import sys,json
from playwright.sync_api import sync_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else "http://127.0.0.1:8776/"
R=[]
def ck(n,c,info=""):
    R.append(bool(c));print(("OK  " if c else "FAIL"),n,("" if c else str(info)[:600]),flush=True)

SIM=r"""([lang,lvl,prof,days])=>{
 S.lang=lang;S.lvl=lvl;S.ad=null;S.sk={};S.md={};S.sr={};S.sc={};S.mi={};S.rq={};build();XDIRTY=1;xens();
 let now=Date.UTC(2026,9,1,9);ADP.now=()=>now;
 if(!document.getElementById('fb')){const d=document.createElement('div');d.id='fb';document.body.appendChild(d)}
 const tys=["listen","listenP","dict","read","cloze","es2fr","type","build","fr2es","conjT","speakF","rep","speakC"];let n=0,errs=[];
 const cnt={};
 for(let d=0;d<days;d++){for(let i=0;i<60;i++){
   const ty=tys[i%tys.length];R={mode:"lesson",t:"Mélange",n:0,ok:0,xp:0};ADP.cur=adpSk(ty);let q;try{q=mkQ(ty,0)}catch(e){errs.push(ty+':'+e);continue}finally{ADP.cur=null}
   if(!q)continue;const k=MODL[q.ty];cnt[k]=(cnt[k]||0)+1;const p=prof[k];const v=((cnt[k]*0.6180339887)%1)<p?1:0;
   R.q=q;R.done=false;try{fin(v===1,q.sol||"",q.key||null)}catch(e){errs.push('fin '+q.ty+':'+e)}n++;now+=6e5}
  now+=864e5}
 return {n,errs:errs.slice(0,5),est:Object.fromEntries(ADP.SKS.map(k=>[k,adpEst(k)])),f:Object.fromEntries(ADP.SKS.map(k=>[k,adpF(k)])),t:adpT()}}"""
DIST=r"""([N])=>{const c={co:0,ce:0,ee:0,eo:0};let tot=0;
 for(let s=0;s<N;s++){R={mode:"lesson",t:"Mélange",n:0,ok:0,xp:0,hist:[]};for(let i=0;i<10;i++){const ty=pickType();R.hist.push({k:"x"+i,t:ty});S.md[lg()]=(S.md[lg()]||[]).concat(MODL[ty]).slice(-80);c[MODL[ty]]++;tot++}}
 return Object.fromEntries(Object.entries(c).map(([k,v])=>[k,v/tot]))}"""
DIFF=r"""([N])=>{const out={};for(const ty of ["listen","fr2es","type","es2fr"]){let cur=0,n=0;
 for(let i=0;i<N;i++){R={mode:"lesson",t:"Mélange",n:0,ok:0,xp:0};ADP.cur=adpSk(ty);let q;try{q=mkQ0(ty,0)}finally{ADP.cur=null}if(!q||!q.w)continue;n++;if((+q.w[2]||1)===lv())cur++}
 out[ty]=n?cur/n:null}return out}"""
with sync_playwright() as p:
    b=p.chromium.launch();ctx=b.new_context(locale="fr-FR");pg=ctx.new_page();err=[]
    pg.on("pageerror",lambda e:err.append(str(e)))
    pg.goto(BASE+"index.html");pg.wait_for_timeout(2500)
    pg.evaluate("()=>{try{FX.play=()=>{};speak=()=>{};aud=()=>{};axPre=()=>{}}catch(e){}}")
    # ---- profil vierge (utilisateur existant sans profil) : aucune erreur, rien d'inventé
    pg.evaluate("()=>{S.ad=null;prog('p')}")
    t=pg.inner_text("#app")
    ck("ancienne progression sans profil : carte affichée, 4 compétences « pas encore évaluées »",t.count("Pas encore évalué")==4,t[:400])
    # ---- A : fort en compréhension orale, faible en expression écrite
    A=pg.evaluate(SIM,["es",2,{"co":.95,"ce":.8,"ee":.35,"eo":.75},6])
    ck("réponses passées par fin() sans erreur",not A['errs'] and A['n']>300,A['errs'])
    print("   A estimations",{k:(v['lvl'],v['st']) for k,v in A['est'].items()},"facteurs",{k:round(v,2) for k,v in A['f'].items()})
    ck("A : CO estimée au-dessus de EE (estimations séparées)",(A['est']['co']['lvl'] or 0)>(A['est']['ee']['lvl'] or 0),A['est'])
    dA=pg.evaluate(DIST,[300]);fA=pg.evaluate(DIFF,[400])
    pg.evaluate("()=>prog('p')");cardA=pg.inner_text("#app")
    # ---- B : profil inverse
    B=pg.evaluate(SIM,["es",2,{"co":.35,"ce":.8,"ee":.95,"eo":.75},6])
    print("   B estimations",{k:(v['lvl'],v['st']) for k,v in B['est'].items()},"facteurs",{k:round(v,2) for k,v in B['f'].items()})
    dB=pg.evaluate(DIST,[300]);fB=pg.evaluate(DIFF,[400])
    print("   parts réelles A",{k:round(v*100) for k,v in dA.items()},"B",{k:round(v*100) for k,v in dB.items()})
    print("   items du niveau en cours A",fA,"B",fB)
    ck("parcours différent : plus d'expression écrite pour A que pour B",dA['ee']>dB['ee']*1.3,(dA,dB))
    ck("parcours différent : plus de compréhension orale pour B que pour A",dB['co']>dA['co']*1.3,(dA,dB))
    ck("compétence maîtrisée allégée mais jamais supprimée (≥ 8 % des exercices)",dA['co']>=.08 and dB['ee']>=.08,(dA,dB))
    ck("pratique des 4 compétences dans les deux profils (≥ 8 % chacune)",all(v>=.08 for v in list(dA.values())+list(dB.values())),(dA,dB))
    ck("difficulté par compétence : A tire plus d'items du niveau en cours à l'écoute (listen) qu'en expression écrite (fr2es)",fA['listen']>fA['fr2es']+.05,fA)
    ck("difficulté par compétence : B l'inverse",fB['fr2es']>fB['listen']+.05,fB)
    ck("carte Progrès : CO et EE affichées séparément avec le niveau de parcours à part","Ton niveau par compétence" in cardA and "Compréhension orale ·" in cardA and "Expression écrite ·" in cardA and "niveau de parcours" in cardA,cardA[:600])
    # ---- robustesse : profil A établi, puis 3 erreurs d'écoute
    pg.evaluate(SIM,["es",2,{"co":.95,"ce":.8,"ee":.35,"eo":.75},6])
    r=pg.evaluate("""()=>{const e0=adpEst('co').lvl,f0=adpF('co');for(let i=0;i<3;i++){R={mode:"lesson",t:"CO",n:0,ok:0,xp:0};const q=mkQ('dict',0);R.q=q;R.done=false;fin(false,q.sol,q.key)}return{e0,e1:adpEst('co').lvl,f0,f1:adpF('co')}}""")
    ck("3 erreurs d'écoute ne retirent pas le niveau CO et changent peu sa fréquence",r['e1']==r['e0'] and r['f1']-r['f0']<.35,r)
    # ---- test de placement : il alimente le profil
    pl=pg.evaluate("""()=>{S.ad=null;let now=Date.UTC(2026,9,1,9);ADP.now=()=>now;test(0);let i=0;while(R.mode==='test'&&T.i<T.list.length&&i<80){const q=R.q;R.done=false;fin(MODL[q.ty]==='co',q.sol,null);T.i++;if(T.i<T.list.length){R.q=T.list[T.i]}i++}
      const st=adpSt();return{co:Object.values(st.e.co||{}).reduce((a,c)=>a+c.n,0),ee:Object.values(st.e.ee||{}).reduce((a,c)=>a+c.n,0),est:adpEst('co')}}""")
    ck("les réponses du test de niveau alimentent le profil (écoute et écrit)",pl['co']>0 and pl['ee']>0,pl)
    ck("un seul test le même jour ne suffit pas à déclarer un niveau fiable",pl['est']['st']!="stable",pl)
    # ---- autres langues et sauvegarde
    ok5=pg.evaluate("""()=>{const out={};for(const l of ['va','ca','gl','eu']){const r=(()=>{S.lang=l;S.lvl=1;build();XDIRTY=1;xens();let e=0;for(let i=0;i<40;i++){R={mode:'lesson',t:'Mélange',n:0,ok:0,xp:0,hist:[]};try{const ty=pickType();ADP.cur=adpSk(ty);const q=mkQ(ty,0);ADP.cur=null;R.q=q;R.done=false;fin(true,q.sol||'',q.key||null)}catch(x){e++}}return e})();out[l]={err:r,n:Object.values((adpSt().e.ce)||{}).length+Object.values((adpSt().e.co)||{}).length}}return out}""")
    ck("valencien, catalan, galicien, basque : séries et profil sans erreur",all(v['err']==0 and v['n']>0 for v in ok5.values()),ok5)
    sv=pg.evaluate("()=>{save();const k=U?'cast:'+U:'cast';const o=JSON.parse(ST.get(k)||'{}');return !!(o.ad&&o.ad.L&&o.ad.L.es)}")
    ck("le profil est enregistré avec la progression (stockage local, hors ligne)",sv)
    ck("aucune erreur JavaScript",not err,err[:3])
    b.close()
print(f"\n{sum(R)} OK, {len(R)-sum(R)} échec(s)");sys.exit(0 if all(R) else 1)
