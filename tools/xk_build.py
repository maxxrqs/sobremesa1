#!/usr/bin/env python3
"""Lot D (chantier 3) : écrit les paires XK de tools/xk_data.txt dans castellano.html (entre /*XK*/ et /*XK-END*/).
Usage : python3 tools/xk_build.py [--check]"""
import sys,os
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out={};lang=None
for n,ln in enumerate(open(os.path.join(R,"tools","xk_data.txt"),encoding="utf-8"),1):
    ln=ln.rstrip("\n")
    if not ln.strip() or ln.startswith("# "):continue
    if ln.startswith("-- "):lang=ln[3:].strip();out[lang]=[];continue
    f=ln.split("|");assert len(f)==10 and f[1] in "2345" and lang,(n,ln)
    assert all(x and "`" not in x and "${" not in x for x in f),(n,ln)
    out[lang].append(ln)
js="{"+",".join(f'{l}:`{chr(10).join(v)}`' for l,v in out.items())+"}"
p=os.path.join(R,"castellano.html");s=open(p,encoding="utf-8").read()
a=s.index("const XK=/*XK*/")+len("const XK=/*XK*/");b=s.index("/*XK-END*/",a)
if "--check" in sys.argv:sys.exit(0 if s[a:b]==js else 1)
s=s[:a]+js+s[b:];open(p,"w",encoding="utf-8").write(s)
print("paires XK :",{l:len(v) for l,v in out.items()})
