# Sobremesa en PWA

## 1. Mettre l'appli en ligne (GitHub Pages, gratuit)
1. Crée un dépôt public sur GitHub (ex. `sobremesa`).
2. Dépose-y TOUT le contenu des deux zips, en gardant les dossiers : `sobremesa-app.zip` (appli, tr/) et `sobremesa-audio.zip` (dossier a/ : voix et audios, ~230 Mo, GitHub accepte ça). Sur le site GitHub, glisse les fichiers par lots d'environ 100 maximum (« Add file > Upload files »). Plus simple : relie GitHub à Claude et je m'en occupe.
3. Dépôt > Settings > Pages > Source : « Deploy from a branch », branche `main`, dossier `/ (root)`.
4. L'adresse sera `https://TONNOM.github.io/sobremesa/` : ouvre-la sur ton téléphone, puis « Ajouter à l'écran d'accueil ».

Nouveau : le dossier `v/` contient les voix neuronales humaines (euskara : Antton ; galego : 3 voix ; valencià : Lluc, Gina ; català : Grau, Elia), ~320 Mo en plus. Dépose-le aussi à la racine. L'appli propose le choix de la voix dans Outils ; pour tout mot sans nouvelle voix, elle utilise l'ancienne.

## 2. Relais IA (conversation et traducteur)

Le relais est un Worker Cloudflare (`worker.js`) entre l'appli et Gemini. **Il est public par nature** : son adresse est dans `config.js`, servi à tout visiteur. Sa protection repose sur des plafonds durables, pas sur le secret de l'adresse. Voir aussi la réserve n°4 dans `RESERVES.md`.

**Fonctionnement**
- L'appli (`shim.js`) obtient d'abord un jeton **Cloudflare Turnstile** (vérification anti-robot, invisible sauf si Cloudflare demande un clic), puis l'échange contre une **session signée** (1 h) sur `POST /session`.
- Chaque appel IA (`POST /ai`) porte cette session. Le Worker vérifie la signature et l'expiration, puis n'accepte que les deux invites exactes de l'appli : conversation (`conv`) et traduction (`trad`). Toute autre invite est refusée.
- Le Worker choisit le modèle, la longueur maximale de réponse et les délais. Ses erreurs sont génériques (`unauthorized`, `rate_limited`, `unavailable`…).
- Les compteurs sont tenus par un **Durable Object** (`Budget`, stockage SQLite) : par session (total et par minute), par IP, global par jour (requêtes et volume de texte), nombre de sessions. Ils repartent à zéro à minuit UTC. Sans ce Durable Object, ou s'il est en erreur, le relais refuse tout (503).
- Quotas par défaut, réglables par variables du Worker :
  - `REQ_DAY` 2000 requêtes IA par jour au total, `CHARS_DAY` 4 000 000 caractères ;
  - `REQ_IP_DAY` 300 par IP (IPv4 complète, ou préfixe /64 en IPv6), `REQ_SESSION` 60 par session, `REQ_SESSION_MIN` 12 par minute ;
  - `SESS_IP_DAY` 20 sessions par IP, `SESS_DAY` 1000 sessions par jour, `SESSION_TTL` 3600 s.

**Mise en place (une fois)**

Le plus simple : préparer les deux clés des étapes 1 et 2, puis lancer `node deploiement/relais/deployer.mjs` (ou le même kit téléchargé). Il fait les étapes 3 à 5 tout seul, demande les clés en saisie masquée, génère `SESSION_SECRET` et `IP_SECRET`, déploie et vérifie (`--verifier` pour contrôler sans rien changer). Test du kit : `MINIFLARE_DIR=<dossier> node tests/deploiement_relais.mjs`. Détail manuel, si besoin :
1. Clé Gemini : https://aistudio.google.com/apikey. Dans Google Cloud, la restreindre à l'API « Generative Language ». Garder le projet sans facturation, ou abaisser les quotas et poser une alerte de budget.
2. Turnstile : Cloudflare > Turnstile > Add widget, nom d'hôte `maxxrqs.github.io`, mode « Managed » ou « Invisible ». Noter la **clé publique** (sitekey) et la **clé secrète**.
3. Depuis la racine du dépôt :
   - `cp wrangler.example.toml wrangler.toml`. Retirer le bloc `[[ratelimits]]` si le compte le refuse ;
   - `npx wrangler@4 login` ;
   - `npx wrangler@4 secret put GEMINI_KEY` ;
   - `npx wrangler@4 secret put TURNSTILE_SECRET` ;
   - `npx wrangler@4 secret put SESSION_SECRET` (valeur : `openssl rand -base64 48`) ;
   - `npx wrangler@4 secret put IP_SECRET` (autre valeur générée de la même façon : sert aux empreintes HMAC des IP, l'IP brute n'est jamais stockée).
   Les secrets se saisissent au clavier et ne vont jamais dans un fichier du dépôt.
4. Tests locaux (Gemini et Turnstile simulés), avec `npm install miniflare@3` dans un dossier de travail :
   - `MINIFLARE_DIR=<ce dossier> node tests/relais_worker.mjs`
   - `MINIFLARE_DIR=<ce dossier> node tests/relais_app.mjs`
5. Vérification sans envoi : `npx wrangler@4 deploy --dry-run --outdir /tmp/sobremesa-ia`. Puis déploiement : `npx wrangler@4 deploy` (le Worker garde son adresse `sobremesa-ia.….workers.dev`).
6. Dans `config.js` : `window.SOB_AI` (adresse du Worker) et `window.SOB_TS` (clé publique Turnstile). Puis `python3 build_pwa.py` et publication habituelle. Déployer la page juste après le Worker : une ancienne page reçoit des 401.
7. Contrôle : ouvrir `diag.html` sur le site. Il doit afficher « 401 → OK » sans session, puis une session et une traduction.

Sans relais (`SOB_AI` vide), l'appli marche avec le dictionnaire local et les fonctions IA affichent « indisponible ».

**Limites de sécurité**
- Turnstile freine les robots mais n'authentifie personne. Les plafonds sont la vraie protection.
- **Le plafond global est partagé par tous.** Quelques dizaines de sessions suffisent à l'épuiser en quelques minutes. L'IA est alors **indisponible pour tous les utilisateurs** jusqu'à minuit UTC, mais le coût reste borné. `REQ_SESSION` = 60 réduit la consommation d'une session isolée ; ce n'est pas une protection contre une attaque déterminée.
- Le jour des compteurs est fixé par l'horloge du Durable Object et ne recule jamais.
- Les offres gratuites Cloudflare ont leurs propres plafonds quotidiens : 100 000 requêtes Worker, et pour les Durable Objects 100 000 requêtes et 100 000 lignes écrites. Au-delà, le relais refuse (jamais d'accès sans plafond) jusqu'à minuit UTC.
- Toute modification des invites, mascottes ou scénarios de `castellano.html` doit être reportée dans `worker.js` (listes `MASCOTS`, `SCENES`, gabarits) et dans `diag.html`, et le Worker redéployé **avant** la page. `tests/relais_app.mjs` détecte l'écart.

## 3. Système audio (voix)

**Ordre de lecture d'un son** (tout est dans `castellano.html`, fonction `aud`) :
1. **Enregistrements** (`a/` pour le castillan, `v/<voix>/` pour valencià, català, galego, euskara) : clips MP3 mono 22 kHz regroupés en paquets de ~4,8 Mo avec un index `.json`. L'appli ne télécharge **que le clip demandé** (requête HTTP `Range`, quelques ko), le garde dans un cache persistant (`sobclips-v1`, ≈ 3000 clips max) et le rejoue sans réseau. Si le serveur ignore `Range`, elle prend le paquet entier et découpe.
2. **Voix du système** (Android, iOS, Windows, macOS), seulement si l'appareil a une voix **de la bonne langue** (castillan d'Espagne de préférence ; valencià : voix valencienne, sinon catalane). Jamais une voix d'une autre langue.
3. **Piper** (voix neuronale en WebAssembly, ~20 Mo, une fois) pour les textes dynamiques (traducteur, conversation). Le galicien est lu avec un modèle catalan : l'appli l'indique.
4. **eSpeak** en dernier recours, pour castillan/català/valencià seulement.
5. Sinon un message clair (hors ligne / réseau / pas de voix), sans lecture dans une mauvaise langue.

**Compléter les enregistrements** quand le contenu change : `tools/audio_enum.py` liste tous les textes que l'appli peut dire (`tests/audio_texts.json`), `tools/audio_merge.py` fusionne de nouveaux clips dans l'index d'une voix sans toucher aux paquets existants. Les clips ajoutés sont dans les paquets `*_g0.mp3`, `*_g1.mp3`…

**Tests** : `python3 tests/rangesrv.py 8774 .` (serveur avec `Range`, comme GitHub Pages) puis `python3 tests/audio.py http://127.0.0.1:8774/` (intégrité, couverture, langue/variante/voix, latence réseau bridé, hors ligne, secours) et `python3 tests/audio_quality.py` (signal des clips ajoutés).

## 4. Rappel quotidien (notifications, gratuit)
Le fichier `worker-rappel.js` est un second relais Cloudflare, séparé de celui de l'IA.
1. Cloudflare > Workers & Pages > Create > « Hello World », nomme-le `sobremesa-rappel`, colle `worker-rappel.js`, Deploy.
2. Storage & Databases > KV > Create : `sobremesa-rappels`. Puis Worker > Settings > Bindings > Add > KV namespace : nom de variable `SUBS`, espace `sobremesa-rappels`.
3. Worker > Settings > Trigger events > Add > Cron : `0 * * * *` (toutes les heures).
4. Copie l'adresse du worker dans `config.js` : `window.SOB_PUSH="https://sobremesa-rappel.….workers.dev";`
Les clés de notification se créent toutes seules au premier appel. Test : `node tests/rappel_worker.test.mjs`.

## 5. Reconnaissance vocale (exercices oraux)
Moteur : la reconnaissance du navigateur/système (`SpeechRecognition`), réglée sur la langue étudiée (`es-ES`, `ca-ES` pour català et valencià, `gl-ES`, `eu-ES`). Aucune dépendance ajoutée. La notation est dans le bloc `/*ASR-BEGIN*/…/*ASR-END*/` de `castellano.html` :
- tolérés : accents écrits, ponctuation, chiffres dictés (« 9 » = nueve, « 21 » = vint-i-un…), mots collés/coupés, seseo, yeísmo, b/v, h muette, formes valenciennes/centrales ;
- non validés : autre mot réel (pero/perro, playa/plaza, hablo/habla), ñ/ç (año/ano, plaça/placa), négation ajoutée ou oubliée, mot important manquant ;
- « répète » sans note : français entendu, castillan renvoyé pour une autre langue, phrase coupée, résultat partiel incomplet, hésitation du micro entre deux mots, confiance très basse (Chrome seulement).
Tests : `node tests/asr.test.js` (notation) et `python3 tests/mic.py URL` (micro simulé). Les essais sur vrais appareils restent manuels.

## 6. Explications contextuelles (chantier 3, lot A)

- Après une réponse, au plus **une** explication, repliée sous « Pourquoi ? » : erreur repérée par la correction (genre, nombre, terminaison du verbe) → règle qui illustre exactement cette forme ; erreur sur une notion encore fragile (palier ≤ 2) → sa règle, l'emploi du temps, le registre de l'expression ou une phrase d'exemple ; premier réemploi réussi d'une notion de grammaire, de conjugaison ou d'expression → une seule fois. Rien quand la notion est maîtrisée et la réponse juste.
- Le jour de la dernière explication est noté dans l'entrée du carnet (champ `x`) : pas de répétition le même jour, pas de second rappel après une réussite.
- Notions d'appui : dans une phrase à comprendre ou à écrire, les mots et expressions déjà suivis par le carnet gagnent une preuve (paliers 1–2 seulement, une à la fois) ; jamais de nouvelle entrée ni de date de révision modifiée ; une preuve partielle n'est retirée que si la correction situe l'erreur sur ce mot.
- Rattachement question → règle : `tools/qr_rattachements.tsv` (relu à la main ; « - » = aucune règle ne couvre la question). Après une modification des questions ou des règles (`XC`) : `python3 tools/qr_rattachements.py fiche <langue>` (questions à rattacher), compléter le TSV, puis `python3 tools/qr_rattachements.py generer` et `python3 build_pwa.py`. Contrôle : `python3 tools/qr_rattachements.py verifier`.
- Tests : `python3 tests/explications.py URL`.

## 7. Exercices intégrés (chantier 3, lot B)

Trois formats, déclarés dans `MKA` (autonomie exigée) et tirés comme les autres exercices (`NX`, `pickType`, `mkQ`) :
- **Complète** : phrase du corpus à 2 ou 3 trous (verbe conjugué, mot, préposition). Palier ≤ 1 : 2 trous et étiquettes (`itr`, autonomie 2) ; palier 2 : jusqu'à 3 trous ; palier ≥ 3 : trous à écrire (`itrE`, autonomie 3, infinitif indiqué pour un verbe).
- **Transforme** : phrase à un seul verbe, à la 1re ou 2e personne du singulier, sans pronom, possessif, subordonnée ni salutation. Palier ≤ 1 : autre personne du singulier, avec choix (`itf`, 2) ; palier 2 : personne ou vouvoiement (tú → usted, vostè/vosté, vostede) à écrire (`itfE`, 3) ; palier ≥ 3 : de préférence un autre temps enseigné (indicatif courant ; jamais avec un marqueur de temps, « ser », une périphrase verbe + infinitif). Basque : changement de personne seulement.
- **Réponds** : réplique d'un échange `XD`, réponse contrôlée par ses modèles. Palier ≤ 2 : étiquettes de la réponse modèle, 8 mots au plus (`irp`, 2) ; palier ≥ 3 : réponse libre notée par `eoGrade` (`irpE`, 4). La cible n'est comptée que si le modèle reconnu la contient.

Règles communes :
- Cible : notion du carnet fragile (palier ≤ 2) ou à revoir, jamais ancrée, par urgence (`mkUrg`) ; en révision (`mkRvQ`), la notion échue elle-même, une fois sur trois environ. Elle est jugée sur son propre trou (`q.ks`).
- Appuis : autres notions du carnet au palier ≥ 2 ; une preuve par appui réussi (`mkApp`, palier 2 au plus, ni entrée créée ni date changée) ; un trou d'appui faux ne fait reculer aucun palier.
- Rien d'exigé qui n'ait été enseigné : trous et réponses portent sur des notions du carnet, verbes à un temps enseigné (`R.kn.tk`, sinon `tLad`) ; phrases et échanges de la progression réellement effectuée (`R.kn`) ou, hors parcours, dont tous les mots suivis sont introduits (`adIn`).
- Trous sur des mots entiers (en basque, l'auxiliaire est un mot entier ; un auxiliaire seul après un participe n'est jamais pris pour « izan » ou « ukan »).
- Pas dans les étapes de découverte ni dans « S'entraîner » par compétence ; au plus 2 ou 3 par série de 10, sans en ajouter.
- Voix : seules les phrases du corpus et les répliques `XD` sont lues (enregistrées) ; la phrase transformée ne l'est jamais.
- Relecture linguistique : `python3 tools/integres_relecture.py URL` écrit `qa/integres_<langue>.md` (exemples par niveau), à faire valider par un locuteur natif avant publication.
- Tests : `python3 tests/integres.py URL`.

## 8. Mises en situation A1–C1 et contenus B1–C1 (chantier 3, lots C et D)

- **Situations** (`XI`, moteur d'immersion `immP`/`imStart`, étapes « T » dont le format suit le carnet) : 12 A1 + 12 A2 (lot C) et 6 B1 + 6 B2 + 6 C1 (lot D) par langue, soit 210. Sources : `tools/sit_data.py` (2 situations d'origine) et `tools/sit_suite_*.txt` (format décrit en tête de `sit_suite_a1.txt`) ; une consigne propre à une langue (6e champ) remplace la consigne commune quand le contenu diffère. Après modification : `python3 tools/sit_build.py`, `python3 tools/sit_relecture.py` (fiches `qa/situations_<langue>.md`, à faire relire), traductions de l'interface (`tools/sit_tr.json` puis `tr/*.json`), `python3 build_pwa.py`.
- Chaque phrase (réplique, modèle, réponses fausses) n'utilise que des notions introduites au plus tard dans le niveau de la situation ; la place dans le parcours (`sitLayout`) et l'ouverture (`sitOK`) suivent la progression réellement effectuée, indépendamment de la langue d'interface. Le premier échange (qui affiche aussi le contexte) est court pour tenir sur 360 × 640.
- **Paires à distinguer** (`XK`, lot D) : `tools/xk_data.txt` → `python3 tools/xk_build.py`. Dans la correction (`xpl`) : confusion précise entre les deux notions (forme de l'une attendue, forme de l'autre donnée, en réponse écrite ou en choix multiple) → explication de la paire, priorité 1 ; réponse juste sur une notion encore fragile (palier ≤ 2) → différence d'usage, une seule fois (marque dans `S.tp`, déjà utilisé par les astuces) et dans le budget des astuces. Une paire n'apparaît qu'à partir de son niveau et quand ses deux exemples ne contiennent que des notions déjà rencontrées. Aucune entrée de carnet créée, aucune date modifiée.
- **Astuces** (`TIPS`) : complétées pour le valencien, le catalan, le galicien et le basque (20 à 29 par langue, A1–C1) ; déclencheur = mot, expression ou phrase du parcours.
- **Audio** : répliques et mots « À retenir » à enregistrer avec `.github/workflows/audio-gen.yml` (plan `audio/plan.json`, 9 voix, jamais Laura), puis `tools/audio_merge.py`. Tant que ce n'est pas fait, `tests/situations.py` (contrôle audio) et `tests/audio_cover_full.py` signalent les textes lus par la voix de secours.
- Tests : `python3 tests/situations.py URL`, `python3 tests/xk.py URL`.
