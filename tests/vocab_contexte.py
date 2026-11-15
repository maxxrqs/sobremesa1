# Développement pédagogique — chantiers 1 et 2 : vocabulaire en contexte.
# Chaque mot (A1 à C1) a une phrase d'exemple dans les cinq langues (mot ciblé entre crochets), traduite dans les langues d'interface ;
# la phrase sert à la découverte, aux listes et à deux exercices : compréhension (ctxC) et production écrite (ctxP), répétition espacée comprise.
# Usage : python3 tests/rangesrv.py 8772 .  puis  python3 tests/vocab_contexte.py [URL] [page]   (défauts : http://localhost:8772/ index.html)
import sys,re,json,collections
from playwright.sync_api import sync_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else "http://localhost:8772/"
PAGE=sys.argv[2] if len(sys.argv)>2 else "index.html"
R=[]
def ck(n,c,info=""):
    R.append(bool(c));print(("OK  " if c else "FAIL")+" ["+PAGE+"] "+n+("" if c else "  "+str(info)[:700]),flush=True)
LANGS=["es","va","ca","gl","eu"]
# ---- 1. données (lecture du fichier)
src=open(PAGE,encoding="utf-8").read()
blk=lambda n:[l for l in re.search(r"const "+n+r"=`\n(.*?)`",src,re.S).group(1).strip().split("\n") if l.strip()]
RW,RR,RX=blk("RW"),blk("RR"),blk("RX")
CAP={1:7,2:10,3:14}
mots={}  # clé (glose fr) -> [niveau minimal, [mots par langue de chaque ligne]]
for l in RW:
    c=l.split("|");m=mots.setdefault(c[2],[9,[]]);m[0]=min(m[0],int(c[1]));m[1].append(c[3:8])
for l in RR:
    c=l.split("|");m=mots.setdefault(c[3],[9,[]]);m[0]=min(m[0],int(c[2]));m[1].append(c[4:9])
ex={l.split("|")[0]:l.split("|") for l in RX}
parN=collections.Counter(v[0] for v in mots.values())
for niv in range(1,6):
    sel={k:v for k,v in mots.items() if v[0]==niv};manq=[k for k in sel if k not in ex];mauv=[];longs=[]
    for k,(n,rows) in sel.items():
        if k not in ex:continue
        for i,lg in enumerate(LANGS):
            s=ex[k][1+i]
            if any(r[i].strip() for r in rows) and not re.fullmatch(r"[^\[\]]*\[[^\[\]]+\][^\[\]]*",s):mauv.append((k,lg,s))
            if s and len(s.replace("[","").replace("]","").split())>CAP.get(niv,99):longs.append((k,lg,s))
    nom=["","A1","A2","B1","B2","C1"][niv]
    ck(f"données {nom} : les {len(sel)} mots ont une phrase d'exemple ; un seul mot ciblé entre crochets dans chaque langue où il existe"+(f" ; {CAP[niv]} mots max." if niv in CAP else ""),
       not manq and not mauv and not longs,{"sans":manq[:8],"crochets":mauv[:8],"longues":longs[:4]})
ck("données : aucune clé en double ni phrase orpheline (toute clé RX correspond à un mot)",len(ex)==len(RX) and all(k in mots for k in ex),[k for k in ex if k not in mots][:6])
trd={l:json.load(open(f"tr/{l}.json",encoding="utf-8")) for l in ["en","it","de","pt"]}
nt=[(l,r.split("|")[6]) for r in RX for l in trd if not trd[l].get(r.split("|")[6])]
ck(f"traductions : les {len(RX)} phrases françaises d'exemple sont traduites en anglais, italien, allemand et portugais (+ 2 consignes)",
   not nt and all(trd[l].get("Complète la phrase") and trd[l].get("Dans cette phrase, que veut dire le mot en gras ?") for l in trd),nt[:8])
P=lambda xp:json.dumps({"v":2,"xp":xp,"streak":0,"last":"","sc":{},"lvl":1,"lang":"es","PL":{},"bd":{},"nt":[],"t":1793000000000,"ob":1,"masSeen":1})
SEED="(P)=>{localStorage.clear();localStorage.setItem('acct:moi1','{\"h\":\"z\"}');localStorage.setItem('cast:moi1',P);localStorage.setItem('cast_user','moi1')}"
with sync_playwright() as p:
    b=p.chromium.launch();ctx=b.new_context(locale="fr-FR");pg=ctx.new_page();err=[];pg.on("pageerror",lambda e:err.append(str(e)[:200]))
    pg.goto(BASE+PAGE);pg.wait_for_timeout(700);pg.evaluate(SEED,P(40));pg.reload();pg.wait_for_timeout(2500)
    # ---- 2. couverture dans l'appli, par langue
    cov=pg.evaluate("""(L)=>{const o={};for(const l of L){S.lang=l;S.lvl=1;build();xens();const m=ctxMap(),ws=[...ALL,...LP].filter(w=>w[0]);
      const sans=[...new Set(ws.filter(w=>!m.get(w[0])).map(w=>w[0]))];o[l]={n:new Set(ws.map(w=>w[0])).size,sans}}S.lang='es';build();return o}""",LANGS)
    ck("chaque mot A1–C1 affiché dans l'appli (leçons et listes) a sa phrase, dans les cinq langues",all(not v["sans"] for v in cov.values()),{l:(v["n"],v["sans"][:5]) for l,v in cov.items()})
    # ---- 3. génération des exercices (5 langues × 5 niveaux ; longueur bornée par niveau)
    gen=pg.evaluate("""(L)=>{const o={};for(const l of L)for(let v=1;v<=5;v++){S.lang=l;S.lvl=v;build();xens();R={mode:"free",t:"Mélange",n:0,ok:0,xp:0};const bad=[];let nc=0,np=0,hv=0;
      for(let i=0;i<40;i++){const c=NX.ctxC.mk(0),q=NX.ctxP.mk(0);
        if(c){nc++;if((c.w[2]||1)===v)hv++;const okc=c.o.length===4&&new Set(c.o).size===4&&c.o.includes(c.g)&&c.p[1]&&c.es.includes(c.p[1])&&c.g===c.w[1]&&nwd([c.es])<=CTXW[v];if(!okc)bad.push(["C",c.es,c.o])}
        if(q){np++;const okp=q.es&&q.say.includes(q.p[1])&&q.xf&&q.hint===q.w[1]&&!/^-|…|\\.\\.\\./.test(q.w[0])&&q.p[0]+q.p[1]+q.p[2]===q.say&&nwd([q.say])<=CTXW[v];if(!okp)bad.push(["P",q.say,q.es])}}
      o[l+v]={nc,np,hv,bad:bad.slice(0,3)}}S.lang='es';S.lvl=1;build();return o}""",LANGS)
    ck("exercices de contexte générés dans les 5 langues à chaque niveau A1→C1 : 4 sens distincts dont le bon, mot à écrire = forme réelle, longueur adaptée au niveau",
       all(v["nc"]==40 and v["np"]==40 and not v["bad"] for v in gen.values()),{k:v for k,v in gen.items() if v["nc"]<40 or v["np"]<40 or v["bad"]})
    ck("exercices de contexte : aux niveaux A2→C1, les mots du niveau courant sont bien proposés",all(gen[l+str(v)]["hv"]>0 for l in LANGS for v in range(2,6)),{k:v["hv"] for k,v in gen.items()})
    # ---- 4. compréhension (ctxC) : affichage et réponse
    pg.evaluate("()=>{start('Mélange');R.q=NX.ctxC.mk(0);R.done=false;draw()}");pg.wait_for_timeout(200)
    vu=pg.evaluate("()=>({h:document.querySelector('.q h2').innerText,b:(document.querySelector('.q .txt b.w')||{}).innerText,n:document.querySelectorAll('.q .opt').length,p1:R.q.p[1],key:R.q.key,sc:S.sc[R.q.key]||0})")
    i=pg.evaluate("()=>R.q.o.indexOf(R.q.g)");pg.locator(".q .opt").nth(i).click();pg.wait_for_timeout(300)
    ap=pg.evaluate("(k)=>({sc:S.sc[k]||0,sr:!!(S.sr||{})[k],fb:(document.querySelector('.fbm')||{}).className||''})",vu["key"])
    ck("compréhension : phrase affichée, mot ciblé en gras, 4 propositions ; bonne réponse → mot crédité et planifié en répétition espacée",
       "mot en gras" in vu["h"] and vu["b"]==vu["p1"] and vu["n"]==4 and ap["sc"]==vu["sc"]+1 and ap["sr"] and "ok" in ap["fb"],{"vu":vu,"ap":ap})
    # ---- 5. production (ctxP) : trou dans la phrase, traduction et sens donnés, réponse tapée
    def prod(rep):
        pg.evaluate("()=>{start('Mélange');let q=null;for(let i=0;i<20&&!q;i++){q=NX.ctxP.mk(0)}R.q=q;R.done=false;draw()}");pg.wait_for_timeout(200)
        v=pg.evaluate("()=>({h:document.querySelector('.q h2').innerText,t:document.querySelector('.q .txt').innerText,sub:(document.querySelector('.q p.sub')||{}).innerText,es:R.q.es,key:R.q.key,sc:S.sc[R.q.key]||0,say:R.q.say,ti:!!document.getElementById('ti')})")
        pg.fill("#ti",rep(v["es"]));pg.click("#chk");pg.wait_for_timeout(300)
        a=pg.evaluate("(k)=>({sc:S.sc[k]||0,fb:(document.querySelector('.fbm')||{}).className||''})",v["key"]);return v,a
    v,a=prod(lambda g:g)
    ck("production : phrase avec un trou (mot caché), traduction et sens affichés, saisie ; bonne réponse → mot crédité",
       "Complète la phrase" in v["h"] and "_____" in v["t"] and v["t"].strip()!=v["say"].strip() and bool(v["sub"]),{"v":v})
    ck("production : réponse juste reconnue (retour positif, score du mot +1)",a["sc"]==v["sc"]+1 and "ok" in a["fb"] and v["ti"],{"v":v,"a":a})
    v,a=prod(lambda g:"zzzz")
    ck("production : réponse fausse → retour négatif, mot remis en révision (score du mot baissé ou nul)",a["sc"]<=max(0,v["sc"]-1) and "ko" in a["fb"],{"v":v,"a":a})
    v,a=prod(lambda g:g.upper())
    ck("production : majuscules sans importance (évaluation tolérante existante)", "ok" in a["fb"],{"v":v,"a":a})
    # ---- 6. découverte d'une étape de vocabulaire : la phrase propre au mot
    d=pg.evaluate("""()=>{S.lang='es';S.lvl=1;S.ds={};S.sc={};build();xens();const st=pathPlanMain().flat.find(s=>s.nw&&s.ws&&s.ws.length);const it=discItems(st);
      return it.map(x=>({es:x.es,ex:x.ex&&x.ex[0],c:(ctxMap().get(x.es)||{}).s||null}))}""")
    okd=[x for x in d if x["c"]];bons=[x for x in okd if x["ex"]==x["c"].replace("[","").replace("]","")]
    ck(f"découverte : chaque mot nouveau est présenté avec SA phrase d'exemple ({len(bons)}/{len(okd)})",okd and len(bons)==len(okd),d[:4])
    # ---- 7. listes : exemple sous chaque mot, à chaque niveau
    for lv in range(1,6):
        pg.evaluate("(v)=>{S.lang='es';build();xens();lists();LS.l=v;lrender()}",lv);pg.wait_for_timeout(300)
        li=pg.evaluate("()=>{const r=[...document.querySelectorAll('#lr tr')];return{n:r.length,ex:r.filter(x=>x.querySelector('small.sub span[translate=no]')).length,s:(r[0]&&r[0].innerText)||''}}")
        ck(f"listes {['','A1','A2','B1','B2','C1'][lv]} : chaque mot affiche sa phrase d'exemple et sa traduction ({li['ex']}/{li['n']})",li["n"]>20 and li["ex"]==li["n"],li)
    # ---- 8. répétition espacée : en Révision, les exercices de contexte portent sur les mots dus
    rv=pg.evaluate("""()=>{S.lang='es';S.lvl=1;build();xens();const ws=ALL.filter(w=>(w[2]||1)===1&&ctxMap().get(w[0])).slice(0,6);S.sr={};ws.forEach(w=>{S.sr[w[0]]={b:1,d:dayN()-1}});
      R={mode:"lesson",t:"Révision",n:0,ok:0,xp:0};const due=new Set(srDue().map(w=>w[0])),k=[];for(let i=0;i<30;i++){const q=NX.ctxP.mk(0)||NX.ctxC.mk(0);if(q)k.push(q.key)}
      return{due:due.size,hors:k.filter(x=>!due.has(x)).length,n:k.length}}""")
    ck("répétition espacée : en Révision, les phrases de contexte reprennent les mots arrivés à échéance",rv["n"]==30 and rv["due"]==6 and rv["hors"]==0,rv)
    # ---- 9. intégration au parcours : les étapes de vocabulaire A1 proposent les deux exercices de contexte
    pt=pg.evaluate("""()=>{const o={};for(const [l,v] of [['es',1],['eu',1],['es',3],['gl',5]]){S.lang=l;S.lvl=v;S.pth={};S.rq={};build();xens();PLC=null;const T={};
      for(const st of pathPlanMain().flat.filter(s=>s.nw&&s.ws)){R={mode:'lesson',t:st.t||'Chunk',n:0,ok:0,xp:0,cat:null,pid:st.id,pt:st.pt||null,ws:st.ws||null,dp:st.dp||null,kn:st.kn||null};
        for(let i=0;i<10;i++){R.n=i;try{const q=mkQ(pickType(),0);T[q.ty]=(T[q.ty]||0)+1}catch(e){T.err=(T.err||0)+1}}}o[l+v]=T}S.lang='es';S.lvl=1;build();return o}""")
    ck("parcours A1 (castillan, basque), B1 (castillan), C1 (galicien) : les étapes de vocabulaire proposent compréhension ET production en contexte, sans erreur",
       all(v.get("ctxC",0)>0 and v.get("ctxP",0)>0 and not v.get("err") for v in pt.values()),{l:(v.get("ctxC"),v.get("ctxP"),v.get("err")) for l,v in pt.items()})
    ck("aucune erreur JS",not err,err[:5])
    b.close()
print(f"\n{sum(R)}/{len(R)} contrôles OK");sys.exit(0 if all(R) else 1)
