# Anomalie n°10 de l'audit du 7 novembre (WCAG 1.4.4) : zoom au pincement réautorisé, sur castellano.html et index.html.
#  - balise viewport sans maximum-scale ni user-scalable=no ; plus de blocage des gestes (gesturestart/gesturechange, touchmove à 2 doigts) ;
#  - pincement (CDP Input.synthesizePinchGesture, téléphone émulé ; source « default » : Chromium sans écran n'agrandit pas avec la source « touch »,
#    même sur une page sans restriction) : la page s'agrandit ; avant la correction, user-scalable=no la laissait à l'échelle 1 ;
#  - double-tap : pas de zoom (touch-action:manipulation sur html et sur les boutons), l'appli garde son comportement d'appli ;
#  - champs de saisie ≥ 16 px sur iOS (sinon Safari zoome tout seul au focus quand maximum-scale n'est plus fixé) : la règle
#    @supports (-webkit-touch-callout:none) n'existe que sur iOS ; le test l'applique telle quelle pour mesurer son effet ;
#  - 320 px de large (équivalent du 400 % de WCAG 1.4.10) : pas de défilement horizontal.
# Usage : python3 tests/rangesrv.py 8772 .  puis  python3 tests/zoom_b.py [URL]   (URL par défaut http://localhost:8772/)
import sys
from playwright.sync_api import sync_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else "http://localhost:8772/"
R=[]
def ck(n,c,i=""):
    R.append(bool(c));print("OK  " if c else "FAIL",n,"" if c else str(i)[:400],flush=True)
with sync_playwright() as p:
    b=p.chromium.launch()
    for page in ["castellano.html","index.html"]:
        print("==",page)
        c=b.new_context(locale="fr-FR",viewport={"width":390,"height":844},device_scale_factor=2,is_mobile=True,has_touch=True);pg=c.new_page();er=[]
        pg.on("pageerror",lambda e:er.append(str(e)))
        pg.goto(BASE+page);pg.wait_for_timeout(1500)
        vp=pg.evaluate("document.querySelector('meta[name=viewport]').content")
        ck("viewport sans maximum-scale ni user-scalable=no",("user-scalable=no" not in vp) and ("maximum-scale" not in vp) and "width=device-width" in vp,vp)
        ck("html : touch-action manipulation (pincement permis, double-tap neutralisé)",pg.evaluate("getComputedStyle(document.documentElement).touchAction")=="manipulation",pg.evaluate("getComputedStyle(document.documentElement).touchAction"))
        blk=pg.evaluate("""()=>{const g=new Event('gesturestart',{cancelable:true,bubbles:true});document.body.dispatchEvent(g);
          const mk=(i,x)=>new Touch({identifier:i,target:document.body,clientX:x,clientY:300});
          const t=new TouchEvent('touchmove',{cancelable:true,bubbles:true,touches:[mk(1,100),mk(2,200)]});document.body.dispatchEvent(t);
          return {gesture:g.defaultPrevented,touch2:t.defaultPrevented}}""")
        ck("gestes de zoom non bloqués par script (gesturestart, touchmove à 2 doigts)",not blk["gesture"] and not blk["touch2"],blk)
        pg.evaluate("()=>{S.lang='es';S.lvl=1;S.ob=1;build();welcomeOb()}");pg.wait_for_timeout(300)
        ck("boutons : touch-action manipulation",pg.evaluate("[...document.querySelectorAll('button')].every(x=>getComputedStyle(x).touchAction==='manipulation')"))
        cdp=c.new_cdp_session(pg)
        s0=pg.evaluate("visualViewport.scale")
        cdp.send("Input.synthesizePinchGesture",{"x":195,"y":400,"scaleFactor":2.0,"relativeSpeed":800,"gestureSourceType":"default"});pg.wait_for_timeout(600)
        s1=pg.evaluate("visualViewport.scale")
        ck("pincement : la page s'agrandit (échelle %.2f → %.2f)"%(s0,s1),s1>=1.3,s1)
        vv=pg.evaluate("[Math.floor(visualViewport.width/2),Math.floor(visualViewport.height/2)]");cdp.send("Input.synthesizePinchGesture",{"x":vv[0],"y":vv[1],"scaleFactor":0.4,"relativeSpeed":800,"gestureSourceType":"default"});pg.wait_for_timeout(600)
        ck("pincement inverse : retour à l'échelle 1",abs(pg.evaluate("visualViewport.scale")-1)<.05,pg.evaluate("visualViewport.scale"))
        # double-tap sur un texte (zone sans bouton)
        box=pg.locator(".q h2").first.bounding_box()
        for _ in range(2):
            cdp.send("Input.dispatchTouchEvent",{"type":"touchStart","touchPoints":[{"x":box["x"]+10,"y":box["y"]+10}]});cdp.send("Input.dispatchTouchEvent",{"type":"touchEnd","touchPoints":[]});pg.wait_for_timeout(80)
        pg.wait_for_timeout(600)
        ck("double-tap : pas de zoom",abs(pg.evaluate("visualViewport.scale")-1)<.05,pg.evaluate("visualViewport.scale"))
        # champs de saisie (test de niveau : écrire)
        pg.evaluate("()=>{test();T.i=7;R.q=T.list[7];R.done=false;show()}");pg.wait_for_timeout(300)
        fs=pg.evaluate("""()=>{let txt="";for(const sh of document.styleSheets){try{for(const r of sh.cssRules){if(r.conditionText&&/touch-callout/.test(r.conditionText)&&/select/.test(r.cssText))txt+=[...r.cssRules].map(x=>x.cssText).join("")}}catch(e){}}
          if(!txt)return null;const st=document.createElement("style");st.textContent=txt;document.head.appendChild(st);
          const o=[...document.querySelectorAll('input:not([type=file]),select,textarea')].map(e=>(e.id||e.className)+':'+parseFloat(getComputedStyle(e).fontSize));st.remove();return o}""")
        ck("iOS : champs de saisie ≥ 16 px (pas de zoom automatique au focus)",fs is not None and all(float(x.split(':')[-1])>=16 for x in fs),fs)
        c.close()
        # 320 px
        c=b.new_context(locale="fr-FR",viewport={"width":320,"height":640},is_mobile=True,has_touch=True);pg=c.new_page();pg.goto(BASE+page);pg.wait_for_timeout(1200)
        ov=[]
        for nm,js in [("accueil","0"),("parcours","(S.lang='es',S.lvl=1,S.ob=1,build(),welcomeOb())"),("test","(test(),T.i=7,R.q=T.list[7],R.done=false,show())")]:
            pg.evaluate("()=>{"+js+"}");pg.wait_for_timeout(300)
            w=pg.evaluate("document.documentElement.scrollWidth");ov.append((nm,w))
        ck("320 px : pas de défilement horizontal",all(w<=321 for _,w in ov),ov)
        ck("aucune erreur JavaScript",not er,er);c.close()
    b.close()
print("\n%d/%d OK"%(sum(R),len(R)));sys.exit(0 if all(R) else 1)
