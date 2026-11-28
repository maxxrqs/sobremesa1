# Chantier 3, lot B : exercices intégrés — « Complète » (2–3 trous), « Transforme » (personne, temps, registre), « Réponds » (modèles XD).
# 5 langues étudiées × niveaux A1–C1, 200 essais par format : cible prise dans le carnet, appuis au palier ≥ 2, aucune notion non
# enseignée exigée, difficulté selon le palier, trous sur des mots entiers (basque compris), effets sur le carnet (plafonds de mkRec,
# appuis sans entrée ni date), intégration au parcours (MKA, pickType, révisions), écrans 360 × 640 dans les 5 interfaces, voix enregistrées.
# Usage : python3 tests/integres.py URL
import sys,json
from playwright.sync_api import sync_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else "http://127.0.0.1:8774/"
R=[]
def ck(n,c,i=""):R.append(bool(c));print("OK  " if c else "FAIL",n,"" if c else str(i)[:900],flush=True)
LANGS=["es","va","ca","gl","eu"];UIS=["fr","en","de","it","pt"]
H=r"""
window.SET_=(l,L)=>{S.lang=l;S.lvl=L;S.ob=0;build();XDIRTY=1;xens();XPWC=null;MKDC.clear()};
/* profil type : tout le contenu du niveau introduit, carnet aux paliers 0 à 4 répartis, une notion sur deux à revoir */
window.PROF_=(l,L)=>{SET_(l,L);S.sr={};S.sc={};S.mi={};S.ds={};S.tp={};const t=dayN();let i=0;
  const ent=(k,p)=>{const d=mkDif(k),c=[1,2,3,4].map(P=>P<=p?MKN[d][P]:0);S.sr[k]={b:1,d:t+(i%2?0:3),p,m:1,c,n:3,k:0,s:t-2};if(d===3)S.sr[k].j=[0,0,0,0]};
  ALL.concat(LP).filter(w=>(w[2]||1)<=L).forEach(w=>{S.sc[w[0]]=1;ent(w[0],i++%5)});
  XP.filter(x=>x.l<=L).forEach(x=>{ent('e:'+x.e,i++%5)});Object.keys(VD[l]).filter(v=>vLvl(l,v)<=L).forEach(v=>{S.sc[v]=1;ent('v:'+v,i++%5)});
  start('Mélange');R.n=0;R.hist=[];R.xpi=new Set();R.xpn=0;R.tpn=0;R.tc=0;R.tpl=null};
window.ENT_=(k,p,due)=>{const d=mkDif(k),c=[1,2,3,4].map(P=>P<=p?MKN[d][P]:0);S.sr[k]={b:1,d:dayN()+(due?0:5),p,m:1,c,n:3,k:0,s:dayN()-2};if(d===3)S.sr[k].j=[0,0,0,0];return S.sr[k]};
/* contrôle d'une question intégrée : liste des écarts (vide = conforme) */
window.VAL_=(q,forced)=>{const B=[],sr=S.sr||{},t=dayN(),L=lg(),pc=itP(q.key),e=sr[q.key],tk=itTk(),r=RLs();
  if(!e)B.push('cible hors carnet');else if(!forced&&((e.p||0)>=5||!((e.p||0)<=2||e.d<=t)))B.push('cible ni fragile ni à revoir');
  const ap=q.bl?q.bl.filter(b=>!b.c).map(b=>b.key):q.apk?q.apk.map(x=>x.key):(q.ap||[]).map(x=>x.key);
  if(!ap.length)B.push('aucun appui');ap.forEach(k=>{if(!sr[k]||itP(k)<2)B.push('appui < palier 2 : '+k)});if(ap.includes(q.key))B.push('appui = cible');
  if(q.bl){const n=q.bl.length;
    if(q.ty==='itr'&&!(pc<=2&&(pc<=1?n===2:n>=2&&n<=3)))B.push('itr palier '+pc+' trous '+n);
    if(q.ty==='itrE'&&!(pc>=3&&(pc===3?n===2:n>=2&&n<=3)))B.push('itrE palier '+pc+' trous '+n);
    if(q.bl.filter(b=>b.c).length!==1)B.push('cible pas sur un seul trou');
    q.bl.forEach(b=>{const w=q.ws[b.i];if(czCore(w)!==b.pre+b.g)B.push('trou partiel : '+w+' / '+b.g);if(L==='eu'&&(b.pre||EV.raw(b.g)!==EV.raw(czCore(w))))B.push('basque : mot non entier '+w);
      if(!sr[b.key])B.push('trou hors carnet '+b.key);if(b.kind==='v'){const a=itAn(L,[q.es]),z=a.sl.find(x=>x.i===b.i);if(!z||!z.e.some(x=>itTkOk(tk,x.tk)))B.push('temps non enseigné '+b.g)}});
    if(q.ty==='itr'){const A=q.bl.map(b=>EV.raw(b.g)),K=q.bank.map(x=>EV.raw(x));if(!A.every(a=>K.includes(a)))B.push('réponse absente des étiquettes');if(K.length<=A.length)B.push('aucun intrus');if(new Set(K).size!==K.length)B.push('étiquettes en double')}
    const f=PH.find(x=>x[0]===q.es);if(!f)B.push('phrase inconnue');else if(r&&r.kn&&r.kn.ph&&r.kn.ph.length){if(!r.kn.ph.includes(f))B.push('phrase hors progression')}else if((f[2]||1)>lv()||!itKnown(itAn(L,f)))B.push('phrase non introduite')}
  if(q.ty==='itf'||q.ty==='itfE'){const a=itAn(L,[q.src]),sp=a.vs[0],e0=sp&&sp.e[0];
    if(q.ty==='itf'&&pc>1)B.push('itf palier '+pc);if(q.ty==='itfE'&&pc<2)B.push('itfE palier '+pc);if(q.md==='t'&&pc<3)B.push('temps changé au palier '+pc);
    if(a.vs.length!==1)B.push('plusieurs verbes');if(!e0||e0.p>1)B.push('source pas à la 1re/2e personne du singulier');if(!e0||'v:'+e0.vk!==q.key)B.push('verbe ≠ cible');
    if(L==='eu'&&q.md!=='p')B.push('basque : temps ou registre');if(q.md==='r'&&!ITUD[L])B.push('registre sans vouvoiement');
    if(a.rt.some(x=>x.split(' ').some(y=>(ITPRS_[L]||new Set()).has(y)||(ITSUB_[L]||new Set()).has(y))))B.push('pronom, possessif ou subordonnée');
    if(EV.raw(q.res)===EV.raw(q.src))B.push('transformation sans effet');
    const ok=[0,1,2].some(p=>{const d=VD[L][e0&&e0.vk];return d&&vlist(L,d).some(t=>{try{return EV.raw(vrows(L,d,t).F[p])===EV.raw(q.g)}catch(x){return false}})});if(!ok)B.push('forme visée hors singulier');
    if(q.o&&(!q.o.includes(q.g)||q.o.length<3))B.push('options');
    const f=PH.find(x=>x[0]===q.src);if(!f)B.push('phrase inconnue');else if(r&&r.kn&&r.kn.ph&&r.kn.ph.length){if(!r.kn.ph.includes(f))B.push('phrase hors progression')}else if(!itKnown(itAn(L,f)))B.push('phrase non introduite')}
  if(q.ty==='irp'||q.ty==='irpE'){if(q.ty==='irp'&&pc>2)B.push('irp palier '+pc);if(q.ty==='irpE'&&pc<3)B.push('irpE palier '+pc);
    const z=xdP(L).find(x=>x.m===q.models[0]&&x.n===q.npc);if(!z)B.push('échange inconnu');else if(r&&r.kn&&r.kn.sc?!r.kn.sc.has(z.n+'|'+z.m):z.l>lv())B.push('échange hors progression');
    if(!itHas(q.models[0],q.cf))B.push('cible absente du modèle');if(!itKnown(itAn(L,[q.models[0],''])))B.push('modèle non introduit');
    if(q.ty==='irp'&&q.toks.slice().sort().join('|')!==q.models[0].split(' ').sort().join('|'))B.push('étiquettes ≠ modèle')}
  return B};
window.GEN_=(fn,n)=>{const o={n:0,bad:[],ty:{},keys:new Set(),md:{}};for(let i=0;i<n;i++){let q=null;try{q=window[fn]()}catch(x){o.bad.push('exception '+x.message);continue}if(!q)continue;o.n++;o.ty[q.ty]=(o.ty[q.ty]||0)+1;if(q.md)o.md[q.md]=(o.md[q.md]||0)+1;o.keys.add(q.key);
  const b=VAL_(q,false);if(b.length&&o.bad.length<6)o.bad.push(q.ty+' '+(q.es||q.src||q.npc)+' : '+b.join(', '))}o.keys=o.keys.size;return o};
window.SNAP_=k=>JSON.stringify(S.sr[k]);
/* question d'un type donné, cible mise au palier voulu (essais sur les notions du carnet) */
window.FORCE_=(fn,ty,p)=>{const ks=shuf(Object.keys(S.sr).filter(k=>!k.startsWith('q:'))).slice(0,600);for(const k of ks){const old=S.sr[k];ENT_(k,p,true);let q=null;try{q=window[fn](k)}catch(e){}if(q&&q.ty===ty&&q.key===k)return q;S.sr[k]=old}return null};
window.ANS_=(q,ok)=>{/* répond à une question intégrée affichée ; ok = tableau de booléens par trou (itr/itrE) ou booléen */
  R.q=q;R.done=false;draw();
  if(q.ty==='itr'){const used=new Set();q.bl.forEach((b,k)=>{let j=q.bank.findIndex((w,j)=>!used.has(j)&&(ok[k]?EV.raw(w)===EV.raw(b.g):!q.bl.some(c=>EV.raw(c.g)===EV.raw(w))));if(j<0)j=q.bank.findIndex((w,j)=>!used.has(j)&&EV.raw(w)!==EV.raw(b.g));used.add(j);q.fill[k]=j});itChk()}
  else if(q.ty==='itrE'){q.bl.forEach((b,k)=>{const e=document.getElementById(k?'ti'+k:'ti');e.value=ok[k]?b.g:'zzzz'});itChk()}
  else if(q.ty==='itf'){ans(ok?q.o.indexOf(q.g):q.o.findIndex(x=>x!==q.g))}
  else if(q.ty==='itfE'){document.getElementById('ti').value=ok?q.g:'zzzz';itChkF()}
  else if(q.ty==='irp'){const w=q.models[0].split(' ');const used=new Set();q.cur=[];(ok?w:w.slice().reverse()).forEach(x=>{const j=q.toks.findIndex((y,j)=>!used.has(j)&&y===x);used.add(j);q.cur.push(j)});irpChk()}
  else if(q.ty==='irpE'){document.getElementById('ti').value=ok===true?q.models[0]:typeof ok==='string'?ok:'zzzz qqq';irpChk()}};
0;
"""
with sync_playwright() as p:
    b=p.chromium.launch();errs=[]
    def page(ui="fr",w=420,h=900):
        c=b.new_context(service_workers="block",locale={"fr":"fr-FR","en":"en-GB","de":"de-DE","it":"it-IT","pt":"pt-PT"}[ui],viewport={"width":w,"height":h})
        pg=c.new_page();pg.on("pageerror",lambda e:errs.append(str(e)))
        pg.goto(BASE+"index.html");pg.wait_for_timeout(2500)
        if ui!="fr":pg.evaluate("(u)=>{if(typeof setUI==='function')setUI(u)}",ui);pg.wait_for_timeout(600)
        pg.evaluate(H);return pg
    pg=page();ev=pg.evaluate
    # ---------- 1. déclaration : MKA, compétences, registre des formats ----------
    r=ev("""()=>({mka:['itr','itf','irp','itrE','itfE','irpE'].map(t=>MKA[t]),modl:['itr','itrE','itf','itfE','irp','irpE'].every(t=>MODL[t]&&TYK[t]&&NXD[t]),nx:ITT.every(t=>NX[t]&&typeof NX[t].mk==='function'),pq:PQPH.includes('itr')&&PQPH.includes('itf')&&PQSC.includes('irp')})""")
    ck("MKA : trois formats intégrés déclarés (propositions 2 · trous écrits et transformation écrite 3 · réponse libre 4)",r["mka"]==[2,2,2,3,3,4],r)
    ck("formats rattachés aux compétences (MODL, TYK), au rendu (NXD), au registre NX et aux filtres de progression (PQPH, PQSC)",r["modl"] and r["nx"] and r["pq"],r)
    # ---------- 2. 200 essais par format, 5 langues × A1–C1 : cible, appuis, notions enseignées, difficulté, mots entiers ----------
    tot={}
    for l in LANGS:
        for L in [1,2,3,4,5]:
            r=ev("""([l,L])=>{PROF_(l,L);return {tr:GEN_('itTrou',200),tf:GEN_('itTrf',200),rp:GEN_('itRep',200)}}""",[l,L])
            bad=[x for k in r for x in r[k]["bad"]]
            for k in r:tot.setdefault(l,{});tot[l][k]=tot[l].get(k,0)+r[k]["n"]
            ck(f"{l} A{L}/{['A1','A2','B1','B2','C1'][L-1]} : questions conformes (cible du carnet, appuis ≥ 2, notions enseignées, palier, mots entiers) — "+", ".join(f"{k} {r[k]['n']} ({r[k]['keys']} cibles)" for k in r),not bad,bad)
    ck("chaque format est proposé dans chacune des 5 langues (au moins un niveau)",all(all(v[k]>0 for k in v) for v in tot.values()),tot)
    # difficulté : tous les modes apparaissent quand le carnet le permet (es, B1)
    r=ev("""()=>{const o={};for(const l of ['es','gl']){PROF_(l,3);for(const [fn,ty,p] of [['itTrou','itr',0],['itTrou','itr',2],['itTrou','itrE',3],['itTrou','itrE',4],['itTrf','itf',0],['itTrf','itfE',2],['itTrf','itfE',3],['itRep','irp',1],['itRep','irpE',3]]){
        const q=FORCE_(fn,ty,p);o[l+':'+ty+p]=q?[q.bl?q.bl.length:q.md||'',VAL_(q,true).join(',')]:null}
      PROF_(l,3);let t=0,r=0;for(let i=0;i<30;i++){const q=FORCE_('itTrf','itfE',3);if(q&&q.md==='t')t++;if(q&&q.md==='r')r++}o[l+':temps/registre']=[t,r]}return o}""")
    ck("difficulté selon le palier : chaque mode est atteint au bon palier (2 trous à étiquettes → 3 trous écrits ; choix → écrit → temps ; réponse guidée → libre)",
       all(v is not None and (not isinstance(v[1],str) or v[1]=="") for k,v in r.items() if "/" not in k) and r["es:temps/registre"][0]>0 and r["es:itr0"][0]==2 and r["es:itrE3"][0]==2,r)
    r=ev("""()=>{PROF_('eu',5);const b=GEN_('itTrf',300);return b.md}""")
    ck("basque : transformation de personne uniquement (ni temps ni registre)",list(r.keys())==["p"],r)
    # ---------- 3. progression réelle : étape du parcours (R.kn), découverte et entraînement par compétence exclus ----------
    r=ev("""()=>{const o={};for(const l of ['es','eu']){PROF_(l,2);const pl=pathPlan(),st=Object.values(pl.map).find(s=>!s.nw&&!s.test&&s.kn&&s.kn.ph&&s.kn.ph.length>=8&&(s.pt||[]).some(x=>ITPH.includes(x)));if(!st){o[l]='pas d\\'étape';continue}
        R={mode:'lesson',t:st.t||'Chunk',n:0,ok:0,xp:0,cat:null,pid:st.id,pt:st.pt||null,ws:st.ws||null,dp:st.dp||null,gp:st.gp||null,go:st.go||null,xs:st.xs||null,qs:st.qs||null,vs:st.vs||null,pp:st.pp||null,kn:st.kn||null,tn:st.tn||null,hist:[]};try{adFix(st)}catch(e){}
        const g=[GEN_('itTrou',150),GEN_('itTrf',150),GEN_('itRep',150)];const ty=new Set();for(let i=0;i<400;i++)ty.add(pickType());
        o[l]={n:g.map(x=>x.n),bad:g.flatMap(x=>x.bad),pick:[...ty].filter(x=>ITT.includes(x))}}
      PROF_('es',2);const nw=Object.values(pathPlan().map).find(s=>s.nw&&!s.test&&s.kn);R={mode:'lesson',t:nw.t||'Chunk',n:0,ok:0,xp:0,pid:nw.id,pt:nw.pt||null,ws:nw.ws||null,kn:nw.kn,hist:[]};
      const a=new Set();for(let i=0;i<400;i++)a.add(pickType());o.nw=[...a].filter(x=>ITT.includes(x));
      start('EE');const c=new Set();for(let i=0;i<300;i++)c.add(pickType());o.sk=[...c].filter(x=>ITT.includes(x));return o}""")
    ck("étape du parcours : phrases, échanges et temps limités à la progression réellement effectuée (es, eu)",all(isinstance(r[l],dict) and not r[l]["bad"] and sum(r[l]["n"])>0 for l in ["es","eu"]),r)
    ck("étape du parcours : les formats intégrés font partie des tirages (pickType)",all(r[l]["pick"] for l in ["es","eu"]),r)
    ck("étape de découverte et entraînement d'une compétence : aucun exercice intégré",r["nw"]==[] and r["sk"]==[],r)
    # fréquence : pas de multiplication artificielle (séances de 10 questions)
    r=ev("""()=>{PROF_('es',3);const c=[];for(let s=0;s<30;s++){start('Mélange');R.hist=[];let n=0;for(let i=0;i<10;i++){next();if(/^i(tr|tf|rp)/.test(R.q.ty))n++;R.done=true;R.n++}c.push(n)}return c}""")
    ck("séance de 10 questions : au plus 3 exercices intégrés, en moyenne 2 au plus (formats diversifiés, pas multipliés)",max(r)<=3 and sum(r)/len(r)<=2 and sum(r)>0,r)
    # ---------- 4. révisions (rvQ → mkRvQ) : la notion échue elle-même, exercice selon son palier ----------
    r=ev("""()=>{PROF_('es',3);const ix=mkIdx(),o={n:0,it:0,same:0,bad:[]};const ks=Object.keys(S.sr).filter(k=>!/^[eq]:/.test(k)).slice(0,400);
      for(const k of ks){const c=mkCand(k,ix);if(!c)continue;R.kn=null;let q=null;try{q=mkRvQ(c,[])}catch(e){}if(!q)continue;o.n++;if(q.key===k)o.same++;if(/^i(tr|tf|rp)/.test(q.ty)){o.it++;const b=VAL_(q,true);if(b.length&&o.bad.length<5)o.bad.push(q.ty+' '+b.join(','))}}return o}""")
    ck(f"révision ciblée : la question porte toujours sur la notion échue ; {r['it']} sur {r['n']} en exercice intégré, conformes",r["n"]>0 and r["same"]==r["n"] and 0<r["it"]<r["n"] and not r["bad"],r)
    # ---------- 5. carnet : cible jugée sur son trou, appuis sans entrée ni date, plafonds de mkRec ----------
    r=ev("""()=>{PROF_('es',3);let q=null;for(let i=0;i<300&&!q;i++){const x=itTrou();if(x&&x.ty==='itr'&&x.bl.length===2)q=x}if(!q)return null;
      const ap=q.bl.find(b=>!b.c).key,keys=Object.keys(S.sr).length,due0=mkDue().filter(c=>c.key!==q.key).length,a0=JSON.parse(SNAP_(ap)),c0=JSON.parse(SNAP_(q.key)),sc0=S.sc[q.key]||0;
      ANS_(q,q.bl.map(()=>true));const a1=S.sr[ap],c1=S.sr[q.key];
      return {keys:Object.keys(S.sr).length===keys,due:mkDue().filter(c=>c.key!==q.key).length===due0,ap:[a0.d,a0.b,a0.m,a0.s,a0.k].join()===[a1.d,a1.b,a1.m,a1.s,a1.k].join()&&a1.p<=Math.max(2,a0.p),
        cible:[c0.n+1===c1.n,c1.s===dayN(),(S.sc[q.key]||0)===sc0+1,c1.p<=2],fb:!!document.querySelector('#fb .fb.ok')}}""")
    ck("réussite complète : cible enregistrée (mkRec), carnet sans nouvelle entrée, révisions dues des autres notions inchangées",r and r["keys"] and r["due"] and all(r["cible"]) and r["fb"],r)
    ck("réussite complète : appui sans changement de boîte, de date, de facilité ni de compteur, palier 2 au plus",r and r["ap"],r)
    r=ev("""()=>{PROF_('es',3);let q=null;for(let i=0;i<300&&!q;i++){const x=itTrou();if(x&&x.ty==='itr'&&x.bl.length===2)q=x}const ap=q.bl.find(b=>!b.c).key;
      const e=S.sr[ap];e.p=2;e.c=e.c.slice();e.c[2]=1;const c0=S.sr[q.key].k||0,sc0=S.sc[q.key]||0;ANS_(q,q.bl.map(b=>b.c));const A=S.sr[ap];
      const r1={ap:[A.p,A.c[2]],cible:[(S.sc[q.key]||0)===sc0+1,(S.sr[q.key].k||0)===c0],part:!!document.querySelector('#fb .fb.pt')};
      PROF_('es',3);q=null;for(let i=0;i<300&&!q;i++){const x=itTrou();if(x&&x.ty==='itr'&&x.bl.length===2)q=x}const ap2=q.bl.find(b=>!b.c).key,a0=JSON.stringify(S.sr[ap2].c),k0=S.sr[q.key].k||0;
      ANS_(q,q.bl.map(b=>!b.c));r1.ko=[(S.sr[q.key].k||0)===k0+1,JSON.stringify(S.sr[ap2].c)!==a0||S.sr[ap2].p>=2];return r1}""")
    ck("appui faux, cible juste : cible réussie, appui inchangé (ni recul de palier, ni preuve au-delà du palier 2 touchée)",r["ap"]==[2,1] and all(r["cible"]) and r["part"],r)
    ck("cible fausse, appui juste : échec enregistré sur la cible seulement, preuve d'appui gagnée",all(r["ko"]),r)
    r=ev("""()=>{const o={};PROF_('es',3);const run=(ty,p0,n)=>{const q=FORCE_(ty.startsWith('itr')?'itTrou':ty.startsWith('itf')?'itTrf':'itRep',ty,p0);if(!q)return 'aucune';
        const k=q.key;const P=[];for(let i=0;i<n;i++){const z=Object.assign({},q,{res:null,val:null,done:0,ks:null});if(z.fill)z.fill=z.bl.map(()=>null);if(z.cur)z.cur=[];if(z.ap&&!z.bl)z.ap=z.ap.map(x=>Object.assign({},x));S.sr[k].d=dayN();ANS_(z,z.bl?z.bl.map(()=>true):true);P.push(S.sr[k].p)}return {k,P}};
      for(const [ty,cap,p0] of [['itr',2,0],['itf',2,0],['irp',2,0],['itrE',3,3],['itfE',3,2]])o[ty]=[run(ty,p0,8),cap];return o}""")
    ck("jamais d'accélération : 8 réussites d'affilée ne dépassent pas le palier du format (2 avec propositions, 3 trous ou transformation écrits)",all(isinstance(v[0],dict) and max(v[0]["P"])<=v[1] for v in r.values()),r)
    r=ev("""()=>{PROF_('es',3);let q=null;for(let i=0;i<40&&!q;i++){const x=FORCE_('itRep','irpE',3);if(x&&x.models.some(m=>!itHas(m,x.cf)))q=x}if(!q)return 'aucune';
      const m=q.models.find(m=>!itHas(m,q.cf)),n0=S.sr[q.key].n;ANS_(q,m);const a=S.sr[q.key].n===n0;
      PROF_('es',3);q=FORCE_('itRep','irpE',3);const n1=S.sr[q.key].n;ANS_(q,true);return {variante:a,modele:S.sr[q.key].n===n1+1,ok:!!document.querySelector('#fb .fb.ok')}}""")
    ck("réponse libre : variante acceptée sans la cible → cible non comptée ; modèle avec la cible → cible enregistrée",isinstance(r,dict) and r["variante"] and r["modele"] and r["ok"],r)
    r=ev("""()=>{PROF_('es',3);const keys=new Set(['b','d','p','m','c','n','k','s','j','x']);let bad=[];for(let i=0;i<40;i++){const f=[itTrou,itTrf,itRep][i%3];const q=f();if(!q)continue;ANS_(q,q.bl?q.bl.map(()=>Math.random()<.6):Math.random()<.6);if(R.done)save()}
      for(const k in S.sr)for(const f in S.sr[k])if(!keys.has(f))bad.push(k+'.'+f);return {bad:bad.slice(0,5),n:Object.keys(S.sr).length}}""")
    ck("profils : aucun nouveau champ dans le carnet (b, d, p, m, c, n, k, s, j, x seulement), sauvegarde sans erreur",r["bad"]==[],r)
    # ---------- 6. voix : uniquement des phrases et répliques enregistrées (jamais la phrase transformée) ----------
    r=ev("""()=>{const said=[],sp0=window.speak;window.speak=t=>{said.push(String(t))};const bad=[];
      for(const l of LK){PROF_(l,3);for(let i=0;i<45;i++){const f=[itTrou,itTrf,itRep][i%3],q=f();if(!q)continue;ANS_(q,q.bl?q.bl.map(()=>true):true)}
        const ok=new Set(PH.map(x=>x[0]).concat(xdP(l).flatMap(z=>[z.n,z.m])));said.splice(0).forEach(t=>{if(!ok.has(t))bad.push(l+' : '+t)})}
      window.speak=sp0;return bad.slice(0,6)}""")
    ck("voix : seules des phrases du corpus et des répliques XD sont lues (pas de voix de secours pour une phrase transformée)",r==[],r)
    # ---------- 7. écrans 360 × 640 dans les 5 interfaces ----------
    for ui in UIS:
        pm=page(ui,360,640)
        r=pm.evaluate("""()=>{const o={},T={itr:'Complète la phrase',itrE:'Complète la phrase',itf:'Transforme la phrase',itfE:'Transforme la phrase',irp:'Réponds',irpE:'Réponds'};
          for(const l of ['es','eu']){PROF_(l,l==='eu'?5:3);const got={};for(const [fn,ty,p] of [['itTrou','itr',1],['itTrou','itrE',4],['itTrf','itf',1],['itTrf','itfE',3],['itRep','irp',1],['itRep','irpE',3]]){const q=FORCE_(fn,ty,p);if(q)got[ty]=q}
            for(const ty in got){const q=got[ty];R.q=q;R.done=false;draw();scrollTo(0,0);const c=document.querySelector('.q'),h=document.querySelector('.q h2'),btn=document.getElementById('chk')||[...document.querySelectorAll('.q .opt')].pop();
              const bb=btn?btn.getBoundingClientRect().bottom:9999;o[l+':'+ty]={fit:bb<=innerHeight+1,w:document.documentElement.scrollWidth<=innerWidth+1,tr:h&&h.textContent.trim().startsWith(tr(T[ty])),lab:q.lab?q.lab:''}}}return o}""")
        bad={k:v for k,v in r.items() if not (v["fit"] and v["w"] and v["tr"])}
        lab_ok=ui=="fr" or all(not v["lab"] or not any(x in v["lab"] for x in ["Change de personne","Passe au vouvoiement","Mets le verbe"]) for v in r.values())
        ck(f"interface {ui} : 6 variantes affichées en 360 × 640 sans défilement ni débordement, consignes traduites ({len(r)} écrans)",len(r)>=10 and not bad and lab_ok,bad or r)
        pm.context.close()
    import os
    base=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","tr")
    keys=["Transforme la phrase","Change de personne : {0}","Passe au vouvoiement : {0}","Mets le verbe au temps : {0}","Réponds"]
    miss=[(u,k) for u in ["en","de","it","pt"] for k in keys if not json.load(open(os.path.join(base,u+".json"),encoding="utf-8")).get(k)]
    ck("traductions des nouvelles consignes présentes (en, de, it, pt)",miss==[],miss)
    ck("aucune erreur JavaScript",errs==[],errs[:5])
    b.close()
print(f"\n{sum(R)}/{len(R)} contrôles réussis");sys.exit(0 if all(R) else 1)
