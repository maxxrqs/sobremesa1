# Sobremesa en PWA

## 1. Mettre l'appli en ligne (GitHub Pages, gratuit)
1. Crée un dépôt public sur GitHub (ex. `sobremesa`).
2. Dépose-y TOUT le contenu des deux zips, en gardant les dossiers : `sobremesa-app.zip` (appli, tr/) et `sobremesa-audio.zip` (dossier a/ : voix et audios, ~230 Mo, GitHub accepte ça). Sur le site GitHub, glisse les fichiers par lots d'environ 100 maximum (« Add file > Upload files »). Plus simple : relie GitHub à Claude et je m'en occupe.
3. Dépôt > Settings > Pages > Source : « Deploy from a branch », branche `main`, dossier `/ (root)`.
4. L'adresse sera `https://TONNOM.github.io/sobremesa/` : ouvre-la sur ton téléphone, puis « Ajouter à l'écran d'accueil ».

Nouveau : le dossier `v/` contient les voix neuronales humaines (euskara : Antton ; galego : 3 voix ; valencià : Lluc, Gina ; català : Grau, Elia), ~320 Mo en plus. Dépose-le aussi à la racine. L'appli propose le choix de la voix dans Outils ; pour tout mot sans nouvelle voix, elle utilise l'ancienne.

## 2. Brancher l'IA plus tard (gratuit)
1. Clé Gemini gratuite : https://aistudio.google.com/apikey
2. Compte gratuit sur https://dash.cloudflare.com > Workers & Pages > Create > « Hello World » > colle `worker.js` > Deploy.
3. Worker > Settings > Variables : ajoute `GEMINI_KEY` (type Secret) et `ALLOWED_ORIGIN` = `https://TONNOM.github.io`.
4. Copie l'adresse du Worker dans `config.js` : `window.SOB_AI="https://….workers.dev";` puis recommit.

Sans cette étape, l'appli marche avec le dictionnaire local et les fonctions IA affichent « indisponible ».


## 3. Système audio (voix)

**Ordre de lecture d'un son** (tout est dans `castellano.html`, fonction `aud`) :
1. **Enregistrements** (`a/` pour le castillan, `v/<voix>/` pour valencià, català, galego, euskara) : clips MP3 mono 22 kHz regroupés en paquets de ~4,8 Mo avec un index `.json`. L'appli ne télécharge **que le clip demandé** (requête HTTP `Range`, quelques ko), le garde dans un cache persistant (`sobclips-v1`, ≈ 3000 clips max) et le rejoue sans réseau. Si le serveur ignore `Range`, elle prend le paquet entier et découpe.
2. **Voix du système** (Android, iOS, Windows, macOS), seulement si l'appareil a une voix **de la bonne langue** (castillan d'Espagne de préférence ; valencià : voix valencienne, sinon catalane). Jamais une voix d'une autre langue.
3. **Piper** (voix neuronale en WebAssembly, ~20 Mo, une fois) pour les textes dynamiques (traducteur, conversation). Le galicien est lu avec un modèle catalan : l'appli l'indique.
4. **eSpeak** en dernier recours, pour castillan/català/valencià seulement.
5. Sinon un message clair (hors ligne / réseau / pas de voix), sans lecture dans une mauvaise langue.

**Compléter les enregistrements** quand le contenu change : `tools/audio_enum.py` liste tous les textes que l'appli peut dire (`tests/audio_texts.json`), `tools/audio_merge.py` fusionne de nouveaux clips dans l'index d'une voix sans toucher aux paquets existants. Les clips ajoutés sont dans les paquets `*_g0.mp3`, `*_g1.mp3`…

**Tests** : `python3 tests/rangesrv.py 8774 .` (serveur avec `Range`, comme GitHub Pages) puis `python3 tests/audio.py http://127.0.0.1:8774/` (intégrité, couverture, langue/variante/voix, latence réseau bridé, hors ligne, secours) et `python3 tests/audio_quality.py` (signal des clips ajoutés).
