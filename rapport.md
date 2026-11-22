# Rapport de génération audio

Mode : complet · échecs : 1

## Échecs

- gl_b : clés ≠ textes demandés

## Identité des voix (distance MFCC-DTW, plus petit = plus proche)

| Voix | Distances aux voix de l'appli | F0 générée / appli | Verdict |
|---|---|---|---|
| es_dora | es_laura 27.69, es_dora 12.38 | 182.3 / 175.0 Hz | identique |
| va_gina | va_gina 11.59, va_lluc 31.08 | 206.1 / 189.3 Hz | identique |
| va_lluc | va_gina 29.85, va_lluc 11.49 | 154.2 / 153.1 Hz | identique |
| ca_elia | ca_elia 11.31, ca_grau 33.59 | 183.4 / 185.3 Hz | identique |
| ca_grau | ca_elia 32.97, ca_grau 11.37 | 119.2 / 118.2 Hz | identique |
| gl_a | gl_b 31.05, gl_c 23.75, gl_a 13.48 | 89.5 / 116.7 Hz | identique |
| gl_b | gl_b 15.12, gl_c 29.41, gl_a 31.4 | 217.2 / 239.7 Hz | identique |
| gl_c | gl_b 30.08, gl_c 12.69, gl_a 23.65 | 111.1 / 103.5 Hz | identique |
| eu_antton | eu_antton 12.89 | 131.1 / 131.7 Hz | identique (seuil 19.38) |

## Clips gl_a

- « Para rematar, que nos di? » : 1.31 s, 0.052 s/car (voix 0.069), pic 0.71, silences [0.12, 0.2] — conforme

## Clips gl_b


## Clips gl_c

- « Que teña un bo día! » : 1.18 s, 0.062 s/car (voix 0.067), pic 0.68, silences [0.11, 0.21] — conforme

## Extraits d'écoute (dossier ecoute/)

### es_dora_comparaison_clip_actuel_puis_regenere.mp3

-   0.0 s — castillan · es_dora · « Un kilo de naranjas, por favor. » · clip actuel de l'appli
-   2.7 s — castillan · es_dora · « Un kilo de naranjas, por favor. » · régénéré par kokoro ef_dora
-   5.6 s — castillan · es_dora · « Tengo dolor de cabeza. » · clip actuel de l'appli
-   8.0 s — castillan · es_dora · « Tengo dolor de cabeza. » · régénéré par kokoro ef_dora

### va_gina_comparaison_clip_actuel_puis_regenere.mp3

-   0.0 s — valencien · va_gina · « Ja és tard, toque el dos. » · clip actuel de l'appli
-   2.3 s — valencien · va_gina · « Ja és tard, toque el dos. » · régénéré par matxa (locuteur 7, accent valencia)
-   4.7 s — valencien · va_gina · « si tinguera diners » · clip actuel de l'appli
-   6.7 s — valencien · va_gina · « si tinguera diners » · régénéré par matxa (locuteur 7, accent valencia)

### va_lluc_comparaison_clip_actuel_puis_regenere.mp3

-   0.0 s — valencien · va_lluc · « Ja és tard, toque el dos. » · clip actuel de l'appli
-   2.4 s — valencien · va_lluc · « Ja és tard, toque el dos. » · régénéré par matxa (locuteur 6, accent valencia)
-   4.8 s — valencien · va_lluc · « si tinguera diners » · clip actuel de l'appli
-   6.9 s — valencien · va_lluc · « si tinguera diners » · régénéré par matxa (locuteur 6, accent valencia)

### ca_elia_comparaison_clip_actuel_puis_regenere.mp3

-   0.0 s — catalan · ca_elia · « Reconec que em vaig equivocar. » · clip actuel de l'appli
-   2.5 s — catalan · ca_elia · « Reconec que em vaig equivocar. » · régénéré par matxa (locuteur 3, accent central)
-   5.0 s — catalan · ca_elia · « M'ha agradat molt » · clip actuel de l'appli
-   6.9 s — catalan · ca_elia · « M'ha agradat molt » · régénéré par matxa (locuteur 3, accent central)

### ca_grau_comparaison_clip_actuel_puis_regenere.mp3

-   0.0 s — catalan · ca_grau · « Reconec que em vaig equivocar. » · clip actuel de l'appli
-   2.5 s — catalan · ca_grau · « Reconec que em vaig equivocar. » · régénéré par matxa (locuteur 2, accent central)
-   5.0 s — catalan · ca_grau · « M'ha agradat molt » · clip actuel de l'appli
-   6.9 s — catalan · ca_grau · « M'ha agradat molt » · régénéré par matxa (locuteur 2, accent central)

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
-   6.7 s — galicien · gl_c · « Despois de comermos, fomos pasear » · régénéré par hitz_gl_paulo

### eu_antton_comparaison_clip_actuel_puis_regenere.mp3

-   0.0 s — basque · eu_antton · « beldur izaten nintzen » · clip actuel de l'appli
-   2.4 s — basque · eu_antton · « beldur izaten nintzen » · régénéré par hitz_eu_antton
-   4.8 s — basque · eu_antton · « Elkarteak diru-laguntza publiko bat jaso du. » · clip actuel de l'appli
-   8.6 s — basque · eu_antton · « Elkarteak diru-laguntza publiko bat jaso du. » · régénéré par hitz_eu_antton

### gl_a_nouveaux_textes.mp3

-   0.0 s — galicien · gl_a · « Para rematar, que nos di? » · nouveau clip, hitz_gl_iago

### gl_c_nouveaux_textes.mp3

-   0.0 s — galicien · gl_c · « Que teña un bo día! » · nouveau clip, hitz_gl_paulo
