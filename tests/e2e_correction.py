import json,sys
from playwright.sync_api import sync_playwright
R=[]
def ck(n,c,info=""):
    R.append((n,bool(c)));print(("OK  " if c else "FAIL"),n,info if not c else "",flush=True)
with sync_playwright() as p:
    b=p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required']);ctx=b.new_context(locale="fr-FR");pg=ctx.new_page();err=[]
    pg.on("pageerror",lambda e:err.append(str(e)))
    pg.goto("http://localhost:8772/index.html");pg.wait_for_timeout(2500)
    pg.evaluate("()=>{S.lvl=1;try{save()}catch(e){}}")
    # --- 1 : réponse « presque » dans une leçon
    pg.evaluate("()=>{start('Mélange');R.q={ty:'type',fr:'porte',es:'puerta',say:'puerta',key:'puerta',sol:'puerta = porte',acc:['puerta']};R.done=false;R.n=0;R.ok=0;R.xp=0;S.sc['puerta']=2;draw()}")
    pg.fill("#ti","puertas");pg.click("#chk");pg.wait_for_timeout(300)
    st=pg.evaluate("()=>({ok:R.ok,xp:R.xp,sc:S.sc['puerta'],cls:document.querySelector('#fb .fb').className,txt:document.querySelector('#fb').innerText,btn:!!document.querySelector('#fb .btn')})")
    ck("presque: R.ok=0.5, XP=5",st['ok']==.5 and st['xp']==5,st)
    ck("presque: boîte 'pt' + message pluriel + bouton Continuer",'pt' in st['cls'] and 'pluriel de' in st['txt'] and st['btn'],st)
    ck("presque: niveau du mot inchangé",st['sc']==2,st)
    # --- 2 : accent manquant => 100 %
    pg.evaluate("()=>{adv()}");pg.wait_for_timeout(500)
    pg.evaluate("()=>{R.q={ty:'type',fr:'réunion',es:'reunión',say:'reunión',key:'reunión',sol:'reunión = réunion',acc:['reunión']};R.done=false;draw()}")
    pg.fill("#ti","reunion");pg.click("#chk");pg.wait_for_timeout(300)
    st=pg.evaluate("()=>({ok:R.ok,xp:R.xp,cls:document.querySelector('#fb .fb').className,txt:document.querySelector('#fb').innerText})")
    ck("accent manquant: 100 % (+10 XP) avec rappel",st['ok']==1.5 and st['xp']==15 and 'ok' in st['cls'].split() and 'écrit' in st['txt'],st)
    # --- 3 : faux
    pg.wait_for_timeout(3200);pg.evaluate("()=>{R.q={ty:'type',fr:'chien',es:'perro',say:'perro',key:'perro',sol:'perro = chien',acc:['perro']};R.done=false;draw()}")
    pg.fill("#ti","gato");pg.click("#chk");pg.wait_for_timeout(300)
    st=pg.evaluate("()=>({ok:R.ok,xp:R.xp,cls:document.querySelector('#fb .fb').className,mi:(S.mi||{}).perro})")
    ck("réponse fausse: 0 point, boîte ko",st['ok']==1.5 and 'ko' in st['cls'] and st['mi'] and st['mi']['n']==1,st)
    # --- 4 : parcours complet de 10 questions
    def run(pattern,pid_idx):
        pg.evaluate("(i)=>{const pid=pathPlan().units[0].steps[i].id;window.__pid=pid;S.pth&&delete S.pth[pthK(pid)];start('Mélange',null,pid)}",pid_idx)
        for kind in pattern:
            pg.wait_for_timeout(450)
            ans={'F':'reunion','H':'puertas','W':'zzzz'}[kind]
            es,key={'F':('reunión','reunión'),'H':('puerta','puerta'),'W':('perro','perro')}[kind]
            pg.evaluate("([es,key])=>{R.q={ty:'type',fr:'x',es,say:es,key,sol:es,acc:[es]};R.done=false;draw()}",[es,key])
            pg.fill("#ti",ans);pg.click("#chk");pg.wait_for_timeout(120)
            pg.evaluate("()=>{adv()}")
        pg.wait_for_timeout(1800)
        return pg.evaluate("()=>({ok:R.ok,xp:R.xp,pth:(S.pth||{})[pthK(window.__pid)]||0,txt:document.querySelector('.end')?document.querySelector('.end').innerText:'',big:(document.querySelector('.big')||{}).innerText})")
    r=run("FFFFHHHHWW",0)
    ck("parcours 4F+4H+2W = 6/10 -> étape validée",r['ok']==6 and r['pth']==6 and 'validée' in r['txt'] and r['big'].startswith('6/10'),r)
    ck("XP du parcours = 4*10+4*5",r['xp']==60,r)
    r=run("FFFHHHHHWW",1)
    ck("parcours 3F+5H+2W = 5,5/10 -> étape NON validée",r['ok']==5.5 and r['pth']==0 and r['big'].replace('\n','').startswith('5,5/10'),r)
    r=run("FFFFFFFFFF",2)
    ck("parcours parfait: 10/10 + bonus série parfaite",r['ok']==10 and 'série parfaite' in r['txt'] and r['xp']==100,r)
    # --- 5 : dictée et QCM
    pg.evaluate("()=>{start('Mélange');R.q={ty:'dict',fr:'',es:'adiós',say:'adiós',key:'adiós',sol:'adiós',acc:['adiós']};R.done=false;R.ok=0;R.xp=0;draw()}")
    pg.fill("#ti","chao");pg.click("#chk");pg.wait_for_timeout(200)
    ck("dictée: synonyme refusé (c'est l'audio qui fait foi)",pg.evaluate("()=>R.ok")==0)
    pg.evaluate("()=>{R.q={ty:'dict',fr:'',es:'adiós',say:'adiós',key:'adiós',sol:'adiós',acc:['adiós']};R.done=false;draw()}")
    pg.fill("#ti","adios");pg.click("#chk");pg.wait_for_timeout(200)
    ck("dictée: accent manquant accepté",pg.evaluate("()=>R.ok")==1)
    pg.evaluate("()=>{start('Mélange');R.q=mkQ('es2fr',0);R.done=false;R.ok=0;R.xp=0;draw()}")
    pg.evaluate("()=>{const q=R.q;ans(q.o.indexOf(q.g))}");pg.wait_for_timeout(200)
    ck("QCM: bonne réponse = 1 point entier, +10 XP",pg.evaluate("()=>[R.ok,R.xp]")==[1,10])
    pg.evaluate("()=>{start('Mélange');R.q=mkQ('es2fr',0);R.done=false;R.ok=0;R.xp=0;draw()}")
    pg.evaluate("()=>{const q=R.q;ans(q.o.findIndex(x=>x!==q.g))}");pg.wait_for_timeout(200)
    ck("QCM: mauvaise réponse = 0",pg.evaluate("()=>[R.ok,R.xp]")==[0,0])
    pg.evaluate("()=>{start('Mélange');R.q={ty:'build',es:'Me llamo Max',fr:'x',say:'Me llamo Max',toks:['Me','llamo','Max'],cur:[0,1,2],sol:'x'};R.done=false;R.ok=0;R.xp=0;draw()}")
    pg.evaluate("()=>chk()");pg.wait_for_timeout(200)
    ck("ordre des mots: logique inchangée (1 point)",pg.evaluate("()=>R.ok")==1)
    # --- 6 : mode test de niveau (score partiel pondéré)
    t=pg.evaluate("""()=>{const a=window.adv;window.adv=()=>{};T={p:0,m:0,k:{},i:0,l:1,list:[]};R={mode:'test',q:{ty:'type',wt:2,es:'puerta'},done:false,ok:0,xp:0};fin(.5,'x',null);const o=[T.p,T.m,T.k.ee.c,T.k.ee.n];R.done=false;fin(0,'x',null);const o2=[T.p,T.m];window.adv=a;return [o,o2]}""")
    ck("test de niveau: crédit partiel pondéré (0,5 × poids 2 = 1 point)",t[0]==[1,2,.5,1] and t[1]==[1,4],t)
    # --- 7 : traductions du feedback
    en=pg.evaluate("""async()=>{await trLoad('en');UI='en';const r=EV.grade('puertas',{ty:'type',es:'puerta',acc:['puerta']});UI='fr';return r.m}""")
    ck("feedback traduit (anglais)",'plural of' in en,en)
    for l,mot in (('it','plurale'),('de','Plural'),('pt','plural')):
        m=pg.evaluate("""async(l)=>{await trLoad(l);UI=l;const r=EV.grade('puertas',{ty:'type',es:'puerta',acc:['puerta']});UI='fr';return r.m}""",l)
        ck("feedback traduit ("+l+")",mot in m,m)
    # --- 8 : autres langues, vraies données
    for lang,ans,exp in (('ca','adeu','adéu'),('gl','adeus','adeus'),('eu','AGUR','agur'),('va','adeu','adéu')):
        r=pg.evaluate("""([lang,ans,exp])=>{S.lang=lang;if(typeof setLang==='function'){}return null}""",[lang,ans,exp])
    ck("aucune erreur JavaScript",not err,err)
    b.close()
bad=[n for n,c in R if not c]
print(len(R)-len(bad),"/",len(R),"OK");sys.exit(1 if bad else 0)
