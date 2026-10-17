# Astuces linguistiques : données, accessibilité des déclencheurs, traductions, comportement (Chrome headless).
import sys,json,urllib.request
from playwright.sync_api import sync_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else "http://localhost:8772/"
R=[]
def ck(n,c,info=""):
    R.append(bool(c));print(("OK  " if c else "FAIL"),n,("" if c else info),flush=True)
with sync_playwright() as p:
    b=p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required']);pg=b.new_context(locale="fr-FR").new_page();err=[]
    pg.on("pageerror",lambda e:err.append(str(e)))
    pg.goto(BASE+"index.html");pg.wait_for_timeout(2500)
    d=pg.evaluate("""()=>{const o={n:0,lv:[],dup:[],unreach:[],long:[],noFr:[]};
      for(const l of Object.keys(TIPS)){S.lang=l;build();const seen=new Set();
        const heads=[...ALL.map(w=>tpN(w[0])),...PH.map(x=>tpN(x[0]))];
        for(const t of TIPS[l]){o.n++;if(!(t[1]>=1&&t[1]<=5))o.lv.push([l,t[0]]);const g=tpN(t[0]);if(seen.has(g))o.dup.push([l,t[0]]);seen.add(g);
          if(t[2].length>260||t[2].length<20)o.long.push([l,t[0],t[2].length]);
          const ok=heads.some(h=>h===g||(g.includes(' ')&&(' '+h+' ').includes(' '+g+' ')));if(!ok)o.unreach.push([l,t[0]]);
          const w=ALL.find(w=>tpN(w[0])===g)||PH.find(x=>tpN(x[0])===g);const lvItem=w?(w[2]||1):null;if(lvItem&&lvItem>t[1])o.lv.push([l,t[0],'tip<item',t[1],lvItem])}}
      return o}""")
    ck(f"{d['n']} astuces : niveaux valides, sans doublon, longueur raisonnable",not d['lv'] and not d['dup'] and not d['long'],d)
    ck("chaque déclencheur correspond à un mot ou une phrase réellement présents dans la langue",not d['unreach'],d['unreach'])
    miss={}
    allt=pg.evaluate("()=>Object.entries(TIPS).flatMap(([l,a])=>a.map(t=>t[2]))")
    for ui in ["en","it","de","pt"]:
        tr=json.load(urllib.request.urlopen(BASE+f"tr/{ui}.json"))
        miss[ui]=[t[:40] for t in allt if not tr.get(t) or tr.get(t)==t]+([] if tr.get("Bon à savoir") not in (None,"Bon à savoir") else ["label"])
    ck("traductions en/it/de/pt présentes pour toutes les astuces",not any(miss.values()),miss)
    # ---- comportement
    SETUP="""([lang,lvl])=>{S.lang=lang;S.lvl=lvl;build();S.tp={};start('Mélange')}"""
    def ask(js):return pg.evaluate(js)
    pg.evaluate(SETUP,["es",1])
    r=ask("""()=>{R.q={ty:'type',fr:'s\\'il vous plaît',es:'por favor',say:'por favor',key:'por favor',sol:'por favor = s\\'il vous plaît'};R.done=false;R.n=0;R.ok=0;R.xp=0;R.tc=0;R.tn=0;R.tl=0;S.tp={};
      const orig=Math.random;Math.random=()=>0.1;draw();document.getElementById('ti').value='por favor';chkT();Math.Random=0;Math.random=orig;
      return{ok:R.ok,xp:R.xp,tip:(document.querySelector('.fbm .tip')||{}).innerText||'',btn:!!document.querySelector('#fb .btn'),cls:document.querySelector('#fb .fb').className}}""")
    ck("bonne réponse : 100 % conservé, astuce 'porfa' affichée, bouton Continuer présent",r['ok']==1 and r['xp']==10 and 'porfa' in r['tip'] and r['btn'] and 'ok' in r['cls'].split(),r)
    r=ask("""()=>{R.q={ty:'type',fr:'s\\'il vous plaît',es:'por favor',say:'por favor',key:'por favor',sol:'x'};R.done=false;R.ok=0;R.xp=0;R.tc=5;R.tn=0;R.tl=0;S.tp={};
      const orig=Math.random;Math.random=()=>0.1;draw();document.getElementById('ti').value='zzzz';chkT();Math.random=orig;
      return{ok:R.ok,tip:!!document.querySelector('.fbm .tip'),cls:document.querySelector('#fb .fb').className}}""")
    ck("réponse fausse : toujours 0 point (l'astuce n'y change rien)",r['ok']==0 and 'ko' in r['cls'].split(),r)
    r=ask("""()=>{S.lvl=1;R.q={ty:'type',fr:'x',es:'la sobremesa',say:'la sobremesa',key:'la sobremesa',sol:'x'};R.done=false;R.tc=5;R.tn=0;R.tl=0;S.tp={};
      const orig=Math.random;Math.random=()=>0.1;draw();document.getElementById('ti').value='la sobremesa';chkT();Math.random=orig;return !!document.querySelector('.fbm .tip')}""")
    ck("astuce de niveau B1 non affichée à un niveau A1",r is False,r)
    r=ask("""()=>{S.lvl=3;S.tp={};R.q={ty:'type',fr:'x',es:'la sobremesa',say:'la sobremesa',key:'la sobremesa',sol:'x'};const a=tpFind(R.q);S.lvl=1;const b=tpFind(R.q);return[!!a,!!b]}""")
    ck("tpFind respecte le niveau (B1 oui, A1 non)",r==[True,False],r)
    # série de 10 questions déclencheuses, 200 séries : plafond, espacement, non-répétition
    r=ask("""()=>{S.lang='es';S.lvl=3;build();const keys=TIPS.es.filter(t=>t[1]<=3).map(t=>t[0]);let max=0,gapBad=0,tot=0,rep=0;const orig=Math.random;
      for(let s=0;s<200;s++){start('Mélange');S.tp={};R.tc=0;let last=-9,n=0,seen=new Set();
        for(let i=0;i<10;i++){const k=keys[(i+s)%keys.length];const q={ty:'type',key:k,es:k,say:k};R.q=q;const t=tpGet(q);if(t){n++;tot++;if(R.tc-last<3)gapBad++;last=R.tc;if(seen.has(t[0]))rep++;seen.add(t[0])}}
        max=Math.max(max,n)}
      return{max,gapBad,tot,rep}}""")
    ck(f"200 séries : ≤ 2 astuces par série, espacées d'au moins 3 questions, aucune répétition (max={r['max']}, total={r['tot']})",r['max']<=2 and r['gapBad']==0 and r['rep']==0 and r['tot']>100,r)
    r=ask("""()=>{S.lang='es';S.lvl=3;build();start('Mélange');S.tp={};let c=0;const keys=TIPS.es.map(t=>t[0]);
      for(let s=0;s<300;s++){R.tc=0;R.tn=0;R.tl=0;const q={ty:'type',key:keys[s%keys.length],es:keys[s%keys.length]};if(tpGet(q))c++}return{c,seen:Object.keys(S.tp).length}}""")
    ck("une astuce déjà vue n'est plus jamais reproposée",r['c']==r['seen'] and r['c']<=len(allt),r)
    # affichage traduit
    r=ask("""async()=>{await trLoad('en');UI='en';S.lang='es';S.lvl=1;build();start('Mélange');S.tp={};R.tc=5;R.tn=0;R.tl=0;R.q={ty:'type',fr:'x',es:'por favor',say:'por favor',key:'por favor',sol:'x'};R.done=false;
      const orig=Math.random;Math.random=()=>0.1;draw();document.getElementById('ti').value='por favor';chkT();Math.random=orig;return (document.querySelector('.fbm .tip')||{}).innerText||''}""")
    ck("l'astuce s'affiche traduite quand l'interface est en anglais",'Good to know' in r and 'informal' in r,r)
    ck("aucune erreur JS",not err,err[:3])
    b.close()
print(f"\n{sum(R)}/{len(R)} contrôles OK");sys.exit(0 if all(R) else 1)
