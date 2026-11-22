# Prérequis fondés sur les apprentissages réels (chantier 2, réserve 1) : les étapes d'entraînement n'utilisent que des mots
# et expressions découverts ou rencontrés par l'apprenant dans la langue étudiée ; phrases limitées au point réellement atteint.
# Cas : étapes toutes débloquées, reprise d'une ancienne étape, changement de langue et retour, notion d'une étape antérieure
# jamais présentée, notions rencontrées / maîtrisées toujours utilisables, anciennes marques de découverte, rien de réinitialisé.
# Usage : python3 tests/prerequis.py URL
import sys
from playwright.sync_api import sync_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else "http://127.0.0.1:8774/"
R=[]
def ck(n,c,i=""):R.append(bool(c));print("OK  " if c else "FAIL",n,"" if c else str(i)[:700],flush=True)
H=r"""
window.CLR_=()=>{S.sr={};S.sc={};S.mi={};S.cns={};S.pth={};S.pa={};S.pthAll=0;S.ds={};S.dsm=1;S.PL={};MKDC.clear()};
window.SET_=(l,L)=>{if(S.lang!==l){S.lang=l}S.lvl=L;PLC=null;build();XDIRTY=1;xens()};
window.WIX_=()=>{const m=new Map();ALL.concat(LP).forEach(w=>{if(w&&w[0]&&!m.has(w[0]))m.set(w[0],w)});return m};
/* vérification indépendante : mots connus = clés découvertes (S.ds « langue|clé »), répondues (S.sc) ou suivies (S.sr) */
window.KTEST_=()=>{const l=lg(),K=new Set(),add=k=>pqToks(k.startsWith('e:')?k.slice(2):k).forEach(t=>K.add(t));
  Object.keys(S.ds||{}).filter(k=>k.startsWith(l+'|')).forEach(k=>add(k.slice(l.length+1)));Object.keys(S.sc||{}).filter(k=>S.sc[k]>0).forEach(add);Object.keys(S.sr||{}).forEach(add);return K};
window.SUPOK_=(R0)=>{const pd=pqData(),l=pd.l,K=KTEST_(),ds=S.ds||{};const st0=pathPlan().map[R.pid]||{};window.OWN_=new Set((st0.tn||[]).map(k=>'tk:'+k).concat(st0.tn&&R.kn&&R.kn.vb&&R.kn.vb.length?['vb:'+R.kn.vb[0]]:[]));const tk=k=>(pd.TR[k]!=null&&pd.TR[k]<=R0)||!!ds['t:'+l+':'+k];
  const okT=([t,r])=>r<=R0||K.has(t)||(pd.V[t]&&Object.keys(pd.V[t]).some(vk=>K.has(nzI(vk).split(' ')[0])&&[...pd.V[t][vk]].some(tk)));
  const bad=[];(R.kn&&R.kn.ph||[]).forEach(x=>{const q=pqRank(x[0],x[1]);if(q.r===Infinity||!q.tk.filter(z=>z[1]<Infinity).every(okT))bad.push(x[0])});
  (R.pp||[]).forEach(x=>{const q=pqRank(x[0],x[1]);if(!q.tk.filter(z=>z[1]<Infinity).every(okT))bad.push('pp:'+x[0])});
  (R.kn&&R.kn.vb||[]).forEach(v=>{const t=nzI(v).split(' ')[0];if(!(pqFuzzy(pd,t)<=R0||K.has(t)))bad.push('vb:'+v)});
  (R.kn&&R.kn.tk||[]).forEach(k=>{if(!tk(k))bad.push('tk:'+k)});return bad.filter(b=>!(window.OWN_&&OWN_.has(b)))};
/* ouvre une étape, valide la fiche de découverte éventuelle, puis génère n questions comme la leçon (révisions comprises) */
window.CHK_=(id,n)=>{const st=pathPlan().map[id];const W0=WIX_(),known0=new Set([...W0.keys()].filter(k=>adIn(k)));pstart(id);let pres=[];if(DISC&&document.querySelector('.dsc')){pres=DISC.items.map(x=>x.k);discGo()}const presBad=pres.filter(k=>known0.has(k));
  if(!R||R.mode!=='lesson')return {id,err:'pas de leçon'};const W=WIX_(),bad=[],asked=[];
  for(let i=0;i<(n||25);i++){R.n=i%10;let q=null;try{q=rvQ()}catch(e){}if(!q){const ty=pickType();try{q=mkQ(ty,0)}catch(e){}}if(!q||!q.key)continue;const k=String(q.key);
    if(k.startsWith('e:')||W.has(k)){asked.push(k);if(!adIn(k))bad.push(q.ty+':'+k)}}
  const rk=adRk(st),sb=rk<st.rk?SUPOK_(rk):[],phBad=sb.length,ppBad=0;
  const xkBad=[...((R.kn&&R.kn.xk)||[])].filter(e=>!adIn('e:'+e)&&!(st.nw&&st.xs&&st.xs.has(e))).length,wsBad=(R.ws||[]).filter(w=>!adIn(w[0])&&!st.nw).map(w=>w[0]);
  home();return {id,pres,presBad,bad,asked:asked.length,phBad,ppBad,xkBad,wsBad,rk,srk:st.rk}};
/* parcours séquentiel simulé : chaque étape ouverte, découverte validée, réussie (7/10 ou plus) */
window.SEQ_=(n)=>{const done=[];for(const it of pathItems()){if(done.length>=n)break;if(it.test)continue;const st=pathPlan().map[it.id];pstart(it.id);if(DISC&&document.querySelector('.dsc'))discGo();
  (st.ws||[]).slice(0,6).forEach(w=>{S.sc[w[0]]=Math.max(1,S.sc[w[0]]||0)});const k=pthK(it.id);S.pth[k]=8;S.pa[k]=8;home();done.push(it.id)}return done};
0;
"""
with sync_playwright() as p:
    b=p.chromium.launch();c=b.new_context(service_workers="block");pg=c.new_page()
    errs=[];pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.goto(BASE+"index.html");pg.wait_for_timeout(2500);ev=pg.evaluate
    ev("()=>{S.ob=0;save()}");ev(H)
    # ---------- 1. toutes les étapes débloquées dès le départ ----------
    res={}
    for l,L in [("es",1),("es",3),("ca",2),("eu",1),("gl",5),("va",4)]:
        res[f"{l}{L}"]=ev("""([l,L])=>{SET_(l,L);CLR_();S.pthAll=1;const pm=pathPlanMain().map;/* étapes de leçon seulement : une étape « Mise en situation » (sit) lance le moteur d'immersion, pas une leçon (cf. path.py) */const ids=pathItems().filter(x=>!x.test&&!(pm[x.id]||{}).sit).map(x=>x.id);const pick=ids.filter((_,i)=>i%3===2).slice(0,14);const out=[];
            for(const id of pick){CLR_();S.pthAll=1;out.push(CHK_(id,25))}return out}""",[l,L])
    bad={k:[x for x in v if x.get("err") or x["bad"] or x["phBad"] or x["ppBad"] or x["xkBad"] or x["wsBad"]] for k,v in res.items()}
    bad={k:v for k,v in bad.items() if v}
    n=sum(len(v) for v in res.values());asked=sum(x.get("asked",0) for v in res.values() for x in v);pres=sum(len(x.get("pres",[])) for v in res.values() for x in v)
    ck(f"toutes les étapes débloquées, profil neuf ({n} étapes ouvertes au hasard, 6 langues/niveaux) : {asked} questions sur des mots ou expressions, toutes sur des notions présentées ({pres} présentées d'abord) ; phrases au point réellement atteint",not bad and asked>50,bad)
    # ---------- 2. reprise d'une ancienne étape (parcours suivi normalement) ----------
    r=ev("""()=>{SET_('es',1);CLR_();const done=SEQ_(14);const sr0=JSON.stringify(S.sr),pth0=JSON.stringify(S.pth);const out=[];
        for(const id of done.slice(0,10)){const st=pathPlan().map[id];const c=CHK_(id,20);out.push({id,rkSame:c.rk===c.srk,pres:c.pres.length,presBad:c.presBad,bad:c.bad,wsBad:c.wsBad})}
        return {out,unchanged:JSON.stringify(S.pth)===pth0}}""")
    ok=all(x["rkSame"] and not x["bad"] and not x["wsBad"] and not x["presBad"] for x in r["out"]) and r["unchanged"]
    ck("reprise d'une ancienne étape : même rang du parcours, aucune notion déjà connue re-présentée, aucune notion inconnue demandée, progression intacte",ok,r)
    r=ev("""()=>{SET_('es',1);CLR_();const done=SEQ_(14);const nxt=pathItems().find(x=>!x.done&&!x.lock&&!x.test);const st=pathPlan().map[nxt.id];pstart(nxt.id);const same=R.kn&&JSON.stringify(R.kn.ph.slice(0,30))===JSON.stringify(st.kn.ph.slice(0,30));home();return {id:nxt.id,same,rk:adRk(st),srk:st.rk}}""")
    ck("parcours suivi dans l'ordre : l'étape suivante garde exactement ses phrases d'avant (aucun changement pour l'apprenant régulier)",r["same"] and r["rk"]==r["srk"],r)
    # ---------- 3. changement de langue puis retour ----------
    r=ev("""()=>{SET_('es',1);CLR_();const shared=ALL.concat(LP).filter(w=>(w[2]||1)<=1).map(w=>w[0]);
        const id=pathItems().find(x=>!x.test&&pathPlan().map[x.id].nw&&pathPlan().map[x.id].ws).id;pstart(id);const ks=DISC?DISC.items.map(x=>x.k):[];discGo();home();
        const esIn=ks.filter(k=>adIn(k)).length;setLang('gl');SET_('gl',1);const glW=new Set(ALL.concat(LP).map(w=>w[0]));const common=ks.filter(k=>glW.has(k));
        const glIn=common.filter(k=>adIn(k));S.pthAll=1;const pr=Object.values(pathPlan().map).find(s=>!s.nw&&s.ws&&s.ws.some(w=>common.includes(w[0])));let c=null;if(pr)c=CHK_(pr.id,25);
        setLang('es');SET_('es',1);const back=ks.filter(k=>adIn(k)).length;return {ks:ks.length,esIn,common,glIn,c,back}}""")
    ck(f"changement de langue : mots découverts en castillan ({r['ks']}) non comptés en galicien, même écrits pareil ({len(r['common'])} en commun : {', '.join(r['common'][:4])})",r["esIn"]==r["ks"] and not r["glIn"],r)
    ck("en galicien, une étape d'entraînement ne les interroge pas sans les présenter",r["c"] is None or (not r["c"]["bad"] and not r["c"]["wsBad"]),r["c"])
    ck("retour en castillan : découvertes retrouvées",r["back"]==r["ks"],r)
    # ---------- 4. notion d'une étape antérieure jamais présentée ----------
    r=ev("""()=>{SET_('es',1);CLR_();S.pthAll=1;const fl=pathPlanMain().flat;const m=fl.find((s,i)=>!s.nw&&s.ws&&s.ws.length&&fl.slice(0,i).some(x=>x.nw&&x.ws&&x.ws.some(w=>s.ws.some(y=>y[0]===w[0]))));
        const prev=fl.find(x=>x.nw&&x.ws&&x.ws.some(w=>m.ws.some(y=>y[0]===w[0])));const notions=prev.ws.map(w=>w[0]).filter(k=>m.ws.some(y=>y[0]===k));
        const before=notions.filter(k=>adIn(k)).length;const c=CHK_(m.id,30);return {m:m.id,prev:prev.id,notions,before,pres:c.pres,bad:c.bad,wsBad:c.wsBad,asked:c.asked,phBad:c.phBad,rk:c.rk,srk:c.srk}}""")
    pres_or_absent=r["before"]==0 and not r["bad"] and not r["wsBad"] and r["rk"]<r["srk"]
    ck(f"notion d'une étape antérieure ({r['prev']}) jamais présentée : présentée avant d'être demandée dans {r['m']}, ou écartée ; phrases limitées",pres_or_absent and r["phBad"]==0,r)
    r=ev("""()=>{SET_('es',2);CLR_();S.pthAll=1;const st=Object.values(pathPlan().map).find(s=>!s.nw&&s.t&&!s.ru&&!s.tn&&s.ws&&s.ws.length>=8);pstart(st.id);const disc=!!document.querySelector('.dsc'),n=DISC?DISC.items.length:0,pre=!!(DISC&&DISC.items.pre);
        if(DISC)discGo();const ws=(R.ws||[]).map(w=>w[0]);const ok=ws.every(k=>adIn(k));home();return {id:st.id,disc,n,ws:ws.length,ok}}""")
    ck("étape de compétence (écoute, écrit…) sans fiche propre : les mots manquants sont présentés d'abord (4 au plus), puis seuls des mots introduits sont utilisés",r["disc"] and 1<=r["n"]<=4 and r["ok"],r)
    # ---------- 5. notions rencontrées ou maîtrisées : toujours utilisables ----------
    r=ev("""()=>{SET_('es',2);CLR_();S.pthAll=1;const st=Object.values(pathPlan().map).find(s=>!s.nw&&s.t&&!s.ru&&!s.tn&&s.ws&&s.ws.length>=12);const w=st.ws.map(w=>w[0]);
        const enc=w.slice(0,4),mas=w.slice(4,8);enc.forEach(k=>S.sc[k]=1);mas.forEach(k=>S.sr[k]={b:4,d:dayN()+20,p:4,m:1.2,c:[1,1,2,2],n:8,k:0,s:dayN()-5});
        pstart(st.id);const pres=DISC&&document.querySelector('.dsc')?DISC.items.map(x=>x.k):[];if(pres.length)discGo();const ws=(R.ws||[]).map(w=>w[0]);home();return {pres,enc:enc.every(k=>ws.includes(k)),mas:mas.every(k=>ws.includes(k)),reshown:pres.filter(k=>enc.includes(k)||mas.includes(k)),others:ws.filter(k=>!enc.includes(k)&&!mas.includes(k)&&!pres.includes(k))}}""")
    ck("mots rencontrés en réponse (score) et mots maîtrisés (carnet) : utilisés sans être re-présentés ; les autres seulement s'ils viennent d'être présentés",r["enc"] and r["mas"] and not r["reshown"] and not r["others"],r)
    r=ev("""()=>{SET_('es',2);CLR_();S.pthAll=1;const st=Object.values(pathPlan().map).find(s=>s.id==='BR2')||Object.values(pathPlan().map).find(s=>!s.nw&&s.xs&&s.xs.size>=6);if(!st)return {skip:1};
        const xs=[...st.xs];xs.slice(0,5).forEach(e=>S.sc['e:'+e]=1);pstart(st.id);if(DISC&&document.querySelector('.dsc'))discGo();const xk=[...R.kn.xk],rx=R.xs?[...R.xs]:[];const asked=[];
        for(let i=0;i<30;i++){let q=null;try{q=mkExp(['exM','exE','exL'][i%3])}catch(e){}if(q)asked.push(q.key)}home();return {xk:xk.length,allIn:xk.every(e=>adIn('e:'+e)),rx:rx.length,asked:[...new Set(asked)],ok:asked.every(k=>adIn(k))}}""")
    ck("expressions : seules celles rencontrées par l'apprenant sont interrogées dans une étape d'entraînement",r.get("skip") or (r["allIn"] and r["ok"] and r["xk"]==5),r)
    # ---------- 6. anciennes marques de découverte (sans langue) ----------
    r=ev("""()=>{SET_('es',1);CLR_();const w=ALL.find(w=>(w[2]||1)===1)[0],x=XP[0].e;S.ds={[w]:1,['e:'+x]:1,'t:es:pres':1,'zzz-inconnu':1};delete S.dsm;
        const a=adIn(w),b=adIn('e:'+x),keep=S.ds[w]===1&&S.ds['t:es:pres']===1&&S.ds['zzz-inconnu']===1&&!S.ds['es|zzz-inconnu'];setLang('ca');SET_('ca',1);const c=adIn(w);setLang('es');SET_('es',1);return {a,b,keep,c,mig:S.dsm}}""")
    ck("anciennes marques de découverte : reportées une fois sur la langue en cours, conservées telles quelles, sans effet sur une autre langue",r["a"] and r["b"] and r["keep"] and not r["c"] and r["mig"]==1,r)
    # ---------- 7. rien n'est réinitialisé ----------
    r=ev("""()=>{SET_('es',2);CLR_();const done=SEQ_(6);S.pthAll=1;const s0=JSON.stringify([S.pth,S.pa,S.sc,S.sr]);for(const it of pathItems().filter(x=>!x.test).slice(0,30)){pstart(it.id);home()}
        return JSON.stringify([S.pth,S.pa,S.sc,S.sr])===s0}""")
    ck("ouvrir 30 étapes (avec ou sans découverte) ne modifie ni la progression, ni les scores, ni le carnet",r)
    # ---------- 8. niveaux : progression réellement effectuée ----------
    LV=r"""
window.DONE_=(L,n)=>{const pc=pqData().plans[L];let i=0;for(const x of pc.flat){if(x.test)continue;if(n!=null&&x.nw&&i>=n)break;if(x.nw)i++;const k=lg()+':'+L+':'+x.id;S.pth[k]=8;S.pa[k]=8;
  (x.ws||[]).slice(0,4).forEach(w=>S.ds[adDK(w[0])]=1);(x.xi||[]).slice(0,4).forEach(z=>S.ds[adDK('e:'+z.e)]=1)}};
/* étape d'entraînement d'A2 riche en phrases, ouverte telle quelle (S.pthAll : accessible ne veut pas dire acquis) */
window.OPEN_=(pick)=>{const fl=pathPlanMain().flat;const st=pick?fl.find(pick):fl.filter(x=>!x.nw&&x.kn&&x.kn.ph.length>=20&&x.pp).slice(-1)[0];const n0=st.kn.ph.length;S.pthAll=1;pstart(st.id);if(DISC&&document.querySelector('.dsc'))discGo();
  const r0=adRk(st),o={id:st.id,R0:r0,srk:st.rk,n0,ph:(R.kn&&R.kn.ph||[]).length,vb0:st.kn.vb.length,vb:(R.kn&&R.kn.vb||[]).length,bad:r0<st.rk?SUPOK_(r0):[],phs:(R.kn&&R.kn.ph||[]).slice()};home();return o};
0;"""
    ev(LV)
    r=ev("""()=>{SET_('es',1);CLR_();DONE_(1,5);S.lvl=2;SET_('es',2);const a=OPEN_();const nw=pathItems().find(x=>!x.test&&pathPlan().map[x.id].nw).id;const b=OPEN_(x=>x.id===nw);delete a.phs;delete b.phs;
        return {a,b,a1:adLvDone(1)}}""")
    ck(f"passé en A2 sans avoir terminé A1 : supports limités à la progression A1 réellement faite ({r['a']['ph']} phrases sur {r['a']['n0']} prévues, {r['a']['vb']} verbes sur {r['a']['vb0']}), aucune notion inconnue",not r["a1"] and r["a"]["R0"]<2000 and r["a"]["ph"]<r["a"]["n0"] and not r["a"]["bad"] and r["b"]["R0"]<r["b"]["srk"] and not r["b"]["bad"],r)
    r=ev("""()=>{SET_('es',1);CLR_();S.lvl=2;SET_('es',2);const a=OPEN_();delete a.phs;CLR_();SET_('es',3);const b=OPEN_();delete b.phs;return {a,b}}""")
    ck("niveau seulement choisi ou débloqué (A2, B1) sans rien de fait : aucun support d'un niveau antérieur imposé",r["a"]["R0"]==0 and r["b"]["R0"]==0 and not r["a"]["bad"] and not r["b"]["bad"] and r["a"]["ph"]<r["a"]["n0"],r)
    r=ev("""()=>{SET_('es',1);CLR_();DONE_(1);SET_('es',2);const done=adLvDone(1);const fl=pathPlanMain().flat;const i=fl.findIndex(x=>!x.nw&&x.kn&&x.kn.ph.length>=8&&x.pp);
        fl.slice(0,i).forEach(x=>{if(x.test)return;const k=lg()+':2:'+x.id;S.pth[k]=8;S.pa[k]=8;(x.ws||[]).slice(0,4).forEach(w=>S.ds[adDK(w[0])]=1)});const st=fl[i];pstart(st.id);if(DISC&&document.querySelector('.dsc'))discGo();
        const same=JSON.stringify((R.kn.ph||[]).map(x=>x[0]))===JSON.stringify(st.kn.ph.map(x=>x[0]))&&JSON.stringify(R.kn.vb)===JSON.stringify(st.kn.vb)&&JSON.stringify(R.kn.tk)===JSON.stringify(st.kn.tk);home();return {done,id:st.id,same,R0:adRk(st),srk:st.rk}}""")
    ck("A1 terminé, A2 suivi dans l'ordre : A1 compte comme acquis, supports exactement ceux prévus (aucun changement)",r["done"] and r["same"] and r["R0"]==r["srk"],r)
    r=ev("""()=>{SET_('es',1);CLR_();DONE_(1);SET_('es',2);DONE_(2,3);const base=OPEN_();
        /* notions d'A2 rencontrées hors parcours (Mélange, révisions) : mots de phrases prévues mais pas encore atteintes */
        const pd=pqData(),st=pathPlanMain().flat.find(x=>x.id===base.id),K=KTEST_(),beyond=st.kn.ph.filter(x=>{const q=pqRank(x[0],x[1]);return q.r>base.R0}),need=new Set();
        beyond.slice(0,40).forEach(x=>pqRank(x[0],x[1]).tk.forEach(([t,r])=>{if(r>base.R0&&!K.has(t))need.add(t)}));
        const W=new Map();ALL.concat(LP).forEach(w=>{pqToks(w[0]).forEach(t=>{if(!W.has(t))W.set(t,w[0])})});const met=[...need].map(t=>W.get(t)).filter(Boolean).slice(0,25);met.forEach(k=>S.sc[k]=1);
        const after=OPEN_(x=>x.id===base.id);const K2=KTEST_();const usesMet=after.phs.some(x=>pqRank(x[0],x[1]).tk.some(([t,r])=>r>after.R0&&K2.has(t)));
        return {R0:base.R0,srk:base.srk,a2:adLvDone(2),before:base.ph,after:after.ph,met:met.length,usesMet,bad:after.bad,bad0:base.bad}}""")
    ck(f"A1 terminé, A2 entamé, notions d'A2 rencontrées : phrases qui les utilisent admises ({r['before']} → {r['after']}), les autres toujours écartées",not r["a2"] and r["R0"]<r["srk"] and r["after"]>r["before"] and r["usesMet"] and not r["bad"] and not r["bad0"],r)
    r=ev("""()=>{SET_('es',1);CLR_();DONE_(1,5);SET_('es',2);const st=pathPlanMain().flat.filter(x=>!x.nw&&x.kn&&x.kn.ph.length>=20&&x.pp).slice(-1)[0];const s0=JSON.stringify([S.pth,S.pa,S.sc,S.sr]);OPEN_(x=>x.id===st.id);
        const R0=adRk(st),K=KTEST_();const ex=st.kn.ph.find(x=>pqRank(x[0],x[1]).tk.some(([t,r])=>r>R0&&r<Infinity&&!K.has(t)&&!pqData().V[t]));OPEN_(x=>x.id===st.id);pstart(st.id);if(DISC&&document.querySelector('.dsc'))discGo();
        const kept=!!ex&&R.kn.ph.some(x=>x[0]===ex[0]);home();return {ex:ex&&ex[0],kept,unchanged:JSON.stringify([S.pth,S.pa,S.sc,S.sr])===s0}}""")
    ck("phrase prévue mais qui introduirait une notion inconnue : écartée ; aucune progression modifiée",r["ex"] and not r["kept"] and r["unchanged"],r)
    ck("aucune erreur JavaScript",not errs,errs[:3])
    b.close()
print(sum(R),"/",len(R),"OK");sys.exit(0 if all(R) else 1)
