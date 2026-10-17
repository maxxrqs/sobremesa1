# Micro : getUserMedia / SpeechRecognition, cas accordé, refusé, politique du cadre, API absente, erreurs réseau, cycle de vie des pistes.
import sys
from playwright.sync_api import sync_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else "http://localhost:8772/"
R=[]
def ck(n,c,i=""):
    R.append(bool(c));print("OK  " if c else "FAIL",n,"" if c else str(i)[:400],flush=True)
# faux getUserMedia / SpeechRecognition contrôlables
INIT="""
window.__tr={started:0,stopped:0};window.__srErr=null;window.__srRes=null;window.__gum='ok';
navigator.mediaDevices.getUserMedia=async()=>{if(window.__gum!=='ok'){const e=new Error('x');e.name=window.__gum;throw e}
 return {getTracks:()=>[{stop(){window.__tr.stopped++}}]}};
window.__sr=1;
class FSR{constructor(){}start(){window.__tr.started++;setTimeout(()=>{if(window.__srErr){this.onerror&&this.onerror({error:window.__srErr});this.onend&&this.onend()}
 else if(window.__srRes){this.onresult&&this.onresult({results:[[{transcript:window.__srRes}]]});this.onend&&this.onend()}else{this.onend&&this.onend()}},20)}abort(){}stop(){}}
window.SpeechRecognition=FSR;window.webkitSpeechRecognition=FSR;
"""
def setup(b,init=INIT,**kw):
    c=b.new_context(locale="fr-FR",**kw);pg=c.new_page();errs=[];pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.add_init_script(init);pg.goto(BASE+"index.html");pg.wait_for_timeout(2000);return c,pg,errs
def ask(pg):
    pg.evaluate("""()=>{S.lang='es';S.lvl=1;S.mute=true;build();R={mode:'t',ok:0,xp:0,hist:[],done:false};R.q={ty:'speak',es:'¿Dónde está la playa?',fr:'Où est la plage ?',say:'¿Dónde está la playa?',key:null,sol:'¿Dónde está la playa?'};draw()}""");pg.wait_for_timeout(300)
def fbt(pg):return pg.evaluate("document.getElementById('fb')?document.getElementById('fb').innerText:''")
with sync_playwright() as p:
    b=p.chromium.launch()
    c,pg,er=setup(b);ask(pg)
    ck("bouton Parler présent",pg.query_selector("button[onclick='rec()']"))
    # 1 accordé + reconnaissance correcte
    pg.evaluate("window.__srRes='dónde está la playa'");pg.click("button[onclick='rec()']");pg.wait_for_timeout(500)
    ck("accordé : reconnaissance → bonne réponse",pg.evaluate("R.ok")>0 and "reconnu" in fbt(pg),fbt(pg))
    ck("pistes libérées après getUserMedia",pg.evaluate("__tr.stopped")==pg.evaluate("1"),pg.evaluate("__tr"))
    # 2 mauvaise phrase
    ask(pg);pg.evaluate("window.__srRes='hola'");pg.click("button[onclick='rec()']");pg.wait_for_timeout(500)
    ck("accordé : mauvaise phrase → refusée",pg.evaluate("R.ok")==0 and pg.evaluate("R.done"),fbt(pg))
    # 3 refus utilisateur (NotAllowedError), permissions API 'denied'
    ask(pg);pg.evaluate("window.__gum='NotAllowedError';navigator.permissions.query=async()=>({state:'denied'})");pg.click("button[onclick='rec()']");pg.wait_for_timeout(500)
    t=fbt(pg);ck("refus enregistré : instructions cadenas/réglages",("cadenas" in t) and "Réessayer" in t and "Écrire à la place" in t,t)
    ck("refus : SpeechRecognition pas démarré",pg.evaluate("__tr.started")==2,pg.evaluate("__tr"))
    # 4 fenêtre fermée sans répondre ('prompt') → réessai possible, puis accordé
    ask(pg);pg.evaluate("navigator.permissions.query=async()=>({state:'prompt'})");pg.click("button[onclick='rec()']");pg.wait_for_timeout(400)
    t=fbt(pg);ck("prompt ignoré : message + Réessayer",("Autorisation du micro" in t) and "Réessayer" in t,t)
    pg.evaluate("window.__gum='ok';window.__srRes='dónde está la playa'");pg.click("button:has-text('Réessayer')");pg.wait_for_timeout(500)
    ck("Réessayer après autorisation → fonctionne",pg.evaluate("R.ok")>0,fbt(pg))
    # 5 politique de permissions (iframe) : pas de Réessayer inutile
    ask(pg);pg.evaluate("window.__gum='NotAllowedError';navigator.permissions.query=async()=>({state:'granted'});Object.defineProperty(document,'permissionsPolicy',{value:{allowsFeature:()=>false},configurable:true})")
    pg.click("button[onclick='rec()']");pg.wait_for_timeout(400);t=fbt(pg)
    ck("cadre sans droit micro : message dédié, sans Réessayer",("fenêtre intégrée" in t) and "Réessayer" not in t and "Écrire à la place" in t,t)
    # 6 Écrire à la place fonctionne
    pg.click("button:has-text('Écrire à la place')");pg.wait_for_timeout(300)
    ck("secours « Écrire à la place » affiche un champ de saisie",pg.query_selector("input[type=text],input:not([type]),textarea"),pg.evaluate("document.body.innerText.slice(0,200)"))
    # 7 erreurs de reconnaissance : réseau, service, audio
    for code,frag in [("network","connexion internet"),("service-not-allowed","désactivée"),("audio-capture","Aucun micro"),("not-allowed","Autorisation du micro")]:
        pg.evaluate("Object.defineProperty(document,'permissionsPolicy',{value:undefined,configurable:true});window.__gum='ok';navigator.permissions.query=async()=>({state:'prompt'})")
        ask(pg);pg.evaluate(f"window.__srRes=null;window.__srErr='{code}'");pg.click("button[onclick='rec()']");pg.wait_for_timeout(500)
        ck(f"erreur SR {code}",frag in fbt(pg),fbt(pg))
    # 8 NotFoundError (aucun micro)
    ask(pg);pg.evaluate("window.__srErr=null;window.__gum='NotFoundError'");pg.click("button[onclick='rec()']");pg.wait_for_timeout(400)
    ck("aucun micro détecté",("Aucun micro" in fbt(pg)),fbt(pg))
    ck("aucune erreur JavaScript",not er,er);c.close()
    # 9 API absentes : pas de bouton oral (SR absente) / mediaDevices absent
    c,pg,er=setup(b,"delete window.SpeechRecognition;delete window.webkitSpeechRecognition;")
    ck("SpeechRecognition absente : l'exercice oral n'est pas proposé",pg.evaluate("typeof SR==='undefined'||!SR"))
    c.close()
    c,pg,er=setup(b,INIT+"Object.defineProperty(navigator,'mediaDevices',{value:undefined,configurable:true});")
    ask(pg);pg.click("button[onclick='rec()']");pg.wait_for_timeout(400)
    ck("mediaDevices absent : message clair + secours",("indisponible" in fbt(pg)) and "Écrire à la place" in fbt(pg),fbt(pg));c.close()
    b.close()
print(sum(R),"/",len(R),"OK");sys.exit(0 if all(R) else 1)
