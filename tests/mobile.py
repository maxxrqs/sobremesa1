# Compatibilité mobile : repli color-mix (équivalence avec le rendu natif), API absentes (iOS/Firefox), tailles d'écran, copie, audio.
import sys,re
from playwright.sync_api import sync_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else "http://localhost:8772/"
R=[]
def ck(n,c,i=""):
    R.append(bool(c));print("OK  " if c else "FAIL",n,"" if c else str(i)[:400],flush=True)
def num(x):
    m=re.findall(r"[-\d.]+",x);return [float(v) for v in m]
def rgba(x):
    # "rgb(r,g,b)", "rgba(...)", "color(srgb r g b / a)"
    if x.startswith("color("):
        v=num(x.split("srgb")[1]);r,g,b=[c*255 for c in v[:3]];a=v[3] if len(v)>3 else 1;return [r,g,b,a]
    v=num(x);return v[:3]+[v[3] if len(v)>3 else 1]
with sync_playwright() as p:
    b=p.chromium.launch()
    # 1. équivalence du repli color-mix avec le calcul natif, thèmes clair et sombre
    for scheme in ["light","dark"]:
        c=b.new_context(color_scheme=scheme);pg=c.new_page();er=[];pg.on("pageerror",lambda e:er.append(str(e)))
        pg.goto(BASE+"index.html");pg.wait_for_timeout(2000)
        exprs=pg.evaluate("""()=>{const t=[...document.querySelectorAll('style')].map(e=>e.__cm||e.textContent).join('\\n'),o=new Set();let i=0;
          for(;;){const k=t.indexOf('color-mix(',i);if(k<0)break;let d=0,j=k+9;for(;j<t.length;j++){if(t[j]==='(')d++;else if(t[j]===')'){d--;if(!d)break}}o.add(t.slice(k,j+1));i=j+1}return [...o]}""")
        res=pg.evaluate("""(ex)=>ex.map(x=>{const d=document.createElement('div');d.style.color=x;document.body.appendChild(d);const nat=getComputedStyle(d).color;d.remove();return [x,nat,CMX.ev(x)]})""",exprs)
        bad=[]
        for x,nat,mine in res:
            if mine is None:
                if 'var(--tool)' in x or 'var(--tc)' in x or 'var(--c)' in x or 'var(--u' in x:continue   # variable propre à l'élément : le repli laisse l'expression telle quelle
                bad.append((x,"None"));continue
            a,m=rgba(nat),rgba(mine)
            if any(abs(a[i]-m[i])>2 for i in range(3)) or abs(a[3]-m[3])>.02:bad.append((x,nat,mine))
        ck(f"color-mix repli = rendu natif ({scheme}, {len(res)} expressions)",not bad and len(res)>20,bad[:3]);ck(f"{scheme} : aucune erreur JS",not er,er);c.close()
    # 2. chemin de repli réellement utilisé : navigateur sans color-mix
    c=b.new_context();pg=c.new_page();er=[];pg.on("pageerror",lambda e:er.append(str(e)))
    pg.add_init_script("const _s=CSS.supports.bind(CSS);CSS.supports=function(a,b){return String(b||a).includes('color-mix')?false:_s.apply(null,arguments)}")
    pg.goto(BASE+"index.html");pg.wait_for_timeout(2500)
    left=pg.evaluate("""()=>{const t=[...document.querySelectorAll('style')].map(e=>e.textContent).join('\\n'),o=[];let i=0;for(;;){const k=t.indexOf('color-mix(',i);if(k<0)break;let d=0,j=k+9;for(;j<t.length;j++){if(t[j]==='(')d++;else if(t[j]===')'){d--;if(!d)break}}const x=t.slice(k,j+1);if(!/var\\(--(tool|tc|c|u)\\b/.test(x))o.push(x);i=j+1}return o}""")
    ck("sans color-mix : plus aucune expression dans les feuilles de style",not left,left)
    pg.evaluate("S.lang='es';S.lvl=1;S.mute=true;home()");pg.wait_for_timeout(300)
    pg.evaluate("document.documentElement.dataset.theme='dark'");pg.wait_for_timeout(300)
    ck("sans color-mix : changement de thème sans erreur",not er,er);c.close()
    # 3. API absentes (iOS Safari/Firefox) : pas de vibrate, speechSynthesis, SpeechRecognition, audioSession
    c=b.new_context();pg=c.new_page();er=[];pg.on("pageerror",lambda e:er.append(str(e)))
    pg.add_init_script("delete navigator.vibrate;Object.defineProperty(navigator,'vibrate',{value:undefined});delete window.SpeechRecognition;delete window.webkitSpeechRecognition;try{Object.defineProperty(window,'speechSynthesis',{value:undefined,configurable:true})}catch(e){};Object.defineProperty(window,'AudioContext',{value:undefined});Object.defineProperty(window,'webkitAudioContext',{value:undefined});try{Object.defineProperty(navigator,'clipboard',{value:undefined})}catch(e){}")
    pg.goto(BASE+"index.html");pg.wait_for_timeout(2500)
    pg.evaluate("S.lang='es';S.lvl=1;S.mute=false;home()");pg.wait_for_timeout(300)
    for i in range(3):
        pg.evaluate("""()=>{try{FX.play('good');FX.play('bad');fxOk(true);fxOk(false)}catch(e){window.__e=String(e)}}""")
    ck("audio/vibration/synthèse vocale absents : sons et retours sans plantage",not er and not pg.evaluate("window.__e"),[er,pg.evaluate("window.__e")])
    pg.evaluate("tools()");pg.wait_for_timeout(300);ck("outils s'affichent sans API",pg.evaluate("document.getElementById('app').innerText.length")>50)
    ck("exercice oral non proposé sans SpeechRecognition",pg.evaluate("!SR"));c.close()
    # 4. copie : repli execCommand si clipboard absent
    c=b.new_context();pg=c.new_page();pg.add_init_script("Object.defineProperty(navigator,'clipboard',{value:undefined})")
    pg.goto(BASE+"index.html");pg.wait_for_timeout(2000)
    r=pg.evaluate("""()=>{window.TS={out:{t:'hola'}};let called=0;const o=document.execCommand;document.execCommand=function(c){if(c==='copy')called=1;return true};const b=document.createElement('button');tcopy(b);document.execCommand=o;return [called,b.textContent]}""")
    ck("copie sans navigator.clipboard : repli execCommand",r[0]==1,r);c.close()
    # 5. tailles d'écran : pas de défilement horizontal sur écrans étroits (iPhone SE, Android compact, grands)
    for w,h in [(320,568),(360,640),(375,667),(390,844),(430,932),(768,1024)]:
        c=b.new_context(viewport={"width":w,"height":h},has_touch=True,is_mobile=True,device_scale_factor=2);pg=c.new_page();er=[];pg.on("pageerror",lambda e:er.append(str(e)))
        pg.goto(BASE+"index.html");pg.wait_for_timeout(1800)
        pg.evaluate("S.lang='es';S.lvl=1;S.mute=true;home()");pg.wait_for_timeout(300)
        o={}
        for sc in ["home()","lists()","conj()","exc()","expr()","scn()","trad()","tools()","menu()"]:
            try:
                pg.evaluate(sc);pg.wait_for_timeout(250);o[sc]=pg.evaluate("document.documentElement.scrollWidth-innerWidth")
            except Exception as e:o[sc]="ERR "+str(e)[:40]
        wide={k:v for k,v in o.items() if not isinstance(v,(int,float)) or v>1}
        ck(f"{w}x{h} : pas de défilement horizontal sur 9 écrans",not wide,wide);ck(f"{w}x{h} : aucune erreur JS",not er,er);c.close()
    b.close()
print(sum(R),"/",len(R),"OK");sys.exit(0 if all(R) else 1)
