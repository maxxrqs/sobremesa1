#!/usr/bin/env python3
"""Linguistique (audit du 7 novembre, n°12 à 14) : temps composés entraînés (passé composé es, passé périphrastique
et passé composé ca/va), verbes ajoutés aux tableaux (oír, andar, valer, traducir ; pór, oír ; haver), « D'on ets? »
et graphie catalane « soc » (norme IEC) dans les contenus catalans, avec leurs enregistrements.
Usage : python3 tests/rangesrv.py 8772 .  puis  python3 tests/ling_a.py [url_base]"""
import sys, json, os
from playwright.sync_api import sync_playwright
BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8772/"
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
R = []
def ck(n, c, i=""):
    R.append(bool(c)); print("OK  " if c else "FAIL", n, "" if c else str(i)[:600], flush=True)
JS = r"""()=>{const o={};const row=(l,v,k)=>{S.lang=l;build();const d=VD[l][v],t=vlist(l,d).find(t=>t.k===k);return t?vrows(l,d,t):null};
 o.comer=row("es","comer","pc");o.levantarse=row("es","levantarse","pc");o.menjar_pp=row("ca","menjar","pp");o.menjar_pf=row("ca","menjar","pf");
 o.rentarse=row("ca","rentar-se","pf");o.anarsen=row("ca","anar-se'n","pf");o.anarsen_imp=row("ca","anar-se'n","imp");o.va_pp=row("va","menjar","pp");
 o.haber_que=vlist("es",VD.es["haber que"]).map(t=>t.k);o.gl=vlist("gl",VD.gl["comer"]).map(t=>t.k);
 o.lad={};for(const l of ["es","va","ca"]){o.lad[l]=TLAD[l].map(a=>a.join(","))}
 /* exercices : un temps composé demandé produit bien un exercice de conjugaison avec ses formes */
 o.ex={};for(const [l,k] of [["es","pc"],["ca","pp"],["ca","pf"],["va","pp"]]){S.lang=l;S.lvl=2;build();R={mode:"lesson",tn:[k],n:0,ok:0};let q=null,n=0;
   for(let i=0;i<30&&!q;i++){const z=mkConj();if(z&&z.tn===gl(vlist(l,VD[l].ser||Object.values(VD[l])[0]).find(t=>t.k===k).fr))q=z;n++}R=null;o.ex[l+k]=q?{g:q.g,o:q.o,tn:q.tn}:null}
 /* parcours A2 : une étape « nouveau temps » par temps composé, expliquée ; étapes des temps simples inchangées */
 o.path={};for(const l of ["es","va","ca"]){S.lang=l;S.lvl=2;build();const pc=planCore(2),ts=pc.flat.filter(x=>x.tn);
   o.path[l]=ts.map(x=>{S.ds={};const d=discItems(x);return [x.id,x.tn[0],d.length,!!d.intro]})}
 /* « Tous les temps » : chaque temps composé n'apparaît qu'une fois */
 S.lang="ca";build();VS={s:"menjar",t:"pres",all:1};verb();const h=document.getElementById("app").innerHTML;o.allvaig=(h.match(/<b>vaig menjar<\/b>/g)||[]).length;
 VS={s:"menjar",t:"pp",all:0};verb();o.chip=document.getElementById("app").innerHTML.includes("<b>vaig menjar</b>");
 /* verbes ajoutés */
 o.nv={};for(const [l,v] of [["es","oír"],["es","andar"],["es","valer"],["es","traducir"],["gl","pór"],["gl","oír"],["ca","haver"]]){const d=VD[l][v];
   o.nv[l+":"+v]=d?{lv:vLvl(l,v),bad:Object.entries(d.t).filter(([k,a])=>Array.isArray(a)&&(k==="imv"?a.length<2:a.length!==6||a.some(f=>!f))).map(x=>x[0]),t:d.t}:null}
 /* pas de forme composée dans l'index qui classe les phrases du parcours */
 S.lang="es";build();for(const z in PQ)delete PQ[z];const pd=pqData();o.pqcmp=Object.values(pd.V).some(x=>Object.values(x).some(s=>s.has("pc")));
 /* catalan : « D'on ets? » et « soc » partout dans le contenu (les explications de XC citent l'ancienne graphie) */
 const k=LK.indexOf("ca"),rx=RX.trim().split("\n").map(z=>z.split("|")[1+k]||"");
 o.ca={xd:XD.ca,scn:SCN.ca.join("\n"),rx:rx.join("\n"),ptb:JSON.stringify(PTB.ca)};
 return o}"""
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(); err = []
    pg.on("pageerror", lambda e: err.append(str(e)))
    pg.goto(BASE + "index.html"); pg.wait_for_timeout(2500)
    o = pg.evaluate(JS)
    b.close()
# n°12 — formes des temps composés
ck("es : passé composé (he comido…)", o["comer"]["F"] == ["he comido", "has comido", "ha comido", "hemos comido", "habéis comido", "han comido"], o["comer"])
ck("es : pronominal au passé composé (me he levantado…)", o["levantarse"]["F"][0] == "me he levantado" and o["levantarse"]["F"][4] == "os habéis levantado", o["levantarse"])
ck("ca : passé périphrastique (vaig menjar… ; variantes vàrem, vàreu)", o["menjar_pp"]["F"] == ["vaig menjar", "vas menjar", "va menjar", "vam menjar", "vau menjar", "van menjar"] and o["menjar_pp"]["alt"][3] == "vàrem menjar" and o["menjar_pp"]["alt"][4] == "vàreu menjar", o["menjar_pp"])
ck("ca : passé composé (he menjat…)", o["menjar_pf"]["F"] == ["he menjat", "has menjat", "ha menjat", "hem menjat", "heu menjat", "han menjat"], o["menjar_pf"])
ck("ca : pronoms élidés devant l'auxiliaire (m'he rentat, me n'he anat, ens n'hem anat)", o["rentarse"]["F"][0] == "m'he rentat" and o["anarsen"]["F"][0] == "me n'he anat" and o["anarsen"]["F"][3] == "ens n'hem anat", [o["rentarse"]["F"], o["anarsen"]["F"]])
ck("ca : anar-se'n à l'imparfait (me n'anava, ens n'anàvem)", o["anarsen_imp"]["F"][0] == "me n'anava" and o["anarsen_imp"]["F"][3] == "ens n'anàvem", o["anarsen_imp"]["F"])
ck("va : passé périphrastique (vaig menjar…)", o["va_pp"]["F"][0] == "vaig menjar" and o["va_pp"]["F"][3] == "vam menjar", o["va_pp"])
ck("verbe impersonnel (haber que) et galicien : pas de temps composé ajouté", "pc" not in o["haber_que"] and not {"pc", "pp", "pf"} & set(o["gl"]), [o["haber_que"], o["gl"]])
ck("échelle des temps : passé composé (es) et périphrastique + passé composé (ca/va) dès A2, jamais en A1",
   all(lad[0] == "pres" and all(x in lad[i].split(",") for i in (1, 2, 3) for x in (["pc"] if l == "es" else ["pp", "pf"])) for l, lad in o["lad"].items()), o["lad"])
ck("exercices de conjugaison sur les temps composés (es pc, ca pp/pf, va pp)", all(o["ex"][k] and len(o["ex"][k]["o"]) >= 3 and " " in o["ex"][k]["g"] for k in o["ex"]), o["ex"])
for l, ts in o["path"].items():
    want = {"es": ["pc"], "va": ["pp", "pf"], "ca": ["pp", "pf"]}[l]
    ks = [t[1] for t in ts]
    ck(f"{l} A2 : une étape « nouveau temps » expliquée pour chaque temps composé, ids des temps simples conservés",
       all(w in ks for w in want) and all(t[2] >= 2 and t[3] for t in ts) and [t[0] for t in ts if t[1] not in want] == [f"t{i}" for i in range(len(ts) - len(want))], ts)
ck("« Tous les temps » : le passé périphrastique n'est affiché qu'une fois ; la puce du temps l'affiche", o["allvaig"] == 1 and o["chip"], [o["allvaig"], o["chip"]])
ck("formes composées hors de l'index de classement des phrases (parcours inchangé)", not o["pqcmp"])
# n°12 — verbes ajoutés
EXP = {"es:oír": ("pres", 0, "oigo", 2), "es:andar": ("pret", 0, "anduve", 2), "es:valer": ("fut", 0, "valdré", 2), "es:traducir": ("pres", 0, "traduzco", 2),
       "gl:pór": ("pres", 5, "poñen", 2), "gl:oír": ("pres", 0, "oio", 3), "ca:haver": ("ps", 0, "haguí", 2)}
for k, (t, i, f, lv) in EXP.items():
    v = o["nv"][k]
    ck(f"{k} : tableau complet, niveau {lv}, forme témoin {f}", v and not v["bad"] and v["t"][t][i] == f and v["lv"] == lv, v and [v["bad"], v["t"].get(t), v["lv"]])
# n°13 et n°14
ck("ca : « D'on ets? » (et plus « De on ets? »)", "|D'on ets?|" in o["ca"]["xd"] and "De on ets" not in o["ca"]["xd"])
import re
for z in ["xd", "scn", "rx", "ptb"]:
    ck(f"ca ({z}) : graphie « soc », plus de « sóc »", not re.search(r"\b[Ss]óc\b", o["ca"][z]), re.findall(r".{0,30}\b[Ss]óc\b.{0,20}", o["ca"][z])[:3])
# enregistrements des textes catalans modifiés : les deux voix des dialogues catalans
TX = ["D'on ets?", "Soc francès.", "Soc de França.", "Soc francesa.", "Soc una persona organitzada, resolutiva i acostumada a treballar en equip.",
      "No, gràcies, soc una torrada.", "Sí, soc al·lèrgic al meu quadern.", "Soc el lloguer del mes.", "Jo soc l'Ana.", "Soc al·lèrgic als fruits secs."]
for v in ["ca_elia", "ca_grau"]:
    k = json.load(open(f"{ROOT}/v/{v}/{v}.json"))["k"]
    ck(f"{v} : clips des textes catalans corrigés", all(t in k for t in TX), [t for t in TX if t not in k])
ck("aucune erreur JS", not err, err[:3])
print(sum(R), "/", len(R), "OK"); sys.exit(0 if all(R) else 1)
