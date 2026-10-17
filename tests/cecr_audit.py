# Audit CECRL : invariants de données + simulation de la génération d'exercices (Chrome headless).
# Usage : python3 tests/cecr_audit.py [http://localhost:8772/index.html]
import sys,json
from playwright.sync_api import sync_playwright
URL=sys.argv[1] if len(sys.argv)>1 else "http://localhost:8772/index.html"
R=[]
def ck(n,c,info=""):
    R.append(bool(c));print(("OK  " if c else "FAIL"),n,("" if c else info),flush=True)
SIM="""([lang,lvl,N])=>{
 S.lang=lang;S.lvl=lvl;build();XDIRTY=1;xens();
 const out={n:0,bad:[],dictWord:0,dictN:0,types:{},convBad:[],cap:{}};
 const capP=CAPW.p[lvl],capC=CAPW.c[lvl];
 const lvOf=(arr,i,v)=>{const m=arr.filter(x=>x[i]===v).map(x=>x[2]||1);return m.length?Math.min(...m):0};
 start('Mélange');
 const types=['type','dict','build','speak','cloze','listenP','readP','fr2P','listen','es2fr','fr2es','tf','conj','exM','exE','exL','listenT'];
 for(let k=0;k<N;k++){
  const ty=types[k%types.length];R.lock=0;let q;try{q=mkQ0(ty,0)}catch(e){out.bad.push(['EXC',ty,String(e)]);continue}
  out.n++;out.types[q.ty]=(out.types[q.ty]||0)+1;
  const nw=s=>String(s).trim().split(/\\s+/).length;
  
  if((q.ty==='type'||q.ty==='dict')&&nw(q.es)>capP)out.bad.push(['len-p',q.ty,q.es]);
  if((q.ty==='build'||q.ty==='speak'||q.ty==='listenP'||q.ty==='readP'||q.ty==='fr2P')&&nw(q.es)>capC)out.bad.push(['len-c',q.ty,q.es]);
  if(q.ty==='listenP'||q.ty==='readP'){q.o.forEach(o=>{const L=lvOf(PH,1,o);if(L>lvl)out.bad.push(['dist-lvl',q.ty,o,L])})}
  if(q.ty==='fr2P'){q.o.forEach(o=>{const L=lvOf(PH,0,o);if(L>lvl)out.bad.push(['dist-lvl',q.ty,o,L])})}
  if(q.ty==='cloze'){const f=PH.find(x=>x[0]===q.say);if(f&&(f[2]||1)>lvl)out.bad.push(['phrase-lvl',q.ty,q.say])}
  if(q.ty==='es2fr'||q.ty==='fr2es'||q.ty==='listen'||q.ty==='tf'){const L=lvOf(ALL,0,q.say);if(L>lvl&&L>0)out.bad.push(['word-lvl',q.ty,q.say,L])}
  if(q.ty==='es2fr'||q.ty==='fr2es'){q.o.forEach(o=>{const L=lvOf(ALL,q.ty==='es2fr'?1:0,o);if(L>lvl&&L>0)out.bad.push(['dist-lvl',q.ty,o,L])})}
  if(q.ty==='listenT'){const tx=TX.filter(x=>x[0]===q.say);if(!tx.length||Math.min(...tx.map(x=>x[2]))>lvl)out.bad.push(['text-lvl',q.say.slice(0,30)]);if(!q.o.includes(q.g)||q.o.length!==4||!q.sa.length)out.bad.push(['listenT-shape',q.say.slice(0,30)])}
  if(q.ty==='conj'){const v=q.verb,L=vLvl(lang,v);if(L>lvl)out.convBad.push(['verb-lvl',v,L]);
    const lad=tLad(lang);if(lad){const t=vlist(lang,VD[lang][v]).find(t=>gl(t.fr)===q.tn||t.fr===q.tn);if(t&&!lad.includes(t.k))out.convBad.push(['tense',v,t.k])}}
 }
 
 for(let k=0;k<240;k++){R.lock=0;const q=mkQ0('dict',0);out.dictN++;if(ALL.some(x=>x[0]===q.es))out.dictWord++}
 return out}"""
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_context(locale="fr-FR").new_page();err=[]
    pg.on("pageerror",lambda e:err.append(str(e)))
    pg.goto(URL);pg.wait_for_timeout(2500)
    # ---- A. invariants de données (toutes langues)
    d=pg.evaluate("""()=>{const o={idio:[],conn:[],rw:[],verbs:[],xe:0,ph1:0,ph2:0,xcSample:[]};
      for(const [lg,txt] of Object.entries(JSON.parse(JSON.stringify(XE)))){for(const r of txt.split("\\n")){const c=r.split("|");if(c.length!==9||c[0]!=="E")continue;o.xe++;const L=+c[8];
        if((c[1]==="Expressions idiomatiques"||c[1]==="Proverbes")&&L<3)o.idio.push([lg,c[2],L]);
        if(c[1].startsWith("Connecteurs")&&c[7]==="formel"&&L<3)o.conn.push([lg,c[2],L]);
        if(L<=2&&c[5].split(/\\s+/).length>14)o.idio.push([lg,c[2],'long',L])}}
      const need={'el ayuntamiento':2,'mil':2,'el primero':2,'cuatrocientos':2};
      S.lang='es';build();ALL.forEach(w=>{if(need[w[0]]!==undefined&&(w[2]||1)!==need[w[0]])o.rw.push(w[0])});
      REF.filter(z=>z.c==='Verbes'&&['reír','llorar','soñar','acordarse','morir','nacer','parecer','conducir','guardar','creer'].includes(z.t[0])&&z.l<2).forEach(z=>o.verbs.push(z.t[0]));
      o.ph1=Math.max(...PH.filter(x=>(x[2]||1)===1).map(x=>x[0].trim().split(/\\s+/).length));
      return o}""")
    ck("XE (5 langues, %d lignes) : aucun idiome/proverbe sous B1, aucun exemple long sous B1"%d['xe'],not d['idio'],d['idio'][:5])
    xq=pg.evaluate("()=>XC.gl.split('\\n').map(r=>r.split('|')).filter(c=>c.length===9&&c[0]==='Q'&&c[1]==='Infinitif personnel'&&+c[8]<3).length")
    ck("XC gl : infinitif personnel conjugué ≥ B1",xq==0,xq)
    ck("XE : connecteurs formels ≥ B1",not d['conn'],d['conn'][:5])
    ck("RW : mots reclassés (ayuntamiento, mil, el primero, cuatrocientos)",not d['rw'],d['rw'])
    ck("REF : verbes peu fréquents ≥ A2",not d['verbs'],d['verbs'])
    ck("RP niveau A1 : phrases ≤ 6 mots (max=%d)"%d['ph1'],d['ph1']<=6,d['ph1'])
    lad=pg.evaluate("()=>{S.lang='es';const r={};for(const v of [1,2,3,4,5]){S.lvl=v;r[v]=tLad('es')}return r}")
    ck("échelle des temps es : A1 présent seul, A2 +passé/imparfait/futur, B1 +conditionnel/subj., tout dès C1",lad['1']==['pres'] and 'pret' in lad['2'] and 'cond' not in lad['2'] and 'cond' in lad['3'] and 'sra' not in lad['3'] and lad['5'] is None,lad)
    # ---- B. simulation par langue et par niveau
    for lang in ["es","va","ca","gl","eu"]:
        for lvl in [1,2,3,4,5]:
            o=pg.evaluate(SIM,[lang,lvl,480])
            ck(f"{lang} A{lvl if lvl<4 else ''}{'' if lvl<4 else ('B1' if lvl==3 else 'B2' if lvl==4 else 'C1')} niv.{lvl} : {o['n']} questions, longueurs / pools / niveaux de mots",not o['bad'],o['bad'][:4])
            ck(f"{lang} niv.{lvl} : conjugaison (verbes et temps du niveau)",not o['convBad'],o['convBad'][:4])
            if lvl==1:
                ck(f"{lang} niv.1 : dictée mot-d'abord ≥ 45 % (obs. {o['dictWord']}/{o['dictN']})",o['dictWord']/o['dictN']>=.45)
            if lvl>=4:
                ck(f"{lang} niv.{lvl} : dictée = phrases (mots isolés {o['dictWord']}/{o['dictN']})",o['dictWord']<=o['dictN']*.1)
    # ---- C. écoute de texte continu : jamais en A1, présente dès A2 en compréhension orale, texte caché avant la réponse
    r=pg.evaluate("""()=>{S.lang='es';build();const o={};for(const v of [1,2,3]){S.lvl=v;start('CO');R.hist=[];const c={};for(let i=0;i<400;i++){const t=pickType();c[t]=(c[t]||0)+1}o[v]=c.listenT||0}
      S.lvl=3;start('CO');R.q=mkQ0('listenT',0);R.done=false;draw();const h=document.querySelector('.q').innerText;const hidden=!h.includes(R.q.say.slice(0,25));const n=document.querySelectorAll('.opt').length;
      const spk=document.querySelector('.spk')!=null;const okAns=R.q.o.indexOf(R.q.g);ans(okAns);const fb=document.querySelector('#fb').innerText;return{o,hidden,n,spk,fbOk:fb.includes(R.q.say.slice(0,15)),cls:document.querySelector('#fb .fb').className}}""")
    pl=pg.evaluate("()=>{const o=[];for(const l of Object.keys(PTB))PTB[l].forEach(x=>{if(x[1]==='l'&&x[0]<=3&&/hubiera sabido|haguera sabut|hagués sabut|soubese|jakin izan banu/i.test(x[2]))o.push([l,x[2]])});return o}")
    ck("test de niveau : plus de condicional passé (B2) en écoute de niveau ≤ B1",not pl,pl)
    ck("listenT : 0 en A1, présent en A2 et B1 (tirages %s)"%r['o'],r['o']['1']==0 and r['o']['2']>40 and r['o']['3']>40,r['o'])
    ck("listenT : texte caché, 4 réponses, bouton audio, bonne réponse reconnue, transcription affichée après",r['hidden'] and r['n']==4 and r['spk'] and 'ok' in r['cls'].split() and r['fbOk'],r)
    ck("aucune erreur JS",not err,err[:3])
    b.close()
print(f"\n{sum(R)}/{len(R)} contrôles OK");sys.exit(0 if all(R) else 1)
