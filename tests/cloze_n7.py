# Anomalie n°7 de l'audit du 7 novembre : phrases à trous (type « cloze »).
# Avant : trou sur un mot quelconque, intrus tirés au hasard selon leur longueur (autre nature de mot), traduction qui désignait la réponse
#   (ex. « Hablo ___ e inglés » / « Je parle français et anglais » : contrato / hablar / francés / hora).
# Après : trou sur un verbe conjugué, intrus = autres personnes du même verbe au même temps. La traduction reste (aide au sens),
#   mais toutes les options ont le même sens : seule la conjugaison départage. Phrases ambiguës exclues.
# Usage : python3 tests/cloze_n7.py [URL]   (teste castellano.html et index.html, puis compare les deux pages)
import sys,json
from playwright.sync_api import sync_playwright
URL=sys.argv[1] if len(sys.argv)>1 else "http://127.0.0.1:8772/"
res=[]
def ck(n,ok,d=""):res.append(ok);print(("OK   " if ok else "FAIL ")+n+("" if ok else f"  {str(d)[:400]}"))
GEN="""([L,lv,U,N])=>{UI=U;S.lang=L;S.lvl=lv;build();xens();R={mode:'lesson',t:'EE',n:0,ok:0,xp:0,hist:[]};
  const I=czIdx(L),nz=s=>String(s).toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,''),out=[];let fb=0;
  const cog=(a,fr)=>nz(fr).split(/[^a-z]+/).some(w=>w.length>=4&&nz(a).length>=4&&w.slice(0,4)===nz(a).slice(0,4));
  for(let i=0;i<N;i++){const q=mkQ0('cloze',0);if(q.ty!=='cloze'){fb++;if(q.ty!=='build')out.push({bad:'type '+q.ty});continue}
    const lo=q.o.map(x=>x.toLowerCase()),ga=I.m.get(q.g.toLowerCase())||[],par=ga.length?ga[0].fs.map(x=>x.toLowerCase()):[];
    const ps=new Set(ga.map(h=>h.p)),fr0=I.fr[q.es];
    out.push({txt:q.txt,fr:q.fr,g:q.g,o:q.o,fr0,
      one:q.o.filter(x=>x===q.g).length===1,dist:new Set(lo).size===4,hole:q.txt.includes('_____')&&!q.txt.includes(q.g+' ')||q.txt.includes('_____'),
      same:lo.every(x=>par.includes(x)),
      ambig:q.o.filter(x=>x!==q.g).some(x=>ga.some(h=>[...ps].some(p=>nz(h.fs[p])===nz(x)))),
      p2:ps.has(1)||ps.has(4),
      o3:(ps.has(2)&&q.o.some(x=>x!==q.g&&nz(x)===nz(par[5])))||(ps.has(5)&&q.o.some(x=>x!==q.g&&nz(x)===nz(par[2]))),
      cogOnly:cog(q.g,q.fr)&&!q.o.filter(x=>x!==q.g).some(x=>cog(x,q.fr)),
      fill:q.es===q.txt.replace('_____',q.g)})}
  return{fb,out}}"""
def run(pg,page):
    pg.goto(URL+page);pg.wait_for_timeout(2500)
    allq=[]
    for U in ["fr","en"]:
        for L in ["es","va","ca","gl","eu"]:
            for lv in [1,2,3,4,5]:
                r=pg.evaluate(GEN,[L,lv,U,60]);q=r["out"]
                for x in q:x.update(L=L,lv=lv,U=U)
                allq+=q
                ck(f"[{page}] {U}/{L}/niv{lv} : {len(q)} phrases à trous générées, {r['fb']} repli(s) « build », aucun autre type",
                   len(q)>=40 and not any("bad" in x for x in q),r["fb"])
    q=[x for x in allq if "bad" not in x]
    ck(f"[{page}] une seule bonne réponse, 4 options distinctes, trou visible, phrase complète = phrase d'origine ({len(q)} questions)",
       all(x["one"] and x["dist"] and x["hole"] and x["fill"] for x in q),[x for x in q if not(x["one"] and x["dist"] and x["fill"])][:3])
    ck(f"[{page}] intrus de même nature et même sens : toutes les options sont des formes du même verbe au même temps",
       all(x["same"] for x in q),[x for x in q if not x["same"]][:3])
    ck(f"[{page}] la traduction ne désigne plus la réponse : 0 question où seule la bonne option ressemble à un mot de la traduction",
       sum(x["cogOnly"] for x in q)==0,[x for x in q if x["cogOnly"]][:3])
    ck(f"[{page}] aucune réponse légitime refusée : aucun intrus n'est une autre lecture possible de la forme attendue (ex. hablaba 1re/3e pers.)",
       not any(x["ambig"] for x in q),[x for x in q if x["ambig"]][:3])
    ck(f"[{page}] phrases avec « vous », « on », « quelqu'un », « il paraît » jamais utilisées (personne ambiguë)",
       not any(x["fr0"] is None or __import__("re").search(r"(?i)(^|\W)(vous|on|quelqu'un|para[iî]t)(\W|$)",x["fr0"]) for x in q))
    ck(f"[{page}] 3e personne : l'autre nombre n'est jamais proposé (sujet sous-entendu ou impersonnel : van/va suspendre)",
       not any(x["o3"] for x in q),[x for x in q if x["o3"]][:3])
    ck(f"[{page}] interface en anglais : jamais de trou à la 2e personne (« you » = tú/vosotros/usted)",
       not any(x["p2"] for x in q if x["U"]=="en"))
    ck(f"[{page}] interface en français : la 2e personne reste exercée (tu)",any(x["p2"] for x in q if x["U"]=="fr"))
    # cas précis
    c=pg.evaluate("""()=>{UI='fr';const g=(L,s)=>{S.lang=L;build();xens();return czCand(L,s).map(z=>[z.g,z.d])};return{
      hablo:g('es','Hablo francés e inglés'),llamaron:g('es','Mientras cocinaba, llamaron a la puerta.'),dicen:g('es','Dicen que el alquiler va a subir otra vez.'),
      hiha:g('va',"Perdone, hi ha alguna farmàcia prop d'ací?"),canto:g('gl','Canto máis o penso, menos o entendo.'),
      ser:g('es','Son las ocho y media.'),gire:g('es','Gire a la derecha en el semáforo y siga todo recto.'),dudas:g('es','Aunque siempre haya negado los hechos, las pruebas no dejan lugar a dudas.'),pares:g('va','Els meus pares viuen a Madrid.'),eu:g('eu','Enpresa batean lan egiten dut'),pots:g('va','Pots repetir-ho, per favor?'),agrada:g('va','M\\'agrada molt la paella')}}""")
    ck(f"[{page}] exemple de l'audit « Hablo ___ e inglés » : le trou ne peut plus porter que sur le verbe (Hablo / habla, hablan…)",
       [z[0] for z in c["hablo"]]==["Hablo"] and "francés" not in json.dumps(c["hablo"]),c["hablo"])
    ck(f"[{page}] sujet impersonnel (« quelqu'un a sonné », « il paraît ») : pas de trou (llamó/llamaron, dice/dicen tous deux possibles)",
       c["llamaron"]==[] and c["dicen"]==[],c)
    ck(f"[{page}] impératif de politesse (« Tournez… continuez ») : pas de trou ; noms pluriels « dudas », « pares » jamais pris pour des verbes",
       c["gire"]==[] and all(z[0]!="dudas" for z in c["dudas"]) and all(z[0]!="pares" for z in c["pares"]),c)
    ck(f"[{page}] « hi ha » (va/ca) jamais troué ; « canto » (gl, = combien) jamais pris pour cantar",
       all(z[0]!="ha" for z in c["hiha"]) and all(z[0].lower()!="canto" for z in c["canto"]),c)
    ck(f"[{page}] exemples réels : Son las ocho (soy/eres/somos…), basque « dut » (duzu/du/dugu…), « Pots » (va), élision « M'agrada »",
       c["ser"] and c["ser"][0][0]=="Son" and "soy" in c["ser"][0][1] and "es" not in c["ser"][0][1] and c["eu"] and c["eu"][0][0]=="dut" and "duzu" in c["eu"][0][1]
       and c["pots"] and c["pots"][0][0]=="Pots" and c["agrada"] and c["agrada"][0][0]=="agrada",c)
    # affichage et notation
    r=pg.evaluate("""()=>{UI='fr';S.lang='es';S.lvl=1;build();xens();R={mode:'lesson',t:'EE',n:3,ok:2,xp:20,hist:[]};let q;for(let i=0;i<30;i++){q=mkQ0('cloze',0);if(q.ty==='cloze')break}
      R.q=q;R.done=false;show();const h=document.querySelector('.q,#app,body').innerHTML,sub=!!document.querySelector('h2 .sub'),o0=R.ok,x0=R.xp;ans(q.o.indexOf(q.g));
      const good={d:R.ok-o0,x:R.xp-x0};let q2;for(let i=0;i<30;i++){q2=mkQ0('cloze',0);if(q2.ty==='cloze')break}R.q=q2;R.done=false;show();const o1=R.ok;ans(q2.o.findIndex(x=>x!==q2.g));
      return{trad:h.includes(q.fr),sub,good,bad:R.ok-o1}}""")
    ck(f"[{page}] la traduction reste affichée comme aide au sens ; bonne option comptée (+1, XP), mauvaise option non comptée",
       r["trad"] and r["good"]["d"]==1 and r["good"]["x"]>0 and r["bad"]==0,r)
    cand=pg.evaluate("""()=>{UI='fr';const o={};for(const L of ['es','va','ca','gl','eu']){S.lang=L;build();xens();const k=LK.indexOf(L);
      o[L]=RP.trim().split('\\n').map(l=>{const s=l.split('|')[2+k];return czCand(L,s).map(z=>z.g+':'+z.d.join(','))})}return o}""")
    cov={L:sum(1 for x in v if x) for L,v in cand.items()}
    ck(f"[{page}] couverture : phrases utilisables par langue {cov} (sur {len(cand['es'])})",all(n>=60 for n in cov.values()),cov)
    return cand
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page();err=[];pg.on("pageerror",lambda e:err.append(str(e)))
    a=run(pg,"castellano.html");c=run(pg,"index.html")
    ck("castellano.html et index.html : mêmes trous et mêmes intrus possibles pour toutes les phrases des 5 langues",a==c)
    ck("aucune erreur JS",not err,err[:3]);b.close()
print(f"\n{sum(res)}/{len(res)} contrôles OK");sys.exit(0 if all(res) else 1)
