#!/usr/bin/env python3
"""Génère les clips manquants des situations du lot C (répliques du personnage + mots « À retenir »), voix par voix.
Lit audio/plan.json ; écrit out/<voix>/gap.json + <voix>_gN.mp3 (format de tools/audio_merge.py), out/generation.json.
Ne touche jamais au dossier v/ : la fusion se fait ensuite, à part, avec tools/audio_merge.py (qui n'écrase aucune clé).
Usage : python3 tools/audio_ci/generer.py [out]"""
import importlib.util, json, os, sys, time, traceback
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from commun import LOCK, RACINE, Arret, axN, index, prochain_paquet, synth, traiter, decoder
import numpy as np

# Sortie vide ou invalide du modèle (aHoTTS écrit alors un WAV silencieux sans erreur) : jusqu'à TENTATIVES synthèses
# de la même phrase, à texte, voix, modèle et paramètres identiques. Toute autre erreur n'est jamais relancée.
TENTATIVES = 4
RELANCABLES = ("signal vide", "mp3 silencieux", "décodage impossible")
CRETE_MIN = 0.05  # le clip traité est normalisé à 0,75 : en dessous, le MP3 n'est pas exploitable


class Echec(Exception):
    def __init__(self, msg, essais):
        super().__init__(msg); self.essais = essais


def controle_mp3(b):
    """Décode le MP3 produit et refuse un fichier vide ou silencieux."""
    x, _ = decoder(b)
    if not len(x) or float(np.abs(x).max()) < CRETE_MIN:
        raise RuntimeError("mp3 silencieux")


def clip(voix, t):
    """Renvoie (mp3, nombre d'essais) ; lève Echec(message, essais) après épuisement ou sur une erreur non relançable."""
    for n in range(1, TENTATIVES + 1):
        try:
            x, sr = synth(voix, t)
            b = traiter(x, sr); controle_mp3(b)
            return b, n
        except Arret:
            raise
        except Exception as e:
            m = str(e)[:200]
            if m not in RELANCABLES or n == TENTATIVES:
                raise Echec(m, n)

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(RACINE, "out")
PLAN = json.load(open(os.environ.get("AUDIO_PLAN") or os.path.join(RACINE, "audio", "plan.json"), encoding="utf-8"))


def textes_situations():
    sp = importlib.util.spec_from_file_location("d", os.path.join(RACINE, "tools", "sit_data.py"))
    d = importlib.util.module_from_spec(sp); sp.loader.exec_module(d)
    o = {}
    for l, ss in d.SIT.items():
        L = o.setdefault(l, [])
        for sid, (T, V) in ss.items():
            for t in T:
                if t[0] not in L: L.append(t[0])
            for w, _ in V:
                if w not in L: L.append(w)
    return o


def manquants(voix, textes):
    ks = {axN(k) for k in index(voix)["k"]}; vus = set(); o = []
    for t in textes:
        n = axN(t)
        if n in ks or n in vus: continue
        vus.add(n); o.append(t)
    return o


def main():
    os.makedirs(OUT, exist_ok=True)
    T = textes_situations(); res = {"mode": PLAN["mode"], "voix": {}}
    for voix in PLAN["voix"]:
        v = LOCK["voix"][voix]
        ok = v.get("statut") == "confirme" or (v.get("statut") == "provisoire" and PLAN["mode"] == "echantillon")
        if not ok or (v["moteur"] == "ahotts" and not v.get("modele")):
            raise Arret(f"VOIX NON CONFIRMÉE : {voix} (statut {v.get('statut')}, mode {PLAN['mode']}) — génération refusée")
        miss = manquants(voix, T.get(v["langue"], []))
        if PLAN["mode"] == "echantillon":
            # échantillon représentatif : la réplique la plus longue, la plus courte et un mot « À retenir » (ordre stable)
            rep = [t for t in miss if " " in t]; mots = [t for t in miss if t not in rep]
            sel = []
            for t in [max(rep, key=len, default=None), min(rep, key=len, default=None), (mots or [None])[0]]:
                if t and t not in sel: sel.append(t)
            miss = sel[: PLAN.get("par_voix", 3)]
        d = os.path.join(OUT, voix); os.makedirs(d, exist_ok=True)
        n0 = prochain_paquet(voix); pk = []; K = {}; cur = bytearray(); bad = []; essais = {}; t0 = time.time()
        for t in miss:
            try:
                b, n = clip(voix, t)
            except Echec as e:
                bad.append([t, str(e)]); essais[t] = {"tentatives": e.essais, "resultat": str(e)}; continue
            essais[t] = {"tentatives": n, "resultat": "valide"}
            if cur and len(cur) + len(b) > LOCK["traitement"]["paquet_max"]:
                pk.append(bytes(cur)); cur = bytearray()
            K[t] = [len(pk), len(cur), len(b)]; cur += b
        if cur: pk.append(bytes(cur))
        noms = [f"{voix}_g{n0 + i}.mp3" for i in range(len(pk))]
        for n, b in zip(noms, pk):
            open(os.path.join(d, n), "wb").write(b)
        json.dump({"p": noms, "k": K}, open(os.path.join(d, "gap.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
        res["voix"][voix] = {"demandes": miss, "generes": len(K), "echecs": bad, "tentatives": essais, "paquets": noms, "secondes": round(time.time() - t0, 1)}
        print(voix, len(K), "clips", len(bad), "échecs", flush=True)
    json.dump(res, open(os.path.join(OUT, "generation.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if any(r["echecs"] for r in res["voix"].values()):
        raise Arret("ÉCHECS DE SYNTHÈSE : voir out/generation.json")


if __name__ == "__main__":
    try:
        main()
    except Arret as e:
        os.makedirs(OUT, exist_ok=True); open(os.path.join(OUT, "ARRET.txt"), "a").write(str(e) + "\n"); print(e, file=sys.stderr); sys.exit(2)
    except Exception:
        traceback.print_exc(); sys.exit(3)
