# Carnet de maîtrise — validation du chantier 1 (décisions du 20/11) :
# classification des exercices par compétence réelle, cohérence carnet / boîte / dates, file de révision sans attente
# indéfinie, séance « Réviser » et compteurs sur les 4 catégories (5 langues × A1–C1), astuce + conjugaison en séance Mélange.
# Usage : python3 tests/carnet2.py URL
import sys,json
from playwright.sync_api import sync_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else "http://127.0.0.1:8774/"
R=[]
def ck(n,c,i=""):R.append(bool(c));print("OK  " if c else "FAIL",n,"" if c else str(i)[:700],flush=True)
H=r"""window.CLR_=()=>{S.sr={};S.sc={};S.mi={};MKDC.clear()};window.SET_=(l,L)=>{S.lang=l;S.lvl=L;PLC=null;build();XDIRTY=1;xens()};0;"""
with sync_playwright() as p:
    b=p.chromium.launch();c=b.new_context(service_workers="block");pg=c.new_page()
    errs=[];pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.goto(BASE+"index.html");pg.wait_for_timeout(2500);ev=pg.evaluate
    ev("()=>{S.ob=0;save()}");ev(H)
    # ---------- 1. classification ----------
    r=ev("""()=>{const bad=[],seen={};for(const L of [1,3,5]){SET_('es',L);const pl=pathPlan();
        for(const id of Object.keys(pl.map)){const st=pl.map[id];R={mode:'lesson',t:st.t||'Chunk',n:0,ok:0,xp:0,cat:null,pid:id,pt:st.pt||null,ws:st.ws||null,dp:st.dp||null,gp:st.gp||null,go:st.go||null,xs:st.xs||null,qs:st.qs||null,vs:st.vs||null,pp:st.pp||null,kn:st.kn||null,tn:Array.isArray(st.tn)?st.tn:null};
          for(let n=0;n<6;n++){let q=null;try{q=mkQ(pickType(),0)}catch(e){}if(!q)continue;const a=MKA[q.ty],aide=(Array.isArray(q.o)&&q.o.length>0)||!!q.toks||!!q.hint||!!q.models||!!q.opts||!!q.L;seen[q.ty]=1;
            if(a===undefined)bad.push(q.ty+': non classé');else if(aide&&a>=4)bad.push(q.ty+': choix ou aide classé production seule');else if(!aide&&a===4&&!q.acc&&!['type','speakF'].includes(q.ty))bad.push(q.ty+'?')}}}
        return {bad:[...new Set(bad)],types:Object.keys(seen).length,qcm4:Object.keys(MKA).filter(k=>MKA[k]===4)}}""")
    ck(f"classification : aucun choix multiple ni exercice avec aide n'est compté comme production seule ({r['types']} types générés)",not r["bad"],r)
    ck("production seule (4) réservée à : écrire, phrase de grammaire écrite, conjugaison écrite, traduire à l'oral, réponse libre (lot B)",sorted(r["qcm4"])==sorted(["type","excT","conjT","speakF","irpE"]),r["qcm4"])
    # ---------- 2. cohérence carnet / boîte / dates ----------
    r=ev("""()=>{SET_('es',3);CLR_();const ks=['hola','gracias','e:'+XP[3].e,'q:'+EQ[5].k,'v:tener','v:hablar'];const tys=Object.keys(MKA);const bad=[];
        S.sc.gracias=4;S.sr.gracias={b:3,d:dayN()+2};
        for(let i=0;i<4000;i++){const k=ks[i%ks.length],ty=tys[Math.floor(Math.random()*tys.length)],s=[1,1,1,0,.5][Math.floor(Math.random()*5)];
          const e0=S.sr[k]?mkGet(k):null,b0=e0?e0.b:0,due=!e0||e0.d<=dayN();const e=mkRec(k,{ty},s),dif=mkDif(k),t=dayN();
          const exb=s>=1?(due?Math.min(5,b0+1):b0):s>0?b0:0;
          if(e.b!==exb)bad.push('boîte '+k);
          if(s>=1&&due&&e.d<t+1)bad.push('date réussite '+k);if(s===0&&e.d!==t)bad.push('date erreur '+k);if(s>=1&&!due&&e0&&e.d!==e0.d)bad.push('date modifiée hors échéance '+k);
          if(e.p<0||e.p>5||(e.p<5&&e.p!==mkPal(e,dif)))bad.push('palier/preuves '+k+' '+e.p+' '+mkPal(e,dif));
          if(e.p===5&&mkPal(e,dif)<4)bad.push('ancrage sans production '+k);
          if(e.m<.6||e.m>1.5)bad.push('facilité '+k);if(e.c.some((x,P)=>x>MKN[dif][P+1]))bad.push('preuves au-delà du besoin '+k);
          if(Math.random()<.3){const sh=Math.floor(Math.random()*30);const z=S.sr[k];z.s-=sh;z.d-=sh;if(z.j)z.j=z.j.map(x=>x?x-sh:0)}}
        return [...new Set(bad)].slice(0,8)}""")
    ck("cohérence sur 4 000 réponses aléatoires (6 notions, 4 catégories, tous types, ancien profil) : boîte = règle historique, dates, paliers = preuves, facilité bornée",not r,r)
    # ---------- 3. file de révision : pas d'attente indéfinie ----------
    r=ev("""()=>{SET_('es',2);CLR_();const pl=pathPlan();const st=Object.values(pl.map).find(s=>s.kn&&s.ws&&s.ws.length);
        const pool=ALL.concat(LP).filter(w=>(w[2]||1)<=2&&!st.ws.some(x=>x[0]===w[0])).slice(0,60);
        /* 60 notions échues dont 20 très fragiles qui retombent sans cesse à 0 ; les autres sont bien connues */
        pool.forEach((w,i)=>{S.sr[w[0]]={b:i<20?0:3,d:dayN()-1,p:i<20?1:4,m:1,c:i<20?[1,0,0,0]:[1,1,2,2],n:3,k:0,s:dayN()-3}});
        const served=new Map();let day=0;
        for(let lesson=0;lesson<200&&served.size<60;lesson++){R={mode:'lesson',t:'',n:0,ok:0,xp:0,pid:st.id,ws:st.ws,dp:st.dp,kn:st.kn,pt:st.pt,tn:null};for(let n=0;n<10;n++){R.n=n;/* chantier 2 : emplacements adaptés à la charge, toute l'étape est parcourue */const q=rvQ();if(!q)continue;
            if(!served.has(q.key))served.set(q.key,lesson);const i=pool.findIndex(w=>w[0]===q.key);mkRec(q.key,q,i<20?0:1)}
          if(lesson%3===2){for(const k in S.sr){S.sr[k].d-=1;if(S.sr[k].s!=null)S.sr[k].s-=1}}}
        const strong=pool.slice(20).map(w=>served.get(w[0]));return {servi:served.size,maxStrong:Math.max(...strong.map(x=>x===undefined?999:x))}}""")
    ck(f"file de révision : 60 notions en retard dont 20 qui échouent sans cesse → toutes servies (dernière notion solide servie à la leçon {r['maxStrong']+1})",r["servi"]==60 and r["maxStrong"]<200,r)
    # ---------- 4. séance « Réviser » et compteurs : 4 catégories × 5 langues × A1–C1 ----------
    res={}
    for l in ["es","va","ca","gl","eu"]:
        for L in [1,2,3,4,5]:
            res[f"{l}{L}"]=ev("""([l,L])=>{SET_(l,L);CLR_();const ks={};
                const w=ALL.concat(LP).find(w=>(w[2]||1)<=L);const x=XP.find(x=>x.l<=L);const q=EQ.find(x=>x.l<=L);const v=Object.keys(VD[l]).find(v=>vLvl(l,v)<=L);
                if(w)ks.w=w[0];if(x)ks.e='e:'+x.e;if(q)ks.q='q:'+q.k;if(v)ks.v='v:'+v;Object.values(ks).forEach(k=>S.sr[k]={b:1,d:dayN()-1});
                const n=mkDueN();tools();const btn=[...document.querySelectorAll('button')].find(b=>/start\\('Révision'\\)/.test(b.getAttribute('onclick')||'')&&b.querySelector('span'));
                start('Révision');const got={};for(let i=0;i<10;i++){if(typeof R.q!=='object'||!R.q)break;const k=R.q.key;if(R.q.rvw)for(const t in ks)if(ks[t]===k)got[t]=R.q.ty;R.done=true;R.n++;if(R.n>=10)break;next()}
                home();return {n,att:Object.keys(ks).length,btn:btn?btn.textContent:'',got}}""",[l,L])
    bad={k:v for k,v in res.items() if v["n"]!=v["att"] or str(v["n"]) not in v["btn"] or len(v["got"])!=v["att"]}
    ck("séance « Réviser » : mots, expressions, grammaire et conjugaisons échus repris dans la séance, 5 langues × A1–C1",not bad,bad)
    ck("compteur « À revoir » de l'accueil = total des 4 catégories (5 langues × A1–C1)",all(v["n"]==v["att"] and str(v["n"]) in v["btn"] for v in res.values()),{k:(v["n"],v["btn"]) for k,v in list(res.items())[:4]})
    print("    exemple es2 :",res["es2"]["got"]," eu5 :",res["eu5"]["got"])
    r=ev("""()=>{SET_('es',2);CLR_();S.sr['e:'+XP[0].e]={b:1,d:dayN()-1};S.sr['q:'+EQ[0].k]={b:1,d:dayN()-1};home();const h=document.querySelector('.hsv');
        const hs=h?h.textContent:'';XP.filter(x=>x.l<=2).slice(0,15).forEach(x=>S.sr['e:'+x.e]={b:1,d:dayN()-1});EQ.filter(x=>x.l<=2).slice(0,15).forEach(x=>S.sr['q:'+x.k]={b:1,d:dayN()-1});
        const g=lvGate().items[1];return {hs,n:mkDueN(),g:g.t,ok:g.ok,cle:tr("{0} notions à revoir avant le test",mkDueN())}}""")
    ck("bandeau « À revoir » et condition du test de niveau comptent aussi expressions et grammaire (30 notions échues → test de niveau en attente)",r["hs"].endswith("2") and r["g"]==r["cle"] and str(r["n"]) in r["g"] and not r["ok"],r)
    r=ev("""()=>{SET_('es',2);CLR_();start('Révision');const t=[];for(let i=0;i<10&&R.q;i++){t.push(R.q.ty);R.done=true;R.n++;if(R.n>=10)break;next()}home();return t.length}""")
    ck("séance « Réviser » sans rien d'échu : révision libre inchangée (10 questions)",r==10,r)
    # ---------- 5. astuce puis conjugaison en séance Mélange (bogue corrigé) ----------
    r=ev("""()=>{const out={err:[],conj:0,tips:0};for(const l of ['es','va','ca','gl','eu'])for(const L of [1,3,5]){SET_(l,L);CLR_();S.tp={};
        for(let run=0;run<25;run++){home();start('Mélange');for(let i=0;i<10;i++){try{const q=mkQ('conj',0);if(q&&q.ty==='conj')out.conj++;R.q=q||R.q;
              const tp=tpGet(R.q.ty?R.q:{key:'hola'});if(tp)out.tips++;R.tpn=0;R.tpl=-9;/* astuce possible à chaque question */
              R.q=mkQ('es2fr',0);R.done=true;R.n++;if(R.n<10)next()}catch(e){out.err.push(l+L+': '+String(e).slice(0,80));break}}}}home();return out}""")
    ck(f"séance Mélange : {r['tips']} astuces puis {r['conj']} questions de conjugaison, aucune erreur (5 langues × A1/B1/C1)",not r["err"] and r["conj"]>0,r["err"][:3])
    r=ev("""()=>{SET_('es',2);CLR_();const pl=pathPlan();const st=Object.values(pl.map).find(s=>Array.isArray(s.tn)&&s.tn.length);if(!st)return 'aucune étape de conjugaison';
        pstart(st.id);const tn0=JSON.stringify(R.tn);S.tp={};let tips=0,err='';for(let i=0;i<10;i++){try{if(tpGet({key:'tener',es:'tener'}))tips++;R.tc+=3;const q=mkQ('conj',0)}catch(e){err=String(e)}}
        const r={tn0,tn1:JSON.stringify(R.tn),tips,err};home();return r}""")
    ck("étape de conjugaison : les temps de l'étape (R.tn) ne sont plus écrasés par le compteur d'astuces",isinstance(r,dict) and r["tn0"]==r["tn1"] and not r["err"],r)
    ck("aucune erreur JavaScript",not errs,errs[:3])
    b.close()
print(sum(R),"/",len(R),"OK");sys.exit(0 if all(R) else 1)
