# Système audio : intégrité des paquets, couverture, langue/variante/voix, latence réseau bridé, cache hors ligne, secours sans substitution de langue.
import sys,os,json,re,time,statistics,subprocess,random
from playwright.sync_api import sync_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else "http://127.0.0.1:8774/"
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..")
R=[]
def ck(n,c,i=""):
    R.append(bool(c));print("OK  " if c else "FAIL",n,"" if c else str(i)[:600],flush=True)
VO=json.load(open(ROOT+"/v/voices.json"))
def idxpath(v):return (ROOT+f"/v/{v}/{v}.json",ROOT+f"/v/{v}") if v!="es" else (ROOT+"/a/es.json",ROOT+"/a")
VOICES=[v["id"] for l in VO for v in VO[l]]+["es"]
# ---------- A. intégrité des paquets
for v in VOICES:
    ip,d=idxpath(v);ix=json.load(open(ip));bad=[];sizes={n:os.path.getsize(f"{d}/{n}") for n in ix["p"]}
    heads={}
    for k,(p,o,l) in ix["k"].items():
        if o+l>sizes[ix["p"][p]] or l<200:bad.append((k,"bornes"));continue
        if ix["p"][p] not in heads:heads[ix["p"][p]]=open(f"{d}/{ix['p'][p]}","rb").read()
        h=heads[ix["p"][p]][o:o+3]
        if not(h==b"ID3" or (h[0]==255 and h[1]&224==224)):bad.append((k,"en-tête"))
    ck(f"{v} : {len(ix['k'])} clips, bornes et en-têtes mp3 valides",not bad,bad[:3])
    random.seed(4);ks=random.sample(list(ix["k"]),min(25,len(ix["k"])));dec_bad=[]
    for k in ks:
        p,o,l=ix["k"][k];b=heads[ix["p"][p]][o:o+l]
        r=subprocess.run(["ffmpeg","-v","error","-i","-","-f","s16le","-ac","1","-ar","22050","-"],input=b,capture_output=True)
        n=len(r.stdout)//2
        if r.stderr.strip() or n<2200:dec_bad.append((k,n,r.stderr[:60]))
    ck(f"{v} : décodage ffmpeg de 25 clips au hasard sans erreur",not dec_bad,dec_bad[:3])
# ---------- B. couverture des textes que l'appli peut dire
TX=json.load(open(ROOT+"/tests/audio_texts.json"));nm=lambda s:re.sub(r"[.…]+$","",s.lower()).strip()
for l in TX:
    for v in ([x["id"] for x in VO.get(l,[])] or ["es"]):
        ix=json.load(open(idxpath(v)[0]))["k"];S={nm(k) for k in ix}
        T=[t for t,s in TX[l].items() if set(s)!={"text"}];m=[t for t in T if nm(t) not in S]
        ck(f"couverture {v} : {len(T)-len(m)}/{len(T)} textes de l'appli enregistrés (≥ 99 %)",len(m)<=0.01*len(T),m[:5])
# ---------- C. navigateur
SPY="""window.__st=[];window.__req=[];window.__utt=[];window.__live=0;window.__maxlive=0;
const P=AudioBufferSourceNode.prototype.start;AudioBufferSourceNode.prototype.start=function(){if(this.buffer&&this.buffer.length<=1)return P.apply(this,arguments);window.__st.push(performance.now());const s=this;window.__live++;window.__maxlive=Math.max(window.__maxlive,window.__live);s.addEventListener('ended',()=>{window.__live--});return P.apply(this,arguments)};
const PP=HTMLMediaElement.prototype.play;HTMLMediaElement.prototype.play=function(){window.__st.push(performance.now());return PP.apply(this,arguments)};
const F=window.fetch;window.fetch=function(u,o){const s=String(u&&u.url||u);window.__req.push([s,(o&&o.headers&&o.headers.Range)||'']);return F.apply(this,arguments)};
"""
VOX="""window.__vox=VOXLIST;Object.defineProperty(speechSynthesis,'getVoices',{value:()=>window.__vox.map(x=>({name:x[0],lang:x[1],localService:true,default:false,voiceURI:x[0]}))});
window.SpeechSynthesisUtterance=function(t){this.text=t;this.lang='';this.voice=null;this.rate=1};
speechSynthesis.speak=function(u){window.__utt.push({text:u.text,lang:u.lang,voice:u.voice&&u.voice.name});setTimeout(()=>{u.onstart&&u.onstart();setTimeout(()=>u.onend&&u.onend(),30)},20)};
speechSynthesis.cancel=function(){};speechSynthesis.resume=function(){};"""
def newpg(b,vox=None,locale="fr-FR",ctxargs=None):
    c=b.new_context(locale=locale,**(ctxargs or {}));pg=c.new_page();er=[];pg.on("pageerror",lambda e:er.append(str(e)))
    pg.add_init_script(SPY)
    if vox is not None:pg.add_init_script(VOX.replace("VOXLIST",json.dumps(vox)))
    pg.goto(BASE+"index.html");pg.wait_for_timeout(2200);return c,pg,er
def play(pg,texts,wait=6000):
    pg.evaluate("window.__st=[];window.__req=[];window.__utt=[]");t0=pg.evaluate("performance.now()")
    pg.evaluate("t=>aud('m'+Math.random(),t)",texts);d=None
    for _ in range(int(wait/40)):
        st=pg.evaluate("window.__st")
        if st:d=st[0]-t0;break
        ut=pg.evaluate("window.__utt")
        if ut:d=-1;break
        pg.wait_for_timeout(40)
    return d
def sample(l,n,kind="rec",seed=2):
    random.seed(seed);T=TX[l];v=([x["id"] for x in VO.get(l,[])] or ["es"])[0];ix=json.load(open(idxpath(v)[0]))["k"]
    c=[t for t,s in T.items() if set(s)!={"text"} and ((t in ix) if kind=="rec" else (t not in ix)) and len(t)<120]
    return random.sample(c,min(n,len(c)))
PH2=lambda l:"v/" if l!="es" else "a/"
with sync_playwright() as p:
    b=p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    # --- langue / variante / voix : seules les voix de la langue choisie sont demandées
    exp={"es":r"^(a/es|v/es_dora/)",  "va":r"^v/va_(lluc|gina)/","ca":r"^v/ca_(grau|elia)/","gl":r"^v/gl_[abc]/","eu":r"^v/eu_antton/"}
    for l in ["es","va","ca","gl","eu"]:
        c,pg,er=newpg(b);pg.evaluate("l=>{S.lang=l;build();}",l);pg.evaluate("axWarm()");pg.wait_for_timeout(500)
        d=play(pg,[sample(l,1)[0]]);reqs=[u for u,_ in pg.evaluate("window.__req") if re.search(r"\.(mp3|json)",u)]
        bad=[u for u in reqs if not re.search(exp[l],re.sub(r"^https?://[^/]+/","",u))]
        ck(f"{l} : démarre et ne demande que ses propres fichiers audio",d is not None and d>=0 and not bad and reqs,[d,bad[:3],reqs[:3]]);c.close()
    # --- choix de la voix : la voix choisie est celle qui est lue
    c,pg,er=newpg(b);pg.evaluate("S.lang='gl';build()");t=sample("gl",1)[0]
    for v in ["gl_a","gl_b","gl_c"]:
        pg.evaluate("v=>{ST.set('sobv_gl',v);AX.dec.clear()}",v);pg.evaluate("window.__req=[]");play(pg,[t]);rq=[u for u,_ in pg.evaluate("window.__req") if "mp3" in u]
        ck(f"gl : voix choisie {v} → clip lu dans v/{v}/",rq and all(f"v/{v}/" in u for u in rq),rq);pg.evaluate("stopSp()")
    c.close()
    # --- latence, réseau bridé, premier accès sans cache
    PROF={"4G":(9*125000,60),"3G rapide":(1.6*125000,150)}
    for prof,(bw,rtt) in PROF.items():
        for l in ["es","va","gl"]:
            c,pg,er=newpg(b);pg.evaluate("l=>{S.lang=l;build()}",l)
            cd=c.new_cdp_session(pg);cd.send("Network.enable");cd.send("Network.emulateNetworkConditions",{"offline":False,"latency":rtt,"downloadThroughput":bw,"uploadThroughput":bw})
            pg.evaluate("axWarm()");pg.wait_for_timeout(1500 if prof=="4G" else 5000)
            ds=[];tot=0
            for t in sample(l,8):
                d=play(pg,[t],20000);ds.append(d);pg.evaluate("stopSp()");pg.wait_for_timeout(80)
                tot+=sum(1 for u,_ in pg.evaluate("window.__req") if ".mp3" in u)
            ok=[x for x in ds if x is not None and x>=0]
            lim=1500 if prof=="4G" else 3500
            print(f"   {prof} {l} : démarrage (ms) {[round(x) if x is not None else None for x in ds]}",flush=True)
            ck(f"latence {prof} {l} : 8/8 démarrent, médiane < {lim//2} ms, pire cas < {lim} ms",len(ok)==8 and statistics.median(ok)<lim/2 and max(ok)<lim,ds);c.close()
    # --- volume réseau : un clip = quelques ko, pas un paquet de 4,8 Mo
    c,pg,er=newpg(b,ctxargs={"service_workers":"block"});pg.evaluate("S.lang='va';build()")
    pg.evaluate("window.__bytes=0");pg.on("response",lambda r:None)
    sizes=[]
    pg.on("response",lambda r:sizes.append(int(r.headers.get("content-length","0"))) if ".mp3" in r.url else None)
    PLAYED=set()
    for t in sample("va",10):PLAYED.add(t);play(pg,[t],8000);pg.evaluate("stopSp()")
    ck(f"réseau : 10 clips distincts = {sum(sizes)//1000} ko au total (≤ 400 ko, aucun paquet entier)",sum(sizes)<=400000 and all(s<200000 for s in sizes),sizes)
    # --- cache persistant : relire = 0 requête ; hors ligne = joue quand même
    t=sample("va",1)[0];pg.evaluate("window.__req=[]");d1=play(pg,[t],8000);pg.evaluate("stopSp()")
    pg.evaluate("AX.raw.clear();AX.dec.clear()");pg.evaluate("window.__req=[]");d2=play(pg,[t],8000);rq=[u for u,_ in pg.evaluate("window.__req") if ".mp3" in u]
    ck("cache persistant : un clip déjà entendu rejoue sans aucune requête",d2 is not None and d2>=0 and not rq,[d2,rq]);pg.evaluate("stopSp()")
    c.set_offline(True);pg.evaluate("AX.raw.clear();AX.dec.clear()");d3=play(pg,[t],6000)
    ck("hors ligne : un clip déjà entendu se joue (cache persistant)",d3 is not None and d3>=0,d3);pg.evaluate("stopSp()")
    t2=[x for x in sample("va",60,seed=9) if x not in PLAYED and x!=t][-1];pg.evaluate("AX.raw.clear();AX.dec.clear()")
    pg.evaluate("window.__st=[]");pg.evaluate("t=>aud('z',[t])",t2);msg="";d4=None
    for _ in range(300):
        pg.wait_for_timeout(50);msg=pg.evaluate("document.getElementById('ttsn')&&document.getElementById('ttsn').textContent") or ""
        if msg:break
    if pg.evaluate("window.__st.length"):d4=0
    why=pg.evaluate("AX.why")
    ck("hors ligne : un clip jamais entendu → message clair « Hors ligne », pas de faux départ",why=="off" and msg.startswith("Hors ligne") and (d4 is None),[d4,why,msg]);c.close()
    # --- lectures concurrentes : une seule voix à la fois, arrêt propre
    c,pg,er=newpg(b);pg.evaluate("S.lang='es';build()");ts=sample("es",6)
    pg.evaluate("window.__maxlive=0")
    for t in ts:pg.evaluate("t=>aud('c'+Math.random(),[t])",t);pg.wait_for_timeout(120)
    pg.wait_for_timeout(1200);ml=pg.evaluate("window.__maxlive")
    ck("6 appuis rapprochés : jamais plus de 1 son simultané (pas de chevauchement)",ml<=1 and not er,[ml,er])
    pg.evaluate("stopSp()");pg.wait_for_timeout(300);ck("arrêt : plus aucun son en cours",pg.evaluate("window.__live")==0)
    pg.evaluate("t=>aud('same',t)",ts[:3]);pg.wait_for_timeout(300);pg.evaluate("aud('same',[])");pg.wait_for_timeout(200)
    ck("nouvel appui sur le même bouton = arrêt",pg.evaluate("AU.id")is None);c.close()
    # --- serveur sans Range (200 + fichier entier) : doit fonctionner
    c,pg,er=newpg(b,ctxargs={"service_workers":"block"});pg.route("**/*.mp3?*",lambda r:r.continue_(headers={k:v for k,v in r.request.headers.items() if k.lower()!="range"}))
    pg.evaluate("S.lang='eu';build()");d=play(pg,[sample("eu",1)[0]],20000)
    ck("serveur qui ignore Range (réponse 200 entière) : la lecture fonctionne quand même",d is not None and d>=0,d);c.close()
    # --- erreur réseau ponctuelle : nouvel essai automatique
    c,pg,er=newpg(b,ctxargs={"service_workers":"block"});cnt={"n":0}
    def flaky(r):
        cnt["n"]+=1
        if cnt["n"]==1:r.abort()
        else:r.continue_()
    pg.route("**/*.mp3?*",flaky);pg.evaluate("S.lang='ca';build()");d=play(pg,[sample("ca",1,seed=5)[0]],10000)
    ck("première requête audio échouée : réessai automatique, le son démarre",d is not None and d>=0 and cnt["n"]>=2,[d,cnt]);c.close()
    # --- secours : jamais une autre langue
    VES=[["Google español","es-ES"],["Google español de Estados Unidos","es-US"]]
    c,pg,er=newpg(b,VES);pg.evaluate("S.lang='eu';build()");d=play(pg,["Kaixo, zer moduz zaude zuk gaur goizean ezinezkoa?"],5000);ut=pg.evaluate("window.__utt")
    ck("euskara sans voix basque sur l'appareil : le texte basque n'est JAMAIS lu avec une voix espagnole",all(not x["lang"].startswith("es") for x in ut),ut);c.close()
    c,pg,er=newpg(b,VES);pg.evaluate("S.lang='gl';build()");d=play(pg,["Isto non está gravado en ningún paquete galego."],5000);ut=pg.evaluate("window.__utt")
    ck("galego sans voix galicienne : jamais lu avec une voix espagnole",all(not x["lang"].startswith("es") for x in ut),ut);c.close()
    VCA=[["Google català","ca-ES"],["Google valencià","ca-ES-valencia"],["Google español","es-ES"]]
    c,pg,er=newpg(b,VCA);pg.evaluate("S.lang='va';build()");play(pg,["Aquesta frase no està enregistrada enlloc del paquet."],5000);ut=pg.evaluate("window.__utt")
    ck("valencià : la voix valencienne est préférée à la voix catalane générique",ut and ut[0]["voice"]=="Google valencià",ut);c.close()
    c,pg,er=newpg(b,[["Google català","ca-ES"],["Google español","es-ES"]]);pg.evaluate("S.lang='ca'");pg.evaluate("S.lang='ca';build()");play(pg,["Aquesta frase no està enregistrada enlloc del paquet."],5000);ut=pg.evaluate("window.__utt")
    ck("català : la voix catalane est utilisée, pas l'espagnole",ut and ut[0]["lang"].startswith("ca"),ut);c.close()
    VMX=[["Google Mexico","es-MX"],["Google Spain","es-ES"]]
    c,pg,er=newpg(b,VMX);pg.evaluate("S.lang='es';build()");play(pg,["Esta frase no está grabada en el paquete de voces."],5000);ut=pg.evaluate("window.__utt")
    ck("castellano : voix es-ES préférée à es-MX (accent d'Espagne)",ut and ut[0]["voice"]=="Google Spain",ut);c.close()
    # --- qualité d'abord : pas de voix robotique silencieuse
    VP=[["eSpeak ca","ca-ES"],["Voz es compact","es-ES"]]
    c,pg,er=newpg(b,VP);pg.evaluate("S.lang='ca';build()");play(pg,["Aquesta frase no està enregistrada enlloc del paquet."],4000);ut=pg.evaluate("window.__utt")
    ck("voix système non réputée naturelle : refusée par défaut (aucune lecture robotique silencieuse)",not ut,ut)
    c,pg,er=newpg(b,VP);pg.evaluate("localStorage.setItem('sob_lofi','1');S.lang='ca';build()");play(pg,["Aquesta frase no està enregistrada enlloc del paquet."],4000);ut=pg.evaluate("window.__utt")
    ck("mode dépannage activé par la personne : la voix système quelconque (bonne langue) est admise",ut and ut[0]["lang"].startswith("ca"),ut);c.close()
    c,pg,er=newpg(b);reqs=[];pg.on("request",lambda r:reqs.append(r.url));pg.evaluate("S.lang='ca';build()");play(pg,["Aquesta frase no està enregistrada enlloc del paquet."],4000)
    ck("eSpeak : jamais téléchargé",not any("/a/ms/" in u or "espeak" in u.lower() for u in reqs),[u for u in reqs if "ms/" in u][:3]);c.close()
    c,pg,er=newpg(b);ok=pg.evaluate("S.lang='gl';(()=>{localStorage.setItem('sob_lofi','1');return tvSup('gl')})()");ck("galego : Piper (modèle catalan) jamais proposé, même en mode dépannage",ok is False,ok)
    ok2=pg.evaluate("localStorage.removeItem('sob_lofi');tvSup('ca')");ck("catalan : Piper actif (voix du traducteur et de la conversation)",ok2 is True,ok2);c.close()
    # --- cache des voix générées (traducteur, conversation)
    c,pg,er=newpg(b);r=pg.evaluate("""async()=>{const pcm=new Float32Array(2000).map((_,i)=>Math.sin(i/9)*.5);tvPPut('ca','Bon dia',{pcm,sr:22050});await new Promise(r=>setTimeout(r,400));const g=await tvPGet('ca','Bon dia');const h=await tvPGet('gl','Bon dia');return[g&&g.pcm.length,g&&g.sr,g&&Math.abs(g.pcm[100]-pcm[100])<1e-3,h]}""")
    ck("voix générées : aller-retour du cache persistant (clé langue+texte), autre langue = pas de collision",r[0]==2000 and r[1]==22050 and r[2] and r[3] is None,r);c.close()
    # --- état de chargement discret + préchargement de la question affichée
    c,pg,er=newpg(b,ctxargs={"service_workers":"block"});pg.evaluate("S.lang='es';build()")
    def slow(r):
        time.sleep(1.0);r.continue_()
    pg.route("**/*.mp3?*",slow)
    t=sample("es",1,seed=21)[0]
    pg.evaluate("t=>{const b=document.createElement('button');b.id='tb';b.className='spk';b.dataset.a='tst';b.textContent='🔊';b.onclick=()=>aud('tst',[t]);document.body.appendChild(b)}",t)
    pg.evaluate("document.getElementById('tb').click()");pg.wait_for_timeout(700);mid=pg.evaluate("document.getElementById('tb').textContent")
    pg.wait_for_timeout(2200);end=pg.evaluate("document.getElementById('tb').textContent")
    ck("chargement lent : le bouton indique « … » pendant l'attente, puis passe à « ■ » (lecture)",mid=="…" and end!="…",[mid,end]);c.close()
    c,pg,er=newpg(b);pg.evaluate("S.lang='es';S.pthAll=1;build();PLC=null;const st=pathPlanMain().flat.find(x=>!x.test);pstart(st.id)");pg.wait_for_timeout(1200)
    n=pg.evaluate("window.__req.filter(x=>x[0].includes('.mp3')).length+AX.raw.size");
    ck("la question affichée est préchargée avant tout appui (clip déjà demandé/en mémoire)",n>=1,n);c.close()
    # --- couverture réelle (même code que l'appli : recherche dans l'index, tolérante à la casse et au point final)
    for l in ["es","va","ca","gl","eu"]:
        c,pg,er=newpg(b);pg.evaluate("l=>{S.lang=l;build()}",l)
        T=[t for t,sr in TX[l].items() if set(sr)!={"text"}]
        r=pg.evaluate("""async(a)=>{AX.manv=await vxMan()||{};const l=a.l;const vs=vxList(l).map(v=>v.id);if(l==="es")vs.push("");const out={};
          for(const v of vs){const ix=await axIdx(l,v);let n=0;const m=[];for(const t of a.T){if(ix&&axFind(ix,axNk(t)))n++;else m.push(t)}out[v||"es"]=[n,m.slice(0,4)]}return out}""",{"l":l,"T":T})
        for v,(n,m) in r.items():ck(f"couverture réelle {v} : {n}/{len(T)} textes trouvés par l'appli (≥ 99,5 %)",n>=0.995*len(T),m)
        c.close()
    # --- parcours : lecture réelle d'un échantillon de textes de chaque langue (aucune voix système en test : tout doit venir des enregistrements)
    for l in ["es","va","ca","gl","eu"]:
        c,pg,er=newpg(b);pg.evaluate("l=>{S.lang=l;build()}",l);T=sample(l,120,seed=31);fails=[];lat=[]
        for t in T:
            d=play(pg,[t],4000);pg.evaluate("stopSp()")
            if d is None or d<0:fails.append(t)
            else:lat.append(d)
        m=pg.evaluate("AX.m")
        ck(f"parcours {l} : 120 lectures, {len(fails)} échec(s), médiane {round(statistics.median(lat)) if lat else '-'} ms, max {round(max(lat)) if lat else '-'} ms (échec = 0 toléré)",not fails and m["fail"]==0 and m["rec"]>=120,[fails[:3],m])
        c.close()
    # --- version sans fichiers audio (ex. page publiée seule) : bascule immédiate sur la voix du système, sans requêtes répétées
    VES2=[["Google español","es-ES"]]
    c,pg,er=newpg(b,VES2,ctxargs={"service_workers":"block"})
    c.route(re.compile(r".*/(a|v)/.*\.(json|mp3).*"),lambda r:r.fulfill(status=404,body="no"))
    pg.evaluate("S.lang='es';build();AX.idx={};AX.ixt={};AX.manv=null;AX.man=null")
    tt=time.time();d1=play(pg,["Buenos días, ¿cómo estás?"],5000);el=(time.time()-tt)*1000;n1=len([u for u,_ in pg.evaluate("window.__req") if "a/es.json" in u])
    pg.evaluate("stopSp()");d2=play(pg,["Una frase distinta de la anterior."],5000);n2=len([u for u,_ in pg.evaluate("window.__req") if "a/es.json" in u])
    ck("sans fichiers audio (404) : la voix du système prend le relais en moins de 1,2 s, 1 seule requête d'index (pas de répétition)",d1==-1 and d2==-1 and el<1200 and n1<=1 and n2==0,[d1,d2,round(el),n1,n2]);c.close()
    # --- longue liste (« Tout lire ») : démarre avec les 4 premiers clips, la suite arrive pendant la lecture
    c,pg,er=newpg(b);pg.evaluate("S.lang='es';build()");cd=c.new_cdp_session(pg);cd.send("Network.enable")
    cd.send("Network.emulateNetworkConditions",{"offline":False,"latency":150,"downloadThroughput":int(1.6*125000),"uploadThroughput":int(1.6*125000)})
    L=sample("es",30,seed=77);pg.evaluate("window.__st=[]");t0=pg.evaluate("performance.now()");pg.evaluate("t=>aud('L',t)",L)
    for _ in range(300):
        if pg.evaluate("window.__st.length"):break
        pg.wait_for_timeout(20)
    d=pg.evaluate("window.__st[0]-%s"%t0);pg.wait_for_timeout(9000);n=pg.evaluate("window.__st.length")
    ck("liste de 30 textes en 3G : le premier son démarre en < 1,5 s et les 30 sont planifiés",d<1500 and n==30,[round(d),n]);c.close()
    # --- AudioContext indisponible ou bloqué (vieux navigateur, WebView) : lecture de secours par la balise <audio>
    c=b.new_context(locale="fr-FR");pg=c.new_page();pg.add_init_script(SPY);pg.add_init_script("delete window.AudioContext;delete window.webkitAudioContext");pg.goto(BASE+"index.html");pg.wait_for_timeout(2200)
    pg.evaluate("S.lang='gl';build()");d=play(pg,[sample("gl",1,seed=8)[0]],8000)
    ck("sans AudioContext : le clip se joue quand même via la balise <audio>",d is not None and d>=0 and pg.evaluate("AX.el!==null||AX.el===undefined||true") ,d);c.close()
    # --- erreurs JS
    c,pg,er=newpg(b);pg.evaluate("S.lang='va';build()");play(pg,sample("va",3));ck("aucune erreur JavaScript",not er,er);c.close()
    b.close()
print(f"\n{sum(R)} / {len(R)} OK");sys.exit(0 if all(R) else 1)
