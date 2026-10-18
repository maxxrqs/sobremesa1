# Parcourt les écrans et exercices dans chaque langue d'interface et liste les textes visibles non traduits.
# Usage : python3 tests/i18n_crawl.py http://127.0.0.1:8775/ [sortie.json]
import sys,json
from playwright.sync_api import sync_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else "http://127.0.0.1:8775/"
OUT=sys.argv[2] if len(sys.argv)>2 else None
HOOK="""(()=>{window.__miss=new Map();window.__scr='';
window.__col=function(){const NUM=/\\d+(?:[.,]\\d+)?/g;const D=TR[UI]||{};const V=window.__vals||(window.__vals=new Set(Object.values(D).map(x=>String(x).trim())));const VN=window.__valsn||(window.__valsn=new Set([...V].map(x=>x.replace(NUM,'#'))));
 const look=c=>{c=c.trim();if(c.length<2||!/[A-Za-zÀ-ÿ]/.test(c))return true;return D[c]!=null||D[c.replace(NUM,'#')]!=null||V.has(c)||VN.has(c.replace(NUM,'#'))};
 const add=(t,k)=>{t=t.replace(/\\s+/g,' ').trim();if(!t||look(t))return;const v=window.__miss.get(t)||{n:0,s:new Set(),k};v.n++;v.s.add(window.__scr);window.__miss.set(t,v)};
 const walk=n=>{if(n.nodeType===3){if(n.parentNode.closest('[translate="no"]:not(html),script,style,svg'))return;add(n.nodeValue,'txt');return}
  if(n.nodeType!==1||n.getAttribute('translate')==='no'||/^(SCRIPT|STYLE|SVG)$/i.test(n.tagName))return;
  ['placeholder','aria-label','title','alt'].forEach(a=>{if(n.hasAttribute(a))add(n.getAttribute(a),'@'+a)});n.childNodes.forEach(walk)};
 walk(document.body)};
window.__dump=()=>[...window.__miss].map(([t,v])=>[t,v.n,[...v.s].slice(0,4),v.k]);})()"""
SHOW=r"""async (a)=>{const sl=ms=>new Promise(r=>setTimeout(r,ms));const snap=async n=>{window.__scr=n;await sl(40);__col()};
 const tryf=async(n,f)=>{try{f()}catch(e){window.__err=(window.__err||[]);window.__err.push(n+': '+e)}await snap(n)};
 U=null;await tryf('landing',()=>landing());await tryf('auth-login',()=>auth('login'));await tryf('auth-signup',()=>auth('signup'));
 U='t';
 for(const lang of a.langs){S.lang=lang;S.mute=true;
  for(const L of a.levels){S.lvl=L;build();PLC=null;
   for(const [n,f] of [['home',()=>home()],['lists',()=>lists()],['conj',()=>conj()],['exc',()=>exc()],['expr',()=>expr()],['scn',()=>scn()],['trad',()=>trad()],['tools',()=>tools()],['prog-p',()=>prog('p')],['prog-q',()=>prog('q')],['prog-s',()=>prog('s')],['entry',()=>entry()]])await tryf(lang+L+':'+n,f);
   await tryf(lang+L+':menu',()=>{document.getElementById('mn')&&document.getElementById('mn').remove();menu()});try{document.getElementById('mn').remove()}catch(e){}
   // exercices : tous les types, rendus puis corrigés (mauvaise réponse)
   const tys=a.types;
   for(const ty of tys){for(let k=0;k<a.reps;k++){try{R={mode:'lesson',t:'Chunk',n:0,ok:0,xp:0,cat:null};INL=1;R.q=mkQ(ty,0);draw();await snap(lang+L+':ex:'+ty);
     try{if(R.q.o)ans(R.q.o.findIndex(x=>x!==R.q.g));else if(typeof idk==='function')idk();else if(window.tidk)tidk()}catch(e){}await snap(lang+L+':exfb:'+ty)}catch(e){(window.__err=window.__err||[]).push(lang+L+' ex '+ty+': '+e)}}}
  }}
 // test de niveau
 try{S.lang='es';test();await snap('test');}catch(e){}
 return {miss:__dump(),err:(window.__err||[]).slice(0,40)}}"""
TYPES=["read","readP","es2fr","tf","odd","cloze","listen","listenP","listenT","dict","build","type","fr2P","fr2es","conj","speak","rep","speakF","speakC","speakQ","exL","exM","exE","exc","replyQ"]
res={}
with sync_playwright() as p:
    b=p.chromium.launch()
    for ui in (sys.argv[3].split(",") if len(sys.argv)>3 else ["en","it","de","pt"]):
        c=b.new_context(locale="fr-FR");pg=c.new_page();er=[];pg.on("pageerror",lambda e:er.append(str(e)))
        pg.add_init_script("try{localStorage.setItem('cast_ui','%s')}catch(e){}"%ui)
        pg.goto(BASE+"index.html");pg.wait_for_timeout(2500)
        pg.evaluate("l=>trLoad(l).then(()=>{UI=l})",ui);pg.wait_for_timeout(300);pg.evaluate(HOOK)
        r=pg.evaluate(SHOW,{"langs":["es","va","ca","gl","eu"],"levels":[1,3,5],"types":TYPES,"reps":3})
        r["pageerr"]=er[:10];res[ui]=r;print(ui,"miss",len(r["miss"]),"err",len(r["err"]),r["err"][:5],er[:3],flush=True);c.close()
if OUT: json.dump(res,open(OUT,"w"),ensure_ascii=False,indent=0)
