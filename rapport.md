# Rapport de génération audio

Mode : echantillon · échecs : 0

## Identité des voix (distance MFCC-DTW, plus petit = plus proche)

| Voix | Distances aux voix de l'appli | F0 générée / appli | Verdict |
|---|---|---|---|
| es_laura | es_laura 14.11, es_dora 26.09 | 190.2 / 186.9 Hz | identique |
| es_dora | es_laura 27.69, es_dora 12.38 | 182.3 / 175.0 Hz | identique |
| va_gina | va_gina 11.72, va_lluc 30.79 | 220.0 / 189.3 Hz | identique |
| va_lluc | va_gina 30.07, va_lluc 11.23 | 157.5 / 153.1 Hz | identique |
| ca_elia | ca_elia 10.9, ca_grau 33.29 | 183.0 / 185.3 Hz | identique |
| ca_grau | ca_elia 32.82, ca_grau 11.85 | 118.5 / 118.2 Hz | identique |
| eu_antton | eu_antton 13.28 | 129.3 / 131.7 Hz | identique (seuil 20.1) |

## Galicien : modèles HiTZ candidats × voix de l'appli (proposition à valider)

| Modèle | gl_a (Voz C) | gl_b (Voz A) | gl_c (Voz B) | F0 |
|---|---|---|---|---|
| hitz_gl_brais | 30.14 | 29.56 | 29.17 | 165.8 Hz |
| hitz_gl_celtia | 30.82 | 14.83 | 29.34 | 220.6 Hz |
| hitz_gl_iago | 14.31 | 31.23 | 23.53 | 91.0 Hz |
| hitz_gl_icia | 33.91 | 26.11 | 29.53 | 238.4 Hz |
| hitz_gl_paulo | 23.53 | 29.76 | 11.67 | 108.9 Hz |
| hitz_gl_sabela | 34.58 | 25.84 | 30.32 | 210.0 Hz |

F0 des voix de l'appli : {'gl_b': 239.7, 'gl_c': 103.5, 'gl_a': 116.7}

- **gl_a** : hitz_gl_iago (14.31), puis hitz_gl_paulo (23.53), écart 64 %
- **gl_b** : hitz_gl_celtia (14.83), puis hitz_gl_sabela (25.84), écart 74 %
- **gl_c** : hitz_gl_paulo (11.67), puis hitz_gl_iago (23.53), écart 102 %

Proposition à valider par Max : aucune correspondance n'est appliquée automatiquement.

## Clips es_laura

- « Sí, puede pagar con tarjeta. Gracias, ¡hasta luego! » : 3.79 s, 0.074 s/car (voix 0.09), pic 0.7, silences [0.12, 0.19] — conforme
- « ¡Buen viaje! » : 1.07 s, 0.089 s/car (voix 0.09), pic 0.77, silences [0.12, 0.2] — conforme

## Clips es_dora

- « Sí, puede pagar con tarjeta. Gracias, ¡hasta luego! » : 3.13 s, 0.061 s/car (voix 0.087), pic 0.73, silences [0.12, 0.19] — conforme
- « ¡Buen viaje! » : 1.1 s, 0.091 s/car (voix 0.087), pic 0.71, silences [0.12, 0.19] — conforme

## Clips va_gina

- « Sí, pot pagar amb targeta. Gràcies, fins després! » : 3.29 s, 0.067 s/car (voix 0.081), pic 0.79, silences [0.12, 0.21] — conforme
- « No passa res. » : 0.99 s, 0.076 s/car (voix 0.081), pic 0.7, silences [0.12, 0.19] — conforme

## Clips va_lluc

- « Sí, pot pagar amb targeta. Gràcies, fins després! » : 3.42 s, 0.07 s/car (voix 0.082), pic 0.76, silences [0.12, 0.19] — conforme
- « No passa res. » : 1.1 s, 0.084 s/car (voix 0.082), pic 0.7, silences [0.12, 0.19] — conforme

## Clips ca_elia

- « Sí, pot pagar amb targeta. Gràcies, fins després! » : 3.6 s, 0.074 s/car (voix 0.08), pic 0.73, silences [0.12, 0.19] — conforme
- « Bon viatge! » : 0.97 s, 0.088 s/car (voix 0.08), pic 0.75, silences [0.12, 0.2] — conforme

## Clips ca_grau

- « Sí, pot pagar amb targeta. Gràcies, fins després! » : 3.81 s, 0.078 s/car (voix 0.078), pic 0.76, silences [0.12, 0.19] — conforme
- « Bon viatge! » : 0.89 s, 0.081 s/car (voix 0.078), pic 0.66, silences [0.12, 0.18] — conforme

## Clips eu_antton

- « Bai, baina bost euro gehiago ordaindu behar duzu. » : 2.85 s, 0.058 s/car (voix 0.116), pic 0.72, silences [0.12, 0.2] — conforme
- « trena galdu » : 1.04 s, 0.095 s/car (voix 0.116), pic 0.72, silences [0.12, 0.18] — conforme
- « txartela » : 0.94 s, 0.118 s/car (voix 0.116), pic 0.72, silences [0.12, 0.18] — conforme
