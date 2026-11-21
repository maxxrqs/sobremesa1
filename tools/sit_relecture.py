#!/usr/bin/env python3
"""Lot C : fiches de relecture native des situations (qa/situations_<langue>.md), à partir de tools/sit_data.py."""
import os,importlib.util
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sp=importlib.util.spec_from_file_location("d",os.path.join(R,"tools","sit_data.py"));d=importlib.util.module_from_spec(sp);sp.loader.exec_module(d)
NOM={"es":"castillan","va":"valencien","ca":"catalan","gl":"galicien","eu":"basque"}
os.makedirs(os.path.join(R,"qa"),exist_ok=True)
for l,ss in d.SIT.items():
    o=[f"# Relecture native — situations A1–A2 ({NOM[l]})","","Pour chaque échange : réplique du personnage, consigne donnée à l'apprenant, réponse modèle, variantes acceptées et réponses fausses proposées dans le format à choix.",
       "À vérifier : naturel et correction de chaque phrase, registre (vouvoiement du personnage), variantes réellement acceptables, réponses fausses réellement fausses mais plausibles.",""]
    for sid,(T,V) in ss.items():
        lv,ti,cx,ch,I=d.META[sid];o+=[f"## {ti} (A{lv}) — `{sid}`","",f"_{cx}_ · personnage : {ch}",""]
        for i,t in enumerate(T):
            n,m,va,ws,kw=t[:5];ins=t[5] if len(t)>5 else I[i]
            o+=[f"{i+1}. **{n}**",f"   - consigne : {ins}",f"   - modèle : {m}",f"   - variantes : {' · '.join(va)}",f"   - fausses : {' · '.join(ws)}",""]
        o+=["À retenir : "+" · ".join(f"{w} = {f}" for w,f in V),"",""]
    open(os.path.join(R,"qa",f"situations_{l}.md"),"w").write("\n".join(o))
print("qa/situations_*.md écrits")
