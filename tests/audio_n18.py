# N°18 — appuis rapides : jamais deux sons en même temps, mesuré sur l'horloge réelle des sources
# (début planifié → arrêt effectif ou fin naturelle), et non sur l'événement « ended », qui arrive
# quelques millisecondes après l'arrêt et donnait de faux chevauchements dans tests/audio.py.
# Usage : python3 tests/audio_n18.py [URL de base] [tours par page (défaut 60)] [pages séparées par des virgules]
# A. clips enregistrés : 5 langues, 10 voix, délais réseau aléatoires (0 à 600 ms) sur fetch et sur le cache,
#    appuis espacés de 0 à 250 ms, clips non enregistrés (voix système simulée), arrêts et ré-appuis mêlés.
# B. reprise lente du contexte audio (iPhone, Android en arrière-plan) : un son généré (Piper) ne doit pas
#    démarrer après un nouvel appui, ni dans la conversation (tvPlayPcm), ni dans la chaîne de secours d'aud().
import sys,json,random,re
from playwright.sync_api import sync_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else "http://127.0.0.1:8830/"
N=int(sys.argv[2]) if len(sys.argv)>2 else 60
PAGES=(sys.argv[3] if len(sys.argv)>3 else "castellano.html,index.html").split(",")
import os;ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..")
R=[]
def ck(n,c,i=""):
    R.append(bool(c));print("OK  " if c else "FAIL",n,"" if c else str(i)[:600],flush=True)
SPY="""window.__iv=[];window.__dl=[0,0];window.__rnd=Math.random;
(()=>{const T=()=>performance.now();
const P=AudioBufferSourceNode.prototype.start,SP=AudioBufferSourceNode.prototype.stop;
AudioBufferSourceNode.prototype.start=function(w){if(this.buffer&&this.buffer.length<=1)return P.apply(this,arguments);
  const c=this.context,a=T()+Math.max(0,(w||0)-c.currentTime)*1000,r={k:'src',a,b:a+this.buffer.duration*1000};this.__r=r;window.__iv.push(r);return P.apply(this,arguments)};
AudioBufferSourceNode.prototype.stop=function(w){const r=this.__r;if(r){const t=T()+Math.max(0,(w||0)-this.context.currentTime)*1000;if(t<r.b)r.b=t}return SP.apply(this,arguments)};
const PL=HTMLMediaElement.prototype.play,PA=HTMLMediaElement.prototype.pause;
HTMLMediaElement.prototype.play=function(){if(this.loop||this.volume===0)return PL.apply(this,arguments);const r={k:'el',a:T(),b:1e15};this.__r=r;window.__iv.push(r);
  const f=()=>{if(this.__r===r&&r.b>T())r.b=T()};this.addEventListener('ended',f,{once:true});this.addEventListener('error',f,{once:true});
  const p=PL.apply(this,arguments);if(p&&p.catch)p.catch(f);return p};
HTMLMediaElement.prototype.pause=function(){const r=this.__r;if(r&&r.b>T())r.b=T();return PA.apply(this,arguments)};
/* réseau et cache lents : délai aléatoire dans [__dl[0], __dl[1]] ms */
const wait=()=>new Promise(z=>setTimeout(z,window.__dl[0]+window.__rnd()*(window.__dl[1]-window.__dl[0])));
const F=window.fetch;window.fetch=function(u,o){const s=String(u&&u.url||u);if(/\\.mp3/.test(s))return wait().then(()=>F.call(window,u,o));return F.apply(this,arguments)};
if(window.Cache){const M=Cache.prototype.match;Cache.prototype.match=function(q){const s=String(q&&q.url||q);if(/sob\\.local/.test(s))return wait().then(()=>M.apply(this,arguments));return M.apply(this,arguments)}}
/* voix système simulée (clips non enregistrés) : un énoncé dure 400 ms sauf annulation */
window.__ut=[];Object.defineProperty(speechSynthesis,'getVoices',{value:()=>window.__novox?[]:[{name:'Google español',lang:'es-ES',localService:true,default:false,voiceURI:'g-es'},{name:'Google català',lang:'ca-ES',localService:true,default:false,voiceURI:'g-ca'},{name:'Google euskara',lang:'eu-ES',localService:true,default:false,voiceURI:'g-eu'},{name:'Google galego',lang:'gl-ES',localService:true,default:false,voiceURI:'g-gl'}]});
window.SpeechSynthesisUtterance=function(t){this.text=t;this.lang='';this.voice=null;this.rate=1};
let Q=[];speechSynthesis.speak=function(u){Q.push(u);if(Q.length===1)nx()};
function nx(){const u=Q[0];if(!u)return;setTimeout(()=>{if(Q[0]!==u)return;const r={k:'utt',a:T(),b:1e15};u.__r=r;window.__iv.push(r);u.onstart&&u.onstart();
  u.__to=setTimeout(()=>{if(Q[0]!==u)return;r.b=T();Q.shift();u.onend&&u.onend();nx()},400)},15)}
speechSynthesis.cancel=function(){const q=Q;Q=[];q.forEach(u=>{clearTimeout(u.__to);if(u.__r&&u.__r.b>T())u.__r.b=T();u.onerror&&u.onerror({error:'canceled'})})};
speechSynthesis.resume=function(){};
})();"""
def overlap(iv,tol=3.0):
    s=sorted([x for x in iv if x["b"]-x["a"]>tol],key=lambda x:x["a"]);worst=0;pair=None
    for i,x in enumerate(s):
        for y in s[i+1:]:
            if y["a"]>=x["b"]:break
            o=min(x["b"],y["b"])-y["a"]
            if o>worst:worst,pair=o,(x["k"],y["k"])
    return (worst if worst>tol else 0),pair
TX=json.load(open(ROOT+"/tests/audio_texts.json"));VO=json.load(open(ROOT+"/v/voices.json"))
def ixk(v):return json.load(open(ROOT+(f"/v/{v}/{v}.json" if v else "/a/es.json")))["k"]
REC={};UNREC={}
for l in ["es","va","ca","gl","eu"]:
    vs=[x["id"] for x in VO[l]]+([""] if l=="es" else [])
    for v in vs:REC[(l,v)]=[t for t,s in TX[l].items() if set(s)!={"text"} and t in ixk(v) and len(t)<120]
    UNREC[l]=[f"zq{l} essai {i} sin grabar" for i in range(20)]
COMBOS=list(REC)
DELAYS=[(0,0),(0,50),(0,200),(50,600),(0,600)]
GAPS=[0,15,40,120,250]
with sync_playwright() as p:
    b=p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    for page in PAGES:
        rnd=random.Random(18);c=b.new_context(locale="fr-FR",service_workers="block");pg=c.new_page();er=[];pg.on("pageerror",lambda e:er.append(str(e)))
        pg.add_init_script(SPY);pg.goto(BASE+page);pg.wait_for_timeout(2200)
        pg.evaluate("window.__rs=18;window.__rnd=()=>{window.__rs=(window.__rs*16807)%2147483647;return window.__rs/2147483647}")
        st={"tours":0,"chev":0,"sons":0,"pire":0.0,"types":set(),"voix":set()};bad=[]
        for k in range(N):
            l,v=COMBOS[k%len(COMBOS)];dl=DELAYS[(k//len(COMBOS))%len(DELAYS)] if k>=len(COMBOS) else DELAYS[k%len(DELAYS)]
            pg.evaluate("([l,v])=>{stopSp();S.lang=l;if(l==='gl')S.mas=({gl_c:'gecko',gl_a:'toro',gl_b:'lora'})[v]||S.mas;ST.set('sobv_'+l,v||'0');AX.dec.clear();AX.raw.clear();build()}",[l,v])
            pg.wait_for_timeout(250);pg.evaluate("d=>{window.__dl=d;window.__iv=[]}",list(dl))
            seq=[]
            for i in range(6):
                r=rnd.random()
                if r<0.12:seq.append(("stop",None))
                elif r<0.22:seq.append(("txt",[rnd.choice(UNREC[l])]))
                elif r<0.30:seq.append(("txt",rnd.sample(REC[(l,v)],3)))
                elif r<0.36 and seq and seq[-1][0]=="txt":seq.append(("same",None))
                else:seq.append(("txt",[rnd.choice(REC[(l,v)])]))
            last=None
            for kind,arg in seq:
                if kind=="stop":pg.evaluate("stopSp()")
                elif kind=="same" and last:pg.evaluate("a=>aud(a[0],a[1])",last)
                else:last=["b"+str(rnd.random()),arg];pg.evaluate("a=>aud(a[0],a[1])",last)
                pg.wait_for_timeout(rnd.choice(GAPS))
            pg.wait_for_timeout(dl[1]+900)
            iv=pg.evaluate("window.__iv");pg.evaluate("stopSp()");pg.wait_for_timeout(30)
            w,pair=overlap(iv);st["tours"]+=1;st["sons"]+=len(iv);st["types"]|={x["k"] for x in iv};st["voix"].add(f"{l}/{v or 'origine'}")
            if w:st["chev"]+=1;st["pire"]=max(st["pire"],w);bad.append((k,l,v,dl,round(w,1),pair))
        print(f"   {page} : {st['tours']} tours, {st['sons']} sons, types {sorted(st['types'])}, {len(st['voix'])} voix, chevauchements {st['chev']} (pire {round(st['pire'],1)} ms)",flush=True)
        ck(f"{page} A : {st['tours']} séries de 6 appuis (5 langues, {len(st['voix'])} voix, délais 0–600 ms) → 0 chevauchement",st["chev"]==0 and not er,[bad[:5],er[:2]])
        # --- B. reprise lente du contexte audio : un son généré ne démarre pas après un nouvel appui
        pg.evaluate("window.__dl=[0,0]")
        res=[]
        for rep in range(10):
            res.append(pg.evaluate("""async(rep)=>{stopSp();window.__iv=[];const c=axCtx();await c.suspend();const R=c.resume.bind(c);
              window.__novox=1;c.resume=()=>{window.__rp=(window.__rp||0)+1;return new Promise(z=>setTimeout(()=>R().then(z,z),250))};
              const pcm=new Float32Array(22050).map((_,i)=>Math.sin(i/9)*.3),r={pcm,sr:22050};
              /* 1) conversation : tvPlayPcm, puis nouvel appui pendant la reprise */
              AU.id='tq';const tok=AU.tok;const p1=tvPlayPcm(r,tok);await new Promise(z=>setTimeout(z,60+rep*10));aud('n18b'+rep,[]);stopSp();
              await p1;const a=window.__iv.length;
              /* 2) chaîne de secours d'aud() (Piper) avec contexte suspendu */
              await c.suspend();const sv={sup:tvSup,gen:tvGen};tvSup=()=>true;tvGen=async()=>r;S.lang='eu';
              aud('n18p'+rep,['zq texto sin grabar '+rep]);await new Promise(z=>setTimeout(z,700));const t2=window.__iv.length;
              /* nouvel appui pendant la reprise : seul le nouveau son doit exister */
              stopSp();await c.suspend();window.__iv=[];aud('n18q'+rep,['zq otro texto '+rep]);
              window.__rp=0;for(let i=0;i<300&&!window.__rp;i++)await new Promise(z=>setTimeout(z,10));const rp=window.__rp;
              stopSp();await new Promise(z=>setTimeout(z,600));const b=window.__iv.length;
              tvSup=sv.sup;tvGen=sv.gen;c.resume=R;window.__novox=0;await c.resume();stopSp();return [a,t2,b,rp]}""",rep))
        ck(f"{page} B : reprise lente du contexte (10 essais) → aucun son généré ne démarre après l'arrêt",all(x[0]==0 and x[2]==0 and x[3]>=1 for x in res),res)
        ck(f"{page} B : témoin — sans nouvel appui, le son généré se joue bien",all(x[1]>=1 for x in res),res)
        c.close()
    b.close()
print(f"\n{sum(R)}/{len(R)} contrôles réussis");sys.exit(0 if all(R) else 1)
