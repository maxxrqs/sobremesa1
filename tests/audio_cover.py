#!/usr/bin/env python3
"""Garde-fou audio : chaque mot du vocabulaire (table REF de castellano.html) doit avoir un enregistrement
dans au moins une voix de sa langue (v/voices.json). Sinon l'appli le lit avec une voix de secours robotique.
Usage : python3 tests/audio_cover.py [--write dossier]   → code de sortie 1 s'il manque des clips.
Avec --write, écrit <dossier>/miss_<voix>.json (textes à générer pour cette voix)."""
import json, os, re, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
COL = {"es": 4, "va": 5, "ca": 6, "gl": 7, "eu": 8}
nm = lambda t: re.sub(r"[.…]+$", "", re.sub(r"\s+", " ", t).strip().lower()).strip()
lines = open(f"{ROOT}/castellano.html", encoding="utf-8").read().split("\n")
rows = [l.split("|") for l in lines if l.count("|") == 8 and re.match(r"^[^|<>{}]+\|[^|]*\|\d\|", l)]
VO = json.load(open(f"{ROOT}/v/voices.json"))
out = sys.argv[sys.argv.index("--write") + 1] if "--write" in sys.argv else None
bad = 0
for l, c in COL.items():
    texts = []
    seen = set()
    for r in rows:
        t = re.sub(r"\s+", " ", r[c]).strip()
        if t and nm(t) not in seen:
            seen.add(nm(t)); texts.append(t)
    allk = set()
    for v in [x["id"] for x in VO.get(l, [])]:
        keys = {nm(k) for k in json.load(open(f"{ROOT}/v/{v}/{v}.json"))["k"]}
        allk |= keys
        miss = [t for t in texts if nm(t) not in keys]
        print(("ok  " if not miss else "info"), v, f"{len(texts)-len(miss)}/{len(texts)}", ("" if not miss else "(lus par une autre voix de la langue) " + ", ".join(miss[:5]) + (" …" if len(miss) > 5 else "")))
        if out and miss:
            os.makedirs(out, exist_ok=True)
            json.dump(miss, open(f"{out}/miss_{v}.json", "w"), ensure_ascii=False)
    none = [t for t in texts if nm(t) not in allk]
    print(("OK  " if not none else "FAIL"), l, f"{len(texts)-len(none)}/{len(texts)} mots enregistrés au moins une fois", ("" if not none else "→ voix de secours robotique pour : " + ", ".join(none[:8]) + (" …" if len(none) > 8 else "")))
    bad += len(none)
sys.exit(1 if bad else 0)
