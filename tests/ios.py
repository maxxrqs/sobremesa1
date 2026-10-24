# iOS (simulation) : audio et micro avec les contraintes de WebKit reproduites dans Chromium.
# Modèle : seuls touchend/pointerup/click/keydown sont des gestes ; AudioContext ne reprend que dans un geste et peut rester
# « interrupted » (resume() sans fin) ; un <audio> n'est autorisé hors geste qu'après une lecture lancée dans un geste ;
# speechSynthesis ignore les phrases tant qu'aucune n'a été lancée dans un geste ; SpeechRecognition.start() hors geste → not-allowed.
# Ce n'est PAS un test sur iPhone : il vérifie la logique de l'appli face à ces règles, pas Safari lui-même.
import sys
from playwright.sync_api import sync_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else "http://127.0.0.1:8774/"
R=[]
def ck(n,c,i=""):
    R.append(bool(c));print("OK  " if c else "FAIL",n,"" if c else str(i)[:400],flush=True)
IPHONE="Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1"
ANDROID="Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Mobile Safari/537.36"
INIT="""
window.__g=0;window.__log=[];window.__els=[];window.__ctxs=[];window.__gumN=0;window.__sr={mode:'ok',res:'dónde está la playa',sess:null,started:0};
['touchend','pointerup','click','keydown'].forEach(t=>addEventListener(t,()=>{__g=1;setTimeout(()=>{__g=0},0)},{capture:true}));
if(window.__noAS!==1)navigator.audioSession={type:'auto'};
class FCtx{constructor(){this.state='suspended';this.currentTime=0;this.destination={};this.sampleRate=44100;this.__intr=0;__ctxs.push(this)}
 resume(){if(this.__intr)return new Promise(()=>{});if(__g)this.state='running';return Promise.resolve()}
 close(){this.state='closed';return Promise.resolve()}
 createBuffer(c,n,sr){return{duration:n/sr,getChannelData:()=>({set(){}})}}
 createBufferSource(){const t=this;return{buffer:null,onended:null,connect(){},stop(){},start(){if(t.state==='running'){__log.push('ctxplay');const s=this;setTimeout(()=>s.onended&&s.onended(),30)}}}}
 createGain(){return{gain:{value:1,setValueAtTime(){},linearRampToValueAtTime(){},exponentialRampToValueAtTime(){}},connect(){}}}
 createDynamicsCompressor(){return{threshold:{value:0},knee:{value:0},ratio:{value:0},connect(){}}}
 createOscillator(){return{type:'',frequency:{value:0},connect(){},start(){},stop(){}}}
 decodeAudioData(ab,ok){const b={duration:.3};setTimeout(()=>ok&&ok(b),1);return Promise.resolve(b)}}
window.AudioContext=FCtx;window.webkitAudioContext=FCtx;
window.Audio=function(src){const el={src:src||'',paused:true,loop:false,volume:1,currentTime:0,__bl:0,onended:null,onerror:null,setAttribute(){},pause(){this.paused=true},
 play(){if(__g)this.__bl=1;if(!this.__bl)return Promise.reject(Object.assign(new Error('blocked'),{name:'NotAllowedError'}));this.paused=false;
  const s=this;if(!this.loop&&!String(this.src).startsWith('blob:')){}__log.push(this.loop?'keep':'elplay');if(!this.loop)setTimeout(()=>{s.paused=true;s.onended&&s.onended()},30);return Promise.resolve()}};__els.push(el);return el};
const SS={pr:0,getVoices:()=>[{name:'Mónica',lang:'es-ES',localService:true,voiceURI:'m'}],
 speak(u){if(__g)SS.pr=1;__log.push('speak:'+u.text.trim()+(SS.pr?'':':ignoré'));if(!SS.pr||!u.text.trim())return;setTimeout(()=>{u.onstart&&u.onstart();setTimeout(()=>u.onend&&u.onend(),20)},10)},cancel(){},resume(){},pause(){}};
Object.defineProperty(window,'speechSynthesis',{value:SS,configurable:true});window.SpeechSynthesisUtterance=function(t){this.text=t};
if(navigator.mediaDevices)navigator.mediaDevices.getUserMedia=async()=>{__gumN++;return{getTracks:()=>[{stop(){}}]}};
class FSR{start(){const t=this,S=__sr;S.started++;
  if(!__g){setTimeout(()=>{t.onerror&&t.onerror({error:'not-allowed'});t.onend&&t.onend()},20);return}
  S.sess=navigator.audioSession&&navigator.audioSession.type;
  if(S.mode==='hang'){setTimeout(()=>{t.onaudiostart&&t.onaudiostart()},10);return}
  setTimeout(()=>{t.onaudiostart&&t.onaudiostart();t.onsoundstart&&t.onsoundstart();t.onspeechstart&&t.onspeechstart();
   t.onresult&&t.onresult({results:[Object.assign([{transcript:S.res}],{isFinal:true})]});t.onend&&t.onend()},30)}
 stop(){__log.push('srstop')}abort(){}}
window.SpeechRecognition=FSR;window.webkitSpeechRecognition=FSR;
"""
def setup(b,ua,pre=""):
    c=b.new_context(locale="fr-FR",user_agent=ua,has_touch=True,is_mobile=True,viewport={"width":390,"height":844})
    pg=c.new_page();errs=[];pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.add_init_script(pre+INIT);pg.goto(BASE+"index.html");pg.wait_for_timeout(2000);return c,pg,errs
def ask(pg):
    pg.evaluate("""()=>{S.lang='es';S.lvl=1;S.mute=true;build();R={mode:'t',ok:0,xp:0,hist:[],done:false};R.q={ty:'speak',es:'¿Dónde está la playa?',fr:'Où est la plage ?',say:'¿Dónde está la playa?',key:null,sol:'¿Dónde está la playa?'};draw()}""");pg.wait_for_timeout(300)
def fbt(pg):return pg.evaluate("document.getElementById('fb')?document.getElementById('fb').innerText:''")
STUB="""()=>{window.__axGet0=window.__axGet0||axGet;axGet=async(l,t,v)=>({b:{duration:.3},raw:new Uint8Array([255,251,144,0,0,0]).buffer})}"""
def tap(pg):pg.tap("body",position={"x":200,"y":420});pg.wait_for_timeout(150)
with sync_playwright() as p:
    b=p.chromium.launch()
    c,pg,er=setup(b,IPHONE)
    ck("iPhone détecté",pg.evaluate("IOSW"))
    # A. pointerdown seul : pas un geste sur iOS → rien n'est consommé
    pg.evaluate("dispatchEvent(new PointerEvent('pointerdown',{bubbles:true}))");pg.wait_for_timeout(100)
    ck("pointerdown seul : élément audio et voix système non consommés",pg.evaluate("!AX.pel&&!AX.tp"),pg.evaluate("[!!AX.pel,AX.tp]"))
    tap(pg)
    ck("toucher : contexte audio débloqué",pg.evaluate("AX.ctx&&AX.ctx.state")=="running",pg.evaluate("AX.ctx&&AX.ctx.state"))
    ck("toucher : élément <audio> béni",pg.evaluate("!!(AX.pel&&AX.pel.__bl)"))
    ck("toucher : voix système amorcée",pg.evaluate("AX.tp===1&&speechSynthesis.pr===1"))
    ck("iOS ≥ 17 : pas de son muet en boucle",not pg.evaluate("!!AX.kel"))
    # B. lecture normale d'un clip enregistré
    pg.evaluate(STUB);pg.evaluate("__log.length=0;aud('t1',['Hola'])");pg.wait_for_timeout(400)
    ck("clip enregistré joué via le contexte audio","ctxplay" in pg.evaluate("__log"),pg.evaluate("__log"))
    # C. contexte « interrupted » dont resume() ne rend jamais la main (appel, Siri, autre appli) : repli <audio> béni, sans geste
    pg.evaluate("AX.ctx.state='interrupted';AX.ctx.__intr=1;__log.length=0;aud('t2',['Hola'])");pg.wait_for_timeout(1200)
    lg=pg.evaluate("__log");ck("contexte interrompu : son joué par l'élément <audio> béni",lg.count("elplay")>=1,lg)
    ck("contexte interrompu : bouton revenu au repos",pg.evaluate("AU.id")==None,pg.evaluate("AU.id"))
    # contrôle : un new Audio() non béni (ancien comportement) est refusé hors geste
    ck("contrôle : un <audio> neuf hors geste est refusé",pg.evaluate("new Audio('x').play().then(()=>false,e=>e.name==='NotAllowedError')"))
    # D. geste suivant : contexte interrompu recréé
    n0=pg.evaluate("__ctxs.length");tap(pg)
    ck("geste après interruption : nouveau contexte en marche",pg.evaluate("__ctxs.length")>n0 and pg.evaluate("AX.ctx.state")=="running" and pg.evaluate("__ctxs[%d-1].state"%n0) in ("closed","interrupted"),pg.evaluate("__ctxs.map(x=>x.state)"))
    pg.evaluate("__log.length=0;aud('t3',['Hola'])");pg.wait_for_timeout(400)
    ck("après recréation : clip joué par le contexte audio",pg.evaluate("__log").count("ctxplay")>=1,pg.evaluate("__log"))
    # E. arrière-plan → retour : contexte périmé recréé au geste suivant (bug WebKit « running mais muet »), bruitages aussi
    pg.evaluate("S.mute=false;addEventListener('click',()=>FX.play('good'),{once:true})");tap(pg);a0=pg.evaluate("__ctxs.length")
    pg.evaluate("Object.defineProperty(document,'visibilityState',{value:'hidden',configurable:true});document.dispatchEvent(new Event('visibilitychange'));Object.defineProperty(document,'visibilityState',{value:'visible',configurable:true})")
    ck("arrière-plan : contexte marqué périmé",pg.evaluate("AX.stale===1"))
    pg.evaluate("addEventListener('click',()=>FX.play('good'),{once:true})");tap(pg)
    ck("retour : voix et bruitages sur des contextes neufs",pg.evaluate("__ctxs.length")>=a0+2 and pg.evaluate("AX.stale")==0 and pg.evaluate("AX.fxs")==0,pg.evaluate("[a0=%d,__ctxs.length,AX.stale,AX.fxs]"%a0))
    # F. voix système lancée après une attente réseau (hors geste) : parle grâce à l'amorçage
    pg.evaluate("window.__axPlay0=axPlay;axPlay=async()=>false;__log.length=0;aud('t4',['Hola'])");pg.wait_for_timeout(600)
    lg=pg.evaluate("__log");ck("voix système hors geste : phrase prononcée",("speak:Hola" in lg),lg)
    # G. micro : dictée démarrée dans le geste, sans getUserMedia, session audio adaptée puis rétablie
    ask(pg);pg.evaluate("__log.length=0;__sr.mode='ok';__gumN=0");pg.tap("button[onclick='rec()']");pg.wait_for_timeout(500)
    ck("micro : dictée démarrée dans le geste → bonne réponse",pg.evaluate("R.ok")>0,fbt(pg))
    ck("micro : pas de getUserMedia préalable sur iOS",pg.evaluate("__gumN")==0,pg.evaluate("__gumN"))
    ck("micro : session « play-and-record » pendant la dictée",pg.evaluate("__sr.sess")=="play-and-record",pg.evaluate("__sr.sess"))
    ck("micro : session « playback » rétablie après",pg.evaluate("navigator.audioSession.type")=="playback")
    ck("micro : contexte audio recréé au geste suivant",pg.evaluate("AX.stale===1"))
    tap(pg);pg.evaluate(STUB);pg.evaluate("__log.length=0")
    # H. mauvaise réponse et refus d'autorisation
    ask(pg);pg.evaluate("__sr.res='hola'");pg.tap("button[onclick='rec()']");pg.wait_for_timeout(500)
    ck("micro : mauvaise phrase refusée",pg.evaluate("R.done") and pg.evaluate("R.ok")==0,fbt(pg))
    ask(pg);pg.evaluate("rec()");pg.wait_for_timeout(400)
    t=fbt(pg);ck("micro hors geste : message d'autorisation + Réessayer",("Autorisation du micro" in t) and "Réessayer" in t,t)
    ck("micro hors geste : session rétablie",pg.evaluate("navigator.audioSession.type")=="playback")
    # I. dictée bloquée (iOS ne termine jamais) : arrêt forcé puis message, pas d'écran figé
    ask(pg);pg.evaluate("__sr.mode='hang';__log.length=0");pg.tap("button[onclick='rec()']");pg.wait_for_timeout(18500)
    t=fbt(pg);ck("dictée bloquée : arrêt forcé + message + Réessayer","srstop" in pg.evaluate("__log") and "Réessayer" in t and "écoute" not in t,t)
    ck("aucune erreur JavaScript (iPhone)",not er,er);c.close()
    # J. iOS < 17 (sans navigator.audioSession) : son muet en boucle pour ignorer l'interrupteur silence, coupé en arrière-plan
    c,pg,er=setup(b,IPHONE,"window.__noAS=1;");tap(pg)
    ck("iOS < 17 : son muet en boucle lancé au geste",pg.evaluate("!!(AX.kel&&!AX.kel.paused&&AX.kel.loop)"))
    pg.evaluate("Object.defineProperty(document,'visibilityState',{value:'hidden',configurable:true});document.dispatchEvent(new Event('visibilitychange'))")
    ck("iOS < 17 : son muet coupé en arrière-plan",pg.evaluate("AX.kel.paused"))
    ck("aucune erreur JavaScript (iOS < 17)",not er,er);c.close()
    # K. Android : comportement inchangé
    c,pg,er=setup(b,ANDROID)
    ck("Android : pas détecté comme iOS",not pg.evaluate("IOSW"))
    pg.evaluate("dispatchEvent(new PointerEvent('pointerdown',{bubbles:true}))")
    ck("Android : déblocage dès pointerdown (inchangé)",pg.evaluate("AX.un===1"))
    ck("Android : ni élément béni ni amorçage voix",pg.evaluate("!AX.pel&&!AX.tp&&!AX.kel"))
    ask(pg);pg.evaluate("__gumN=0;__sr.mode='ok';__sr.res='dónde está la playa';__sr.sess='x'");pg.tap("button[onclick='rec()']");pg.wait_for_timeout(600)
    ck("Android : vérification micro (getUserMedia) conservée",pg.evaluate("__gumN")>=1 or pg.evaluate("R.ok")>0,[pg.evaluate("__gumN"),fbt(pg)])
    ck("Android : session audio non modifiée par le micro",pg.evaluate("__sr.sess")!="play-and-record" and pg.evaluate("navigator.audioSession.type")=="playback",pg.evaluate("[__sr.sess,navigator.audioSession.type]"))
    ck("aucune erreur JavaScript (Android)",not er,er);c.close()
    b.close()
print(sum(R),"/",len(R),"OK")
sys.exit(0 if all(R) else 1)
