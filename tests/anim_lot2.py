# Animations, lot 2 (A2 tuiles qui volent, A3 paires qui fusionnent, A5 rangée d'accents, C2 correction lettre par lettre,
# C3 « à revoir », E1 pile de cartes) : présence, effets joués une fois, nettoyage, logique des exercices inchangée,
# mode « réduire les animations ». Usage : python3 tests/anim_lot2.py URL
import sys
from playwright.sync_api import sync_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else "http://127.0.0.1:8774/"
R=[]
def ck(n,c,i=""):R.append(bool(c));print("OK  " if c else "FAIL",n,"" if c else str(i)[:600],flush=True)
H=r"""
window.LES_=(lang)=>{S.lang=lang||'es';S.lvl=1;S.ob=0;PLC=null;build();XDIRTY=1;xens();S.sr={};S.sc={};S.cns={};S.pthAll=1;home();
  const id=pathItems().find(x=>!x.test&&pathPlan().map[x.id].nw&&pathPlan().map[x.id].ws).id;pstart(id);if(DISC)discGo();return id};
window.Q_=(ty,ok)=>{for(let i=0;i<60;i++){let q=null;try{q=mkQ(ty,0)}catch(e){q=null}if(q&&q.ty===ty&&(!ok||ok(q))){R.q=q;show();return true}}return false};
window.QCM_=()=>{for(let i=0;i<40;i++){if(R.q&&Array.isArray(R.q.o)&&R.q.o.length>1&&!R.q.void&&R.q.key&&document.querySelectorAll('.q .opt').length)return true;R.q=mkQ(['es2fr','fr2es'][i%2],0);show()}return false};
window.W_=ms=>new Promise(r=>setTimeout(r,ms||30));
0;
"""
def run(rm):
  with sync_playwright() as p:
    b=p.chromium.launch();c=b.new_context(service_workers="block",reduced_motion="reduce" if rm else "no-preference",viewport={"width":390,"height":780});pg=c.new_page()
    errs=[];pg.on("pageerror",lambda e:errs.append(str(e)))
    pg.goto(BASE+"index.html");pg.wait_for_timeout(2500);ev=pg.evaluate;ev(H);T=" (réduit)" if rm else ""
    if not rm:
      r=ev("""()=>({css:!!document.getElementById('sm-anim2'),js:!!document.getElementById('sm-anim2-js'),w:['tk','ordT','pairT','draw','fin','qOut'].filter(k=>!/[\\s\\S]/.test(String(window[k]))).length,
        tr:[tr("à revoir 🔁"),tr("Lettres accentuées")].every(Boolean)})""")
      ck("présence : styles et script du lot 2, enveloppes en place",r["css"] and r["js"] and r["w"]==0 and r["tr"],r)
    # ---------- A2 : tuiles ----------
    r=ev("""async()=>{LES_();if(!Q_('build'))return 'pas de question build';await W_(60);const q=R.q,i=q.toks.findIndex((t,k)=>!q.cur.includes(k));tk(i);
        const el=document.querySelector('.wk[data-i="'+i+'"]'),an=el.getAnimations().filter(a=>!(a instanceof CSSAnimation)&&!(a instanceof CSSTransition));
        const t=an[0]?an[0].effect.getTiming():{};const inLine=!!el.closest('#bl');await W_(700);tk(i);await W_(50);return {cur:q.cur.length,inLine,back:!el.closest('#bl'),n:an.length,d:t.duration,e:t.easing}}""")
    ck("A2"+T+" : la tuile va dans la phrase puis revient, logique inchangée"+("" if rm else ", vol de 420 ms avec rebond"),isinstance(r,dict) and r["inLine"] and r["back"] and r["cur"]==0 and (rm or (r["n"]>=1 and r["d"]==420 and "1.56" in r["e"])),r)
    r=ev("""async()=>{LES_();let oq=null;for(let k=0;k<20&&!oq;k++)oq=NX.ord.mk(1);if(!oq)return 'pas de question ord';R.q=oq;show();await W_(60);const q=R.q,j=q.sh[0];ordT(j);await W_(20);
        const mv=[...document.querySelectorAll('.q [onclick^="ordT("]')].filter(e=>e.getAnimations().some(a=>!(a instanceof CSSAnimation)&&!(a instanceof CSSTransition))).length;return {cur:q.cur.slice(),j,mv}}""")
    ck("A2"+T+" : dialogue à remettre dans l'ordre, la réplique choisie glisse à sa place"+(" (pas d'animation)" if rm else ""),isinstance(r,dict) and r["cur"]==[r["j"]] and (r["mv"]==0 if rm else r["mv"]>=1),r)
    # ---------- A3 : paires ----------
    r=ev("""async()=>{LES_();if(!Q_('pair'))return 'pas de question pair';await W_(60);const q=R.q,i=q.L[0],j=q.L[1];
        pairT('l',i);pairT('r',i);const pr=document.querySelectorAll('.smPr').length,hid=[document.getElementById('pl'+i),document.getElementById('pr'+i)].map(e=>e.style.visibility);
        await W_(520);const tick=document.querySelectorAll('.smTick').length;await W_(1200);
        const after={pr:document.querySelectorAll('.smPr').length,tick:document.querySelectorAll('.smTick').length,vis:[document.getElementById('pl'+i),document.getElementById('pr'+i)].map(e=>e.style.visibility),dn:document.getElementById('pl'+i).classList.contains('dn')};
        pairT('l',j);const k=q.Rr.find(x=>x!==j&&!q.ok.includes(x));pairT('r',k);const ko=document.querySelectorAll('.nxp .opt.ko').length,an=[...document.querySelectorAll('.nxp .opt.ko')].map(e=>getComputedStyle(e).animationName).join(',');
        await W_(600);return {ok:q.ok.slice(),err:q.err,pr,hid,tick,after,ko,an}}""")
    ck("A3"+T+" : bonne paire validée une fois"+(" sans copie animée" if rm else ", les deux mots se rejoignent puis un ✓ apparaît, tout est retiré ensuite"),isinstance(r,dict) and len(r["ok"])==1 and r["after"]["pr"]==0 and r["after"]["tick"]==0 and r["after"]["vis"]==["",""] and r["after"]["dn"] and (r["pr"]==0 if rm else (r["pr"]==2 and r["hid"]==["hidden","hidden"] and r["tick"]==1)),r)
    ck("A3"+T+" : mauvaise paire comptée une fois, les deux mots font un petit « non »",isinstance(r,dict) and r["err"]==1 and r["ko"]==2 and (rm or "smNo" in r["an"]),r)
    # ---------- A5 : accents ----------
    r=ev("""async()=>{LES_();if(!Q_('type'))return 'pas de question type';await W_(60);const kb=document.querySelector('.q #ti+.smKb'),i=document.getElementById('ti');
        const keys=kb?[...kb.querySelectorAll('button')].map(b=>b.textContent):[];i.focus();i.value='espa';i.setSelectionRange(4,4);const nb=[...kb.querySelectorAll('button')].find(b=>b.textContent==='ñ');
        nb.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,cancelable:true}));nb.click();const v1=i.value,foc=document.activeElement===i,car=i.selectionStart;i.value+='ol';
        await W_(450);const fly=document.querySelectorAll('.smFly').length;chkT();return {keys,v1,foc,car,fly,kbAfter:document.querySelectorAll('.smKb').length,done:R.done}}""")
    ck("A5"+T+" : rangée d'accents castillans sous le champ, la lettre s'insère au curseur, le champ garde le focus, rangée retirée à la validation",isinstance(r,dict) and r["keys"][:7]==["á","é","í","ó","ú","ü","ñ"] and r["v1"]=="españ" and r["foc"] and r["car"]==5 and r["fly"]==0 and r["kbAfter"]==0 and r["done"],r)
    r=ev("""async()=>{LES_('ca');if(!Q_('type'))return 'pas de question type';await W_(60);return [...document.querySelectorAll('.q .smKb button')].map(b=>b.textContent).join(' ')}""")
    ck("A5"+T+" : rangée adaptée à la langue (catalan : à è ç ·…)",isinstance(r,str) and "ç" in r and "à" in r and "ñ" not in r,r)
    # ---------- C2 : correction lettre par lettre ----------
    r=ev("""async()=>{LES_();let tries=0,res=null;
        while(tries++<25){if(!Q_('type',q=>EV.show(q.es).replace(/[¿¡?!.,;:]/g,'').length>=5&&EV.show(q.es).replace(/[¿¡?!.,;:]/g,'').length<=30))return 'pas de question type';await W_(30);
          const q=R.q,t=EV.show(q.es).replace(/[¿¡?!.,;:]/g,'').trim(),k=[...t].findIndex(c=>/[a-z]/.test(c));if(k<0)continue;
          const bad=t.slice(0,k)+(t[k]==='x'?'z':'x')+t.slice(k+1);const i=document.getElementById('ti');i.value=bad;chkT();await W_(60);
          const df=document.querySelector('#fb .smDf');if(!df)continue;const dx=df.querySelectorAll('.smDx').length;await W_(1100);
          const fin=[...df.querySelectorAll('span')].filter(s=>!s.classList.contains('smDdel')).map(s=>s.textContent).join('');
          res={t,bad,dx,ok:df.querySelectorAll('.smDok').length,fin,n:document.querySelectorAll('#fb .smDf').length};break}
        return res||'aucune correction affichée'}""")
    ck("C2"+T+" : lettre fautive signalée puis remplacée par la bonne, une seule correction",isinstance(r,dict) and r["ok"]>=1 and r["fin"].lower()==r["t"].lower() and r["n"]==1 and (rm or r["dx"]>=1),r)
    r=ev("""async()=>{LES_();if(!Q_('type'))return 'pas de question type';await W_(30);const q=R.q;document.getElementById('ti').value=EV.show((q.acc||[q.es])[0]);const g=EV.grade(EV.show((q.acc||[q.es])[0]),q);chkT();await W_(60);return {s:g.s,n:g.n||'',df:document.querySelectorAll('.smDf').length}}""")
    ck("C2"+T+" : réponse exacte, aucune correction affichée",isinstance(r,dict) and r["s"]==1 and (r["n"] or r["df"]==0),r)
    r=ev("""async()=>{LES_();if(!Q_('type'))return 'pas de question type';await W_(30);document.getElementById('ti').value='zzzzqqqq wwww';chkT();await W_(60);return document.querySelectorAll('.smDf').length}""")
    ck("C2"+T+" : réponse sans rapport, pas de correction lettre par lettre (le bandeau habituel suffit)",r==0,r)
    # ---------- C3 et E1 ----------
    r=ev("""async()=>{LES_();QCM_();await W_(30);const e=document.querySelector('#app .q');const dk0=[e.classList.contains('smDk2'),e.classList.contains('smDk1')];
        const q=R.q,bad=q.o.findIndex(x=>x!==q.g);ans(bad);fin(false,q.sol,q.key);const st=document.querySelectorAll('#app .q .smRv').length,rv=R.smRv;
        adv();await W_(40);const cl=document.querySelectorAll('.smCl').length;await W_(160);const qs=document.querySelectorAll('#app .q').length,inn=(document.querySelector('#app .q')||{classList:{contains:()=>0}}).classList.contains('smIn');
        await W_(740);const b=document.querySelector('#app .smRvN');return {dk0,st,rv,cl,qs,inn,cl2:document.querySelectorAll('.smCl').length,badge:b?(b.querySelector('.ic,svg')?'🔁':'')+b.textContent.replace(/[^0-9]/g,''):'',n:R.n,st2:document.querySelectorAll('#app .q .smRv').length,ids:document.querySelectorAll('#ti,#fb').length}}""")
    ck("C3"+T+" : erreur = un seul tampon « à revoir », compté une fois",isinstance(r,dict) and r["st"]==1 and r["rv"]==1 and r["st2"]==0,r)
    ck("C3/E1"+T+" : en passant à la suite"+(" (sans copie animée)" if rm else ", la carte s'envole vers le compteur 🔁 1 au bout de la barre, la nouvelle carte avance, la copie est retirée"),isinstance(r,dict) and r["n"]==1 and r["qs"]==1 and r["cl2"]==0 and r["ids"]<=2 and (r["cl"]==0 if rm else (r["cl"]==1 and r["inn"] and r["badge"]=="🔁1")),r)
    ck("E1"+T+" : deux cartes en attente derrière la première question",isinstance(r,dict) and r["dk0"]==[True,False],r)
    r=ev("""async()=>{LES_();QCM_();R.n=8;draw();const a=document.querySelector('#app .q').className;R.n=9;draw();const b=document.querySelector('#app .q').className;R.n=0;draw();
        const q=R.q;ans(q.o.indexOf(q.g));adv();await W_(40);const cl=document.querySelectorAll('.smCl').length;await W_(700);
        return {a1:/smDk1/.test(a)&&!/smDk2/.test(a),b0:!/smDk/.test(b),cl,cl2:document.querySelectorAll('.smCl').length,badge:document.querySelectorAll('.smRvN').length,st:document.querySelectorAll('.smRv').length}}""")
    ck("E1"+T+" : une carte derrière à l'avant-dernière question, aucune à la dernière ; bonne réponse = la carte part sur le côté, sans tampon ni compteur",isinstance(r,dict) and r["a1"] and r["b0"] and r["cl2"]==0 and r["badge"]==0 and r["st"]==0 and (r["cl"]==0 if rm else r["cl"]==1),r)
    # ---------- enchaînement rapide ----------
    r=ev("""async()=>{LES_();let dbl=0;for(let k=0;k<9;k++){QCM_();await W_(5);const n=R.n,q=R.q;ans(Math.random()<.5?q.o.indexOf(q.g):q.o.findIndex(x=>x!==q.g));adv();adv();await W_(140);if(R.n!==n+1)dbl++}
        await W_(1600);return {dbl,n:R.n,cl:document.querySelectorAll('.smCl,.smPr,.smTick,.smFly').length,q:document.querySelectorAll('.q').length,badge:(document.querySelector('.smRvN')||{textContent:''}).textContent.replace(/[^0-9]/g,''),rv:R.smRv||0,rvs:R.smRvS||0}}""")
    ck("enchaînement rapide"+T+" : une question par geste, aucune copie restante, une seule carte, compteur 🔁 juste",isinstance(r,dict) and r["dbl"]==0 and r["n"]==9 and r["cl"]==0 and r["q"]==1 and (r["rv"]==0 or rm or r["badge"]==str(r["rv"])),r)
    # ---------- test de niveau : rien du lot 2 sauf la rangée d'accents ----------
    if not rm:
      r=ev("""async()=>{home();await W_(50);try{tstart&&tstart()}catch(e){}await W_(300);const e=document.querySelector('#app .q');return e?{dk:/smDk/.test(e.className),m:R.mode}:{m:R&&R.mode}}""")
      ck("test de niveau : pas de pile de cartes",isinstance(r,dict) and (r.get("m")!="test" or not r.get("dk")),r)
    ck("aucune erreur JavaScript"+T,not errs,errs[:3])
    b.close()
run(False);run(True)
print(sum(R),"/",len(R),"OK");sys.exit(0 if all(R) else 1)
