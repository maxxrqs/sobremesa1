# Rapport de génération audio

Mode : echantillon · échecs : 0

## Identité des voix (distance MFCC-DTW, plus petit = plus proche)

| Voix | Distances aux voix de l'appli | F0 générée / appli | Verdict |
|---|---|---|---|
| gl_a | gl_b 30.97, gl_c 23.8, gl_a 14.35 | 90.2 / 116.7 Hz | identique |
| gl_b | gl_b 14.56, gl_c 29.29, gl_a 30.97 | 220.5 / 239.7 Hz | identique |
| gl_c | gl_b 29.48, gl_c 11.79, gl_a 23.85 | 111.5 / 103.5 Hz | identique |
| es_laura | es_laura 13.78, es_dora 26.39 | 190.4 / 186.9 Hz | identique |
| es_dora | es_laura 27.67, es_dora 12.04 | 183.1 / 175.0 Hz | identique |
| va_gina | va_gina 12.44, va_lluc 31.02 | 220.5 / 189.3 Hz | identique |
| va_lluc | va_gina 30.39, va_lluc 10.81 | 157.5 / 153.1 Hz | identique |
| ca_elia | ca_elia 11.03, ca_grau 33.49 | 183.8 / 185.3 Hz | identique |
| ca_grau | ca_elia 32.39, ca_grau 11.49 | 117.6 / 118.2 Hz | identique |
| eu_antton | eu_antton 12.68 | 129.4 / 131.7 Hz | identique (seuil 19.18) |

## Clips gl_a

- « Si, pode pagar con tarxeta. Grazas, ata logo! » : 3.71 s, 0.082 s/car (voix 0.092), pic 0.69, silences [0.12, 0.2] — conforme
- « Boa viaxe! » : 0.91 s, 0.091 s/car (voix 0.092), pic 0.73, silences [0.12, 0.18] — conforme

## Clips gl_b

- « Si, pode pagar con tarxeta. Grazas, ata logo! » : 3.92 s, 0.087 s/car (voix 0.091), pic 0.7, silences [0.12, 0.21] — conforme
- « Boa viaxe! » : 1.25 s, 0.125 s/car (voix 0.091), pic 0.71, silences [0.12, 0.2] — conforme

## Clips gl_c

- « Si, pode pagar con tarxeta. Grazas, ata logo! » : 3.68 s, 0.082 s/car (voix 0.09), pic 0.74, silences [0.12, 0.19] — conforme
- « Boa viaxe! » : 0.97 s, 0.097 s/car (voix 0.09), pic 0.71, silences [0.12, 0.19] — conforme

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

### es_laura_comparaison_clip_actuel_puis_regenere.mp3

-   0.0 s — castillan · es_laura · « Un kilo de naranjas, por favor. » · clip actuel de l'appli
-   3.0 s — castillan · es_laura · « Un kilo de naranjas, por favor. » · régénéré par hitz_es_laura
-   5.8 s — castillan · es_laura · « Tengo dolor de cabeza. » · clip actuel de l'appli
-   8.1 s — castillan · es_laura · « Tengo dolor de cabeza. » · régénéré par hitz_es_laura

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
-   5.0 s — catalan · ca_elia · « Mengem en un restaurant. » · clip actuel de l'appli
-   7.3 s — catalan · ca_elia · « Mengem en un restaurant. » · régénéré par matxa (locuteur 3, accent central)

### ca_grau_comparaison_clip_actuel_puis_regenere.mp3

-   0.0 s — catalan · ca_grau · « Reconec que em vaig equivocar. » · clip actuel de l'appli
-   2.5 s — catalan · ca_grau · « Reconec que em vaig equivocar. » · régénéré par matxa (locuteur 2, accent central)
-   5.0 s — catalan · ca_grau · « Mengem en un restaurant. » · clip actuel de l'appli
-   7.4 s — catalan · ca_grau · « Mengem en un restaurant. » · régénéré par matxa (locuteur 2, accent central)

### eu_antton_comparaison_clip_actuel_puis_regenere.mp3

-   0.0 s — basque · eu_antton · « beldur izaten nintzen » · clip actuel de l'appli
-   2.4 s — basque · eu_antton · « beldur izaten nintzen » · régénéré par hitz_eu_antton
-   5.0 s — basque · eu_antton · « Elkarteak diru-laguntza publiko bat jaso du. » · clip actuel de l'appli
-   8.7 s — basque · eu_antton · « Elkarteak diru-laguntza publiko bat jaso du. » · régénéré par hitz_eu_antton

### gl_a_nouveaux_textes.mp3

-   0.0 s — galicien · gl_a · « Si, pode pagar con tarxeta. Grazas, ata logo! » · nouveau clip, hitz_gl_iago
-   4.5 s — galicien · gl_a · « Boa viaxe! » · nouveau clip, hitz_gl_iago

### gl_b_nouveaux_textes.mp3

-   0.0 s — galicien · gl_b · « Si, pode pagar con tarxeta. Grazas, ata logo! » · nouveau clip, hitz_gl_celtia
-   4.7 s — galicien · gl_b · « Boa viaxe! » · nouveau clip, hitz_gl_celtia

### gl_c_nouveaux_textes.mp3

-   0.0 s — galicien · gl_c · « Si, pode pagar con tarxeta. Grazas, ata logo! » · nouveau clip, hitz_gl_paulo
-   4.5 s — galicien · gl_c · « Boa viaxe! » · nouveau clip, hitz_gl_paulo
