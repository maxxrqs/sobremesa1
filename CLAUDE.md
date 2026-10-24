# Sobremesa — règles pour toute session

- Source unique : `castellano.html`. Toute modification s'applique aussi à `index.html` (PWA), puis on change la version `V` de `sw.js`, on pousse sur `main` et on republie l'artefact Sobremesa.
- **Garde-fou audio, avant chaque push qui touche au contenu** (vocabulaire, parcours, phrases) : `python3 tests/audio_cover.py` (vocabulaire), puis `python3 tests/rangesrv.py 8774 .` et `python3 tests/audio_cover_full.py` (phrases, textes, scènes, dialogues). S'il affiche FAIL, des mots seront lus par une voix de secours robotique : générer leurs clips (voir LISEZ-MOI, section 3, et `tools/audio_merge.py`) ou prévenir Max avant de pousser.
- L'artefact Claude ne contient pas les enregistrements (dossiers `a/` et `v/`) : les voix ne s'entendent que sur la PWA hébergée.
- Listes et conjugaison : `python3 tests/listes.py URL` (chaque verbe des listes conjugable, ordre des catégories stable, typographie, Nombres et dates). Les tableaux des verbes ajoutés viennent des dictionnaires Apertium (es, ca, va, gl) et de règles pour le basque ; les formes conjuguées des verbes B1+ n'ont pas encore d'enregistrement (voix de secours).
