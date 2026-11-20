# Intelligence pédagogique (chantier 2) : révisions adaptées à la charge, consolidation ciblée avant les nouveautés
# (jamais bloquante), prérequis réellement introduits, profils débutant / en retard / fragile / avancé / ancien profil,
# changement de langue, 5 langues × A1–C1, aucune remise à zéro.
# Usage : python3 tests/adaptation.py URL
import sys
from playwright.sync_api import sync_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else "http://127.0.0.1:8774/"
R=[]
def ck(n,c,i=""):R.append(bool(c));print("OK  " if c else "FAIL",n,"" if c else str(i)[:700],flush=True)
H=r"""
window.CLR_=()=>{S.sr={};S.sc={};S.mi={};S.cns={};S.pth={};S.pthAll=0;S.ds={};MKDC.clear()};
window.SET_=(l,L)=>{S.lang=l;S.lvl=L;PLC=null;build();XDIRTY=1;xens()};
/* première étape de nouveautés de mots encore à faire, et une étape d'entraînement (non nouvelle) */
window.NW_=()=>{const it=pathItems().find(x=>!x.done&&!x.lock&&!x.test&&pathPlan().map[x.id].nw);return it&&it.id};
window.PR_=()=>Object.values(pathPlan().map).find(s=>!s.nw&&s.kn&&s.ws&&s.ws.length&&!s.test);
/* réserve de mots du niveau (listes comprises), hors mots des premières étapes (pour ne pas tomber sur la notion de l'étape jouée) */
window.POOL_=()=>{const ex=new Set();Object.values(pathPlan().map).slice(0,12).forEach(s=>(s.ws||[]).forEach(w=>ex.add(w[0])));const r=PR_();if(r)(r.ws||[]).forEach(w=>ex.add(w[0]));
  const sn=new Set();return ALL.concat(LP).filter(w=>w&&w[0]&&(w[2]||1)<=lv()&&!ex.has(w[0])&&!sn.has(w[0])&&sn.add(w[0]))};
/* n mots récents fragiles (vus aujourd'hui, palier 1) / solides (palier 4) / échus */
window.FRAG_=(n,from)=>{const w=POOL_().slice(from||0,(from||0)+n);w.forEach(w=>S.sr[w[0]]={b:1,d:dayN()+1,p:1,m:1,c:[1,0,0,0],n:2,k:0,s:dayN()});return w.map(w=>w[0])};
window.SOLID_=(n,from)=>{const w=POOL_().slice(from||30,(from||30)+n);w.forEach(w=>S.sr[w[0]]={b:3,d:dayN()+5,p:4,m:1.1,c:[1,1,2,2],n:6,k:0,s:dayN()-1});return w.map(w=>w[0])};
window.DUE_=(n,late,from)=>{const w=POOL_().slice(from||100,(from||100)+n);w.forEach(w=>S.sr[w[0]]={b:2,d:dayN()-(late||1),p:3,m:1,c:[1,1,2,0],n:5,k:0,s:dayN()-(late||1)-3});return w.map(w=>w[0])};
/* déroule une étape du parcours en répondant juste : nombre de questions de révision et leurs positions */
window.RUN_=(id)=>{const st=pathPlan().map[id];R={mode:'lesson',t:st.t||'Chunk',n:0,ok:0,xp:0,cat:null,pid:id,pt:st.pt||null,ws:st.ws||null,dp:st.dp||null,gp:st.gp||null,go:st.go||null,xs:st.xs||null,qs:st.qs||null,vs:st.vs||null,pp:st.pp||null,kn:st.kn||null,tn:Array.isArray(st.tn)?st.tn:null};
  const pos=[],keys=[];for(let n=0;n<10;n++){R.n=n;let q=null;try{q=rvQ()}catch(e){}if(q&&q.rvw){pos.push(n);keys.push(q.key)}}return {pos,keys,slots:R.rvs}};
0;
"""
with sync_playwright() as p:
    b=p.chromium.launch();c=b.new_context(service_workers="block");pg=c.new_page()
    errs=[];pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.goto(BASE+"index.html");pg.wait_for_timeout(2500);ev=pg.evaluate
    ev("()=>{S.ob=0;save()}");ev(H)
    # ---------- profil débutant ----------
    r=ev("""()=>{SET_('es',1);CLR_();const id=NW_();const ld=adLoad();pstart(id);const offered=!!document.querySelector('.cns');const run=RUN_(id);home();return {id,ld:{f:ld.frag,d:ld.due},offered,run}}""")
    ck("débutant : aucune consolidation, aucune révision imposée (rien d'échu) — la 1re étape se déroule comme avant",not r["offered"] and r["run"]["pos"]==[] and r["ld"]=={"f":0,"d":0},r)
    # ---------- charge normale : comportement d'avant ----------
    r=ev("""()=>{SET_('es',2);CLR_();DUE_(3);const st=PR_();return RUN_(st.id)}""")
    ck("charge normale (3 notions échues) : 2 révisions, en 4e et 8e question, comme avant",r["pos"]==[3,7] and len(set(r["keys"]))==2,r)
    r=ev("""()=>{SET_('es',2);CLR_();DUE_(1);const st=PR_();return RUN_(st.id)}""")
    ck("une seule notion échue : reprise aux mêmes emplacements qu'avant (4e et 8e)",r["pos"]==[3,7],r)
    # ---------- profil avec beaucoup de retard ----------
    r=ev("""()=>{SET_('es',2);CLR_();DUE_(12,2);const a=RUN_(PR_().id);CLR_();DUE_(40,10);const b=RUN_(PR_().id);const nw=NW_();const c=RUN_(nw);return {a,b,c}}""")
    ck("retard modéré (12 échues) : 3 révisions",r["a"]["pos"]==[3,6,8],r["a"])
    ck("gros retard (40 échues, 10 jours) : 4 révisions sur 10, toutes différentes, jamais en 1re ou 2e question",r["b"]["pos"]==[2,4,6,8] and len(set(r["b"]["keys"]))==4,r["b"])
    ck("étape de nouveautés : au plus 3 révisions, même avec un gros retard (les nouveautés gardent ≥ 7 questions)",len(r["c"]["pos"])==3,r["c"])
    r=ev("""()=>{const out={};for(const mode of ['fixe','adapt']){SET_('es',2);CLR_();const pl=pathPlan();const st=PR_();
        const pool=ALL.concat(LP).filter(w=>(w[2]||1)<=2&&!st.ws.some(x=>x[0]===w[0])).slice(0,60);
        pool.forEach((w,i)=>{S.sr[w[0]]={b:i<20?0:3,d:dayN()-1,p:i<20?1:4,m:1,c:i<20?[1,0,0,0]:[1,1,2,2],n:3,k:0,s:dayN()-3}});
        const served=new Set();let lessons=0;const sv=ADCFG.due3,sv4=ADCFG.due4;if(mode==='fixe'){ADCFG.due3=1e9;ADCFG.due4=1e9}
        for(let lesson=0;lesson<300&&served.size<60;lesson++){lessons=lesson+1;R={mode:'lesson',t:'',n:0,ok:0,xp:0,pid:st.id,ws:st.ws,dp:st.dp,kn:st.kn,pt:st.pt,tn:null};
          for(let n=0;n<10;n++){R.n=n;const q=rvQ();if(!q)continue;served.add(q.key);const i=pool.findIndex(w=>w[0]===q.key);mkRec(q.key,q,i<20?0:1)}
          if(lesson%3===2){for(const k in S.sr){S.sr[k].d-=1;if(S.sr[k].s!=null)S.sr[k].s-=1}}}
        ADCFG.due3=sv;ADCFG.due4=sv4;out[mode]=lessons}return out}""")
    ck(f"60 notions en retard dont 20 qui échouent sans cesse : toutes reprises en {r['adapt']} étapes (contre {r['fixe']} avec 2 révisions fixes)",r["adapt"]<=r["fixe"]*2/3,r)
    # ---------- consolidation ciblée ----------
    r=ev("""()=>{SET_('es',1);CLR_();const id=NW_();const fk=FRAG_(10);const pth0=JSON.stringify(S.pth),sr0=JSON.stringify(S.sr);
        pstart(id);const off=!!document.querySelector('.cns'),txt=(document.querySelector('.cns .sub')||{}).textContent||'';const unchanged=JSON.stringify(S.sr)===sr0&&JSON.stringify(S.pth)===pth0;
        consStart(id);const qs=[];for(let i=0;i<10;i++){if(!R.q)break;qs.push([R.q.key,!!R.q.rvw,R.q.ty]);R.done=true;R.n++;if(R.n<10)next()}
        const fragFirst=qs.slice(0,8).every(q=>q[1]&&fk.includes(q[0]));R.n=10;end();const btn=[...document.querySelectorAll('.btn')].find(b=>/pstart/.test(b.getAttribute('onclick')||''));
        const lab=btn&&btn.textContent,att=tr("Passer à l'étape");btn&&btn.click();const again=!!document.querySelector('.cns'),inStep=R.pid===id;home();
        return {off,txt,unchanged,n:qs.length,fragFirst,distinct:new Set(qs.map(q=>q[0])).size,lab,att,again,inStep,pth:S.pth[pthK(id)]||0}}""")
    ck("trop de notions récentes fragiles (10) : consolidation proposée avant l'étape de nouveautés, sans rien modifier",r["off"] and "10" in r["txt"] and r["unchanged"],r)
    ck("consolidation : 10 questions, les notions fragiles d'abord, chacune une seule fois",r["n"]==10 and r["fragFirst"] and r["distinct"]>=8,r)
    ck("après la consolidation : « Passer à l'étape » ouvre directement l'étape (pas de nouvelle proposition, pas de blocage), progression intacte",r["lab"]==r["att"] and not r["again"] and r["inStep"] and r["pth"]==0,r)
    r=ev("""()=>{SET_('es',1);CLR_();const id=NW_();const fk=FRAG_(10);pstart(id);const off=!!document.querySelector('.cns');consSkip(id);const inStep=R.pid===id&&!document.querySelector('.cns');
        const run=RUN_(id);home();pstart(id);const again=!!document.querySelector('.cns');home();return {off,inStep,run,frag:run.keys.filter(k=>fk.includes(k)).length,again}}""")
    ck("« Continuer quand même » : l'étape démarre aussitôt et fait plus de place aux notions fragiles (3 révisions, fragiles en premier)",r["off"] and r["inStep"] and len(r["run"]["pos"])==3 and r["frag"]==3,r)
    ck("proposée une seule fois par étape : jamais de blocage, même si on rejoue l'étape",not r["again"],r)
    r=ev("""()=>{SET_('es',1);CLR_();const id=NW_();FRAG_(4);SOLID_(20);pstart(id);const a=!!document.querySelector('.cns');home();
        CLR_();FRAG_(6);SOLID_(2);pstart(id);const b=!!document.querySelector('.cns');home();
        CLR_();FRAG_(6);SOLID_(20);pstart(id);const c=!!document.querySelector('.cns');home();return {a,b,c}}""")
    ck("seuils : 4 fragiles → non ; 6 fragiles sur 8 récentes → oui ; 6 fragiles sur 26 récentes → non (progression normale si les acquis sont solides)",not r["a"] and r["b"] and not r["c"],r)
    r=ev("""()=>{SET_('es',1);CLR_();FRAG_(10);const pr=PR_();pstart(pr.id);const a=!!document.querySelector('.cns');home();
        const id=NW_();S.pth[pthK(id)]=8;pstart(id);const b=!!document.querySelector('.cns');home();return {a,b}}""")
    ck("pas de consolidation avant une étape d'entraînement ni avant une étape déjà validée",not r["a"] and not r["b"],r)
    # ---------- profil avancé ----------
    r=ev("""()=>{SET_('es',4);CLR_();SOLID_(60,0);DUE_(2,1,200);const id=NW_();pstart(id);const off=!!document.querySelector('.cns');const run=RUN_(id);home();return {off,run}}""")
    ck("profil avancé (60 notions solides, 2 échues) : pas de consolidation, 2 révisions seulement",not r["off"] and r["run"]["pos"]==[3,7],r)
    # ---------- ancien profil (paliers estimés, sans date) ----------
    r=ev("""()=>{SET_('es',2);CLR_();ALL.filter(w=>(w[2]||1)<=2).slice(0,80).forEach((w,i)=>{S.sc[w[0]]=i%3;S.sr[w[0]]={b:i%2,d:dayN()+3}});const sr0=JSON.stringify(S.sr);
        const ld=adLoad();const id=NW_();pstart(id);const off=!!document.querySelector('.cns');home();return {f:ld.frag,rec:ld.rec,off,unchanged:JSON.stringify(S.sr)===sr0}}""")
    ck("ancien profil (paliers estimés sans date) : jamais compté comme fragile, aucune consolidation, données intactes",r["f"]==0 and r["rec"]==0 and not r["off"] and r["unchanged"],r)
    # ---------- prérequis ----------
    r=ev("""()=>{SET_('es',2);CLR_();const st=Object.values(pathPlan().map).find(s=>!s.nw&&s.t&&!s.ru&&!s.tn&&s.ws&&s.ws.length>=8);
        const L2=st.ws.filter(w=>(w[2]||1)===2);if(L2.length<6)return {skip:st.id};const known=L2.slice(0,5);known.forEach(w=>S.ds[w[0]]=1);
        S.pthAll=1;pstart(st.id);const ws=(R.ws||[]).map(w=>w[0]);const bad=ws.filter(k=>{const w=st.ws.find(x=>x[0]===k);return (w[2]||1)===2&&!S.ds[k]});home();
        CLR_();S.pthAll=1;L2.slice(0,2).forEach(w=>S.ds[w[0]]=1);pstart(st.id);const fb=(R.ws||[]).length;home();return {id:st.id,n0:st.ws.length,n:ws.length,bad,fb}}""")
    ck("prérequis : une étape d'entraînement n'interroge que des mots déjà introduits (découverts ou d'un niveau inférieur)",r.get("skip") or (not r["bad"] and r["n"]<r["n0"]),r)
    r=ev("""()=>{SET_('es',2);CLR_();const ids=Object.keys(pathPlan().map).filter(id=>pathPlan().map[id].nw).slice(0,3);const out=[];
        S.pthAll=1;for(const id of ids){const st=pathPlan().map[id];const n0=(st.ws||[]).length;pstart(id);out.push([id,!!document.querySelector('.dsc')||!!R.q]);home()}return out}""")
    ck("étapes de nouveautés : découverte avant l'entraînement, inchangée",all(x[1] for x in r),r)
    # ---------- changement de langue ----------
    r=ev("""()=>{SET_('es',1);CLR_();S.PL={};FRAG_(10);const es=adLoad().frag;setLang('ca');const ca=adLoad().frag;const id=NW_();pstart(id);const offCa=!!document.querySelector('.cns');home();
        setLang('es');const back=adLoad().frag;const id2=NW_();pstart(id2);const offEs=!!document.querySelector('.cns');home();return {es,ca,offCa,back,offEs,cns:Object.keys(S.cns||{})}}""")
    ck("changement de langue : charge et consolidation propres à chaque langue, retrouvées au retour",r["es"]==10 and r["ca"]==0 and not r["offCa"] and r["back"]==10 and r["offEs"] and r["cns"]==["es:1"],r)
    # ---------- 5 langues × A1–C1 ----------
    res={}
    for l in ["es","va","ca","gl","eu"]:
        for L in [1,2,3,4,5]:
            res[f"{l}{L}"]=ev("""([l,L])=>{SET_(l,L);CLR_();const id=NW_();if(!id)return 'pas d’étape';FRAG_(10,0);DUE_(30,8,40);
                let err='';try{const ld=adLoad();pstart(id);const off=!!document.querySelector('.cns');consStart(id);let n=0,rv=0;for(let i=0;i<10;i++){if(!R.q)break;n++;if(R.q.rvw)rv++;R.done=true;R.n++;if(R.n<10)next()}
                  const pr=PR_();const run=pr?RUN_(pr.id):{pos:[]};home();return {f:ld.frag,d:ld.due,off,n,rv,pr:run.pos.length}}catch(e){err=String(e);home();return err}}""",[l,L])
    bad={k:v for k,v in res.items() if not isinstance(v,dict) or not v["off"] or v["n"]!=10 or v["rv"]<8 or v["pr"]!=4}
    ck("5 langues × A1–C1 : charge mesurée, consolidation proposée et jouée (10 questions), 4 révisions en cas de retard",not bad,bad)
    print("    exemple :",res["es1"],res["eu5"])
    ck("aucune erreur JavaScript",not errs,errs[:3])
    b.close()
print(sum(R),"/",len(R),"OK");sys.exit(0 if all(R) else 1)
