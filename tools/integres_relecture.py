# Chantier 3, lot B : pages de relecture linguistique des exercices intégrés (une par langue étudiée), à faire valider par un locuteur natif.
# Pour chaque niveau A1–C1 : des exemples de « Complète » (trous entre crochets, étiquettes proposées), « Transforme » (consigne, phrase
# d'origine → phrase attendue) et « Réponds » (réplique, consigne, modèles acceptés). Les phrases viennent du corpus existant ; seules les
# phrases transformées sont nouvelles (elles ne sont jamais lues à voix haute).
# Usage : python3 tests/rangesrv.py 8774 . puis python3 tools/integres_relecture.py [URL] → qa/integres_<langue>.md
import sys,os
from playwright.sync_api import sync_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else "http://127.0.0.1:8774/"
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","qa")
NOM={"es":"castillan","va":"valencien","ca":"catalan","gl":"galicien","eu":"basque"}
JS=r"""([l,L])=>{S.lang=l;S.lvl=L;S.ob=0;build();XDIRTY=1;xens();XPWC=null;MKDC.clear();S.sr={};S.sc={};S.ds={};const t=dayN();let i=0;
  const ENT=(k,p)=>{const d=mkDif(k),c=[1,2,3,4].map(P=>P<=p?MKN[d][P]:0);S.sr[k]={b:1,d:t,p,m:1,c,n:3,k:0,s:t-2};if(d===3)S.sr[k].j=[0,0,0,0]};
  ALL.concat(LP).filter(w=>(w[2]||1)<=L).forEach(w=>{S.sc[w[0]]=1;ENT(w[0],2+i++%3)});XP.filter(x=>x.l<=L).forEach(x=>ENT('e:'+x.e,2+i++%3));
  Object.keys(VD[l]).filter(v=>vLvl(l,v)<=L).forEach(v=>{S.sc[v]=1;ENT('v:'+v,2+i++%3)});start('Mélange');
  const F=(fn,ty,p)=>{const out=[],seen=new Set();for(const k of shuf(Object.keys(S.sr).filter(k=>!k.startsWith('q:')))){if(out.length>=6)break;const o=S.sr[k];ENT(k,p);let q=null;try{q=window[fn](k)}catch(e){}S.sr[k]=o;
      if(!q||q.ty!==ty)continue;const id=(q.es||q.src||q.npc)+'|'+(q.lab||'');if(seen.has(id))continue;seen.add(id);out.push(q)}return out};
  const tr_=F('itTrou','itr',1).map(q=>'- '+q.ws.map((w,i)=>q.bl.some(b=>b.i===i)?'['+w+']':w).join(' ')+' — étiquettes : '+q.bank.join(', ')+' — _'+q.fr+'_');
  const tf=F('itTrf','itfE',3).concat(F('itTrf','itf',1)).map(q=>'- '+q.lab+' : '+q.src+' → **'+q.res+'**');
  const rp=F('itRep','irpE',3).map(q=>'- « '+q.npc+' » — '+q.hint+' → '+q.models.join(' / '));
  return {tr:tr_,tf,rp}}"""
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_context(locale="fr-FR",service_workers="block").new_page();pg.goto(BASE+"index.html");pg.wait_for_timeout(2500)
    for l in NOM:
        md=[f"# Exercices intégrés — relecture ({NOM[l]})\n","À vérifier par un locuteur natif : phrases naturelles, formes correctes, consignes cohérentes, aucune réponse ambiguë.\n"]
        for L,n in zip([1,2,3,4,5],["A1","A2","B1","B2","C1"]):
            r=pg.evaluate(JS,[l,L])
            md.append(f"\n## {n}\n")
            for k,t in [("tr","Complète (trous entre crochets)"),("tf","Transforme"),("rp","Réponds")]:
                md.append(f"\n### {t}\n");md.extend(r[k] or ["- (aucun exemple à ce niveau avec ce profil)"])
        open(os.path.join(OUT,f"integres_{l}.md"),"w",encoding="utf-8").write("\n".join(md)+"\n")
        print("qa/integres_"+l+".md")
    b.close()
