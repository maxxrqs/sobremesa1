#!/usr/bin/env python3
"""Liste, pour chaque voix, les textes de l'appli (tests/audio_texts.json, produit par audio_enum.py) qui n'ont pas
d'enregistrement. Écrit <sortie>/miss_<voix>.json, à fournir au générateur de voix. Usage : audio_gap.py [dossier_sortie]"""
import json,os,re,sys
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..");OUT=sys.argv[1] if len(sys.argv)>1 else "."
A=json.load(open(ROOT+"/tests/audio_texts.json"));VO=json.load(open(ROOT+"/v/voices.json"))
nm=lambda s:re.sub(r"[.…]+$","",s.lower()).strip()
for l,T in A.items():
    T={t:s for t,s in T.items() if set(s)!={"text"}}
    for v in [x["id"] for x in VO.get(l,[])] or ["es"]:
        k=json.load(open(ROOT+(f"/v/{v}/{v}.json" if v!="es" else "/a/es.json")))["k"];S={nm(x) for x in k}
        m=[t for t in T if nm(t) not in S];json.dump(m,open(f"{OUT}/miss_{v}.json","w"),ensure_ascii=False)
        print(f"{v}: {len(T)-len(m)}/{len(T)} enregistrés, {len(m)} manquants")
