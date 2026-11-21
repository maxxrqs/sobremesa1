# Chantier 3, lot C : mises en situation A1–A2 (moteur d'immersion imStart/immP réactivé, étapes « T » adaptatives).
# Contrôles : données (5–7 échanges, 3 réponses fausses, mots-clés), notions toutes introduites au niveau, notions repérées à chaque étape,
# place dans le parcours (espacée, facultative, jamais bloquante), ouverture selon la progression réellement effectuée, format choisi
# selon le carnet, alternative écrite sans micro, effets sur le carnet (appuis seulement : ni entrée, ni date, palier ≤ 2, une preuve par
# notion), fin d'étape du parcours, écrans 360 × 640 dans les 5 interfaces, scènes A1 et conversation IA inchangées, couverture audio.
# Usage : python3 tests/situations.py [URL]   (serveur : python3 tests/rangesrv.py 8774 .)
import sys,json,subprocess,hashlib,re
from playwright.sync_api import sync_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else "http://127.0.0.1:8774/"
R=[];WARN=[]
def ck(n,c,i=""):R.append(bool(c));print("OK  " if c else "FAIL",n,"" if c else str(i)[:900],flush=True)
LANGS=["es","va","ca","gl","eu"];UIS=["fr","en","de","it","pt"]
H=r"""
window.SET_=(l,L)=>{S.lang=l;S.lvl=L;S.ob=0;build();XDIRTY=1;xens();XPWC=null;PLC=null};
window.ENT_=(k,p)=>{const d=mkDif(k),c=[1,2,3,4].map(P=>P<=p?MKN[d][P]:0);S.sr[k]={b:1,d:dayN()+5,p,m:1,c,n:3,k:0,s:dayN()-2};if(d===3)S.sr[k].j=[0,0,0,0];return S.sr[k]};
window.PREP_=s=>{const L=lg();s.st.forEach(st=>{if(!st.ks){st.ks=sitNo(L,st.m||st.g);st.kn=sitNo(L,st.n)}})};
/* termine toutes les étapes de nouveautés jusqu'au rang r (inclus) du niveau courant */
window.PROG_=r=>{S.pth={};S.pa={};const pl=pathPlanMain();pl.flat.forEach(x=>{if(x.rk!=null&&x.rk<=r&&!x.opt)S.pth[pthK(x.id)]=8})};
"""
def chk_data():
    out=subprocess.run([sys.executable,"tools/sit_build.py","--check"]).returncode
    ck("castellano.html à jour avec tools/sit_data.py",out==0)
with sync_playwright() as p:
    b=p.chromium.launch();c=b.new_context(viewport={"width":360,"height":640},locale="fr-FR");pg=c.new_page();ERR=[];pg.on("pageerror",lambda e:ERR.append(str(e)))
    pg.goto(BASE+"castellano.html");pg.wait_for_timeout(2500);pg.evaluate(H)
    chk_data()
    # 1. données et notions
    for l in LANGS:
        d=pg.evaluate("""l=>{SET_(l,2);const ss=immP(l),bad=[];let n=0;
          ss.forEach(s=>{if(!(s.l===1||s.l===2))bad.push(s.id+' niveau');if(s.st.length<5||s.st.length>7)bad.push(s.id+' échanges '+s.st.length);PREP_(s);
            s.st.forEach((st,i)=>{n++;if(st.k!=='T')bad.push(s.id+' type '+st.k);if(st.o.length!==3||st.o.includes(st.m)||new Set(st.o).size!==3)bad.push(s.id+i+' fausses');
              if(!st.i)bad.push(s.id+i+' consigne');const w=EV.raw(st.m).split(' ');st.kw.forEach(k=>{if(!w.includes(EV.raw(k)))bad.push(s.id+i+' mot-clé '+k)});
              if(!st.ks.length)bad.push(s.id+i+' aucune notion repérée');
              sitTx({st:[st]}).forEach(([t,fr])=>{const q=pqRank(t,fr,1);if(q.r===Infinity||q.bad.length)bad.push(s.id+i+' inconnu « '+t+' » '+q.bad.join(','));else if(q.r>pqEnd(s.l))bad.push(s.id+i+' hors niveau « '+t+' » '+q.r)})});
            if(!s.v.length)bad.push(s.id+' à retenir vide')});
          return {n:ss.length,a1:ss.filter(s=>s.l===1).length,a2:ss.filter(s=>s.l===2).length,st:n,bad}}""",l)
        ck(f"{l} : {d['n']} situations (A1 {d['a1']}, A2 {d['a2']}, {d['st']} échanges), notions introduites au niveau et repérées",d["n"]>0 and not d["bad"],d["bad"][:8])
    # 2. place dans le parcours
    for l in LANGS:
        for L in (1,2):
            d=pg.evaluate("""([l,L])=>{SET_(l,L);const pl=pathPlanMain(),bad=[],us=pl.units,idx=[];
              pl.flat.filter(x=>x.sit).forEach(x=>{const u=us.findIndex(u=>u.steps.includes(x)),s=immP(l).find(z=>z.id===x.sit);idx.push(u);if(u<1)bad.push(x.id+' unité '+u);
                const st=us[u].steps,ur=Math.max(...st.filter(y=>!y.opt).map(y=>y.rk||0));if(sitRk(s)>ur)bad.push(x.id+' placée avant ses notions');
                const k=st.indexOf(x);if(k===st.length-1)bad.push(x.id+' en fin d unité');if(!x.opt)bad.push(x.id+' obligatoire');if(st.filter(y=>y.sit).length>3)bad.push('plus de 3 situations unité '+u)});
              idx.sort((a,b)=>a-b);const nv=idx.filter((u,i)=>i&&u-idx[i-1]<2).length;
              const nS=immP(l).filter(s=>s.l===L).length;
              /* facultative : tout le reste validé → niveau terminé, étape suivante non verrouillée */
              S.pth={};pl.flat.forEach(x=>{if(!x.test&&!x.opt)S.pth[pthK(x.id)]=8});const md=mainDone(),lv=lvSteps();
              S.pth={};const it=pathItems(),si=it.findIndex(x=>x.opt);let nl=true;if(si>=0){for(let i=0;i<it.length;i++){if(i<si)S.pth[pthK(it[i].id)]=8}const it2=pathItems();nl=!it2[si+1]||!it2[si+1].lock}
              return {n:idx.length,nS,units:us.length,idx,bad,md,lv,nl,nv}}""",[l,L])
            ck(f"{l} A{L} : {d['n']}/{d['nS']} situations placées dans leur niveau (unités {d['idx']} sur {d['units']}, ≤ 3 par unité, {d['nv']} voisines), facultatives",not d["bad"] and d["md"] and d["lv"] and d["nl"] and d["n"]==d["nS"],d)
    # 3. ouverture selon la progression réellement effectuée + carte « Situations »
    for l in LANGS:
        d=pg.evaluate("""l=>{SET_(l,1);S.sr={};S.sc={};S.ds={};S.pth={};S.pa={};const ss=immP(l).filter(s=>s.l===1),K=adKnown();const r0=sitR0(),o0=ss.filter(s=>sitOK(s,r0,K)).length;
          const mx=Math.max(...ss.map(s=>sitRk(s)));PROG_(mx);const r1=sitR0(),o1=ss.filter(s=>sitOK(s,r1,adKnown())).length;
          S.mode='im';home();const h=document.body.innerHTML;return {o0,o1,n:ss.length,r0,r1,card:h.includes('imStart('),cv:h.includes('sceneGo(')}}""",l)
        ck(f"{l} : situations fermées au départ ({d['o0']}/{d['n']}), ouvertes après les étapes nécessaires ({d['o1']}/{d['n']}), carte avec scènes et conversation",d["o0"]==0 and d["o1"]==d["n"] and d["card"] and d["cv"],d)
    # 4. format selon le carnet, alternative écrite, évaluation
    for l in LANGS:
        d=pg.evaluate("""l=>{SET_(l,2);S.sr={};const s=immP(l)[0];PREP_(s);const st=s.st[0],out={};
          [0,2,4].forEach(p=>{st.ks.forEach(k=>ENT_(k,p));out[p]=sitMode(st)});
          /* sans micro : saisie écrite */
          st.ks.forEach(k=>ENT_(k,4));imStart(s.id);if(SR){IM.typed=true;imDraw()}out.noMic=!!document.getElementById('ti')&&IM.cur.k==='O';
          document.getElementById('ti').value=st.va[0]||st.m;imW();out.var=IM.g;IM.i=0;imShow();if(SR){IM.typed=true;imDraw()}document.getElementById('ti').value=st.o[0];imW();out.wrong=IM.g;
          /* palier 2 : écrit avec petite faute de frappe acceptée, réponse fausse refusée */
          st.ks.forEach(k=>ENT_(k,2));IM.i=0;imShow();out.w=IM.cur.k;const m=st.m,lw=m.split(' ').reduce((a,b)=>b.length>a.length?b:a,'');document.getElementById('ti').value=m.replace(lw,lw.slice(0,2)+lw.slice(3));imW();out.typo=IM.g;
          IM.i=0;imShow();document.getElementById('ti').value=st.o[1];imW();out.wrong2=IM.g;
          /* palier 0 : choix ; texte jamais masqué si la réplique n'est pas enregistrée */
          st.ks.forEach(k=>ENT_(k,0));st.kn.forEach(k=>ENT_(k,4));IM.rec=new Set();IM.i=0;imShow();out.r=IM.cur.k;out.hidden=IM.cur.a;IM.rec=new Set([st.n]);imShow();out.hidRec=IM.cur.a;imQuit();return out}""",l)
        ck(f"{l} : format selon le palier (0 → choix, 2 → écrit, 4 → oral), écrit sans micro, variantes et fautes de frappe acceptées, fausses refusées, écoute seule si enregistrée",
           d["0"]=="R" and d["2"]=="W" and d["4"]=="O" and d["noMic"] and d["var"] and not d["wrong"] and d["w"]=="W" and d["typo"] and not d["wrong2"] and d["r"]=="R" and not d["hidden"] and d["hidRec"],d)
    # 4b. navigateur sans reconnaissance vocale : l'oral passe à l'écrit
    c2=b.new_context(viewport={"width":360,"height":640},locale="fr-FR");c2.add_init_script("delete window.SpeechRecognition;delete window.webkitSpeechRecognition;");p2=c2.new_page()
    p2.goto(BASE+"castellano.html");p2.wait_for_timeout(2500);p2.evaluate(H)
    d=p2.evaluate("""()=>{SET_('eu',2);S.sr={};const s=immP('eu')[1];PREP_(s);s.st.forEach(st=>st.ks.forEach(k=>ENT_(k,4)));imStart(s.id);const t=document.body.innerText;return {sr:!!SR,k:IM.cur.k,ti:!!document.getElementById('ti'),mic:t.includes('Parler')}}""")
    ck("sans micro ni reconnaissance vocale : réponse écrite proposée à la place de l'oral",not d["sr"] and d["k"]=="O" and d["ti"] and not d["mic"],d);c2.close()
    # 5. carnet : appuis sans accélération
    for l in LANGS:
        d=pg.evaluate("""l=>{SET_(l,2);S.sr={};const s=immP(l).find(x=>x.l===2)||immP(l)[0];PREP_(s);const ks=[...new Set(s.st.flatMap(st=>st.ks))];
          ks.forEach((k,i)=>ENT_(k,i%5));const half=ks.filter((k,i)=>i%7===3);half.forEach(k=>delete S.sr[k]);const b0=JSON.parse(JSON.stringify(S.sr)),n0=Object.keys(S.sr).length;
          imStart(s.id);for(let i=0;i<s.st.length;i++){const st=IM.cur;if(st.k==='R')imR(IM.opts.indexOf(st.g));else{IM.typed=true;imDraw();document.getElementById('ti').value=st.m;imW()}IM.i++;imShow()}
          const bad=[];Object.keys(S.sr).forEach(k=>{const a=b0[k],e=S.sr[k];if(!a){bad.push('créée '+k);return}if(e.d!==a.d||e.b!==a.b||e.s!==a.s)bad.push('date/boîte '+k);
            if((e.p||0)>Math.max(a.p||0,2))bad.push('palier > 2 '+k);const dc=e.c.reduce((x,y)=>x+y,0)-a.c.reduce((x,y)=>x+y,0);if(dc>1)bad.push('plusieurs preuves '+k);if((e.p||0)<(a.p||0))bad.push('recul '+k)});
          const moved=Object.keys(S.sr).filter(k=>JSON.stringify(S.sr[k])!==JSON.stringify(b0[k])).length;
          /* échecs : aucun changement */
          const b1=JSON.stringify(S.sr);imStart(s.id);for(let i=0;i<s.st.length;i++){imSkip();IM.i++;imShow()}const same=JSON.stringify(S.sr)===b1;
          return {bad,moved,n0,same,keys:ks.length}}""",l)
        ck(f"{l} : carnet — {d['moved']} notions d'appui renforcées sur {d['keys']}, aucune entrée créée, ni date, palier ≤ 2, une preuve max ; échecs sans effet",not d["bad"] and d["same"] and d["moved"]>0,d)
    # 6. étape du parcours : note enregistrée, « Continuer le parcours » ne la repropose pas
    d=pg.evaluate("""()=>{SET_('es',1);S.sr={};const pl=pathPlanMain(),x=pl.flat.find(y=>y.sit);const s=immP('es').find(z=>z.id===x.sit);
      S.pth={};pl.flat.forEach(y=>{if(!y.opt&&pl.flat.indexOf(y)<pl.flat.indexOf(x))S.pth[pthK(y.id)]=8});const it=pathItems().find(y=>!y.done&&!y.lock);const first=it&&it.id;
      pstart(x.id);const ok=!!IM&&IM.pid===x.id;for(let i=0;i<s.st.length;i++){imSkip();IM.i++;imShow()}
      const pa=S.pa[pthK(x.id)],it2=pathItems().find(y=>!y.done&&!y.lock&&!(y.opt&&y.last!=null));return {first,sit:x.id,ok,pa,next:it2&&it2.id,end:document.body.innerHTML.includes('pathCont()')}}""")
    ck("parcours : la situation est proposée à son tour, lancée depuis l'étape, notée, puis non reproposée après une tentative",d["first"]==d["sit"] and d["ok"] and d["pa"]==0 and d["next"]!=d["sit"] and d["end"],d)
    # 7. écrans 360 × 640 dans les 5 interfaces : rien à faire défiler, pas de français hors interface française
    FR=re.compile(r"\b(Choisis|Écoute|Continuer|Vérifier|Passer|Quitter|Demande|Salue|Remercie|Dis que|Tu fais|Tu arrives|Accepte|Propose|Réponds|Commande|Paie|Présente-toi|Souhaite|Vendeuse|Guichetier|Rejouer|À retenir|Notions travaillées|Mises en situation)\b")
    for ui in UIS:
        bad=[]
        for l in LANGS:
            pg2=c.new_page();pg2.on("pageerror",lambda e:ERR.append(str(e)));pg2.goto(BASE+"castellano.html");pg2.wait_for_timeout(2500);pg2.evaluate(H)
            r=pg2.evaluate("""async ([ui,l])=>{UI=ui;await trLoad(ui);SET_(l,2);S.sr={};const out=[];
              for(const s of immP(l)){PREP_(s);for(const p of [0,2,4]){s.st.forEach(st=>st.ks.forEach(k=>ENT_(k,p)));imStart(s.id);
                for(let i=0;i<s.st.length;i++){await new Promise(r=>setTimeout(r,5));const h=document.documentElement.scrollHeight,w=document.documentElement.scrollWidth;out.push([s.id,p,i,h,w,document.body.innerText]);
                  const st=IM.cur;if(st.k==='R')imR(IM.opts.indexOf(st.g));else{IM.typed=true;imDraw();document.getElementById('ti').value=st.m;imW()}
                  out.push([s.id,p,i+'f',document.documentElement.scrollHeight,document.documentElement.scrollWidth,document.body.innerText]);IM.i++;imShow()}}}
              S.mode='im';home();out.push(['carte',0,0,0,document.documentElement.scrollWidth,document.body.innerText]);UI='fr';return out}""",[ui,l]);pg2.close()
            for sid,pp,i,h,w,txt in r:
                if h>640 and sid!="carte":bad.append(f"{l}/{sid}/p{pp}/{i} hauteur {h}")
                if w>360:bad.append(f"{l}/{sid}/{i} largeur {w}")
                if ui!="fr":
                    m=FR.search(txt)
                    if m:bad.append(f"{l}/{sid}/{i} français : {m.group(0)}")
        ck(f"interface {ui} : écrans de situation sans défilement à 360 × 640 et entièrement traduits",not bad,bad[:6])
    pg.evaluate("()=>{UI='fr'}")
    # 7b. langue d'interface : rang, place, ouverture et accès identiques dans les 5 interfaces ; situations validées à leur place d'origine
    J5="""async ()=>{await trLoad(UI);const o={};for(const l of ["es","va","ca","gl","eu"]){for(const k in SITLAY)delete SITLAY[k];immP(l).forEach(s=>delete s.rk);
      for(const L of [1,2]){SET_(l,L);const pl=pathPlanMain(),us=pl.units,ss=immP(l).filter(s=>s.l===L),sig=[];
        o[l+L+'place']=pl.flat.filter(x=>x.sit).map(x=>x.sit+'@'+us.findIndex(u=>u.steps.includes(x))).sort().join(' ');
        for(const u of us){const st=u.steps.filter(x=>!x.opt&&!x.test&&x.rk!=null);if(st.length)sig.push(ss.filter(s=>sitOK(s,Math.max(...st.map(x=>x.rk)),new Set())).length)}
        let acc=0;for(const x of pl.flat.filter(y=>y.sit)){S.pth={};pl.flat.forEach(y=>{if(!y.opt&&!y.test&&y.rk!=null&&y.rk<=x.rk)S.pth[pthK(y.id)]=8});const it=pathItems().find(y=>y.id===x.id);if(it&&!it.lock){IM=null;pstart(x.id);if(IM&&IM.pid===x.id)acc++}}
        S.pth={};IM=null;o[l+L+'ouv']=sig.join(',');o[l+L+'acc']=acc}
      o[l+'rk']=immP(l).map(s=>s.id+':'+sitRk(s)).join(' ')}
      return [UI,o]}"""
    R5={}
    for loc in ["fr-FR","en-US","it-IT","de-DE","pt-PT"]:
        c5=b.new_context(viewport={"width":360,"height":640},locale=loc);p5=c5.new_page();p5.on("pageerror",lambda e:ERR.append(str(e)));p5.goto(BASE+"castellano.html");p5.wait_for_timeout(2500);p5.evaluate(H)
        ui,o=p5.evaluate(J5);R5[ui]=o;c5.close()
    ref=R5.get("fr",{})
    ck("interfaces "+"/".join(R5)+" : rang, place, ouverture et accès des 120 situations identiques à l'interface française",len(R5)==5 and all(o==ref for o in R5.values()),{u:[k for k in o if o[k]!=ref.get(k)][:6] for u,o in R5.items() if o!=ref})
    tot=sum(len(ref.get(l+str(L)+"place","").split()) for l in LANGS for L in (1,2));acc=sum(ref.get(l+str(L)+"acc",0) for l in LANGS for L in (1,2))
    lv=[x for l in LANGS for L in (1,2) for x in ref.get(l+str(L)+"place","").split() if x.split("@")[0][1]!=str(L)]
    ck(f"120 situations placées dans leur niveau et réellement lançables depuis le parcours ({tot} placées, {acc} lancées)",tot==120 and acc==120 and not lv,lv[:6])
    CAS={"es":["a1panaderia","a1mesa","a1piso","a1medico","a1compra","a1perdido","a2quedar"],"va":["a1piso","a1tienda","a1compra","a2ropa"],"ca":["a1tienda","a1piso","a1compra"],"gl":["a1tienda"]}
    badc=[f"{l}/{sid}" for l,ids in CAS.items() for sid in ids if not any(x.startswith(sid+"@") for x in ref.get(l+sid[1]+"place","").split())]
    ck("cas signalés au bilan (es « le », « genial » ; va « emporte », « sis-cents » ; ca « moment », « cinquanta » ; gl « momento ») placés dans leur niveau dans les 5 interfaces",not badc,badc)
    ORIG={"es":(22,23),"va":(21,23),"ca":(22,23),"gl":(21,22),"eu":(18,14)}
    bo=[f"{l} {sid} u{u}≠u{exp}" for l,(u1,u2) in ORIG.items() for sid,exp in (("a1mercado",u1),("a2tren",u2)) for x in ref.get(l+sid[1]+"place","").split() if x.startswith(sid+"@") for u in [int(x.split("@")[1])] if u!=exp]
    ck("situations validées avant le lot C à leur emplacement d'origine (a1mercado es u22, va u21, ca u22, gl u21, eu u18 ; a2tren inchangé)",not bo,bo)
    # 8. non-régression : scènes A1 guidées, conversation IA intacte
    d=pg.evaluate("""()=>{SET_('es',1);scnStart(0);const a=typeof SC!=='undefined'&&!!SC;S.mode='im';home();return {a,cv:typeof cvPrompt==='function'&&CVS.length===10}}""")
    ck("scènes A1 guidées toujours lancées, conversation IA présente",d["a"] and d["cv"],d)
    ck("aucune erreur JavaScript",not ERR,ERR[:3])
    # 9. couverture audio des répliques et des mots « À retenir », voix par voix ; une voix suspendue (audio/modeles.lock.json) est listée à part
    VO=json.load(open("v/voices.json"));nm=lambda s:re.sub(r"[.…]+$","",s.lower()).strip();res={};susp={}
    try:LK=json.load(open("audio/modeles.lock.json"))["voix"]
    except Exception:LK={}
    for l in LANGS:
        tx=pg.evaluate("l=>{const o=[];immP(l).forEach(s=>{s.st.forEach(st=>o.push(st.n));s.v.forEach(v=>o.push(v[0]))});return [...new Set(o)]}",l)
        for v in [x["id"] for x in VO[l]]:
            k={nm(x) for x in json.load(open(f"v/{v}/{v}.json"))["k"]};m=[t for t in tx if nm(t) not in k]
            (susp if LK.get(v,{}).get("statut","").startswith("suspendu") else res)[v]=(len(tx)-len(m),len(tx),m)
    ck("audio : répliques et mots « À retenir » enregistrés dans chaque voix "+json.dumps({v:f"{a}/{n}" for v,(a,n,_) in res.items()},ensure_ascii=False),all(not m for _,_,m in res.values()),{v:m for v,(_,_,m) in res.items() if m})
    for v,(a,n,m) in susp.items():print(f"INFO {v} : {a}/{n} enregistrés — voix suspendue ({LK[v].get('statut')}), {len(m)} textes lus par une autre voix de la langue",flush=True)
    b.close()
print(f"\n{sum(R)}/{len(R)} contrôles réussis")
sys.exit(0 if all(R) else 1)
