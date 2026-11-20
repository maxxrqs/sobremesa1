# Carnet de maîtrise (chantier 1) : paliers, preuves selon la difficulté, oublis, ancrage, répétition espacée,
# migration prudente des anciennes progressions, révision ciblée de tous les types de notions (5 langues, A1–C1),
# enregistrement depuis de vraies réponses, sauvegarde et changement de langue.
# Usage : python3 tests/carnet.py URL
import sys,json
from playwright.sync_api import sync_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else "http://127.0.0.1:8774/"
R=[]
def ck(n,c,i=""):R.append(bool(c));print("OK  " if c else "FAIL",n,"" if c else str(i)[:600],flush=True)
H=r"""
window.T_=(ty)=>({ty});
window.REC=(k,ty,s)=>mkRec(k,{ty},s);
window.SHIFT=(k,days)=>{const e=S.sr[k];e.s=(e.s||dayN())-days;e.d=e.d-days;if(e.j)e.j=e.j.map(x=>x?x-days:0)};
window.FRESH_=()=>{S.sr={};S.sc={};S.mi={};MKDC.clear()};
0;
"""
with sync_playwright() as p:
    b=p.chromium.launch();c=b.new_context(service_workers="block");pg=c.new_page()
    errs=[];pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.goto(BASE+"index.html");pg.wait_for_timeout(2500);ev=pg.evaluate
    ev("()=>{S.lang='es';S.lvl=2;S.ob=0;build();XDIRTY=1;xens();save()}");ev(H)
    # ---------- difficulté ----------
    d=ev("()=>{FRESH_();const w2=ALL.find(w=>w[0]==='gracias'),cog=ALL.concat(LP).find(w=>mkDif(w[0])===1);return {hola:mkDif('hola'),cog:cog&&[cog[0],cog[1]],q:mkDif('q:'+EQ[0].k),e:mkDif('e:'+XP[0].e),tener:mkDif('v:tener'),hablar:mkDif('v:hablar')}}")
    ck("difficulté : mot courant 2, mot transparent 1, grammaire 3, verbe irrégulier 3, régulier 2",d["hola"]==2 and d["cog"] and d["q"]==3 and d["tener"]==3 and d["hablar"]==2,d)
    # ---------- paliers et preuves selon la difficulté ----------
    r=ev("""()=>{FRESH_();const k='hola';const P=[];REC(k,'es2fr',1);P.push(S.sr[k].p);REC(k,'cloze',1);P.push(S.sr[k].p);REC(k,'type',1);P.push(S.sr[k].p);REC(k,'type',1);P.push(S.sr[k].p);return P}""")
    ck("notion courante : reconnaît (1) → comprend (2) → 1re production seule insuffisante → 2e : produit seul (4)",r==[1,2,2,4],r)
    r=ev("()=>{FRESH_();const cog=ALL.concat(LP).find(w=>mkDif(w[0])===1)[0];REC(cog,'type',1);return S.sr[cog].p}")
    ck("notion transparente : une production seule réussie suffit (palier 4)",r==4,r)
    r=ev("""()=>{FRESH_();const k='q:'+EQ.find(x=>x.l===1).k;REC(k,'excT',1);const a=S.sr[k].p;REC(k,'excT',1);const b=S.sr[k].p;SHIFT(k,1);REC(k,'excT',1);const c=S.sr[k].p;SHIFT(k,1);REC(k,'excT',1);return [a,b,c,S.sr[k].p]}""")
    ck("notion difficile : paliers 3–4 exigent des preuves sur 2 jours différents (même jour : bloquée à 2, jour suivant : 4)",r[:2]==[1,2] and r[2]==4,r)
    r=ev("()=>{FRESH_();const k='hola';for(let i=0;i<6;i++)REC(k,'tf',1);return S.sr[k].p}")
    ck("réussir 6 fois un vrai/faux ne prouve pas la production (palier 1)",r==1,r)
    # ---------- oublis ----------
    r=ev("""()=>{FRESH_();const k='hola';REC(k,'type',1);REC(k,'type',1);const a=S.sr[k].p;REC(k,'es2fr',0);const b=S.sr[k].p;REC(k,'tf',0);REC(k,'tf',0);REC(k,'tf',0);return [a,b,S.sr[k].p,S.sr[k].k]}""")
    ck("oubli : un seul palier en moins par erreur, jamais sous 1 (pas de remise à zéro)",r[0]==4 and r[1]==3 and r[2]==1 and r[3]==4,r)
    r=ev("""()=>{FRESH_();const k='hola';REC(k,'es2fr',1);REC(k,'cloze',1);const a=S.sr[k].p;REC(k,'type',0);return [a,S.sr[k].p]}""")
    ck("erreur sur un exercice plus exigeant que le palier : pas de recul",r==[2,2],r)
    r=ev("""()=>{FRESH_();const k='hola';REC(k,'es2fr',1);REC(k,'type',0.5);REC(k,'type',0.5);return S.sr[k].p}""")
    ck("« presque » en production seule compte comme production avec appui (palier 3, pas 4)",r==3,r)
    # ---------- ancrage ----------
    r=ev("""()=>{FRESH_();const k='hola';REC(k,'type',1);REC(k,'type',1);SHIFT(k,4);const e0=S.sr[k];e0.d=dayN();REC(k,'type',1);const a=S.sr[k].p;SHIFT(k,10);S.sr[k].d=dayN();REC(k,'es2fr',1);const b=S.sr[k].p;SHIFT(k,10);S.sr[k].d=dayN();REC(k,'type',1);const c=S.sr[k].p;REC(k,'type',0);return [a,b,c,S.sr[k].p]}""")
    ck("ancrage (5) : production réussie après ≥ 10 jours (notion courante), pas après 4 jours ni par un QCM ; oubli → 4",r==[4,4,5,4],r)
    # ---------- répétition espacée : même échelle de boîtes, délais modulés ----------
    r=ev("""()=>{const out=[];for(let run=0;run<300;run++){FRESH_();const k='hola';let ok=true;
        for(let i=0;i<14;i++){const g=Math.random()<.7,ty=['es2fr','type','cloze','tf'][i%4],e0=S.sr[k],nw=!e0,b0=e0?e0.b:0,due=nw||e0.d<=dayN();
          /* règle historique : +1 boîte si réussite et révision due (ou 1re fois), retour à 0 sur erreur, sinon inchangée */
          const exp=g?(due?Math.min(5,b0+1):b0):0;REC(k,ty,g?1:0);const e=S.sr[k];if(e.b!==exp||e.m<.6||e.m>1.5)ok=false;
          SHIFT(k,Math.floor(Math.random()*20))}out.push(ok)}return out.every(x=>x)}""")
    ck("300 séquences aléatoires : la boîte (b) suit exactement l'ancienne règle, facilité bornée 0,6–1,5",r)
    r=ev("""()=>{FRESH_();const k='hola',q='q:'+EQ.find(x=>x.l===1).k;REC(k,'type',1);REC(q,'excT',1);return [S.sr[k].d-dayN(),S.sr[q].d-dayN()]}""")
    ck("délai après 1re réussite : 1 jour minimum pour toute notion",r[0]>=1 and r[1]>=1,r)
    r=ev("""()=>{FRESH_();const a='hola',c=ALL.concat(LP).find(w=>mkDif(w[0])===1)[0],q='q:'+EQ.find(x=>x.l===1).k;
        for(const k of [a,c,q]){for(let i=0;i<4;i++){if(i){SHIFT(k,60);S.sr[k].d=dayN()}REC(k,k===q?'excT':'type',1)}}return [a,c,q].map(k=>S.sr[k].d-dayN())}""")
    ck("délais plus longs pour une notion transparente, plus courts pour une notion difficile",r[1]>=r[0]>=r[2] and r[1]>r[2],r)
    r=ev("""()=>{FRESH_();const k='hola';REC(k,'type',1);REC(k,'type',1);SHIFT(k,30);S.sr[k].d=dayN();const m0=S.sr[k].m;REC(k,'tf',1);const m1=S.sr[k].m;SHIFT(k,30);S.sr[k].d=dayN();REC(k,'type',1);return [m0,m1,S.sr[k].m]}""")
    ck("réussir un exercice trop facile pour son palier n'augmente pas la facilité ; une production seule, si",r[1]==r[0] and r[2]>r[1],r)
    # ---------- migration prudente ----------
    r=ev("""()=>{FRESH_();S.sc={hola:5,gracias:1,adiós:0,'buenos días':4};S.mi={'buenos días':{n:1,t:3}};
        S.sr={hola:{b:4,d:dayN()+3},gracias:{b:1,d:dayN()},adiós:{b:0,d:dayN()},'buenos días':{b:3,d:dayN()+1}};const before=JSON.stringify(S.sr),bsc=JSON.stringify(S.sc);
        const g={h:mkGet('hola'),g:mkGet('gracias'),a:mkGet('adiós'),bd:mkGet('buenos días'),cl:mkGet('claro')};
        return {g,unchanged:JSON.stringify(S.sr)===before&&JSON.stringify(S.sc)===bsc}}""")
    g=r["g"]
    ck("migration : lecture sans aucune écriture (anciennes données intactes)",r["unchanged"])
    ck("migration : bon score ancien → au plus « comprend en contexte » (2), jamais production",g["h"]["p"]==2 and g["bd"]["p"]==2 and g["g"]["p"]==1 and g["a"]["p"]==0 and g["h"]["g"]==1,g)
    ck("migration : boîte et date conservées, facilité réduite par les erreurs passées",g["h"]["b"]==4 and g["bd"]["b"]==3 and g["bd"]["m"]<1 and g["h"]["m"]==1 and g["cl"] is None,g)
    r=ev("""()=>{const e=mkRec('hola',{ty:'type'},1);return {p:e.p,b:e.b,g:e.g,sc:S.sc.hola}}""")
    ck("migration : 1re nouvelle réponse → données complétées, estimation marquée levée, rien perdu",r["p"]==2 and r["b"]==4 and r.get("g") is None and r["sc"]==5,r)
    # ---------- révision ciblée, tous types, 5 langues × A1–C1 ----------
    res={}
    for l in ["es","va","ca","gl","eu"]:
        for L in [1,2,3,4,5]:
            o=ev("""([l,L])=>{S.lang=l;S.lvl=L;PLC=null;build();XDIRTY=1;xens();FRESH_();const pl=pathPlan();const st=Object.values(pl.map).find(s=>s.kn&&s.ws&&s.ws.length)||Object.values(pl.map)[0];
              const out={};const mk=(t)=>{FRESH_();let k=null;
                if(t==='w'){const w=ALL.concat(LP).find(w=>(w[2]||1)<=L&&!(st.ws||[]).some(x=>x[0]===w[0]));k=w&&w[0]}
                if(t==='e'){const x=XP.find(x=>x.l<=L);k=x&&'e:'+x.e}
                if(t==='q'){const x=EQ.find(x=>x.l<=L);k=x&&'q:'+x.k}
                if(t==='v'){const v=Object.keys(VD[l]).find(v=>vLvl(l,v)<=L);k=v&&'v:'+v}
                if(!k)return 'absent';S.sr[k]={b:1,d:dayN()-1};
                if(t==='w'){ALL.concat(LP).filter(w=>(w[2]||1)<=L&&w[0]!==k).slice(0,6).forEach(w=>S.sr[w[0]]={b:1,d:dayN()-1})}
                let hit=0,tys=new Set();for(let i=0;i<12;i++){R={mode:'lesson',t:st.t||'Chunk',n:3,ok:0,xp:0,cat:null,pid:st.id,pt:st.pt||null,ws:st.ws||null,dp:st.dp||null,gp:st.gp||null,go:st.go||null,xs:null,qs:null,vs:null,pp:st.pp||null,kn:st.kn||null,tn:Array.isArray(st.tn)?st.tn:null};
                  const q=rvQ();if(q&&q.rvw&&(t==='w'?mkDue().some(x=>x.key===q.key):q.key===k)){hit++;tys.add(q.ty)}}
                return hit>=8?'ok:'+[...tys].join('/'):'raté '+hit};
              for(const t of ['w','e','q','v'])out[t]=mk(t);return out}""",[l,L])
            res[f"{l}{L}"]=o
    bad={k:v for k,v in res.items() if any(not str(x).startswith(('ok','absent')) for x in v.values())}
    ck("révision ciblée : mots, expressions, grammaire et conjugaison reviennent, 5 langues × A1–C1",not bad,bad)
    print("    détail :",{k:{t:v[t].split(':')[0] for t in v} for k,v in list(res.items())[:3]},"…")
    r=ev("""()=>{S.lang='es';S.lvl=2;PLC=null;build();XDIRTY=1;xens();FRESH_();const pl=pathPlan();const st=Object.values(pl.map).find(s=>s.kn&&s.ws&&s.ws.length);const k='q:'+EQ.find(x=>x.l===1).k;
        const T={};for(const p of [1,2,4]){S.sr[k]={b:2,d:dayN()-1,p,m:1,c:[1,2,p>=3?2:0,p>=4?2:0],j:[0,0,0,0],n:3,k:0};const ts=new Set();
          for(let i=0;i<15;i++){R={mode:'lesson',t:'',n:3,ok:0,xp:0,pid:st.id,ws:st.ws,dp:st.dp,kn:st.kn,pt:st.pt,tn:null};const q=rvQ();if(q&&q.key===k)ts.add(q.ty)}T[p]=[...ts]}return T}""")
    ck("révision ciblée : l'exercice suit le palier (grammaire : vrai/faux → choix → réponse écrite)",r["1"]==["excV"] and r["2"]==["exc"] and set(r["4"])<= {"excT","exc"} and "excT" in r["4"],r)
    r=ev("""()=>{FRESH_();const pl=pathPlan();const st=Object.values(pl.map).find(s=>s.kn&&s.ws&&s.ws.length);S.sr['hola']={b:1,d:dayN()-1};
        const P=[];for(const n of [0,1,2,3,4,5,6,7,8,9]){R={mode:'lesson',t:'',n,ok:0,xp:0,pid:st.id,ws:st.ws,dp:st.dp,kn:st.kn,pt:st.pt,tn:null};P.push(!!rvQ())}
        R={mode:'lesson',t:'',n:3,pid:null};const nop=!rvQ();R={mode:'lesson',t:'',n:3,ok:0,pid:st.id,ws:[['hola','x',1]].concat(st.ws),dp:st.dp,kn:st.kn,tn:null};const cur=!rvQ();return {P,nop,cur}}""")
    ck("charge normale : révision en 4e et 8e question des étapes du parcours, jamais sur une notion de l'étape",r["P"]==[False,False,False,True,False,False,False,True,False,False] and r["nop"] and r["cur"],r)
    # ---------- vraies réponses dans une leçon ----------
    r=ev("""()=>{S.lang='es';S.lvl=2;PLC=null;build();XDIRTY=1;xens();FRESH_();home();start('Mélange');const out={};
        for(const ty of ['exM','exE','exc','conj','fr2es','es2fr']){if(typeof R.tn==='number')R.tn=null;let q=null;for(let i=0;i<10&&!q;i++)q=mkQ(ty,0);if(!q||!q.key){out[ty]='pas de question';continue}R.q=q;show();
          if(q.o){ans(q.o.indexOf(q.g))}else fin(true,q.g||q.es||'',q.key);const e=S.sr[q.key];out[ty]=e?[q.key.slice(0,2),e.p,e.b,mkDif(q.key),MKA[ty]]:'non enregistré';adv()}return out}""")
    exp=lambda d,a:max(P for P in range(0,a+1) if all([0,[0,1,1,1,1],[0,1,1,2,2],[0,1,2,2,2]][d][x]<=1 for x in range(1,P+1)))
    ck("vraies réponses : chaque type de notion entre dans le carnet (e:, q:, v:, mots) avec le palier prévu par sa difficulté",all(isinstance(v,list) and v[1]==exp(v[3],v[4]) for v in r.values()) and r["exM"][0]=="e:" and r["exc"][0]=="q:" and r["conj"][0]=="v:",r)
    # ---------- taille ----------
    sz=ev("""()=>{FRESH_();const ks=ALL.concat(LP).slice(0,1500).map(w=>w[0]).concat(XP.slice(0,300).map(x=>'e:'+x.e),EQ.slice(0,200).map(x=>'q:'+x.k));ks.forEach((k,i)=>{mkRec(k,{ty:['type','es2fr','exc'][i%3]},1);if(i%2)mkRec(k,{ty:'type'},0)});return JSON.stringify(S.sr).length}""")
    ck(f"taille : 2 000 notions suivies = {sz//1024} Ko (localStorage ~5 Mo)",sz<400*1024,sz)
    # ---------- sauvegarde, rechargement, langues (contexte neuf, vrai profil) ----------
    PRO=json.dumps({"v":2,"xp":40,"streak":0,"last":"","sc":{"hola":2},"lvl":2,"lang":"es","PL":{},"bd":{},"nt":[],"t":1793000000000,"ob":1,"masSeen":1,"sr":{"hola":{"b":3,"d":1}}})
    b2=c;c=b.new_context(service_workers="block");pg=c.new_page();pg.on("pageerror",lambda e:errs.append(str(e)));ev=pg.evaluate
    pg.goto(BASE+"index.html");pg.wait_for_timeout(1500)
    ev("(P)=>{localStorage.clear();localStorage.setItem('cast_user','moi1');localStorage.setItem('acct:moi1',JSON.stringify({h:'z'}));localStorage.setItem('cast:moi1',P)}",PRO)
    pg.reload();pg.wait_for_timeout(2500);ev(H)
    r0=ev("()=>({u:typeof U!=='undefined'&&U,hola:S.sr&&S.sr.hola,g:mkGet('hola')})")
    ck("ancien profil chargé : entrée historique intacte, palier estimé à la lecture",r0["hola"]=={"b":3,"d":1} and r0["g"]["p"]==2 and r0["g"]["g"]==1,r0)
    ev("()=>{mkRec('e:Buenos días',{ty:'exE'},1);mkRec('hola',{ty:'type'},1);return save()}");pg.wait_for_timeout(800)
    ev("()=>setLang('ca')");pg.wait_for_timeout(500);ev("()=>{mkRec('bon dia',{ty:'es2fr'},1);return save()}");pg.wait_for_timeout(800)
    pg.reload();pg.wait_for_timeout(2500)
    r=ev("()=>({lang:S.lang,ca:(S.sr['bon dia']||{}).p,es:((S.PL||{}).es||{}).sr})")
    es=r["es"] or {}
    ck("sauvegarde et rechargement : carnet conservé et séparé par langue (es : mot + expression ; ca : mot)",r["lang"]=="ca" and r["ca"]==1 and es.get("hola",{}).get("p")==2 and es.get("hola",{}).get("b")==4 and es.get("e:Buenos días",{}).get("p")==2,r)
    ev("()=>setLang('es')");pg.wait_for_timeout(300)
    ck("retour à la langue précédente : carnet retrouvé",ev("(S.sr.hola||{}).p")==2 and ev("(S.sr['e:Buenos días']||{}).p")==2)
    ck("aucune erreur JavaScript",not errs,errs[:3])
    b.close()
print(sum(R),"/",len(R),"OK");sys.exit(0 if all(R) else 1)
