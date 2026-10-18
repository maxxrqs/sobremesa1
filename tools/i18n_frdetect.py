# Heuristique : ce texte est-il du français (et pas du castillan/catalan/valencien/galicien/basque) ?
import re
FRW=set("le les des du une est et je tu il elle nous vous ils elles on ce cette ces mon ton son ma ta sa mes tes ses pour avec dans sur pas ne que qui au aux très être avoir fait ça où ou mais donc car leur leurs quel quelle quels quelles ici choisis écoute écris traduis réponds dis complète vrai faux mot mots phrase phrases niveau leçon langue langues bonne mauvaise réponse suivant continuer passer vérifier encore tes ton déjà aussi plus moins sans chez vers comme quand alors puis après avant faire dire voir aller venir prendre il y a c'est n'est".split())
def fr_score(t):
    w=re.findall(r"[a-zà-ÿœ']+",t.lower())
    if not w:return 0
    s=0
    for x in w:
        x2=x.split("'")[-1] if "'" in x else x
        if x in FRW or x2 in FRW:s+=1
        if re.match(r"^(j|qu|n|c|s|m|t)'",x):s+=1.5
        if re.search(r"[êâîôûœù]|eau|aux$|oi[ts]?$|ez$",x):s+=1
    s+= 1 if re.search(r"\b(l'|d')[a-zé]",t.lower()) and re.search(r"\b(le|les|des|une|est|et)\b",t.lower()) else 0
    return s/len(w)*min(1,len(w)/2)+ (0.5 if re.search(r"[êâîôûœ]",t) else 0)
def is_fr(t,th=0.34):return fr_score(t)>=th
