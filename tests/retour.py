# Bouton retour : revient à l'écran précédent (et non au menu), les séances sont sautées, la sortie se fait depuis la racine.
import sys
from playwright.sync_api import sync_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else "http://127.0.0.1:8774/"
R=[]
def ck(n,c,i=""):R.append(bool(c));print("OK  " if c else "FAIL",n,"" if c else str(i)[:300],flush=True)
with sync_playwright() as p:
    b=p.chromium.launch();c=b.new_context(service_workers="block");pg=c.new_page();pg.goto(BASE);pg.wait_for_timeout(2500)
    t=lambda:pg.evaluate("(document.querySelector('.ptitle')||document.querySelector('h2')||{}).textContent||''")
    pg.evaluate("home()");pg.wait_for_timeout(300);pg.evaluate("tools()");pg.wait_for_timeout(300);pg.evaluate("lists()");pg.wait_for_timeout(300)
    h1=pg.evaluate("document.body.innerText.slice(0,0)")
    ck("lists : écran des listes affiché",pg.evaluate("SCR")=="lists",pg.evaluate("SCR"))
    pg.go_back();pg.wait_for_timeout(500)
    ck("retour depuis Listes → Outils (pas le menu)",pg.evaluate("!!document.querySelector('h3')&&/Outils|Tools/.test(document.body.innerText)"),pg.evaluate("document.body.innerText.slice(0,80)"))
    pg.evaluate("conj()");pg.wait_for_timeout(300);pg.evaluate("exc()");pg.wait_for_timeout(300)
    pg.go_back();pg.wait_for_timeout(500);ck("exc → retour → conj",pg.evaluate("SCR")=="conj",pg.evaluate("SCR"))
    pg.go_back();pg.wait_for_timeout(500);ck("conj → retour → Outils",pg.evaluate("/Outils|Tools/.test(document.body.innerText)"))
    pg.evaluate("tools()");pg.wait_for_timeout(200);pg.evaluate("start('Mélange')");pg.wait_for_timeout(800)
    ck("séance en cours",pg.evaluate("INL")==1)
    pg.go_back();pg.wait_for_timeout(600)
    ck("retour pendant une séance → écran précédent (Outils), pas la séance",pg.evaluate("INL")==0 and pg.evaluate("/Outils|Tools/.test(document.body.innerText)"),pg.evaluate("[INL,document.body.innerText.slice(0,60)]"))
    pg.go_back();pg.wait_for_timeout(500);ck("encore un retour → accueil",pg.evaluate("SCR")=="home" and not pg.evaluate("/Outils|Tools/.test(document.querySelector('h2.ptitle')?document.querySelector('h2.ptitle').textContent:'')"),pg.evaluate("SCR"))
    b.close()
print(sum(R),"/",len(R),"OK")
