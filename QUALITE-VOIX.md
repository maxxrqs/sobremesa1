# Qualité vocale — état réel, limites, plan de validation (v181)

## Ce qui a été fait
- **Castillan** : les 845 clips « de comblement » (Piper) sont remplacés par Kokoro (voix ef_dora, licence Apache 2.0). Mesure automatique : UTMOS 3,34 contre 3,14 pour Piper sur les mêmes textes ; intelligibilité (Whisper, 150 clips) 0,976.
- **Parcours normal** : enregistrements → voix système *réputée naturelle* (noms Google / Natural / Neural / Siri / Premium / Enhanced / Online / Network) → message honnête. Plus d'eSpeak. Plus de Piper par défaut. Plus de modèle catalan pour le galicien.
- **Mode dépannage** (Outils › Qualité des voix, désactivé par défaut, choisi par la personne) : autorise n'importe quelle voix système de la bonne langue et Piper (jamais pour le galicien). Le traducteur et la conversation n'utilisent donc plus Piper sans ce choix.
- **Signalement** : bouton « Signaler le dernier son » (liste locale copiable : langue, voix, texte). Les textes signalés sont regénérés avec `tools/audio_*`.
- Performance, cache, préchargement, hors ligne : inchangés (batterie `tests/audio.py` : 81/81, exercices 49/49, mobile 22/22, splash 12/12).

## Ce qui n'a PAS été prouvé
- Aucun clip n'a été écouté par moi. Les scores UTMOS (`qa/utmos_echantillon_v181.csv`, 120 clips par voix et par classe) sont des **indices** : le modèle est entraîné sur l'anglais et ne dit rien de l'exactitude de la prononciation ni du naturel réel en euskara, galego ou valencià.
- Échantillon UTMOS moyen : eu 3,6–3,7 ; gl 3,15–3,6 ; ca 3,3–3,5 ; va 3,3–3,4 ; es d'origine 2,78 (26 % sous 2,5), es Kokoro ≈ 3,3. Le castillan d'origine est le plus bas du tableau mais c'est un enregistrement d'IA commerciale que je ne peux ni regénérer ni juger : **à trancher à l'oreille** (comparaison à l'aveugle dans le kit d'écoute).
- Voix ca/va/gl/eu : aucun moteur ouvert plus naturel n'était accessible (Kokoro ne couvre pas ces langues). Elles restent des modèles ouverts (Matxa, AhoTTS) de qualité moyenne à correcte, à confirmer par l'écoute.
- Largeur de bande de plusieurs voix (eu, va_lluc, gl_a) étroite : l'effet « téléphone » peut venir du modèle source, pas du codec.
- GitHub Pages / PWA installée : non testés en réel (github.io inaccessible depuis mon environnement) ; testés avec un serveur Range local et Chromium simulé uniquement.

## Plan de validation à 100 %
1. Kit d'écoute (143 clips, notation naturelle / passable / robotique) → renvoyer le résultat ; les « robotique » sont regénérés (autre voix, autre vitesse, texte nettoyé) ou retirés.
2. Étendre : `tools/mos/score_sample.py` note tout clip ; trier par score, écouter d'abord les 5 % les plus bas de chaque voix (≈ 1 000 clips), puis un échantillon aléatoire de 5 %.
3. Usage réel : le bouton « Signaler » alimente la liste de remplacement en continu.
4. Pour la qualité humaine garantie : enregistrer ou faire enregistrer des locuteurs natifs (gl, eu, va), ou acheter une synthèse neuronale pro (Azure Speech : es-ES, ca-ES, gl-ES, eu-ES ; Google Cloud TTS ; ElevenLabs). Génération par lots unique (≈ 20 000 clips, quelques millions de caractères) : coût à chiffrer avec le fournisseur choisi — **aucun service payant n'est activé**.
