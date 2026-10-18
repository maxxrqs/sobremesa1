# Sobremesa — règles pour toute session

- Source unique : `castellano.html`. Toute modification s'applique aussi à `index.html` (PWA), puis on change la version `V` de `sw.js`, on pousse sur `main` et on republie l'artefact Sobremesa.
- **Garde-fou audio, avant chaque push qui touche au contenu** (vocabulaire, parcours, phrases) : `python3 tests/audio_cover.py`. S'il affiche FAIL, des mots seront lus par une voix de secours robotique : générer leurs clips (voir LISEZ-MOI, section 3, et `tools/audio_merge.py`) ou prévenir Max avant de pousser.
- L'artefact Claude ne contient pas les enregistrements (dossiers `a/` et `v/`) : les voix ne s'entendent que sur la PWA hébergée.
