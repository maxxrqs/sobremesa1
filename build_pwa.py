#!/usr/bin/env python3
"""Génère la PWA (index.html) à partir de castellano.html et change la version V de sw.js.

Source unique : castellano.html, dans le même dossier que ce script.
  python3 build_pwa.py                 construit : index.html + nouvelle version V dans sw.js (horodatage)
  python3 build_pwa.py --version 123   construit avec V="sobremesa-123"
  python3 build_pwa.py --index-only    régénère index.html sans toucher à sw.js
  python3 build_pwa.py --check         n'écrit rien ; code 1 si index.html n'est pas à jour (alias --dry-run)
Options de test : --root DIR (dossier source), --out DIR (dossier de sortie, par défaut = --root).

Le script n'écrit QUE index.html et sw.js (dans --out). Il ne touche ni à tr/, ni à a/, ni à v/.
Il ne dépend pas du contenu de la page : il insère deux blocs propres à la PWA à deux repères,
chacun devant exister exactement une fois dans castellano.html :
  - l'en-tête PWA, juste avant <meta charset="utf-8"> ;
  - les scripts de mise à jour / d'enregistrement du service worker, juste avant <script id="sm-app-js">.
"""
import argparse, os, re, sys, time

# 11 lignes insérées avant <meta charset="utf-8"> (la ligne vide et la répétition de la balise
# « notranslate » et du script de thème clair sont voulues : c'est l'index publié actuel, à l'octet près)
HEAD_ANCHOR = '<meta charset="utf-8">'
HEAD = '''<link rel="manifest" href="manifest.webmanifest">
<meta name="theme-color" content="#CFE9DC">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Sobremesa">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<link rel="icon" href="icon-192.png"><link rel="apple-touch-icon" href="icon-192.png">
<script src="config.js"></script><script src="shim.js"></script>

<meta name="google" content="notranslate">
<script>(function(){var r=document.documentElement,f=function(){if(r.getAttribute("data-theme")!=="light")r.setAttribute("data-theme","light");r.style.colorScheme="light"};f();try{new MutationObserver(f).observe(r,{attributes:true,attributeFilter:["data-theme","style","class"]})}catch(e){}})()</script>
'''

# 3 lignes insérées avant <script id="sm-app-js"> : rechargement différé quand l'appli est masquée
# (message « sob-new » envoyé par sw.js) et enregistrement de sw.js
FOOT_ANCHOR = '<script id="sm-app-js">'
FOOT = '''<script>/* mise à jour : la page vient déjà du réseau (sw.js) ; si une copie ancienne a dû être affichée (connexion lente), on ne recharge pas sous les yeux de l'utilisateur : on attend qu'il quitte l'appli */
if("serviceWorker"in navigator){let pend=0;const sobRl=()=>{if(document.visibilityState==="hidden")location.reload();else pend=1};navigator.serviceWorker.addEventListener("message",e=>{if(e.data==="sob-new")sobRl()});document.addEventListener("visibilitychange",()=>{if(pend&&document.visibilityState==="hidden"){pend=0;location.reload()}})}</script>
<script>if("serviceWorker"in navigator&&location.protocol!=="file:"){addEventListener("load",()=>navigator.serviceWorker.register("sw.js",{updateViaCache:"none"}).then(r=>{const up=()=>{try{r.update()}catch(e){}};document.addEventListener("visibilitychange",()=>{if(document.visibilityState==="visible")up()});void 0}).catch(()=>{}))}</script>
'''

# ligne de version de sw.js : const V="sobremesa-<version>" (le préfixe sert au nettoyage des anciens caches)
V_RE = re.compile(r'^(const V=")sobremesa-([A-Za-z0-9._-]+)(")', re.M)


class BuildError(Exception):
    pass


def read(p):
    with open(p, encoding="utf-8", newline="") as f:
        return f.read()


def write(p, text):
    tmp = p + ".tmp-build"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    os.replace(tmp, p)


def once(s, needle, what):
    n = s.count(needle)
    if n != 1:
        raise BuildError(f"{what} : « {needle} » trouvé {n} fois dans castellano.html (il en faut exactement 1)")
    return s.index(needle)


def build_index(src):
    if 'rel="manifest"' in src:
        raise BuildError("castellano.html contient déjà l'en-tête PWA (manifest) : ce n'est pas la source attendue")
    h = once(src, HEAD_ANCHOR, "repère de l'en-tête")
    f = once(src, FOOT_ANCHOR, "repère des scripts de fin")
    if not (src.find("<head>") < h < f < src.rfind("</body>")):
        raise BuildError("repères mal placés (attendu : <head> … meta charset … sm-app-js … </body>)")
    out = src[:h] + HEAD + src[h:f] + FOOT + src[f:]
    return out


def sw_version(sw):
    m = V_RE.findall(sw)
    if len(m) != 1:
        raise BuildError(f'sw.js : ligne const V="sobremesa-…" trouvée {len(m)} fois (il en faut exactement 1)')
    return m[0][1]


def set_version(sw, v):
    sw_version(sw)
    return V_RE.sub(lambda m: m.group(1) + "sobremesa-" + v + m.group(3), sw, count=1)


def first_diff_line(a, b):
    la, lb = a.split("\n"), b.split("\n")
    for i, (x, y) in enumerate(zip(la, lb), 1):
        if x != y:
            return i
    return min(len(la), len(lb)) + 1


def main(argv=None):
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(description="Construit index.html (PWA) depuis castellano.html et change la version de sw.js")
    ap.add_argument("--root", default=here, help="dossier contenant castellano.html et sw.js (défaut : celui du script)")
    ap.add_argument("--out", help="dossier où écrire index.html et sw.js (défaut : --root)")
    ap.add_argument("--version", help='version imposée : V devient "sobremesa-<version>" (défaut : horodatage)')
    ap.add_argument("--index-only", action="store_true", help="régénère index.html sans changer la version de sw.js")
    ap.add_argument("--check", "--dry-run", dest="check", action="store_true",
                    help="n'écrit rien ; code de sortie 1 si index.html n'est pas à jour")
    a = ap.parse_args(argv)
    root = os.path.abspath(a.root)
    out = os.path.abspath(a.out or root)
    try:
        idx = build_index(read(os.path.join(root, "castellano.html")))
        sw = read(os.path.join(root, "sw.js"))
        cur = sw_version(sw)
        if a.check:
            p = os.path.join(out, "index.html")
            have = read(p) if os.path.exists(p) else ""
            if have != idx:
                print(f"index.html PAS à jour par rapport à castellano.html (premier écart ligne {first_diff_line(have, idx)})."
                      " Lancer : python3 build_pwa.py")
                return 1
            print(f"index.html à jour ; sw.js version sobremesa-{cur}")
            return 0
        if a.version:
            v = a.version[len("sobremesa-"):] if a.version.startswith("sobremesa-") else a.version
            if not re.fullmatch(r"[A-Za-z0-9._-]+", v):
                raise BuildError("version invalide (lettres, chiffres, . _ - seulement)")
        else:
            v = str(int(time.time()))
            if v == cur:
                v = str(int(v) + 1)
        os.makedirs(out, exist_ok=True)
        new_sw = None if a.index_only else set_version(sw, v)
        write(os.path.join(out, "index.html"), idx)
        if new_sw is not None:
            write(os.path.join(out, "sw.js"), new_sw)
            print(f"PWA ok, version sobremesa-{v} (avant : sobremesa-{cur}), {len(idx.encode('utf-8')) // 1024} Ko")
        else:
            print(f"index.html ok (sw.js inchangé : sobremesa-{cur}), {len(idx.encode('utf-8')) // 1024} Ko")
        return 0
    except (BuildError, OSError) as e:
        print("ERREUR :", e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
