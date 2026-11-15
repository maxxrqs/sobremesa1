# Anomalie n°8 de l'audit du 7 novembre : affichage mobile des exercices (360 × 640 et autres formats).
# Pour chaque type d'exercice, sur castellano.html et index.html :
#  - aucun débordement horizontal (page et éléments) ;
#  - avant réponse : toutes les commandes à l'écran sans défilement (un texte long défile dans son propre encadré) ;
#    exception tolérée et mesurée : lecture C1 avec question et options longues (≤ 140 px de défilement vertical, commandes atteignables) ;
#  - après réponse : le retour et « Continuer » sont visibles (après le défilement doux automatique) ;
#  - mesures prises une fois l'animation d'entrée de la carte terminée (elle grossit brièvement la carte) ;
#  - cibles tactiles ≥ 44 px, texte des options ≥ 15 px, textes longs repliés à la ligne.
# Usage : python3 tests/mobile_n8.py [URL]
import sys,json
from playwright.sync_api import sync_playwright
URL=sys.argv[1] if len(sys.argv)>1 else "http://127.0.0.1:8772/"
res=[]
def ck(n,ok,d=""):res.append(bool(ok));print(("OK   " if ok else "FAIL ")+n+("" if ok else f"  {str(d)[:500]}"),flush=True)
TYS=["es2fr","fr2es","listen","type","cloze","listenP","dict","tf","rep","speakF","speakC","pair","err","dlg","ord","tfL","sep","pic","gen","ctxC","ctxP","listenT","read","build","speak","odd","readP","fr2P","speakQ","replyQ","exL","conj","conjT","exc","excV","excT","exM","exE"]
MK="""([ty,L,lv,U])=>{UI=U;S.lang=L;S.lvl=lv;S.mute=true;build();xens();R={mode:'lesson',t:'Mélange',n:3,ok:2,xp:20,hist:[],tot:10};let q=null;
 for(let i=0;i<40&&(!q||q.ty!==ty);i++){try{q=mkQ0(ty,lv>2&&['read','listenT','readP','listenP'].includes(ty)?lv:0)}catch(e){q=null}}if(!q||q.ty!==ty)return null;R.q=q;show();scrollTo(0,0);return true}"""
ME="""async()=>{const _q=document.querySelector('.q');if(_q)await Promise.all(_q.getAnimations({subtree:true}).filter(a=>a.effect&&a.effect.getTiming().iterations!==Infinity).map(a=>a.finished.catch(()=>0)));const iw=innerWidth,ih=innerHeight,de=document.documentElement,vis=e=>{const s=getComputedStyle(e);return s.display!=='none'&&s.visibility!=='hidden'&&e.getClientRects().length};
 const wide=[...document.querySelectorAll('#app *')].filter(e=>{if(!vis(e))return false;const r=e.getBoundingClientRect();return r.width>0&&(r.right>iw+1||r.left<-1)}).map(e=>e.className||e.tagName);
 const sc=[...document.querySelectorAll('#app *')].filter(e=>vis(e)&&/(auto|scroll)/.test(getComputedStyle(e).overflowY)&&e.scrollHeight>e.clientHeight+2);
 const inS=e=>sc.some(s=>s!==e&&s.contains(e));
 const ctl=[...document.querySelectorAll('.q button,.q input,.q textarea,.q select')].filter(e=>vis(e)&&!inS(e));
 const lowest=Math.round(Math.max(0,...ctl.map(e=>e.getBoundingClientRect().bottom)));
 const small=ctl.filter(e=>{const r=e.getBoundingClientRect();return (e.matches('.opt,.btn,input,textarea'))&&r.height<43.5}).map(e=>e.className+':'+Math.round(e.getBoundingClientRect().height));
 const ofs=Math.min(99,...[...document.querySelectorAll('.q .opt')].filter(vis).map(e=>parseFloat(getComputedStyle(e).fontSize)));
 const txt=document.querySelector('.q h2 .txt');
 return {hs:de.scrollWidth-iw,wide:wide.slice(0,4),ph:de.scrollHeight,ih,lowest,small,ofs,inner:sc.map(e=>e.className),txtFs:txt?parseFloat(getComputedStyle(txt).fontSize):0,txtH:txt?txt.clientHeight:0}}"""
REACH="""()=>{/* chaque commande, amenée à l'écran, est bien celle qu'on touche (pas recouverte) */const bad=[];
 for(const e of [...document.querySelectorAll('.q button,.q input,.q textarea')].filter(e=>e.getClientRects().length)){e.scrollIntoView({block:'center'});const r=e.getBoundingClientRect(),x=r.left+r.width/2,y=r.top+r.height/2,h=document.elementFromPoint(x,y);if(!h||!(h===e||e.contains(h)||h.contains(e)))bad.push(e.className+'@'+Math.round(y))}
 scrollTo(0,0);return bad}"""
AFTER="""()=>{const q=R.q;try{if(q.o&&q.o.length&&q.g!=null){ans(q.o.findIndex(x=>x!==q.g))}else fin(false,q.sol||'—',q.key)}catch(e){fin(false,q.sol||'—',q.key)}return 1}"""
ME2="""()=>{const ih=innerHeight,f=document.querySelector('#fb .fb'),b=document.querySelector('#fb button'),r=e=>e?e.getBoundingClientRect():null,v=x=>!!x&&x.top>=-1&&x.bottom<=ih+1;
 return {hs:document.documentElement.scrollWidth-innerWidth,fb:!!f,fbVis:v(r(f)),btn:!!b,btnVis:b?v(r(b)):true}}"""
FULL=[["es",1],["es",3],["es",5],["va",2],["ca",4],["gl",3],["eu",5]]
def run(pg,page):
    pg.goto(URL+page);pg.wait_for_timeout(2500);out={}
    for U in ["fr","en"]:
        for L,lv in FULL:
            for ty in TYS:
                if not pg.evaluate(MK,[ty,L,lv,U]):continue
                pg.wait_for_timeout(200);m=pg.evaluate(ME)
                if U=="fr" and L=="es":m["reach"]=pg.evaluate(REACH)
                pg.evaluate(AFTER);pg.wait_for_timeout(1100);m["after"]=pg.evaluate(ME2);out[f"{U}/{L}{lv}:{ty}"]=m
    types=sorted({k.split(":")[1] for k in out})
    ck(f"[{page}] 360×640 : {len(types)} types d'exercices testés ({len(out)} cas, interface fr et en, 5 langues, A1→C1)",len(types)>=26,types)
    ck(f"[{page}] aucun débordement horizontal (page et éléments)",all(v["hs"]<=0 and not v["wide"] for v in out.values()),[(k,v["hs"],v["wide"]) for k,v in out.items() if v["hs"]>0 or v["wide"]][:4])
    fit=lambda v:v["lowest"]<=v["ih"]
    nf=[k for k,v in out.items() if not fit(v)]
    ok_nf=[k for k in nf if k.endswith(":read") and out[k]["lowest"]-out[k]["ih"]<=140]
    ck(f"[{page}] avant réponse, tout tient sur l'écran : {len(out)-len(nf)}/{len(out)} cas ; lectures C1 à options longues : {len(ok_nf)} cas à moins de 140 px de défilement",
       set(nf)==set(ok_nf),[(k,out[k]["lowest"]) for k in nf if k not in ok_nf][:5])
    ck(f"[{page}] commandes atteignables et non recouvertes (toutes les commandes, interface fr, castillan)",all(not v.get("reach") for v in out.values()),[(k,v["reach"]) for k,v in out.items() if v.get("reach")][:4])
    aft=[k for k,v in out.items() if not(v["after"]["fbVis"] and v["after"]["btnVis"]) or v["after"]["hs"]>0]
    ck(f"[{page}] après réponse : retour et « Continuer » visibles sans défiler à la main",not aft,[(k,out[k]["after"]) for k in aft][:4])
    ck(f"[{page}] cibles tactiles ≥ 44 px (options, boutons, champs)",all(not v["small"] for v in out.values()),[(k,v["small"]) for k,v in out.items() if v["small"]][:4])
    ck(f"[{page}] lisibilité : options ≥ 15 px, textes de lecture 17 px",all(v["ofs"]>=15 and (not v["txtFs"] or v["txtFs"]>=17) for v in out.values()),[(k,v["ofs"],v["txtFs"]) for k,v in out.items() if v["ofs"]<15][:4])
    ck(f"[{page}] texte long trop haut : défile dans son encadré, au moins 120 px visibles",all(v["txtH"]>=120 or not v["inner"] for v in out.values()) and any(v["inner"] for v in out.values()))
    # interactions réelles au doigt
    r=pg.evaluate(MK,["es2fr","es",1,"fr"]);pg.wait_for_timeout(200)
    g=pg.evaluate("R.q.o.indexOf(R.q.g)");o0=pg.evaluate("R.ok");pg.locator(".q .opt").nth(g).tap();pg.wait_for_timeout(400)
    ck(f"[{page}] toucher la bonne option : réponse comptée",pg.evaluate("R.ok")-o0==1 and pg.evaluate("R.done"))
    pg.evaluate(MK,["type","es",1,"fr"]);pg.wait_for_timeout(200)
    pg.locator("#ti").tap();pg.keyboard.type(pg.evaluate("R.q.es"));pg.locator("#chk").tap();pg.wait_for_timeout(400)
    ck(f"[{page}] saisie au clavier puis « Valider » au doigt : réponse comptée, champ et bouton à l'écran",pg.evaluate("R.done") and pg.evaluate("R.ok")==3)
    pg.evaluate(MK,["read","es",5,"fr"]);pg.wait_for_timeout(250)
    sc=pg.evaluate("""()=>{const t=document.querySelector('.q h2 .txt');const a=t.scrollTop;t.scrollTop=t.scrollHeight;t.dispatchEvent(new Event('scroll'));return {can:t.scrollHeight>t.clientHeight,moved:t.scrollTop>a,end:t.classList.contains('n8e')}}""")
    ck(f"[{page}] texte de lecture long : défilement dans l'encadré jusqu'à la fin (indicateur d'ombre retiré en bas)",(not sc["can"]) or (sc["moved"] and sc["end"]),sc)
    # textes très longs injectés : retour à la ligne, aucun débordement
    r=pg.evaluate("""()=>{UI='fr';S.lang='es';build();xens();R={mode:'lesson',t:'Mélange',n:3,ok:2,xp:20,hist:[],tot:10};
      const L='Anticonstitucionalmente'.repeat(3),q={ty:'read',txt:('Una frase bastante larga para probar el ajuste. ').repeat(30)+L,p:'¿'+L+'?',g:L+' uno',o:[L+' uno','Respuesta corta',L+' dos','Otra respuesta con muchas palabras para ocupar varias líneas en la pantalla'],sol:'x',key:null};
      R.q=q;show();scrollTo(0,0);return 1}""");pg.wait_for_timeout(100);r=pg.evaluate("""async()=>{const _q=document.querySelector('.q');if(_q)await Promise.all(_q.getAnimations({subtree:true}).filter(a=>a.effect&&a.effect.getTiming().iterations!==Infinity).map(a=>a.finished.catch(()=>0)));const iw=innerWidth;return {hs:document.documentElement.scrollWidth-iw,wide:[...document.querySelectorAll('#app *')].filter(e=>{const r=e.getBoundingClientRect();return r.width>0&&r.right>iw+1}).length}}""")
    ck(f"[{page}] mots et textes très longs injectés : retour à la ligne, aucun débordement horizontal",r["hs"]<=0 and r["wide"]==0,r)
    return out
with sync_playwright() as p:
    b=p.chromium.launch();err=[]
    c=b.new_context(viewport={"width":360,"height":640},has_touch=True,is_mobile=True);pg=c.new_page();pg.on("pageerror",lambda e:err.append(str(e)))
    a=run(pg,"castellano.html");i=run(pg,"index.html");c.close()
    import urllib.request,re
    blk=lambda pg_:re.findall(r"/\*N8[^*]*\*/.*?(?=\n)|<style id=\"n8-mobile\">.*?</style>",urllib.request.urlopen(URL+pg_).read().decode("utf8"),re.S)
    ck("castellano.html et index.html : mêmes règles et mêmes ajustements N8, mêmes types testés",blk("castellano.html")==blk("index.html") and len(blk("index.html"))==3 and {k.split(":")[1] for k in a}=={k.split(":")[1] for k in i})
    # autres formats : pas de débordement horizontal ; écrans larges et desktop inchangés
    for w,h in [(320,568),(375,667),(390,844),(412,915),(640,360),(768,1024),(1280,800)]:
        c=b.new_context(viewport={"width":w,"height":h},has_touch=w<1000,is_mobile=w<1000);pg=c.new_page();pg.on("pageerror",lambda e:err.append(str(e)))
        pg.goto(URL+"index.html");pg.wait_for_timeout(2000);bad=[]
        for ty in TYS:
            for L,lv in [["es",3],["es",5]]:
                if not pg.evaluate(MK,[ty,L,lv,"fr"]):continue
                pg.wait_for_timeout(120);m=pg.evaluate(ME)
                if m["hs"]>0 or m["wide"]:bad.append((ty,L,lv,m["hs"],m["wide"]))
        st=pg.evaluate("()=>{const q=document.querySelector('.q');return q?getComputedStyle(q).paddingLeft:''}")
        ck(f"{w}×{h} : aucun débordement horizontal sur les types d'exercices"+(" ; mise en page desktop non resserrée" if w>600 else ""),not bad and (w<=600 or st!="14px"),[bad[:3],st]);c.close()
    ck("aucune erreur JS",not err,err[:3]);b.close()
print(f"\n{sum(res)}/{len(res)} contrôles OK");sys.exit(0 if all(res) else 1)
