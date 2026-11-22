# Rapport de génération audio

Mode : complet · échecs : 0

## Identité des voix (distance MFCC-DTW, plus petit = plus proche)

| Voix | Distances aux voix de l'appli | F0 générée / appli | Verdict |
|---|---|---|---|
| es_dora | es_laura 27.72, es_dora 12.42 | 182.3 / 175.0 Hz | identique |
| va_gina | va_gina 11.37, va_lluc 30.46 | 208.1 / 189.3 Hz | identique |
| va_lluc | va_gina 29.22, va_lluc 11.4 | 156.4 / 153.1 Hz | identique |
| ca_elia | ca_elia 11.3, ca_grau 33.38 | 183.4 / 185.3 Hz | identique |
| ca_grau | ca_elia 33.37, ca_grau 11.51 | 116.6 / 118.2 Hz | identique |
| gl_a | gl_b 31.58, gl_c 23.88, gl_a 14.26 | 87.4 / 116.7 Hz | identique |
| gl_b | gl_b 14.9, gl_c 29.48, gl_a 31.91 | 223.4 / 239.7 Hz | identique |
| gl_c | gl_b 29.6, gl_c 11.94, gl_a 23.87 | 108.9 / 103.5 Hz | identique |
| eu_antton | eu_antton 12.67 | 130.7 / 131.7 Hz | identique (seuil 19.39) |

## Clips gl_b

- « Quero aprender a cociñar. Que me recomendas? » : 3.08 s, 0.07 s/car (voix 0.069), pic 0.75, silences [0.12, 0.21] — conforme
- « para o que precises » : 1.23 s, 0.065 s/car (voix 0.069), pic 0.72, silences [0.12, 0.21] — conforme

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
-   4.9 s — basque · eu_antton · « Elkarteak diru-laguntza publiko bat jaso du. » · clip actuel de l'appli
-   8.7 s — basque · eu_antton · « Elkarteak diru-laguntza publiko bat jaso du. » · régénéré par hitz_eu_antton

### gl_b_nouveaux_textes.mp3

-   0.0 s — galicien · gl_b · « Quero aprender a cociñar. Que me recomendas? » · nouveau clip, hitz_gl_celtia
-   3.9 s — galicien · gl_b · « para o que precises » · nouveau clip, hitz_gl_celtia
