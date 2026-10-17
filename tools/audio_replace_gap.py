#!/usr/bin/env python3
"""Remplace les clips « de comblement » d'une voix (paquets *_gN.mp3) par de nouveaux clips (<src>/gap.json + paquets).
Les anciens paquets de comblement sont supprimés de la liste « p » (les index sont renumérotés) et du disque.
Usage : audio_replace_gap.py <dossier_src> <voix>"""
import sys,os,json,re
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..")
src,v=sys.argv[1],sys.argv[2]
ip,d=(f"{ROOT}/a/es.json",f"{ROOT}/a") if v=="es" else (f"{ROOT}/v/{v}/{v}.json",f"{ROOT}/v/{v}")
ix=json.load(open(ip));g=json.load(open(f"{src}/gap.json"))
old=[i for i,p in enumerate(ix["p"]) if re.search(r"_g\d+\.mp3$",p)]
keep=[i for i in range(len(ix["p"])) if i not in old];remap={o:n for n,o in enumerate(keep)}
P=[ix["p"][i] for i in keep];K={}
for t,(pi,o,l) in ix["k"].items():
    if pi in remap:K[t]=[remap[pi],o,l]
base=len(P);import shutil
for n in g["p"]:shutil.copy(f"{src}/{n}",f"{d}/{n}")
P+=g["p"];rep=0
for t,(pi,o,l) in g["k"].items():K[t]=[base+pi,o,l];rep+=1
lost=[t for t,(pi,o,l) in ix["k"].items() if pi in old and t not in g["k"]]
for i in old:
    f=f"{d}/{ix['p'][i]}"
    if os.path.exists(f):os.remove(f)
json.dump({"p":P,"k":K},open(ip,"w"),ensure_ascii=False,separators=(",",":"))
print(v,"remplacés",rep,"clips; sans remplaçant (retirés):",len(lost),lost[:10])
