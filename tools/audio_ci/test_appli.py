#!/usr/bin/env python3
"""Essai des clips générés DANS l'appli, sur une copie jetable du dépôt (le dépôt n'est jamais modifié) :
fusion par tools/audio_merge.py dans la copie, serveur local, puis pour chaque clip : l'appli le trouve dans la voix
choisie et lit exactement les octets produits ; secours : texte absent → aucun clip (pas de voix de remplacement inventée),
voix sans le texte → autre voix enregistrée de la même langue.
Usage : python3 tools/audio_ci/test_appli.py <dossier_out> [port]"""
import json, os, shutil, subprocess, sys, tempfile, time
from playwright.sync_api import sync_playwright
RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.abspath(sys.argv[1]); PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 8791
R = []
def ck(n, c, i=""): R.append(bool(c)); print("OK  " if c else "FAIL", n, "" if c else str(i)[:600], flush=True)
gen = json.load(open(os.path.join(OUT, "generation.json"), encoding="utf-8"))
voix = [v for v, g in gen["voix"].items() if g["generes"]]
tmp = tempfile.mkdtemp(prefix="sobremesa_essai_")
for n in os.listdir(RACINE):
    if n in (".git", "v"): continue
    if n == "tools": shutil.copytree(os.path.join(RACINE, n), os.path.join(tmp, n), symlinks=False); continue  # « tools/.. » doit désigner la copie
    os.symlink(os.path.join(RACINE, n), os.path.join(tmp, n))
os.mkdir(os.path.join(tmp, "v"))
for n in os.listdir(os.path.join(RACINE, "v")):
    s = os.path.join(RACINE, "v", n)
    if n in voix: shutil.copytree(s, os.path.join(tmp, "v", n))
    else: os.symlink(s, os.path.join(tmp, "v", n))
avant = {v: open(os.path.join(RACINE, "v", v, v + ".json"), "rb").read() for v in voix}
subprocess.run([sys.executable, os.path.join(tmp, "tools", "audio_merge.py"), OUT, *voix], check=True, cwd=tmp)  # script de la copie : il écrit dans la copie
for v in voix:
    if open(os.path.join(RACINE, "v", v, v + ".json"), "rb").read() != avant[v]: raise SystemExit("ARRÊT : le dépôt a été modifié")
for v in voix:  # la fusion ne doit rien changer aux clés existantes
    a = json.loads(avant[v]); b = json.load(open(os.path.join(tmp, "v", v, v + ".json")))
    ck(f"{v} : fusion sans écrasement ({len(b['k']) - len(a['k'])} clés ajoutées, anciennes clés identiques)", all(b["k"][k] == x for k, x in a["k"].items()) and b["p"][:len(a["p"])] == a["p"])
srv = subprocess.Popen([sys.executable, os.path.join(RACINE, "tests", "rangesrv.py"), str(PORT), tmp], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1.5)
VO = json.load(open(os.path.join(RACINE, "v", "voices.json")))
lang = {x["id"]: l for l, L in VO.items() for x in L}
try:
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(); err = []; pg.on("pageerror", lambda e: err.append(str(e)))
        pg.goto(f"http://127.0.0.1:{PORT}/castellano.html"); pg.wait_for_timeout(2500)
        for v in voix:
            gp = json.load(open(os.path.join(OUT, v, "gap.json"), encoding="utf-8"))
            for t, (pi, o, l) in gp["k"].items():
                attendu = open(os.path.join(OUT, v, gp["p"][pi]), "rb").read()[o:o + l]
                r = pg.evaluate("""async ([l,v,t])=>{const o=await axGet(l,t,v);if(!o||!o.raw)return {ok:false,why:AX.why};const u=new Uint8Array(o.raw);return {ok:true,n:u.length,h:Array.from(u.slice(0,16)),t:Array.from(u.slice(-16)),d:o.b?o.b.duration:0}}""", [lang[v], v, t])
                ck(f"{v} « {t} » : lu dans l'appli ({r.get('n')} octets, {round(r.get('d', 0), 2)} s)", r["ok"] and r["n"] == len(attendu) and r["h"] == list(attendu[:16]) and r["t"] == list(attendu[-16:]) and r["d"] > 0.25, r)
        # secours : texte jamais enregistré → aucun clip (l'appli passe alors à sa voix système, comme aujourd'hui)
        r = pg.evaluate("""async ()=>{const o=await axGet('es','Zzz frase inexistente 123','es_laura');return {o:!!o,why:AX.why}}""")
        ck("secours : texte absent → aucun clip trouvé (raison « absent »), aucune autre voix substituée", not r["o"] and r["why"] == "absent", r)
        # une voix sans ce texte : l'appli cherche dans les autres voix de la même langue (comportement existant)
        for v in voix:
            l = lang[v]; autres = [x["id"] for x in VO[l] if x["id"] != v]
            gp = json.load(open(os.path.join(OUT, v, "gap.json"), encoding="utf-8"))
            for a in autres:
                ka = json.load(open(os.path.join(tmp, "v", a, a + ".json")))["k"]
                t = next((t for t in gp["k"] if t not in ka), None)
                if not t: continue
                r = pg.evaluate("""async ([l,a,t])=>{S.lang=l;ST.set('sobv_'+l,a);const o=await axGet(l,t,a);AX.last=null;aud('essai',[t]);for(let i=0;i<40&&!AX.last;i++)await new Promise(r=>setTimeout(r,100));stopSp();return {o:!!o,last:AX.last&&AX.last.v}}""", [l, a, t])
                ck(f"voix choisie {a} sans « {t} » : l'appli lit le clip de {v} (même langue), pas de voix système", not r["o"] and r["last"] == v, r)
                break
        ck("aucune erreur JavaScript", not err, err[:3]); b.close()
finally:
    srv.terminate(); shutil.rmtree(tmp, ignore_errors=True)
print(f"\n{sum(R)}/{len(R)} contrôles réussis"); sys.exit(0 if all(R) else 1)
