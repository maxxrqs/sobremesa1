#!/usr/bin/env python3
"""Listes et conjugaison : chaque verbe des listes est conjugable à tous les niveaux, ordre des catégories stable,
typographie homogène (pas de soulignement), vocabulaire « Nombres et dates » progressif et sans doublon.
Usage : python3 tests/listes.py [url_base]"""
import sys
from playwright.sync_api import sync_playwright
BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8772/"
R = []
def ck(n, c, i=""):
    R.append(bool(c)); print("OK  " if c else "FAIL", n, "" if c else str(i)[:500], flush=True)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 390, "height": 844}); err = []
    pg.on("pageerror", lambda e: err.append(str(e)))
    pg.goto(BASE + "index.html"); pg.wait_for_timeout(2500)
    # 1. conjugaison : tout verbe des listes a son tableau, quel que soit le niveau, et s'affiche sans erreur
    r = pg.evaluate("""()=>{const miss=[],bad=[],rows=[];for(const l of LK){S.lang=l;build();const k=LK.indexOf(l);
      for(const x of REF.filter(x=>x.c==="Verbes"&&x.t[k])){const v=x.t[k],d=VD[l][v];if(!d){miss.push([l,v,x.l]);continue}
        for(const [t,row] of Object.entries(d.t))if(Array.isArray(row)&&row.some(f=>!f||typeof f!=="string"))bad.push([l,v,t])}}
      return {miss,bad}}""")
    ck("chaque verbe des listes (5 langues, A1 à C1) a un tableau de conjugaison", not r["miss"], r["miss"][:8])
    ck("tableaux sans case vide", not r["bad"], r["bad"][:8])
    r = pg.evaluate("""()=>{const bad=[];let n=0;for(const l of LK)for(const L of [1,3,5]){S.lang=l;S.lvl=L;build();
      for(const lv of [0,1,2,3,4,5]){LS.c="Verbes";LS.l=lv;LS.q="";lists();const bs=[...document.querySelectorAll('#lr .vl')];
        const k=LK.indexOf(l),want=REF.filter(x=>x.c==="Verbes"&&x.t[k]&&(!lv||x.l===lv)).length;if(bs.length!==want)bad.push([l,L,lv,'liens',bs.length,want]);
        const one=bs[bs.length-1];if(one){one.click();n++;const h=document.getElementById('app').innerHTML;if(SCR!=="verb"||!/<table/.test(h))bad.push([l,L,lv,'ouverture'])}}}
      return {bad,n}}""")
    ck(f"depuis les listes, le lien « conjuguer » existe pour chaque verbe et ouvre le tableau ({r['n']} ouvertures, filtres Tout/A1→C1)", not r["bad"], r["bad"][:6])
    # 2. ordre des catégories identique quel que soit le niveau ; pas de titre répété
    r = pg.evaluate("""()=>{const bad=[],dup=[];for(const l of LK){S.lang=l;build();for(const c of LCATS){let ref=null;
      for(const L of [0,1,2,3,4,5]){LS.c=c;LS.l=L;LS.q='';lists();const hs=[...document.querySelectorAll('#lr h3')].map(e=>e.textContent);
        if(new Set(hs).size!==hs.length)dup.push([l,c,L]);if(!L){ref=hs;continue}const o=hs.map(h=>ref.indexOf(h));
        if(o.some((x,i)=>x<0||(i&&x<o[i-1])))bad.push([l,c,L,hs.slice(0,5)])}}}return{bad,dup}}""")
    ck("ordre des sous-catégories identique pour Tout, A1, A2, B1, B2, C1 (5 langues)", not r["bad"], r["bad"][:3])
    ck("aucune sous-catégorie affichée deux fois", not r["dup"], r["dup"][:3])
    # 3. typographie : mêmes police, graisse et taille pour tous les mots ; aucun soulignement
    for lv in [0, 1, 2]:
        r = pg.evaluate("""(lv)=>{S.lang='es';build();LS.c="Verbes";LS.l=lv;LS.q='';lists();const st=e=>{const s=getComputedStyle(e);return [s.fontFamily,s.fontWeight,s.fontSize].join('/')};
          const w=[...document.querySelectorAll('#lr td:nth-child(2) b, #lr td:nth-child(2) .vl')].map(st),u=[...document.querySelectorAll('#lr *')].filter(e=>getComputedStyle(e).textDecorationLine.includes('underline')).length;
          return {styles:[...new Set(w)],u}}""", lv)
        ck(f"liste Verbes {['Tout','A1','A2'][lv]} : une seule typographie pour les mots, aucun soulignement", len(r["styles"]) == 1 and r["u"] == 0, r)
    # 4. Nombres et dates : progression par niveau, pas de doublon
    r = pg.evaluate("""()=>{const o={};for(const l of LK){S.lang=l;build();const k=LK.indexOf(l),c={};REF.filter(x=>x.c==="Nombres et dates"&&x.t[k]).forEach(x=>c[x.l]=(c[x.l]||0)+1);
      /* doublon = même mot ET même sens (les homographes comme « nou » = neuf / nouveau sont légitimes) */
      const key=x=>x.t[k].trim().toLowerCase()+"|"+String(x.fr).replace(/\s*\(.*\)\s*$/,"").trim().toLowerCase(),all=REF.filter(x=>x.t[k]).map(key),dup=[...new Set(all.filter((x,i)=>all.indexOf(x)!==i))];
      const nd=new Set(REF.filter(x=>x.c==="Nombres et dates"&&x.t[k]).map(key));o[l]={c,dup:dup.filter(x=>nd.has(x))}}return o}""")
    ck("Nombres et dates : du vocabulaire à chaque niveau (A1 à C1), 5 langues", all(all(v["c"].get(str(L), v["c"].get(L, 0)) >= 4 for L in range(1, 6)) for v in r.values()), {l: v["c"] for l, v in r.items()})
    ck("Nombres et dates : aucun mot en double dans les listes (5 langues)", all(not v["dup"] for v in r.values()), {l: v["dup"] for l, v in r.items() if v["dup"]})
    ck("aucune erreur JS", not err, err[:3])
    b.close()
print(sum(R), "/", len(R), "OK"); sys.exit(0 if all(R) else 1)
