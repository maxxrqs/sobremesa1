#!/usr/bin/env python3
"""Garde-fou audio complet : tous les textes que l'appli peut lire à voix haute (mots de tous les niveaux, phrases,
phrases des textes, scènes, dialogues) doivent avoir un enregistrement dans au moins une voix de leur langue.
Usage : python3 tests/rangesrv.py 8774 .  puis  python3 tests/audio_cover_full.py [url] [--write dossier]
Code de sortie 1 s'il manque des clips. --write écrit <dossier>/full_<langue>.json (textes manquants)."""
import sys, json, os
from playwright.sync_api import sync_playwright
BASE = next((a for a in sys.argv[1:] if a.startswith("http")), "http://127.0.0.1:8774/")
OUT = sys.argv[sys.argv.index("--write") + 1] if "--write" in sys.argv else None
JS = r"""async(lang)=>{const SRC={};const add=(s,t)=>{if(typeof t!=="string")return;t=t.replace(/\s+/g," ").trim();if(!t||/^[a-z]:/.test(t))return;(SRC[t]=SRC[t]||new Set()).add(s)};
 for(let L=1;L<=5;L++){S.lang=lang;S.lvl=L;S.pthAll=1;build();try{xens()}catch(e){}
  ALL.forEach(w=>add("mot",w[0]));PH.forEach(p=>add("phrase",p[0]));
  TX.forEach(t=>(t[0].match(/[^.!?]+[.!?]+\s*/g)||[t[0]]).forEach(s=>add("texte",s)))}
 try{(SCN[lang]||[]).forEach(k=>k.split("|").forEach(t=>add("scène",t)))}catch(e){}
 try{xdP(lang).forEach(z=>{add("dialogue",z.n);add("dialogue",z.m);z.va.forEach(v=>add("dialogue",v))})}catch(e){}
 const m=await vxMan();AX.manv=m||{};const ids=(AX.manv[lang]||[]).map(v=>v.id);const ix=[];
 for(const v of ids){const x=await axIdx(lang,v);if(x)ix.push(x)}
 if(lang==="es"){const x=await axIdx("es","");if(x)ix.push(x)}
 const miss={};let n=0;for(const t in SRC){n++;if(!ix.some(x=>axFind(x,axNk(t))))miss[t]=[...SRC[t]]}
 return {n,voices:ids.length,miss}}"""
bad = 0
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(); pg.goto(BASE + "index.html"); pg.wait_for_timeout(2500)
    for l in ["es", "va", "ca", "gl", "eu"]:
        r = pg.evaluate(JS, l); m = r["miss"]; bad += len(m)
        by = {}
        for t, s in m.items():
            for k in s: by[k] = by.get(k, 0) + 1
        print(("OK  " if not m else "FAIL"), l, f"{r['n']-len(m)}/{r['n']} textes enregistrés", ("" if not m else str(by) + " ex. : " + " | ".join(list(m)[:4])), flush=True)
        if OUT and m:
            os.makedirs(OUT, exist_ok=True); json.dump(list(m), open(f"{OUT}/full_{l}.json", "w"), ensure_ascii=False)
    b.close()
sys.exit(1 if bad else 0)
