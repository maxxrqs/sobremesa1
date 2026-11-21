#!/usr/bin/env python3
"""Contrôles de la génération audio : (1) identité des voix — chaque modèle verrouillé régénère des phrases déjà enregistrées
dans l'appli et doit ressembler à SA voix plus qu'aux autres (MFCC + DTW, hauteur de voix) ; pour le galicien, matrice des
6 modèles HiTZ candidats × 3 voix de l'appli (proposition seulement, jamais appliquée) ; (2) chaque clip produit : texte = clé,
décodage complet, format, durée plausible, niveau, silences, pas de fichier vide ; (3) extraits d'écoute.
Usage : python3 tools/audio_ci/verifier.py [out]  (code 1 si un contrôle échoue)"""
import hashlib, json, os, subprocess, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from commun import LOCK, RACINE, SR, Arret, axN, clip_existant, decoder, index, synth, traiter

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(RACINE, "out")
PLAN = json.load(open(os.environ.get("AUDIO_PLAN") or os.path.join(RACINE, "audio", "plan.json"), encoding="utf-8"))
VOIX_APP = json.load(open(os.path.join(RACINE, "v", "voices.json"), encoding="utf-8"))
R = {"identite": {}, "galicien": None, "clips": {}, "echecs": []}


def echec(m):
    R["echecs"].append(m); print("ÉCHEC", m, flush=True)


# ---------- mesures acoustiques ----------
def _utile(x):
    a = np.abs(x); pk = a.max(); nz = np.where(a > pk * 0.02)[0]
    return x[nz[0]:nz[-1] + 1] if len(nz) else x


def mfcc(x, sr=SR):
    x = _utile(x); x = np.append(x[0], x[1:] - 0.97 * x[:-1])
    n, h = 512, 220
    if len(x) < n: x = np.pad(x, (0, n - len(x)))
    F = np.lib.stride_tricks.sliding_window_view(x, n)[::h] * np.hamming(n)
    P = np.abs(np.fft.rfft(F, n)) ** 2
    mel = lambda f: 2595 * np.log10(1 + f / 700); imel = lambda m: 700 * (10 ** (m / 2595) - 1)
    pts = imel(np.linspace(mel(60), mel(8000), 42)); b = np.floor((n + 1) * pts / sr).astype(int)
    fb = np.zeros((40, n // 2 + 1))
    for i in range(40):
        l, c, r = b[i], b[i + 1], b[i + 2]
        if c > l: fb[i, l:c] = (np.arange(l, c) - l) / (c - l)
        if r > c: fb[i, c:r] = (r - np.arange(c, r)) / (r - c)
    E = np.log(P @ fb.T + 1e-10)
    k = np.arange(40); D = np.cos(np.pi / 40 * (k[None, :] + 0.5) * np.arange(1, 14)[:, None])
    return E @ D.T


def dtw(a, b):
    C = np.sqrt(((a[:, None, :] - b[None, :, :]) ** 2).sum(-1)); n, m = C.shape
    D = np.full((n + 1, m + 1), np.inf); D[0, 0] = 0
    for i in range(1, n + 1):
        Ci = C[i - 1]; Dp = D[i - 1]; row = D[i]
        for j in range(1, m + 1):
            row[j] = Ci[j - 1] + min(Dp[j], Dp[j - 1], row[j - 1])
    return float(D[n, m] / (n + m))


def f0(x, sr=SR):
    x = _utile(x); n, h = 1024, 256; out = []
    for i in range(0, len(x) - n, h):
        f = x[i:i + n] - x[i:i + n].mean()
        if np.sqrt((f ** 2).mean()) < 0.02: continue
        ac = np.correlate(f, f, "full")[n - 1:]; lo, hi = sr // 400, sr // 60
        j = lo + int(np.argmax(ac[lo:hi]))
        if ac[j] > 0.45 * ac[0]: out.append(sr / j)
    return float(np.median(out)) if out else 0.0


ECOUTE = []
NOMS = {"es": "castillan", "va": "valencien", "ca": "catalan", "gl": "galicien", "eu": "basque"}


def modele_de(voix, cm=None):
    v = LOCK["voix"][voix]; m = cm or v.get("modele")
    return {"matxa": f"matxa (locuteur {v.get('locuteur')}, accent {v.get('accent')})", "kokoro": f"kokoro {v.get('voix_kokoro')}"}.get(m, m)


def ecoute(nom, morceaux):
    """morceaux : liste de (octets, étiquette) ; une entrée par fichier dans ecoute/INDEX.md (ordre, texte, voix, source)."""
    os.makedirs(os.path.join(OUT, "ecoute"), exist_ok=True)
    sil = np.zeros(int(0.8 * SR), np.float32); y = []; t0 = 0.0; seg = []
    for b, lab in morceaux:
        x, sr = decoder(b); seg.append(f"{t0:5.1f} s — {lab}"); y += [x, sil]; t0 += (len(x) + len(sil)) / SR
    pcm = (np.clip(np.concatenate(y), -1, 1) * 32767).astype("<i2").tobytes()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", str(SR), "-ac", "1", "-i", "-", "-b:a", "48k", os.path.join(OUT, "ecoute", nom + ".mp3")], input=pcm, check=True)
    ECOUTE.append((nom, seg))


def references(langue, n=4):
    vs = [x["id"] for x in VOIX_APP[langue]]; ix = [index(v)["k"] for v in vs]
    ks = [k for k in ix[0] if all(k in i for i in ix[1:]) and 15 <= len(k) <= 60 and len(k.split()) >= 3]
    return sorted(ks, key=lambda k: hashlib.sha1(k.encode()).hexdigest())[:n]


def comparer(voix, langue, cle_modele=None):
    """Distances entre la synthèse du modèle et les clips existants de chaque voix de la langue (moyenne sur les références)."""
    refs = references(langue); D = {v["id"]: [] for v in VOIX_APP[langue]}; F = []; gen = []
    for t in refs:
        x, sr = synth(voix, t, cle_modele); b = traiter(x, sr); g, _ = decoder(b); gen.append(b)
        mg = mfcc(g); F.append(f0(g))
        for v in D:
            e, _ = decoder(clip_existant(v, t)); D[v].append(dtw(mg, mfcc(e)))
    fa = {v: f0(decoder(clip_existant(v, refs[0]))[0]) for v in D}
    return {"refs": refs, "dist": {v: round(float(np.mean(d)), 2) for v, d in D.items()}, "f0_gen": round(float(np.median(F)), 1), "f0_app": {v: round(x, 1) for v, x in fa.items()}, "gen": gen}


def identite():
    for voix in PLAN.get("controle_identite", []):
        v = LOCK["voix"][voix]; c = comparer(voix, v["langue"]); g = c.pop("gen"); d = c["dist"]
        autres = {k: x for k, x in d.items() if k != voix}
        ok = all(d[voix] * 1.10 < x for x in autres.values()) if autres else None
        c["verdict"] = "identique" if ok else ("à juger (voix seule dans sa langue)" if ok is None else "DIFFÉRENTE")
        R["identite"][voix] = c
        L = NOMS[v["langue"]]
        ecoute(f"{voix}_comparaison_clip_actuel_puis_regenere", [m for t, b in zip(c["refs"][:2], g[:2]) for m in ((clip_existant(voix, t), f"{L} · {voix} · « {t} » · clip actuel de l'appli"), (b, f"{L} · {voix} · « {t} » · régénéré par {modele_de(voix)}"))])
        if ok is False: echec(f"identité : {voix} ne ressemble pas à sa voix de l'appli {d}")
    # voix seule dans sa langue (basque) : seuil tiré des voix confirmées identiques des autres langues
    same = [c["dist"][k] for k, c in R["identite"].items() if c["verdict"] == "identique"]
    diff = [x for k, c in R["identite"].items() if c["verdict"] == "identique" for v, x in c["dist"].items() if v != k]
    for k, c in R["identite"].items():
        if c["verdict"].startswith("à juger"):
            if same and diff:
                seuil = (max(same) + min(diff)) / 2; c["seuil"] = round(seuil, 2)
                c["verdict"] = "identique" if c["dist"][k] < seuil else "DIFFÉRENTE"
                if c["verdict"] != "identique": echec(f"identité : {k} au-dessus du seuil {seuil:.2f} ({c['dist'][k]})")
            else:
                echec(f"identité : {k} sans point de comparaison")


def galicien():
    if not PLAN.get("identifier_galicien"): return
    cand = LOCK["voix"]["gl_a"]["candidats"]; M = {}; G = {}
    for cm in cand:
        c = comparer("gl_a", "gl", cm); G[cm] = c.pop("gen"); M[cm] = c
    refs = M[cand[0]]["refs"]; prop = {}
    for app in ("gl_a", "gl_b", "gl_c"):
        rang = sorted(cand, key=lambda cm: M[cm]["dist"][app]); a, b = rang[0], rang[1]
        prop[app] = {"meilleur": a, "distance": M[a]["dist"][app], "suivant": b, "distance_suivant": M[b]["dist"][app],
                     "ecart_relatif": round((M[b]["dist"][app] - M[a]["dist"][app]) / M[a]["dist"][app], 3)}
        ecoute(f"gl_{app}_original_puis_6_candidats", [(clip_existant(app, refs[0]), f"galicien · {app} · « {refs[0]} » · clip actuel de l'appli")] + [(G[cm][0], f"galicien · « {refs[0]} » · candidat {cm}") for cm in cand])
    R["galicien"] = {"candidats": cand, "refs": refs, "matrice": {cm: M[cm]["dist"] for cm in cand}, "f0": {cm: M[cm]["f0_gen"] for cm in cand},
                     "f0_app": M[cand[0]]["f0_app"], "proposition": prop,
                     "note": "Proposition à valider par Max : aucune correspondance n'est appliquée automatiquement."}
    if len({p["meilleur"] for p in prop.values()}) < 3: echec("galicien : deux voix de l'appli désignent le même modèle")


def stats_voix(voix, n=40):
    ix = index(voix); ks = list(ix["k"])[-n:]; r = []
    for k in ks:
        pi, o, l = ix["k"][k]
        with open(os.path.join(RACINE, "v", voix, ix["p"][pi]), "rb") as f: f.seek(o); x, _ = decoder(f.read(l))
        r.append(len(x) / SR / max(1, len(k)))
    return float(np.median(r))


def clips():
    gen = json.load(open(os.path.join(OUT, "generation.json"), encoding="utf-8")) if os.path.exists(os.path.join(OUT, "generation.json")) else {"voix": {}}
    for voix, g in gen["voix"].items():
        d = os.path.join(OUT, voix); gp = json.load(open(os.path.join(d, "gap.json"), encoding="utf-8")); ref = stats_voix(voix); L = []
        if set(gp["k"]) != set(g["demandes"]): echec(f"{voix} : clés ≠ textes demandés")
        ixk = {axN(k) for k in index(voix)["k"]}
        for t, (pi, o, l) in gp["k"].items():
            p = os.path.join(d, gp["p"][pi]); b = open(p, "rb").read()
            pb = []
            if axN(t) in ixk: pb.append("texte déjà enregistré (écrasement)")
            if o + l > len(b) or l < 800: pb.append("position/longueur")
            try:
                x, sr = decoder(b[o:o + l])
            except Exception as e:
                pb.append("décodage"); L.append([t, pb]); echec(f"{voix} « {t} » : {pb}"); continue
            dur = len(x) / sr; a = np.abs(x); pk = float(a.max()); nz = np.where(a > pk * 0.02)[0]
            lead, tail = nz[0] / sr, (len(x) - nz[-1]) / sr; spc = dur / max(1, len(t))
            info = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=channels,sample_rate,bit_rate", "-of", "json", "-"], input=b[o:o + l], capture_output=True).stdout
            s = json.loads(info or b"{}").get("streams", [{}])[0]
            if sr != SR or int(s.get("channels", 0)) != 1: pb.append(f"format {sr} Hz {s.get('channels')} canaux")
            if dur < 0.3: pb.append(f"trop court {dur:.2f} s")
            if not 0.4 * ref <= spc <= 2.5 * ref: pb.append(f"durée {spc:.3f} s/car (voix : {ref:.3f})")
            if not 0.6 <= pk <= 0.9: pb.append(f"niveau {pk:.2f}")
            if not (0.06 <= lead <= 0.25 and 0.12 <= tail <= 0.35): pb.append(f"silences {lead:.2f}/{tail:.2f}")
            if float(np.sqrt((x ** 2).mean())) < 0.01: pb.append("quasi silencieux")
            L.append({"texte": t, "duree": round(dur, 2), "s_par_car": round(spc, 3), "pic": round(pk, 2), "silences": [round(float(lead), 2), round(float(tail), 2)], "problemes": pb})
            if pb: echec(f"{voix} « {t} » : {pb}")
        R["clips"][voix] = {"reference_s_par_car": round(ref, 3), "clips": L}
        if gp["k"]:
            lg_ = LOCK["voix"][voix]["langue"]
            ecoute(f"{voix}_nouveaux_textes", [(open(os.path.join(d, gp["p"][pi]), "rb").read()[o:o + l], f"{NOMS[lg_]} · {voix} · « {t} » · nouveau clip, {modele_de(voix)}") for t, (pi, o, l) in gp["k"].items()])


def rapport():
    m = ["# Rapport de génération audio", "", f"Mode : {PLAN['mode']} · échecs : {len(R['echecs'])}", ""]
    if R["echecs"]: m += ["## Échecs", ""] + [f"- {e}" for e in R["echecs"]] + [""]
    if R["identite"]:
        m += ["## Identité des voix (distance MFCC-DTW, plus petit = plus proche)", "", "| Voix | Distances aux voix de l'appli | F0 générée / appli | Verdict |", "|---|---|---|---|"]
        for k, c in R["identite"].items():
            m.append(f"| {k} | {', '.join(f'{v} {x}' for v, x in c['dist'].items())} | {c['f0_gen']} / {c['f0_app'].get(k)} Hz | {c['verdict']}{' (seuil ' + str(c['seuil']) + ')' if 'seuil' in c else ''} |")
        m.append("")
    if R["galicien"]:
        G = R["galicien"]; m += ["## Galicien : modèles HiTZ candidats × voix de l'appli (proposition à valider)", "", "| Modèle | gl_a (Voz C) | gl_b (Voz A) | gl_c (Voz B) | F0 |", "|---|---|---|---|---|"]
        for cm in G["candidats"]:
            d = G["matrice"][cm]; m.append(f"| {cm} | {d['gl_a']} | {d['gl_b']} | {d['gl_c']} | {G['f0'][cm]} Hz |")
        m += ["", f"F0 des voix de l'appli : {G['f0_app']}", ""] + [f"- **{a}** : {p['meilleur']} ({p['distance']}), puis {p['suivant']} ({p['distance_suivant']}), écart {p['ecart_relatif'] * 100:.0f} %" for a, p in G["proposition"].items()] + ["", G["note"], ""]
    for v, c in R["clips"].items():
        m += [f"## Clips {v}", ""] + [f"- « {x['texte']} » : {x['duree']} s, {x['s_par_car']} s/car (voix {c['reference_s_par_car']}), pic {x['pic']}, silences {x['silences']}{' — ' + '; '.join(x['problemes']) if x['problemes'] else ' — conforme'}" for x in c["clips"]] + [""]
    if ECOUTE:
        m += ["## Extraits d'écoute (dossier ecoute/)", ""]
        for nom, seg in ECOUTE: m += [f"### {nom}.mp3", ""] + [f"- {x}" for x in seg] + [""]
    open(os.path.join(OUT, "rapport.md"), "w", encoding="utf-8").write("\n".join(m))
    json.dump(R, open(os.path.join(OUT, "rapport.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    try:
        identite(); galicien(); clips()
    except Arret as e:
        echec(str(e))
    rapport(); print(open(os.path.join(OUT, "rapport.md"), encoding="utf-8").read())
    sys.exit(1 if R["echecs"] else 0)
