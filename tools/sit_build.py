#!/usr/bin/env python3
"""Lot C (chantier 3) : écrit les situations de tools/sit_data.py dans castellano.html (constante XI, entre /*XI*/ et /*XI-END*/).
Format d'une ligne : S|id|niveau|titre|contexte|personnage · T|id|réplique|consigne|modèle|variantes;;…|3 fausses;;…|mots-clés;… · V|id|mot|traduction
Usage : python3 tools/sit_build.py [--check]"""
import sys,json,re,importlib.util,os
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sp=importlib.util.spec_from_file_location("d",os.path.join(R,"tools","sit_data.py"));d=importlib.util.module_from_spec(sp);sp.loader.exec_module(d)
def ok(x):
    assert "|" not in x and "\n" not in x and "`" not in x and ";;" not in x and "${" not in x, x
    return x
out={}
for l,ss in d.SIT.items():
    L=[]
    for sid,(T,V) in ss.items():
        lv,ti,cx,ch,I=d.META[sid]
        assert 5<=len(T)<=7,(l,sid,len(T))
        L.append("|".join(["S",sid,str(lv),ok(ti),ok(cx),ok(ch)]))
        for i,t in enumerate(T):
            n,m,va,o,kw=t[:5];ins=t[5] if len(t)>5 else I[i]
            assert len(o)==3 and m not in o and n and m,(l,sid,i)
            L.append("|".join(["T",sid,ok(n),ok(ins),ok(m),";;".join(map(ok,va)),";;".join(map(ok,o)),ok(kw)]))
        for w,f in V:L.append("|".join(["V",sid,ok(w),ok(f)]))
    out[l]="\n".join(L)
js="{"+",".join(f'{l}:`{v}`' for l,v in out.items())+"}"
p=os.path.join(R,"castellano.html");s=open(p,encoding="utf-8").read()
a=s.index("const XI=/*XI*/")+len("const XI=/*XI*/");b=s.index("/*XI-END*/",a)
if "--check" in sys.argv:
    sys.exit(0 if s[a:b]==js else 1)
s=s[:a]+js+s[b:];open(p,"w",encoding="utf-8").write(s)
print("situations :",{l:v.count("\nS|")+1 for l,v in out.items()})
