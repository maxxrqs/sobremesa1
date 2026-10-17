#!/usr/bin/env python3
"""Fusionne les clips générés pour combler les trous (dossier <src>/<voix>/gap.json + <voix>_gN.mp3)
dans l'index d'une voix du dépôt : v/<voix>/<voix>.json (ou a/es.json pour le castillan).
Les paquets existants ne sont pas modifiés : les nouveaux paquets s'ajoutent à la fin de la liste « p ».
Usage : audio_merge.py <dossier_src> <voix> [<voix>…]"""
import sys,os,json,shutil
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..")
src=sys.argv[1]
for v in sys.argv[2:]:
    ip,d=(f"{ROOT}/a/es.json",f"{ROOT}/a") if v=="es" else (f"{ROOT}/v/{v}/{v}.json",f"{ROOT}/v/{v}")
    ix=json.load(open(ip));g=json.load(open(f"{src}/{v}/gap.json"));base=len(ix["p"]);new=0
    if any(n in ix["p"] for n in g["p"]):print(v,"déjà fusionné");continue
    for n in g["p"]:shutil.copy(f"{src}/{v}/{n}",f"{d}/{n}")
    ix["p"]+=g["p"]
    for k,(pi,o,l) in g["k"].items():
        if k not in ix["k"]:ix["k"][k]=[base+pi,o,l];new+=1
    json.dump(ix,open(ip,"w"),ensure_ascii=False,separators=(",",":"))
    print(v,"+",new,"clips,",len(g["p"]),"paquets,",sum(os.path.getsize(f"{d}/{n}") for n in g["p"])//1000,"ko")
