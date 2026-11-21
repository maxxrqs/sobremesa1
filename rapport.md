# Rapport de génération audio

Mode : complet · échecs : 1

## Échecs

- gl_c : clés ≠ textes demandés

## Identité des voix (distance MFCC-DTW, plus petit = plus proche)

| Voix | Distances aux voix de l'appli | F0 générée / appli | Verdict |
|---|---|---|---|
| gl_a | gl_b 31.23, gl_c 23.45, gl_a 13.5 | 92.4 / 116.7 Hz | identique |
| gl_b | gl_b 13.95, gl_c 29.53, gl_a 31.49 | 218.3 / 239.7 Hz | identique |
| gl_c | gl_b 30.07, gl_c 12.58, gl_a 23.71 | 111.7 / 103.5 Hz | identique |

## Clips gl_a

- « Que mágoa. » : 0.78 s, 0.078 s/car (voix 0.085), pic 0.71, silences [0.13, 0.2] — conforme
- « Que ben! E hoxe? Que tal o traballo? » : 3.37 s, 0.094 s/car (voix 0.085), pic 0.72, silences [0.12, 0.2] — conforme

## Clips gl_b

- « Que ten? » : 0.73 s, 0.091 s/car (voix 0.087), pic 0.72, silences [0.12, 0.19] — conforme
- « Ola, que tal? » : 0.97 s, 0.074 s/car (voix 0.087), pic 0.73, silences [0.12, 0.2] — conforme
- « Que ben! Falas galego? » : 2.19 s, 0.1 s/car (voix 0.087), pic 0.73, silences [0.12, 0.2] — conforme
- « Que ben! E hoxe? Que tal o traballo? » : 3.53 s, 0.098 s/car (voix 0.087), pic 0.74, silences [0.12, 0.2] — conforme

## Clips gl_c

- « Bos días. Que tal está? » : 2.27 s, 0.099 s/car (voix 0.085), pic 0.72, silences [0.12, 0.18] — conforme
- « Ola, que tal? » : 1.02 s, 0.078 s/car (voix 0.085), pic 0.71, silences [0.12, 0.18] — conforme
- « Que mágoa! Queres tomar un café esta semana? » : 3.13 s, 0.071 s/car (voix 0.085), pic 0.72, silences [0.12, 0.2] — conforme
- « Claro. Que tal? » : 1.78 s, 0.118 s/car (voix 0.085), pic 0.71, silences [0.12, 0.18] — conforme

## Extraits d'écoute (dossier ecoute/)

### gl_a_comparaison_clip_actuel_puis_regenere.mp3

-   0.0 s — galicien · gl_a · « Quero que pagues » · clip actuel de l'appli
-   1.9 s — galicien · gl_a · « Quero que pagues » · régénéré par hitz_gl_iago
-   3.9 s — galicien · gl_a · « Despois de comermos, fomos pasear » · clip actuel de l'appli
-   6.8 s — galicien · gl_a · « Despois de comermos, fomos pasear » · régénéré par hitz_gl_iago

### gl_b_comparaison_clip_actuel_puis_regenere.mp3

-   0.0 s — galicien · gl_b · « Quero que pagues » · clip actuel de l'appli
-   1.9 s — galicien · gl_b · « Quero que pagues » · régénéré par hitz_gl_celtia
-   3.7 s — galicien · gl_b · « Despois de comermos, fomos pasear » · clip actuel de l'appli
-   6.6 s — galicien · gl_b · « Despois de comermos, fomos pasear » · régénéré par hitz_gl_celtia

### gl_c_comparaison_clip_actuel_puis_regenere.mp3

-   0.0 s — galicien · gl_c · « Quero que pagues » · clip actuel de l'appli
-   1.9 s — galicien · gl_c · « Quero que pagues » · régénéré par hitz_gl_paulo
-   3.8 s — galicien · gl_c · « Despois de comermos, fomos pasear » · clip actuel de l'appli
-   6.8 s — galicien · gl_c · « Despois de comermos, fomos pasear » · régénéré par hitz_gl_paulo

### gl_a_nouveaux_textes.mp3

-   0.0 s — galicien · gl_a · « Que mágoa. » · nouveau clip, hitz_gl_iago
-   1.6 s — galicien · gl_a · « Que ben! E hoxe? Que tal o traballo? » · nouveau clip, hitz_gl_iago

### gl_b_nouveaux_textes.mp3

-   0.0 s — galicien · gl_b · « Que ten? » · nouveau clip, hitz_gl_celtia
-   1.5 s — galicien · gl_b · « Ola, que tal? » · nouveau clip, hitz_gl_celtia
-   3.3 s — galicien · gl_b · « Que ben! Falas galego? » · nouveau clip, hitz_gl_celtia
-   6.3 s — galicien · gl_b · « Que ben! E hoxe? Que tal o traballo? » · nouveau clip, hitz_gl_celtia

### gl_c_nouveaux_textes.mp3

-   0.0 s — galicien · gl_c · « Bos días. Que tal está? » · nouveau clip, hitz_gl_paulo
-   3.1 s — galicien · gl_c · « Ola, que tal? » · nouveau clip, hitz_gl_paulo
-   4.9 s — galicien · gl_c · « Que mágoa! Queres tomar un café esta semana? » · nouveau clip, hitz_gl_paulo
-   8.8 s — galicien · gl_c · « Claro. Que tal? » · nouveau clip, hitz_gl_paulo
