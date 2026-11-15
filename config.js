// Adresse du relais IA (Cloudflare Worker). Laisse vide tant que l'IA n'est pas branchée :
// l'appli fonctionne alors avec le dictionnaire local, et les fonctions IA affichent « indisponible ».
window.SOB_AI="https://sobremesa-ia.maxence-roquis.workers.dev";
// Adresse du relais des rappels quotidiens (Cloudflare Worker « worker-rappel.js »). Vide = section masquée.
window.SOB_PUSH="";
// Clé PUBLIQUE (sitekey) du widget Cloudflare Turnstile du relais IA. Obligatoire dès que SOB_AI est rempli
// (sinon les fonctions IA affichent une erreur). Ce n'est pas un secret : la clé secrète reste dans le Worker.
window.SOB_TS="0x4AAAAAAGCMqQ0DyXmx5PzF";
