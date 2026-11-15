# Garde-fou des réserves ouvertes (RESERVES.md) : elles restent documentées, marquées OUVERTE tant que Max n'a pas décidé,
# CLAUDE.md y renvoie, et les phrases galiciennes de la réserve n°15 restent inchangées dans les deux pages.
# Usage : python3 tests/reserves.py
import os,re,sys
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..")
rd=lambda f:open(os.path.join(ROOT,f),encoding="utf-8").read()
R=[]
def ck(n,c,i=""):R.append(bool(c));print(("OK   " if c else "FAIL ")+n+("" if c else "  "+str(i)[:300]))
r=rd("RESERVES.md")
for n in ("4","15"):
    m=re.search(r"^## n°"+n+r" — .*$",r,re.M)
    ck(f"réserve n°{n} présente dans RESERVES.md",m is not None)
    ck(f"réserve n°{n} marquée OUVERTE (jamais présentée comme résolue)",m is not None and "OUVERTE" in m.group(0) and "RÉSOLUE" not in m.group(0),m and m.group(0))
ck("CLAUDE.md renvoie obligatoirement à RESERVES.md","RESERVES.md" in rd("CLAUDE.md"))
GL=["Gustaríame que estiveses alí.","De sabelo antes, actuariamos doutro xeito."]
for p in ("castellano.html","index.html"):
    h=rd(p)
    ck(f"{p} : phrases galiciennes de la réserve n°15 inchangées (une occurrence chacune)",all(h.count(x)==1 for x in GL),[h.count(x) for x in GL])
print(f"\n{sum(R)}/{len(R)} contrôles OK");sys.exit(0 if all(R) else 1)
