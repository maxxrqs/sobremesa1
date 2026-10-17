#!/usr/bin/env python3
"""Assemble une nouvelle voix v/<id>/ à partir de fragments d'index (<id>.json + paquets) et de paquets existants.
Usage : audio_install_voice.py <id> <lang> <label> <dossier_frag>... [--extra <index.json> <dossier_paquets> <préfixe_paquet>]
Les fragments sont des dossiers contenant idx.json {p,k} et les paquets."""
import sys,os,json,shutil
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..")
vid,lang,label=sys.argv[1:4];rest=sys.argv[4:];extra=None
if "--extra" in rest:i=rest.index("--extra");extra=rest[i+1:i+4];rest=rest[:i]
d=f"{ROOT}/v/{vid}";os.makedirs(d,exist_ok=True);P=[];K={}
for fr in rest:
    ix=json.load(open(f"{fr}/idx.json"));b=len(P)
    for n in ix["p"]:shutil.copy(f"{fr}/{n}",f"{d}/{n}")
    P+=ix["p"]
    for t,(pi,o,l) in ix["k"].items():K[t]=[b+pi,o,l]
if extra:
    ixf,pdir,pre=extra;ix=json.load(open(ixf));use=[i for i,p in enumerate(ix["p"]) if p.startswith(pre)];m={}
    for i in use:m[i]=len(P);P.append(ix["p"][i]);shutil.copy(f"{pdir}/{ix['p'][i]}",f"{d}/{ix['p'][i]}")
    for t,(pi,o,l) in ix["k"].items():
        if pi in m:K[t]=[m[pi],o,l]
json.dump({"p":P,"k":K},open(f"{d}/{vid}.json","w"),ensure_ascii=False,separators=(",",":"))
vp=f"{ROOT}/v/voices.json";V=json.load(open(vp));V[lang]=[x for x in V.get(lang,[]) if x["id"]!=vid]
V[lang].insert(0,{"id":vid,"label":label});json.dump(V,open(vp,"w"),ensure_ascii=False)
print(vid,len(K),"clips",len(P),"paquets")
