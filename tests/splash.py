# Écran de chargement : présent dès le premier paint, retiré après le premier écran, sans erreur, manifest cohérent.
import sys,json,urllib.request
from playwright.sync_api import sync_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else "http://localhost:8772/"
R=[]
def ck(n,c,i=""):
    R.append(bool(c));print("OK  " if c else "FAIL",n,"" if c else str(i)[:300],flush=True)
mf=json.load(urllib.request.urlopen(BASE+"manifest.webmanifest"))
ck("manifest : fond de l'écran de démarrage = fond de l'icône",mf["background_color"].upper()=="#CFE9DC",mf)
with sync_playwright() as p:
    b=p.chromium.launch()
    for name,pre in [("visiteur",""),("connecté","try{localStorage.setItem('cast_user','x')}catch(e){}")]:
        c=b.new_context(viewport={"width":390,"height":800});pg=c.new_page();er=[];pg.on("pageerror",lambda e:er.append(str(e)))
        if pre:pg.add_init_script(pre)
        pg.goto(BASE+"index.html",wait_until="commit")
        pg.wait_for_selector("#splash",state="attached",timeout=5000)
        ck(f"{name} : splash dans le DOM dès le chargement",True)
        pg.wait_for_function("!document.getElementById('splash')",timeout=9000)
        ck(f"{name} : splash retiré",True)
        ck(f"{name} : contenu de l'appli affiché",pg.evaluate("document.getElementById('app').innerText.length")>10)
        ck(f"{name} : theme-color restauré",pg.evaluate("document.querySelector('meta[name=theme-color]').content")=="#1B2A4A")
        ck(f"{name} : aucune erreur JS",not er,er);c.close()
    # sécurité : si le script plante, le splash ne bloque pas l'écran
    c=b.new_context();pg=c.new_page();pg.goto(BASE+"index.html");pg.wait_for_timeout(3000)
    ck("splash ne bloque pas les clics (retiré)",pg.evaluate("!document.getElementById('splash')"));c.close()
    b.close()
print(sum(R),"/",len(R),"OK");sys.exit(0 if all(R) else 1)
