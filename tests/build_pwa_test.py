#!/usr/bin/env python3
"""Test de build_pwa.py : python3 tests/build_pwa_test.py
Ne modifie pas le dépôt : toutes les constructions se font dans des dossiers temporaires."""
import os, re, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "build_pwa.py")
V_RE = re.compile(r'^const V="sobremesa-[^"]+"', re.M)
fails = 0


def run(*args):
    p = subprocess.run([sys.executable, "-B", SCRIPT, *args], capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr).strip()


def rd(p):
    with open(p, encoding="utf-8", newline="") as f:
        return f.read()


def ok(cond, msg):
    global fails
    print(("OK   " if cond else "FAIL ") + msg)
    if not cond:
        fails += 1


def snap(d):
    """noms, tailles et dates de tous les fichiers sous d"""
    r = {}
    for b, _, fs in os.walk(d):
        if "__pycache__" in b:
            continue
        for f in fs:
            p = os.path.join(b, f)
            st = os.stat(p)
            r[os.path.relpath(p, d)] = (st.st_size, st.st_mtime_ns)
    return r


def mini_root(t):
    """copie minimale du projet (sources + faux tr/, a/, v/)"""
    for f in ("castellano.html", "index.html", "sw.js"):
        shutil.copy2(os.path.join(ROOT, f), t)
    for d in ("tr", "a", "v/x"):
        os.makedirs(os.path.join(t, d))
        with open(os.path.join(t, d, "f.json"), "w") as f:
            f.write("{}")


idx_ref, sw_ref = rd(os.path.join(ROOT, "index.html")), rd(os.path.join(ROOT, "sw.js"))
cur = re.search(r'const V="sobremesa-([^"]+)"', sw_ref).group(1)
repo_before = {k: v for k, v in snap(ROOT).items() if not k.startswith(("a" + os.sep, "v" + os.sep))}

# 1. le dépôt actuel est cohérent
code, out = run("--check")
ok(code == 0, f"--check sur le dépôt : code {code} ({out})")

with tempfile.TemporaryDirectory() as t:
    # 2. reconstruction avec la version actuelle : identique à l'octet
    code, out = run("--out", t, "--version", cur)
    ok(code == 0, f"construction --version {cur} : code {code}")
    ok(rd(os.path.join(t, "index.html")) == idx_ref, "index.html produit identique à l'index actuel")
    ok(rd(os.path.join(t, "sw.js")) == sw_ref, "sw.js produit identique (même version)")
    ok(sorted(os.listdir(t)) == ["index.html", "sw.js"], f"seuls index.html et sw.js écrits : {sorted(os.listdir(t))}")

with tempfile.TemporaryDirectory() as t:
    # 3. version automatique : sw.js identique à la ligne de version près, version changée
    code, out = run("--out", t)
    sw = rd(os.path.join(t, "sw.js"))
    ok(code == 0 and V_RE.sub("V", sw) == V_RE.sub("V", sw_ref), "sw.js identique à la version près (version auto)")
    nv = re.search(r'const V="sobremesa-(\d+)"', sw)
    ok(bool(nv) and nv.group(1) != cur, f"version auto changée : {nv and nv.group(1)} (avant {cur})")
    code, out = run("--out", t, "--version", "sobremesa-42")
    ok('const V="sobremesa-42"' in rd(os.path.join(t, "sw.js")), "--version accepte le préfixe sobremesa-")
    code, out = run("--out", t, "--version", 'x"y')
    ok(code == 2, "--version invalide refusée")

with tempfile.TemporaryDirectory() as t:
    # 4. --check détecte un écart volontaire ; la construction ne dépend pas du corps de page
    mini_root(t)
    before = snap(t)
    code, out = run("--root", t, "--check")
    ok(code == 0, "--check à jour dans la copie")
    src = rd(os.path.join(t, "castellano.html")).replace("</body>", "<p>écart volontaire</p>\n</body>", 1)
    with open(os.path.join(t, "castellano.html"), "w", encoding="utf-8", newline="") as f:
        f.write(src)
    code, out = run("--root", t, "--check")
    ok(code == 1, f"--check détecte l'écart : code {code} ({out})")
    ok(rd(os.path.join(t, "index.html")) == idx_ref and rd(os.path.join(t, "sw.js")) == sw_ref, "--check n'a rien écrit")
    code, out = run("--root", t)
    idx = rd(os.path.join(t, "index.html"))
    ok(code == 0 and "<p>écart volontaire</p>" in idx, "le corps modifié est repris dans index.html")
    ok(idx.count('rel="manifest"') == 1 and idx.count("sob-new") == src.count("sob-new") + 1, "blocs PWA insérés une seule fois")
    code, out = run("--root", t, "--check")
    ok(code == 0, "--check à jour après reconstruction")
    after = snap(t)
    changed = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
    ok(changed == ["castellano.html", "index.html", "sw.js"], f"fichiers modifiés : {changed} (tr/, a/, v/ intacts)")
    # --index-only ne touche pas sw.js
    sw1 = rd(os.path.join(t, "sw.js"))
    code, out = run("--root", t, "--index-only")
    ok(code == 0 and rd(os.path.join(t, "sw.js")) == sw1, "--index-only laisse sw.js inchangé")

with tempfile.TemporaryDirectory() as t:
    # 5. repère absent ou doublé : erreur claire, rien n'est écrit
    mini_root(t)
    src = rd(os.path.join(ROOT, "castellano.html")).replace('<script id="sm-app-js">', '<script id="sm-app-js"></script><script id="sm-app-js">', 1)
    with open(os.path.join(t, "castellano.html"), "w", encoding="utf-8", newline="") as f:
        f.write(src)
    code, out = run("--root", t)
    ok(code == 2 and rd(os.path.join(t, "index.html")) == idx_ref and rd(os.path.join(t, "sw.js")) == sw_ref,
       f"repère doublé refusé sans écriture : code {code}")
    shutil.copy2(os.path.join(ROOT, "index.html"), os.path.join(t, "castellano.html"))
    code, out = run("--root", t)
    ok(code == 2, "index.html donné comme source : refusé")

repo_after = {k: v for k, v in snap(ROOT).items() if not k.startswith(("a" + os.sep, "v" + os.sep))}
ok(repo_before == repo_after, "dépôt inchangé par le test")
print("\n" + ("TOUT OK" if not fails else f"{fails} ÉCHEC(S)"))
sys.exit(1 if fails else 0)
