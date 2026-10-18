# Audit i18n Sobremesa

À lire à chaque reprise, puis vérifier l'état réel avec les scripts ci-dessous avant de continuer.

## Fonctionnement de la traduction (cartographie)
- Code unique : `castellano.html` (source). `index.html` = même fichier + en-tête PWA + service worker (appliquer chaque correctif aux deux fichiers).
- Langues d'interface : `UIL` = fr (source, clés), en, it, de, pt. Dictionnaires : `tr/en.json`, `tr/it.json`, `tr/de.json`, `tr/pt.json` (clé = texte français exact ; `#` remplace les nombres ; `{0}` = paramètre).
- Fonctions : `gl(s)` (recherche, repli = texte français), `tr(s,...a)` (gl + paramètres), `trText`/`trNode` + `MutationObserver` (traduit tout nœud texte et attributs placeholder/aria-label/title/alt qui correspondent EXACTEMENT à une clé ; `translate="no"` exclut).
- Contenus pédagogiques passés par `gl()` : `RW` (gloses mots), `RP` (phrases), `RT` (questions/réponses de lecture), `RR`/`REF` (listes), `XC` (exceptions), `XE` (expressions) — langue étudiée par langue étudiée.
- Textes en langue étudiée : jamais traduits (colonnes cible, `translate="no"`).

## Outils de contrôle
- `python3 tests/rangesrv.py 8775 .` puis :
- `python3 tests/i18n_keys.py http://127.0.0.1:8775/ [sortie.json]` : inventaire des textes français envoyés à la traduction + clés manquantes / vides par langue.
- `python3 tests/i18n_crawl.py http://127.0.0.1:8775/ [sortie.json] [en,it,...]` : parcourt écrans + 25 types d'exercices (5 langues étudiées × niveaux 1/3/5) et liste les textes affichés non traduits.
- `tools/i18n_frdetect.py` : heuristique « texte français ».

## Étape 1 — Audit initial (terminée, 2026-10-18)
- 15 723 textes français recensés. Clés manquantes : en 5 634, it 5 663, de 5 660, pt 5 637. Clés vides : 0 partout.
- Répartition (en) : exceptions `XC` 3 573 (es 733, va 719, ca 711, gl 706, eu 704) ; expressions `XE` 1 392 ; listes `RR` 318 ; gloses `RW` 165 ; lecture `RT` 99 ; phrases `RP` 70 ; interface 17.
- Aucune ancienne traduction proche retrouvée (les traductions annoncées en v20 ne sont pas dans `tr/`).
- Chemins de code sans traduction (vus au parcours) :
  1. Consignes des dialogues `XD` (« Dis que… », exercices speakQ/replyQ) : jamais passées par `gl`.
  2. Options françaises des questions d'exceptions (`XC` lignes Q, colonnes 4-6) quand elles sont en français.
  3. Questions/réponses de compréhension C1 et phrases C1 hors `RT`/`RP` (ex. « Il ne manquait plus qu'on nous augmente le loyer… ») : source à localiser.
  4. Aria-label « Série » et 16 autres textes d'interface sans clé.

## Étape 2 — Chemins de code (terminée)
- `eoScene` : consigne des dialogues `XD` passée par `gl` (hint, fr).
- `xbuild` : options des QCM d'exceptions traduites seulement si les 4 options ont une clé (options en langue étudiée jamais touchées).
- Points 3-4 : ce sont des clés manquantes (RP/RT), pas du code ; traitées à l'étape 3.
- Inventaire étendu (consignes XD, catégories XD, options françaises des QCM) : 16 237 textes ; manquants en 6 130, it 6 159, de 6 156, pt 6 133.
- Test ajouté : `tests/i18n_keys.py` sort en échec (code 1) si une clé manque (hors `tr/nofr.json`) ou si une traduction est vide.

## Étape 3 — Traductions (en cours)
- Entrées : 6 213 textes uniques, en 2 lots, traduits par langue (en, it, de, pt) ; sorties à fusionner dans `tr/*.json` après contrôle des marqueurs.
- Penser à passer `tr/…json?v=31` à `v=32` (castellano.html + index.html) et changer la version de `sw.js` pour que les téléphones rechargent.

## Prochaine action
Fusionner les traductions contrôlées, créer `tr/nofr.json` (textes non français laissés tels quels), relancer `tests/i18n_keys.py` (doit afficher OK) et `tests/i18n_crawl.py` dans les 4 langues, puis les tests existants (mobile, exercices).

## Fichiers modifiés
- Modifiés : `castellano.html`, `index.html` (eoScene, xbuild).
- Ajoutés : `I18N_AUDIT.md`, `tests/i18n_keys.py`, `tests/i18n_crawl.py`, `tools/i18n_frdetect.py`.
