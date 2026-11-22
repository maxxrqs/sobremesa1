#!/usr/bin/env python3
"""Tests des nouvelles tentatives de generer.py (sortie vide ou invalide), sans moteur réel : synth est remplacé par une fausse synthèse.
Usage : python3 tools/audio_ci/test_generer.py"""
import json, os, sys, tempfile
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generer as G

SR = 22050
SON = (0.5 * np.sin(2 * np.pi * 220 * np.arange(int(0.4 * SR)) / SR)).astype(np.float32)
VIDE = np.zeros(int(0.4 * SR), np.float32)
ok = 0; ko = 0


def verif(nom, cond):
    global ok, ko
    print(("OK  " if cond else "ÉCHEC ") + nom)
    ok += bool(cond); ko += not cond


def faux_synth(scenario, appels):
    """scenario : texte -> liste de sorties successives ('son', 'vide', 'muet' ou une exception)."""
    def s(voix, t):
        appels.append((voix, t))
        r = scenario[t][min(len([a for a in appels if a[1] == t]) - 1, len(scenario[t]) - 1)]
        if isinstance(r, BaseException): raise r
        return {"son": SON, "vide": VIDE}[r], SR
    return s


def lancer(scenario, deja=()):
    """Exécute G.main() sur une fausse voix gl_b avec les textes du scénario ; deja = textes déjà présents dans l'index."""
    appels = []
    with tempfile.TemporaryDirectory() as out:
        G.OUT = out
        G.PLAN = {"mode": "complet", "voix": ["gl_b"]}
        G.textes_situations = lambda: {"gl": list(scenario) + list(deja)}
        G.index = lambda v: {"p": [], "k": {t: [0, 0, 1] for t in deja}}
        G.prochain_paquet = lambda v: 99
        G.synth = faux_synth({**scenario, **{t: [AssertionError("synthèse d'un clip déjà valide")] for t in deja}}, appels)
        try:
            G.main(); arret = None
        except G.Arret as e:
            arret = str(e)
        r = json.load(open(os.path.join(out, "generation.json")))["voix"]["gl_b"]
        gap = json.load(open(os.path.join(out, "gl_b", "gap.json")))
        tailles = {n: os.path.getsize(os.path.join(out, "gl_b", n)) for n in gap["p"]}
    return r, gap, tailles, appels, arret


# 1. première sortie vide, puis sortie valide
r, gap, tl, ap, arret = lancer({"A": ["vide", "son"]})
verif("vide puis valide : 2 synthèses", len(ap) == 2)
verif("vide puis valide : clip retenu", "A" in gap["k"] and r["echecs"] == [] and arret is None)
verif("vide puis valide : generation.json", r["tentatives"]["A"] == {"tentatives": 2, "resultat": "valide"})

# 2. sorties vides jusqu'à épuisement
r, gap, tl, ap, arret = lancer({"B": ["vide", "vide", "vide", "vide", "son"]})
verif("épuisement : exactement 4 synthèses, pas de 5e", len(ap) == G.TENTATIVES == 4)
verif("épuisement : aucun clip, échec signalé", gap["k"] == {} and r["echecs"] == [["B", "signal vide"]])
verif("épuisement : la CI s'arrête", arret is not None and "ÉCHECS DE SYNTHÈSE" in arret)
verif("épuisement : generation.json", r["tentatives"]["B"] == {"tentatives": 4, "resultat": "signal vide"})

# 3. sortie valide dès la première tentative
r, gap, tl, ap, arret = lancer({"C": ["son"]})
verif("valide d'emblée : 1 seule synthèse", len(ap) == 1)
verif("valide d'emblée : generation.json", r["tentatives"]["C"] == {"tentatives": 1, "resultat": "valide"})
verif("valide d'emblée : MP3 non vide", all(t > 0 for t in tl.values()) and gap["k"]["C"][2] > 0)

# 4. aucune nouvelle synthèse d'un clip déjà valide (présent dans l'index)
r, gap, tl, ap, arret = lancer({"D": ["son"]}, deja=("Déjà enregistré",))
verif("clip déjà valide : jamais synthétisé", all(t != "Déjà enregistré" for _, t in ap))
verif("clip déjà valide : ni demandé ni réécrit", r["demandes"] == ["D"] and "Déjà enregistré" not in gap["k"])

# 5. les erreurs sans rapport ne sont pas relancées ni masquées
r, gap, tl, ap, arret = lancer({"E": [RuntimeError("aHoTTS sans sortie : erreur"), "son"]})
verif("autre erreur : 1 seule synthèse", len(ap) == 1)
verif("autre erreur : message d'origine conservé", r["echecs"] == [["E", "aHoTTS sans sortie : erreur"]] and arret is not None)
ap = []; G.synth = faux_synth({"F": [G.Arret("MODÈLE INACCESSIBLE : test"), "son"]}, ap)
try:
    G.clip("gl_b", "F"); verif("Arret (modèle, intégrité) propagé sans tentative", False)
except G.Arret as e:
    verif("Arret (modèle, intégrité) propagé sans tentative", "MODÈLE INACCESSIBLE" in str(e) and len(ap) == 1)

# 6. un MP3 créé mais silencieux n'est pas une réussite : il est refusé puis relancé
import subprocess
from commun import traiter as vrai_traiter
MUET = subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "anullsrc=r=22050:cl=mono", "-t", "0.5", "-b:a", "32k", "-f", "mp3", "-"], capture_output=True, check=True).stdout
try:
    G.controle_mp3(MUET); verif("MP3 silencieux refusé", False)
except RuntimeError as e:
    verif("MP3 silencieux refusé", str(e) == "mp3 silencieux")
G.controle_mp3(vrai_traiter(SON, SR)); verif("MP3 audible accepté", True)
n = [0]
def traiter_muet_puis_bon(x, sr):
    n[0] += 1
    return MUET if n[0] == 1 else vrai_traiter(x, sr)
G.traiter = traiter_muet_puis_bon
r, gap, tl, ap, arret = lancer({"G": ["son", "son"]})
G.traiter = vrai_traiter
verif("MP3 silencieux puis valide : 2 synthèses, clip retenu", len(ap) == 2 and "G" in gap["k"] and r["tentatives"]["G"]["tentatives"] == 2)

print(f"\n{ok} OK, {ko} échec(s)")
sys.exit(1 if ko else 0)
