# Inventaire des textes français envoyés à la traduction (gl/tr), langue d'étude par langue d'étude,
# puis clés manquantes ou vides dans tr/<ui>.json. Usage : python3 tests/i18n_keys.py URL [sortie.json]
import sys,json,re
from playwright.sync_api import sync_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else "http://127.0.0.1:8775/"
JS=r"""()=>{const keys=new Set();const og=window.gl;
 // enregistre toutes les clés demandées pendant la construction des contenus de chaque langue étudiée
 const rec=s=>{if(typeof s==='string'&&s.trim()&&/[A-Za-zÀ-ÿ]/.test(s))keys.add(s)};
 const save=UI;UI='en';
 const src=String(gl);
 for(const l of LK){S.lang=l;try{build();XDIRTY=1;xens()}catch(e){}
  for(const r of RW.trim().split('\n')){rec(r.split('|')[2])}
  for(const r of RP.trim().split('\n')){rec(r.split('|')[1])}
  for(const r of RT.trim().split('\n')){r.split('|').slice(1,6).forEach(rec)}
  (XC[l]||'').trim().split('\n').forEach(L=>{const f=L.split('|');if(f[0]==='R'){[f[2],f[3],f[5]].forEach(rec);f[4].split(' ; ').forEach(x=>rec(x.split(' = ').slice(1).join(' = ')));rec(f[1])}else if(f[0]==='Q'){rec(f[1]);rec(f[2]);rec(f[7])}});
  (XE[l]||'').trim().split('\n').forEach(L=>{const f=L.split('|');if(f[0]==='E'){[f[1],f[3],f[4],f[6],f[7]].forEach(rec)}});
 }
 REF.forEach(r=>{rec(r.fr);rec(r.c);rec(r.s)});
 UI=save;return [...keys]}"""
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page();pg.goto(BASE+"index.html");pg.wait_for_timeout(2500)
    keys=pg.evaluate(JS)
src=open("castellano.html",encoding="utf-8").read()
for m in re.finditer(r'\b(?:tr|gl)\((["\'])((?:\\.|(?!\1).)*?)\1',src):
    k=m.group(2)
    if "\\" in k:
        try:k=json.loads('"'+k.replace('"','\\"').replace("\\'","'")+'"')
        except Exception:pass
    keys.append(k)
keys=sorted(set(keys))
NUM=re.compile(r"\d+(?:[.,]\d+)?")
rep={"total":len(keys)}
for ui in ["en","it","de","pt"]:
    d=json.load(open(f"tr/{ui}.json",encoding="utf-8"))
    miss=[k for k in keys if (d.get(k) is None and d.get(NUM.sub("#",k)) is None)]
    empty=[k for k,v in d.items() if not str(v).strip()]
    rep[ui]={"missing":miss,"empty":empty}
    print(ui,"clés manquantes",len(miss),"vides",len(empty))
print("textes à traduire recensés",len(keys))
if len(sys.argv)>2:json.dump(rep,open(sys.argv[2],"w"),ensure_ascii=False,indent=0)
