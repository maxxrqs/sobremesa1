# Réserves ouvertes — à lire avant toute publication

Ce fichier recense les points connus qui ne sont **pas résolus**. Une réserve ne passe à « RÉSOLUE » que sur décision de Max, une fois la correction déployée et vérifiée. Ne jamais la présenter comme résolue avant.

---

## n°4 — Relais IA exposé — OUVERTE (correctif préparé, non déployé)

**Constat (audit du 7 novembre, vérifié dans le code le 15 novembre 2026)**

- L'adresse du relais IA (Worker Cloudflare) est publique. Elle figure dans `config.js`, et le site GitHub Pages lui-même la sert à tout visiteur : rendre le dépôt privé ne la cacherait pas.
- L'ancien `worker.js` n'authentifie personne :
  - le contrôle d'origine (`Origin`) se falsifie en une ligne hors navigateur ;
  - la limite de 150 requêtes par IP et par jour vit dans la mémoire d'une seule instance (`new Map()`), qui n'est ni globale ni durable, et `hits.clear()` remet tout à zéro ;
  - l'invite est libre (30 messages de 20 000 caractères), sans plafond de réponse ;
  - les erreurs de Google sont renvoyées au client.
- Conséquence : n'importe qui peut se servir du relais comme d'une IA gratuite. Effets possibles :
  - épuisement du quota Gemini (panne de la conversation et du traducteur) ;
  - coûts sans plafond si la facturation Google est active ;
  - usages imputés au compte de Max.
- Aucune clé n'a été trouvée dans le dépôt ni dans son historique : `worker.js` ne contient qu'une valeur d'attente. La clé réelle est dans le Worker déployé, probablement collée dans son code plutôt qu'enregistrée en secret, ce qui reste à vérifier.

**Correctif préparé** (`worker.js`, `shim.js`, `config.js`, `diag.html`, `LISEZ-MOI.md` section 2, `wrangler.example.toml`, tests `tests/relais_worker.mjs` et `tests/relais_app.mjs`)

- Secrets uniquement dans `env` Cloudflare : `GEMINI_KEY`, `TURNSTILE_SECRET`, `SESSION_SECRET` et `IP_SECRET` (ces deux derniers : 32 caractères ou plus). S'il en manque un, le relais répond 503.
- Turnstile vérifié côté Worker :
  - nom d'hôte, action `sobremesa-ia` et ancienneté de 5 min au plus ;
  - usage unique du jeton imposé par le Worker, parce que Cloudflare peut encore accepter un jeton rejoué dans les 5 premières secondes.
- Session signée HMAC, d'1 h par défaut, vérifiée à chaque appel : signature, expiration, durée maximale.
- Plafonds durables tenus par un Durable Object (`Budget`, stockage SQLite) :
  - par session : total et par minute ;
  - par IP et par jour : adresse IPv4 complète, ou **préfixe /64 en IPv6** (un abonné IPv6 dispose de tout un /64). Empreinte HMAC avec `IP_SECRET` ; l'IP brute n'est jamais stockée ;
  - global par jour, en requêtes et en volume de texte ;
  - sessions par IP et sessions globales.
  - Le Durable Object n'est consulté qu'avec une session valide ou un jeton Turnstile valide.
  - Tout incident du Durable Object (erreur, quota Cloudflare épuisé, réponse illisible ou ambiguë, silence de plus de 5 s), comme une erreur du limiteur, entraîne un refus (503), jamais un accès sans plafond.
  - Un client déjà bloqué l'est aussi dans la mémoire de l'instance, ce qui épargne le Durable Object. Ce cache ne contient que des refus, pour la durée fixée par le Durable Object : il n'autorise jamais rien.
  - **Horloge** : le Durable Object date chaque opération avec sa propre horloge, au moment du traitement. Le Worker et le client ne lui transmettent aucune heure.
  - **Le jour courant ne recule jamais** : une horloge en retard est ramenée au jour enregistré, et la minute d'une session ne recule pas non plus. Une requête commencée avant minuit et traitée après est comptée sur le nouveau jour. L'exploitation constatée lors de la revue du 15 novembre (requêtes datées d'avant minuit qui remettaient les compteurs à zéro) est rejouée par les tests et échoue désormais.
- Limiteur natif `RL_IP` facultatif, contre les rafales. Il n'est ni global ni exact, et ne remplace pas le Durable Object.
- Corps limité à 32 Ko, y compris en flux.
- Longueur de l'invite vérifiée **avant toute analyse** : 12 Ko (12 288 caractères) pour la conversation, 6 Ko (6 144) pour la traduction. L'analyse compare ensuite l'invite à des gabarits reconstruits, sans expression régulière à retour arrière : moins de 0,5 ms mesurée pour les pires entrées autorisées.
- **Plus d'usage généraliste** : seuls les deux gabarits de l'appli sont acceptés, conversation (`conv`) et traduction (`trad`). Le Worker reconstruit l'invite à l'identique à partir de listes fermées (mascottes, scénarios, langues, niveaux) et de champs limités :
  - texte à traduire : 3 000 caractères ;
  - historique : 14 messages, 1 500 caractères par ligne, 6 000 au total.
  - Toute autre invite est refusée (400) sans appel à Gemini.
- Modèles, `maxOutputTokens` (2 048 pour la conversation, 4 096 pour la traduction) et température décidés par le serveur. Délai total maîtrisé : moins de 30 s.
- Erreurs génériques. Les journaux ne contiennent ni clé, ni jeton, ni IP, ni texte.
- `shim.js` : obtient la session (widget Turnstile invisible, sauf si Cloudflare demande une interaction), la renouvelle une fois sur 401, et signale les 429 à l'appli (messages existants « Trop de demandes… »).

**Mise à jour du 20 novembre 2026 (branche `securite-relais`, non déployée)**

- L'appli envoie désormais une nouvelle invite de conversation (correction et explication séparées, explication dans la langue de l'apprenant). Le Worker préparé la refusait (400) : l'appli retombait sur l'ancienne invite (repli `CVLEG`), avec un appel en double et une explication non garantie dans la langue de l'apprenant. `worker.js` accepte maintenant les deux versions, reconstruites à l'identique ; toute variante trafiquée reste refusée sans appel à Gemini.
- Empreinte de `worker.js` mise à jour dans `deploiement/relais/relais.json`.
- Tests ajoutés : invite actuelle et ancienne acceptées, invites trafiquées refusées, Turnstile ou Gemini injoignables (refus générique), relais injoignable côté appli (message d'erreur, saisie de nouveau disponible).
- **Toujours OUVERTE** : le Worker en ligne n'a pas été redéployé depuis cette session (accès réseau refusé vers `workers.dev` et `github.io`). La réserve ne sera fermée qu'après déploiement et vérification en ligne (procédure ci-dessous, étape 6).

**Limites résiduelles**, même après déploiement

- Turnstile n'est pas une authentification. Une personne motivée peut résoudre des vérifications (à la main ou via des services payants) et obtenir des sessions. Le relais reste donc **public** : seuls les plafonds bornent l'abus.
- **Épuisement du quota global : risque principal, non résolu.** Le plafond global (`REQ_DAY`, 2 000 requêtes par jour par défaut) est partagé par tous les utilisateurs.
  - Avec `REQ_SESSION` = 60 et 12 requêtes par minute et par session, quelqu'un qui obtient environ 34 sessions (34 vérifications Turnstile, faisables à la main ou via un service payant, en changeant d'IP ou de /64) épuise ce plafond en quelques minutes. Les 1 000 sessions du jour s'épuisent de la même façon.
  - Conséquence : l'IA (conversation et traducteur) est **indisponible pour tous les utilisateurs** jusqu'à minuit UTC. Le reste de l'appli fonctionne.
  - C'est voulu : mieux vaut une panne qu'une facture. Le coût reste borné.
  - Abaisser `REQ_SESSION` de 150 à 60 réduit la consommation d'une session isolée et oblige à ouvrir davantage de sessions. **Ce n'est pas une protection contre une attaque déterminée.**
  - À surveiller : la fréquence des refus « global » dans les journaux du Worker (`"code":"rate_limited"`).
- Les deux gabarits restent utilisables pour obtenir des traductions ou des conversations, dans les limites. Le texte de l'apprenant et le texte à traduire peuvent contenir des tentatives d'injection : les consignes « data, never instructions » et le format JSON imposé en limitent l'intérêt sans l'annuler.
- Couplage : toute modification des invites, mascottes ou scénarios dans `castellano.html` doit être reportée dans `worker.js`, et le Worker redéployé **avant** la page. `tests/relais_app.mjs` détecte l'écart.
- `diag.html` contient une copie du gabarit de traduction : il est concerné par le même couplage (testé par `tests/relais_app.mjs`).
- Offres gratuites Cloudflare (au 15 novembre 2026) : 100 000 requêtes Worker par jour ; pour les Durable Objects (SQLite uniquement), 100 000 requêtes, 100 000 lignes écrites et 5 millions de lignes lues par jour. Une fois ces seuils dépassés, Cloudflare refuse, et le relais avec lui, jusqu'à minuit UTC. Quelqu'un qui inonde le Worker de requêtes peut donc couper l'IA pour la journée, sans jamais obtenir d'accès gratuit.
- Écritures SQLite, mesurées par test (en supposant une ligne par clé écrite ou supprimée, ce que la documentation ne précise pas pour l'API clé-valeur sur SQLite) :
  - 3 par requête IA acceptée, 3 par session ouverte, 0 par refus ;
  - 1 par jour (« day »), plus une suppression par clé de la veille au premier appel du jour.
  - Pire cas avec les plafonds par défaut : 2 000 × 3 + 1 000 × 3 + environ 3 000 suppressions ≈ 12 000 lignes par jour, soit 12 % du quota gratuit. Le plafond `REQ_DAY` ne doit pas dépasser environ 25 000.
  - À confirmer dans les métriques Cloudflare après déploiement.
- Requêtes au Durable Object : 1 par appel autorisé. Un client bloqué en coûte au plus 1 par instance du Worker et par fenêtre (minute, session ou jour).
- Changement de jour UTC : tous les compteurs, y compris celui de la session, repartent à zéro à minuit, une seule fois et jamais à rebours. Une session ouverte avant minuit peut donc consommer jusqu'à 2 × `REQ_SESSION` de part et d'autre. Le plafond global quotidien s'applique normalement à chaque journée.
- Plafonds par IP : une IPv4 partagée (opérateur mobile, entreprise) ou un /64 partagé peut regrouper plusieurs utilisateurs légitimes sous un même plafond.
- Limiteur natif `RL_IP` : disponibilité sur l'offre gratuite non documentée ; demande Wrangler 4.36 ou plus récent.

**Actions manuelles restantes (Max)**

1. Google AI Studio / Google Cloud :
   - créer une **nouvelle** clé Gemini et la restreindre à l'API Generative Language ;
   - vérifier si la facturation est active ; idéalement aucune, sinon des quotas journaliers abaissés et une alerte de budget ;
   - supprimer l'ancienne clé **après** le déploiement.
2. Cloudflare > Turnstile : créer un widget limité au nom d'hôte `maxxrqs.github.io`, mode « Managed » ou « Invisible ». Noter la clé publique (sitekey) et la clé secrète.
3. Cloudflare > Worker `sobremesa-ia` : enregistrer les secrets `GEMINI_KEY`, `TURNSTILE_SECRET`, `SESSION_SECRET` et `IP_SECRET`. Pour générer chacun des deux derniers, séparément : `openssl rand -base64 48`.
4. Déployer avec Wrangler (voir la procédure ci-dessous). Le Durable Object demande une migration, que l'éditeur du tableau de bord ne gère pas bien.
5. Mettre la sitekey dans `config.js` (`window.SOB_TS`), puis publier l'appli. **Sans sitekey, l'IA affiche une erreur.**

**Procédure de déploiement ultérieure**

Raccourci : le kit `deploiement/relais/` (`node deployer.mjs`) exécute les étapes 1 à 4 et le contrôle `curl` de l'étape 6, avec saisie masquée des clés et génération automatique de `SESSION_SECRET` et `IP_SECRET`. Il vérifie que `worker.js` est bien la version N4 v3 validée (empreinte dans `relais.json`, à mettre à jour si `worker.js` change). Détail :

1. `cp wrangler.example.toml wrangler.toml`. Supprimer le bloc `ratelimits` s'il est refusé par le compte. Le `name` doit rester `sobremesa-ia` pour garder l'adresse actuelle.
2. `npx wrangler@4 login`, puis `npx wrangler@4 secret put GEMINI_KEY`, `TURNSTILE_SECRET`, `SESSION_SECRET` et `IP_SECRET` (saisie masquée, rien dans les fichiers).
3. Tests locaux :
   - `MINIFLARE_DIR=<dossier miniflare> node tests/relais_worker.mjs`
   - `MINIFLARE_DIR=<dossier miniflare> node tests/relais_app.mjs`
4. Vérification sans envoi : `npx wrangler@4 deploy --dry-run --outdir /tmp/sobremesa-ia` (doit lister `BUDGET`, `RL_IP` et les variables). Puis `npx wrangler@4 deploy`. Le Worker remplace l'ancien à la même adresse. Dès ce moment, l'ancienne page (sans session) reçoit des 401 : déployer la page dans la foulée.
5. Renseigner `window.SOB_TS` dans `config.js`, régénérer la PWA (`python3 build_pwa.py`, qui change `V`), lancer les contrôles habituels, puis pousser sur `main`.
6. Vérifier en ligne :
   - ouvrir `diag.html` : « 401 → OK », puis une session et une traduction ;
   - `curl -X POST <adresse>/ai -H "Origin: https://maxxrqs.github.io" -d '{}'` doit renvoyer 401 ;
   - la conversation et le traducteur fonctionnent sur le téléphone et dans l'APK ;
   - les journaux du Worker ne contiennent aucun secret.
7. Supprimer l'ancienne clé Gemini.

---

## n°15 — Galicien « estiveses » / « actuariamos » — OUVERTE (validation par un locuteur ou relecteur galicien)

**Phrases concernées** (bloc RP de `castellano.html` et `index.html`, **inchangées**) :
- « Gustaríame que estiveses alí. »
- « De sabelo antes, actuariamos doutro xeito. »

On les retrouve aussi dans les index audio `v/gl_a/gl_a.json`, `v/gl_b/gl_b.json`, `v/gl_c/gl_c.json` et dans `tests/audio_texts.json`.

**Pourquoi rien n'a été corrigé** : l'audit proposait « estiveras » et « teriamos actuado », mais les sources pédagogiques galiciennes consultées contredisent ces deux corrections.
- « En galego non existen os tempos compostos con haber » (Xunta, IES Mendiño, résumé de morphologie verbale). « Teriamos actuado » serait donc un calque. « Ter + participe » est une périphrase itérative ou résultative.
- La forme en -ra ne remplace la forme en -se que dans les phrases désidératives (Xunta, IES San Paio, « O Verbo »). « Gustaríame que estiveras » serait donc hors norme.
- Les phrases actuelles sont jugées normatives : le pospretérito couvre aussi l'irréel du passé.

**Options à trancher par un relecteur natif**
1. Garder les deux phrases telles quelles (choix actuel).
2. « De sabelo antes, actuaramos doutro xeito. » : antepretérito à valeur de conditionnel passé, attesté dans des grammaires mais non confirmé par une source normative.
3. « Gustárame que estiveses alí. »

**Si une phrase change** : la modifier dans `castellano.html` (puis `index.html` via `build_pwa.py`), régénérer les clips des trois voix galiciennes, monter la version `?v=` de l'index audio, lancer `tests/audio_cover_full.py` et `tests/reserves.py`, puis mettre à jour cette fiche.
