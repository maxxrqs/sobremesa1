# QR (chantier 3, lot A) : rattachement de chaque question de grammaire (XC, lignes Q) à la règle qui l'explique (lignes R).
# La source est tools/qr_rattachements.tsv, vérifiée à la main : langue, catégorie, question, réponse, règle (titre source) ou « - ».
#   python3 tools/qr_rattachements.py generer   → réécrit const QR=/*QR*/{…}; dans castellano.html (puis : python3 build_pwa.py)
#   python3 tools/qr_rattachements.py verifier  → code 1 si une question n'a pas d'entrée, si une règle citée n'existe plus,
#                                                 ou si castellano.html n'est pas à jour
#   python3 tools/qr_rattachements.py fiche es  → questions sans entrée, avec les règles de leur catégorie (pour la relecture)
# Empreinte : FNV-1a 32 bits sur le texte (unités UTF-16, comme JavaScript), base 36, 7 caractères (xpH dans l'appli).
import sys,os,json,re,csv
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML=os.path.join(ROOT,"castellano.html");TSV=os.path.join(ROOT,"tools","qr_rattachements.tsv")
LANGS=["es","va","ca","gl","eu"]
def b36(n):
    d="0123456789abcdefghijklmnopqrstuvwxyz";s=""
    while True:
        s=d[n%36]+s;n//=36
        if n==0:return s
def H(s):
    h=0x811c9dc5;b=s.encode("utf-16-le")
    for i in range(0,len(b),2):h^=int.from_bytes(b[i:i+2],"little");h=(h*16777619)&0xffffffff
    return b36(h).rjust(7,"0")[-7:]
def xc(src):return json.JSONDecoder().raw_decode(src,src.index("const XC=")+9)[0]
def parse(X,l):
    R=[];Q=[]
    for r in X[l].strip().split("\n"):
        f=r.split("|")
        if f[0]=="R":R.append(dict(c=f[1],t=f[2]))
        elif f[0]=="Q":Q.append(dict(c=f[1],k=f[2],a=f[3]))
    return R,Q
def lire():
    with open(TSV,encoding="utf-8",newline="") as f:return [r for r in csv.reader(f,delimiter="\t")][1:]
def construire(src):
    X=xc(src);rows=lire();out={};err=[]
    for l in LANGS:
        R,Q=parse(X,l);titres={r["t"] for r in R};m={}
        for row in rows:
            if row[0]!=l:continue
            _,c,k,a,t=row
            if t!="-" and t not in titres:err.append(f"{l} : règle introuvable « {t} »")
            hk=H(k+"|"+a);v="-" if t=="-" else H(t)
            if hk in m and m[hk]!=v:err.append(f"{l} : deux rattachements différents pour « {k} »")
            m[hk]=v
        for q in Q:
            if H(q["k"]+"|"+q["a"]) not in m:err.append(f"{l} : question sans entrée « {q['k']} »")
        out[l]=" ".join(f"{h}:{v}" for h,v in m.items())
    return out,err
def main():
    cmd=sys.argv[1] if len(sys.argv)>1 else "verifier"
    src=open(HTML,encoding="utf-8").read()
    if cmd=="fiche":
        l=sys.argv[2];X=xc(src);R,Q=parse(X,l);vus={(r[2],r[3]) for r in lire() if r[0]==l}
        for q in Q:
            if (q["k"],q["a"]) in vus:continue
            print(f"[{q['c']}] {q['k']} → {q['a']}");print("   règles : "+" | ".join(r["t"] for r in R if r["c"]==q["c"]))
        return
    out,err=construire(src)
    for e in err:print("ERREUR",e)
    blob="const QR=/*QR*/"+json.dumps(out,ensure_ascii=False,separators=(",",":"))+";"
    cur=re.search(r"const QR=/\*QR\*/\{.*?\};",src)
    if cmd=="generer":
        if err:sys.exit(1)
        open(HTML,"w",encoding="utf-8").write(src[:cur.start()]+blob+src[cur.end():]);print("QR écrit dans castellano.html ; lancer python3 build_pwa.py")
    else:
        a_jour=cur and cur.group(0)==blob
        if not a_jour:print("ERREUR castellano.html n'est pas à jour (python3 tools/qr_rattachements.py generer)")
        n={l:len(out[l].split()) for l in LANGS};print("questions par langue :",n)
        sys.exit(1 if err or not a_jour else 0)
if __name__=="__main__":main()
