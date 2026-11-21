"""Outils communs de la génération audio reproductible (GitHub Actions) : modèles verrouillés, moteurs, traitement, paquets."""
import hashlib, io, json, os, re, subprocess, sys, tempfile
import numpy as np, soundfile as sf

RACINE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOCK = json.load(open(os.path.join(RACINE, "audio", "modeles.lock.json"), encoding="utf-8"))
OUTILS = os.environ.get("AUDIO_OUTILS", "/tmp/audio_outils")
MODELES = os.environ.get("AUDIO_MODELES", "/tmp/audio_modeles")
SR = 22050


class Arret(SystemExit):
    """Arrêt explicite : le message est écrit dans le rapport et le job échoue."""


def axN(t):
    """Même normalisation que l'appli (axNk + axN) pour savoir si un texte est déjà enregistré."""
    return re.sub(r"[.…]+$", "", re.sub(r"\s+", " ", str(t)).strip().lower()).strip()


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def modele(cle):
    """Télécharge un modèle depuis sa source officielle (révision figée) et vérifie taille + SHA-256."""
    m = LOCK["modeles"].get(cle)
    if not m:
        raise Arret(f"MODÈLE INCONNU : {cle}")
    os.makedirs(MODELES, exist_ok=True)
    dest = os.path.join(MODELES, cle + "_" + os.path.basename(m.get("fichier") or m["url"]))
    if not (os.path.exists(dest) and os.path.getsize(dest) == m["taille"] and sha256(dest) == m["sha256"]):
        try:
            if "hf" in m:
                from huggingface_hub import hf_hub_download
                p = hf_hub_download(repo_id=m["hf"], filename=m["fichier"], revision=m["revision"])
                subprocess.run(["cp", "-L", p, dest], check=True)
            else:
                subprocess.run(["curl", "-sSfL", "--retry", "3", "-o", dest, m["url"]], check=True)
        except Exception as e:
            raise Arret(f"MODÈLE INACCESSIBLE : {cle} ({m.get('hf') or m.get('url')}) — {str(e)[:300]}")
    t, h = os.path.getsize(dest), sha256(dest)
    if t != m["taille"] or h != m["sha256"]:
        raise Arret(f"INTÉGRITÉ : {cle} taille {t} (attendu {m['taille']}), sha256 {h} (attendu {m['sha256']})")
    return dest


def prep(t):
    """Texte envoyé au moteur (pipeline des lots Dora/Laura) : sans points de suspension, ponctuation finale."""
    s = t.replace("…", "").strip()
    return s if s.endswith(("?", "!", ".")) else s + "."


# ---------- moteurs ----------
def _ahotts(lang, chemin_modele, texte):
    aho = os.path.join(OUTILS, "aHoTTS")
    vdir = os.path.join(aho, "ahotts", "voices", lang, "v_" + hashlib.sha1(chemin_modele.encode()).hexdigest()[:8])
    os.makedirs(vdir, exist_ok=True)
    lien = os.path.join(vdir, "vits.onnx")
    if not os.path.exists(lien):
        os.symlink(chemin_modele, lien)
    dic = {"es": ["-HDic=./ahotts/dicts/es/es_dicc"], "eu": ["-HDic=./ahotts/dicts/eu/eu_dicc"], "gl": ["-HDicDB=./ahotts/dicts/gl/cotovia"]}[lang]
    enc = "iso-8859-1" if lang in ("es", "eu") else "utf-8"
    try:
        data = texte.encode(enc)
    except UnicodeEncodeError as e:
        raise RuntimeError(f"caractère non encodable en {enc} : {e}")
    with tempfile.TemporaryDirectory() as td:
        w = os.path.join(td, "o.wav")
        env = dict(os.environ, LD_LIBRARY_PATH=aho)
        r = subprocess.run(["./ahotts/tts", f"-Lang={lang}", "-Method=Vits", *dic, f"-voice_path={vdir}", w], input=data, cwd=aho, env=env, capture_output=True, timeout=300)
        if not os.path.exists(w):
            raise RuntimeError("aHoTTS sans sortie : " + r.stderr.decode("latin-1")[-300:])
        x, sr = sf.read(w, dtype="float32")
    return (x if x.ndim == 1 else x.mean(1)), sr


_MX = {}


def _matxa(v, texte):
    if "s" not in _MX:
        import onnxruntime
        sys.path.insert(0, os.path.join(OUTILS, "minimal-tts-api"))
        from text import text_to_sequence  # noqa
        _MX["t2s"] = text_to_sequence
        o = onnxruntime.SessionOptions(); o.intra_op_num_threads = 2; o.inter_op_num_threads = 1
        _MX["s"] = onnxruntime.InferenceSession(modele("matxa"), sess_options=o, providers=["CPUExecutionProvider"])
    cl = {"valencia": "catalan_valencia_cleaners", "central": "catalan_cleaners"}[v["accent"]]
    seq = _MX["t2s"](texte, [cl])
    x = [0] * (len(seq) * 2 + 1); x[1::2] = seq
    P = LOCK["traitement"]["matxa"]
    ins = {"x": np.array(x, dtype=np.int64)[None], "x_lengths": np.array([len(x)], dtype=np.int64),
           "scales": np.array([P["temperature"], P["length_scale"]], dtype=np.float32), "spks": np.array([int(v["locuteur"])])}
    _, wav = _MX["s"].run(None, ins)
    return wav.squeeze(0).astype(np.float32), 22050


def _kokoro(v, texte):
    """Kokoro tourne dans son propre environnement (KOKORO_PY) : son phonémiseur intégré ne doit pas remplacer celui de Matxa."""
    py = os.environ.get("KOKORO_PY", sys.executable)
    with tempfile.TemporaryDirectory() as td:
        w = os.path.join(td, "o.wav")
        r = subprocess.run([py, os.path.join(os.path.dirname(os.path.abspath(__file__)), "kokoro_synth.py"), modele("kokoro"), modele("kokoro_voix"),
                            v["voix_kokoro"], str(v["vitesse"]), w], input=texte.encode("utf-8"), capture_output=True, timeout=300)
        if r.returncode or not os.path.exists(w):
            raise RuntimeError("Kokoro : " + r.stderr.decode("utf-8", "replace")[-300:])
        x, sr = sf.read(w, dtype="float32")
    return (x if x.ndim == 1 else x.mean(1)), sr


def synth(voix, texte, cle_modele=None):
    """Synthèse brute (float32, fréquence native) d'un texte pour une voix ; cle_modele force un modèle candidat (identification)."""
    v = LOCK["voix"][voix]
    t = prep(texte)
    if v["moteur"] == "ahotts":
        cm = cle_modele or v["modele"]
        if not cm:
            raise Arret(f"VOIX NON CONFIRMÉE : {voix} n'a pas de modèle validé dans audio/modeles.lock.json")
        return _ahotts(v["langue"], modele(cm), t)
    if v["moteur"] == "matxa":
        return _matxa(v, t)
    if v["moteur"] == "kokoro":
        return _kokoro(v, t)
    raise Arret(f"MOTEUR INCONNU : {v['moteur']}")


# ---------- traitement standard des clips de l'appli ----------
def _resample(x, sr):
    if sr == SR:
        return x
    b = (np.clip(x, -1, 1) * 32767).astype("<i2").tobytes()
    o = subprocess.run(["ffmpeg", "-v", "error", "-f", "s16le", "-ar", str(sr), "-ac", "1", "-i", "-", "-ar", str(SR), "-f", "f32le", "-"], input=b, capture_output=True, check=True).stdout
    return np.frombuffer(o, dtype="<f4").copy()


def traiter(x, sr):
    """Découpe au seuil de 2 % du pic, marges 0,01/0,04 s, niveau 0,75, silences 0,06/0,14 s, MP3 mono 22 050 Hz 32 kbit/s."""
    T = LOCK["traitement"]
    x = _resample(np.asarray(x, dtype=np.float32), sr)
    pk = float(np.abs(x).max()) if len(x) else 0.0
    if pk < 1e-4:
        raise RuntimeError("signal vide")
    nz = np.where(np.abs(x) > pk * T["seuil_decoupe"])[0]
    a = max(0, nz[0] - int(T["marge_avant"] * SR)); b = min(len(x), nz[-1] + int(T["marge_apres"] * SR))
    y = x[a:b] * (T["niveau"] / pk)
    y = np.concatenate([np.zeros(int(T["silence_avant"] * SR), np.float32), y, np.zeros(int(T["silence_apres"] * SR), np.float32)])
    pcm = (np.clip(y, -1, 1) * 32767).astype("<i2").tobytes()
    return subprocess.run(["ffmpeg", "-v", "error", "-f", "s16le", "-ar", str(SR), "-ac", "1", "-i", "-", *T["ffmpeg"], "-f", "mp3", "-"], input=pcm, capture_output=True, check=True).stdout


def decoder(b):
    w = subprocess.run(["ffmpeg", "-v", "error", "-i", "-", "-f", "wav", "-"], input=b, capture_output=True).stdout
    if not w:
        raise RuntimeError("décodage impossible")
    x, sr = sf.read(io.BytesIO(w), dtype="float32")
    return (x if x.ndim == 1 else x.mean(1)), sr


def index(voix):
    return json.load(open(os.path.join(RACINE, "v", voix, voix + ".json"), encoding="utf-8"))


def clip_existant(voix, texte):
    ix = index(voix)
    k = texte if texte in ix["k"] else next((x for x in ix["k"] if axN(x) == axN(texte)), None)
    if not k:
        return None
    pi, o, l = ix["k"][k]
    with open(os.path.join(RACINE, "v", voix, ix["p"][pi]), "rb") as f:
        f.seek(o); return f.read(l)


def prochain_paquet(voix):
    """Premier numéro gN libre : jamais un paquet existant (index ou fichier)."""
    ix = index(voix); n = -1
    for p in ix["p"]:
        m = re.search(r"_g(\d+)\.mp3$", p)
        if m: n = max(n, int(m.group(1)))
    n += 1
    while os.path.exists(os.path.join(RACINE, "v", voix, f"{voix}_g{n}.mp3")):
        n += 1
    return n
