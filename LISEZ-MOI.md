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
