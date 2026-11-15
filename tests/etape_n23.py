# N°23 — validation d'une étape du parcours à 7/10 (demi-points compris) au lieu de 6/10.
# Règle : end() valide si R.ok ≥ 7 ; une étape dont le meilleur score enregistré (S.pth) est ≥ 6 (ancienne règle,
# ou migration de l'ancien parcours) reste validée : rien n'est invalidé, déblocages et fin de niveau inchangés.
# Usage : python3 tests/etape_n23.py [URL de base] [pages séparées par des virgules]
import sys
from playwright.sync_api import sync_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else "http://127.0.0.1:8830/"
PAGES=(sys.argv[2] if len(sys.argv)>2 else "castellano.html,index.html").split(",")
R=[]
def ck(n,c,i=""):
    R.append(bool(c));print("OK  " if c else "FAIL",n,"" if c else str(i)[:700],flush=True)
FIN="""([i,ok,pre])=>{const st=pathPlan().units[0].steps,pid=st[i].id,pk=pthK(pid);S.pth=S.pth||{};delete S.pth[pk];if(pre!=null)S.pth[pk]=pre;
  UNLQ=null;start('Mélange',null,pid);R.ok=ok;R.xp=ok*10;R.rec=[{s:'x'}];R.miss=[];end();
  const e=document.querySelector('.end'),t=e?e.innerText:'',dis=!!document.querySelector('.btn.dis');let em='';
  if(dis){endErr();em=(document.getElementById('endm')||{}).innerText||''}
  return {pth:(S.pth||{})[pk]||0,val:/Étape validée/.test(t),deja:/déjà validée/.test(t),f7:/Il faut 7 bonnes réponses sur 10/.test(t),f6:/\\b6 bonnes/.test(t),
    err:/Voir mes erreurs/.test(t),dis,cont:/Continuer le parcours/.test(t),em,big:(document.querySelector('.big')||{}).innerText||'',fl:(S.fl||{})[pk]||0}}"""
with sync_playwright() as p:
    b=p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    for page in PAGES:
        c=b.new_context(locale="fr-FR",service_workers="block");pg=c.new_page();er=[];pg.on("pageerror",lambda e:er.append(str(e)))
        pg.goto(BASE+page);pg.wait_for_timeout(2500);pg.evaluate("()=>{S.lvl=1;S.lang='es';try{save()}catch(e){}}")
        # --- A. le seuil, avec les demi-points
        res={k:pg.evaluate(FIN,[0,k,None]) for k in (5.5,6,6.5,6.9,7,7.5,10)}
        ko=[k for k in (5.5,6,6.5,6.9) if res[k]["val"] or res[k]["pth"] or not res[k]["f7"] or res[k]["f6"] or not res[k]["dis"] or not res[k]["err"] or "7/10" not in res[k]["em"]]
        ck(f"{page} : 5,5 · 6 · 6,5 · 6,9 /10 → étape NON validée, « Il faut 7 bonnes réponses sur 10 », Voir mes erreurs, Continuer bloqué (7/10)",not ko,{k:res[k] for k in ko})
        ok=[k for k in (7,7.5,10) if not(res[k]["val"] and res[k]["pth"]==k and not res[k]["dis"] and not res[k]["err"] and res[k]["cont"])]
        ck(f"{page} : 7 · 7,5 · 10 /10 → étape validée, meilleur score enregistré, parcours ouvert",not ok,{k:res[k] for k in ok})
        # --- B. migration : une étape déjà validée sous l'ancienne règle (6 ou 6,5) le reste
        m=pg.evaluate(FIN,[0,6.5,6]);m2=pg.evaluate(FIN,[0,3,6.5])
        ck(f"{page} : étape déjà validée à 6/10 puis refaite à 6,5 → toujours validée (6 conservé), « déjà validée », parcours ouvert",
           m["pth"]==6 and m["deja"] and not m["dis"] and not m["val"],m)
        ck(f"{page} : étape validée à 6,5 puis refaite à 3 → reste validée",m2["pth"]==6.5 and m2["deja"] and not m2["dis"],m2)
        lg=pg.evaluate("""()=>{const pl=pathPlan(),u=pl.units[0],ids=u.steps.filter(x=>!x.test).map(x=>x.id);S.pth={};ids.forEach(id=>{S.pth[pthK(id)]=6});
          const it=pathItems(),d=it.filter(x=>ids.includes(x.id)).every(x=>x.done),nx=it.find(x=>!x.done);
          const u2=pl.units[1],lock=u2?pathItems().find(x=>x.id===u2.steps[0].id):null;
          const un=unitUnlocked(u.steps[u.steps.length-1].id);
          const all=pl.flat.filter(x=>!x.test).map(x=>x.id);all.forEach(id=>{S.pth[pthK(id)]=6});const lv=lvSteps();S.pth={};
          return {d,nx:nx&&nx.id,u1:ids.length,lock2:lock?!!lock.lock:null,un:!!un||u.steps[u.steps.length-1].test===true,lv}}""")
        ck(f"{page} : progression existante à 6/10 partout → étapes « faites », unité suivante ouverte, niveau terminé (rien n'est invalidé)",
           lg["d"] and lg["lock2"] is not True and lg["lv"],lg)
        # --- C. XP : la validation ne change pas l'XP gagné ; réduction ×0,5 au-delà de 8/10 inchangée
        x=pg.evaluate("""()=>{const pid=pathPlan().units[0].steps[0].id,pk=pthK(pid),r0=R;S.pth={};R={pid};const a=xpGain(1,0,true,{});S.pth[pk]=7;const b=xpGain(1,0,true,{});S.pth[pk]=8;const c=xpGain(1,0,true,{});R=r0;S.pth={};return [a,b,c]}""")
        ck(f"{page} : XP par bonne réponse inchangé (10 ; 10 à 7/10 ; ×0,5 dès 8/10)",x==[10,10,5],x)
        # --- D. textes : parcours verrouillé, visite guidée, traductions
        t=pg.evaluate("""()=>{home();const el=document.querySelector('.pn')||document.body;lkErr(el);const m=(document.querySelector('.lkm')||{}).textContent||'';
          const H=document.documentElement.innerHTML,tour=H.includes('Il faut sept bonnes réponses sur dix')&&!H.includes('Il faut six bonnes réponses');return {m,tour}}""")
        ck(f"{page} : étape verrouillée → message « au moins 7/10 » ou « 7 bonnes réponses » ; visite guidée « sept bonnes réponses sur dix »",
           ("7/10" in t["m"] or "7 bonnes" in t["m"]) and "6/10" not in t["m"] and t["tour"],t)
        trs={}
        for ui in ["en","de","it","pt"]:
            trs[ui]=pg.evaluate("""async(ui)=>{UI=ui;await trLoad(ui);const o=[tr("Il faut 7 bonnes réponses sur 10 pour valider l'étape."),tr("Valide d'abord « {0} » avec au moins 7/10 pour continuer.","X"),tr("Il faut au moins 7/10 pour continuer le parcours : recommence l'étape."),
              tr("Ton chemin pas à pas : des étapes courtes qui s'enchaînent jusqu'au test du niveau suivant. Il faut sept bonnes réponses sur dix pour valider une étape.")];UI='fr';return o}""",ui)
        bad={k:v for k,v in trs.items() if not(all(s and "Il faut" not in s and "Ton chemin" not in s for s in v) and "7" in v[0] and "7/10" in v[1] and "7/10" in v[2] and "6" not in "".join(v))}
        ck(f"{page} : traductions en/de/it/pt à jour (7, 7/10, sept), aucune trace de 6/10",not bad,bad)
        ck(f"{page} : aucune erreur JavaScript",not er,er[:3]);c.close()
    b.close()
print(f"\n{sum(R)}/{len(R)} contrôles réussis");sys.exit(0 if all(R) else 1)
