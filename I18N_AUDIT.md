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

## Prochaine action
Étape 2 : corriger les chemins de code 1-4 (passage par `gl`), puis étape 3 : traduire les clés manquantes par lots (en, it, de, pt), étape 4 : test de non-régression.

## Fichiers modifiés
- Ajoutés : `I18N_AUDIT.md`, `tests/i18n_keys.py`, `tests/i18n_crawl.py`, `tools/i18n_frdetect.py`.
