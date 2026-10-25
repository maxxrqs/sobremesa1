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
window.__ev={a:1,s:1,sp:1};window.__srInt=null;window.__gumN=0;
const _g=navigator.mediaDevices.getUserMedia;navigator.mediaDevices.getUserMedia=async(...a)=>{window.__gumN++;return _g(...a)};
class FSR{start(){window.__tr.started++;const t=this,E=window.__ev;setTimeout(()=>{E.a&&t.onaudiostart&&t.onaudiostart();E.s&&t.onsoundstart&&t.onsoundstart();E.sp&&t.onspeechstart&&t.onspeechstart();
 if(window.__srErr){t.onerror&&t.onerror({error:window.__srErr})}
 else if(window.__srInt){t.onresult&&t.onresult({results:[Object.assign([{transcript:window.__srInt}],{isFinal:false})]})}
 else if(window.__srRes){t.onresult&&t.onresult({results:[Object.assign([{transcript:window.__srRes}],{isFinal:true})]})}
 t.onend&&t.onend()},20)}abort(){}stop(){}}
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
    ask(pg);pg.evaluate("window.__gum='NotAllowedError';navigator.permissions.query=async()=>({state:'prompt'});Object.defineProperty(document,'permissionsPolicy',{value:{allowsFeature:()=>false},configurable:true})")
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
    # 7b événements : micro non démarré / aucun son / bruit seul / non compris / résultat intermédiaire seul accepté
    pg.evaluate("Object.defineProperty(document,'permissionsPolicy',{value:undefined,configurable:true});window.__gum='ok';window.__srErr=null;navigator.permissions.query=async()=>({state:'prompt'})")
    for ev,res,frag in [({'a':0,'s':0,'sp':0},None,"n'a pas démarré"),({'a':1,'s':0,'sp':0},None,"Aucun son capté"),({'a':1,'s':1,'sp':0},None,"qu'un bruit"),({'a':1,'s':1,'sp':1},None,"pas compris")]:
        ask(pg);pg.evaluate(f"window.__ev={ev!r}".replace("'a'","a").replace("'s'","s").replace("'sp'","sp"));pg.evaluate("window.__srRes=null;window.__srInt=null")
        pg.click("button[onclick='rec()']");pg.wait_for_timeout(500)
        ck(f"fin sans résultat ({frag})",frag in fbt(pg),fbt(pg))
    ask(pg);pg.evaluate("window.__ev={a:1,s:1,sp:1};window.__srRes=null;window.__srInt='dónde está la playa'");pg.click("button[onclick='rec()']");pg.wait_for_timeout(500)
    ck("résultat intermédiaire seul (pas de final) : accepté à la fin de session",pg.evaluate("R.ok")>0,fbt(pg))
    # 7c réponses incertaines : on redemande sans valider ni pénaliser (une fois), langue maternelle toujours redemandée
    def askq(es):pg.evaluate("""(es)=>{S.lang='es';S.lvl=1;S.mute=true;build();R={mode:'t',ok:0,xp:0,hist:[],done:false};R.q={ty:'speak',es,fr:'',say:es,key:null,sol:es};draw()}""",es);pg.wait_for_timeout(300)
    pg.evaluate("window.__srInt=null;navigator.permissions.query=async()=>({state:'granted'})")
    ask(pg);pg.evaluate("window.__srRes='je ne sais pas'");pg.click("button[onclick='rec()']");pg.wait_for_timeout(500)
    ck("français entendu : pas de note, demande de répéter",not pg.evaluate("R.done") and "français" in fbt(pg) and "Réessayer" in fbt(pg),fbt(pg))
    pg.click("button[onclick='rec()']");pg.wait_for_timeout(500)
    ck("français entendu 2 fois : toujours pas de pénalité",not pg.evaluate("R.done"),fbt(pg))
    pg.evaluate("window.__srRes='dónde está la playa'");pg.click("button:has-text('Réessayer')");pg.wait_for_timeout(500)
    ck("puis bonne réponse → validée",pg.evaluate("R.ok")==1,fbt(pg))
    ask(pg);pg.evaluate("window.__srRes='dónde está'");pg.click("button[onclick='rec()']");pg.wait_for_timeout(500)
    ck("début seulement : demande de répéter",not pg.evaluate("R.done") and "début" in fbt(pg),fbt(pg))
    pg.click("button[onclick='rec()']");pg.wait_for_timeout(500)
    ck("début seulement 2e fois : noté, non validé",pg.evaluate("R.done") and pg.evaluate("R.ok")<1,fbt(pg))
    ask(pg);pg.evaluate("window.__srRes=null;window.__srInt='dónde está'");pg.click("button[onclick='rec()']");pg.wait_for_timeout(500)
    ck("résultat partiel incomplet : demande de répéter",not pg.evaluate("R.done") and "Réessayer" in fbt(pg),fbt(pg))
    pg.evaluate("window.__srInt=null")
    askq("Empiezo a las nueve.");pg.evaluate("window.__srRes='empiezo a las 9'");pg.click("button[onclick='rec()']");pg.wait_for_timeout(500)
    ck("chiffre dicté (9 = nueve) → validé",pg.evaluate("R.ok")==1,fbt(pg))
    askq("Tengo un perro.");pg.evaluate("window.__srRes='tengo un pero'");pg.click("button[onclick='rec()']");pg.wait_for_timeout(500)
    ck("perro/pero : non validé",pg.evaluate("R.done") and pg.evaluate("R.ok")<1,fbt(pg))
    pg.evaluate("window.__srRes=null")
    # 7d erreur à l'oral : passage automatique à l'exercice suivant (après la correction), pas avant
    pg.evaluate("window.__adv0=adv;window.__advN=0;adv=()=>{window.__advN++};0")
    ask(pg);pg.evaluate("window.__srRes='hola'");pg.click("button[onclick='rec()']");pg.wait_for_timeout(1500)
    ck("erreur orale : correction affichée, pas encore passé",pg.evaluate("R.done") and pg.evaluate("__advN")==0 and "Continuer" in fbt(pg),fbt(pg))
    pg.wait_for_timeout(4500)
    ck("erreur orale : passe tout seul à l'exercice suivant",pg.evaluate("__advN")==1,pg.evaluate("__advN"))
    ask(pg);pg.evaluate("window.__advN=0;window.__srRes='je ne sais pas'");pg.click("button[onclick='rec()']");pg.wait_for_timeout(5500)
    ck("« répète » (incertain) : ne passe pas tout seul",pg.evaluate("__advN")==0 and not pg.evaluate("R.done"),fbt(pg))
    pg.evaluate("adv=window.__adv0;0")
    # permission déjà accordée : pas de getUserMedia (évite de bloquer le micro avant la reconnaissance)
    ask(pg);pg.evaluate("window.__srInt=null;window.__srRes='dónde está la playa';navigator.permissions.query=async()=>({state:'granted'});window.__gumN=0");pg.click("button[onclick='rec()']");pg.wait_for_timeout(500)
    ck("permission accordée : getUserMedia non appelé, reconnaissance lancée",pg.evaluate("__gumN")==0 and pg.evaluate("R.ok")>0,pg.evaluate("__gumN"))
    pg.evaluate("window.__srRes=null")
    # 8 NotFoundError (aucun micro)
    ask(pg);pg.evaluate("navigator.permissions.query=async()=>({state:'prompt'});window.__srErr=null;window.__gum='NotFoundError'");pg.click("button[onclick='rec()']");pg.wait_for_timeout(400)
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
