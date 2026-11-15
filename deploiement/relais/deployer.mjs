#!/usr/bin/env node
// Sobremesa — déploiement du relais IA sécurisé (N4 v3). Une seule commande : node deployer.mjs
// Ce script : vérifie les fichiers, connecte Cloudflare (le navigateur s'ouvre, tu cliques « Allow »),
// demande 2 clés en saisie MASQUÉE (jamais affichées ni enregistrées sur le disque), génère les 2 autres,
// envoie les 4 secrets à Cloudflare, déploie, puis vérifie que les protections répondent en ligne.
// Rien n'est modifié sans ta confirmation (« OUI »). Uniquement des fonctions gratuites de Cloudflare.
// Options : --verifier (contrôles en ligne seulement, aucun changement)
import { spawn } from "node:child_process";
import { createHash, randomBytes } from "node:crypto";
import { existsSync, readFileSync, writeFileSync, mkdtempSync, rmSync, copyFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const CFG = JSON.parse(readFileSync(path.join(HERE, "relais.json"), "utf8"));
const WRANGLER = process.env.SOB_WRANGLER || `npx --yes wrangler@${CFG.wrangler}`;   // SOB_WRANGLER : tests uniquement
const URL0 = (process.env.SOB_RELAIS_URL || CFG.url).replace(/\/+$/, "");          // SOB_RELAIS_URL : tests uniquement
const VERIF = process.argv.includes("--verifier");
const SECRETS = ["GEMINI_KEY", "TURNSTILE_SECRET", "SESSION_SECRET", "IP_SECRET"];

const say = s => process.stdout.write(s + "\n");
const step = (n, s) => say(`\n[${n}] ${s}`);
const stop = s => { say("\n✖ " + s + "\nRien d'autre n'a été modifié. Envoie une capture de ce message à Claude."); process.exit(1); };

function run(args, { input, quiet } = {}) {
  return new Promise(res => {
    const p = spawn(WRANGLER + " " + args, { shell: true, cwd: WORK, stdio: [input !== undefined ? "pipe" : quiet ? "ignore" : "inherit", quiet ? "pipe" : "inherit", quiet ? "pipe" : "inherit"], env: { ...process.env, WRANGLER_SEND_METRICS: "false" } });
    let out = "";
    if (quiet) { p.stdout.on("data", d => out += d); p.stderr.on("data", d => out += d); }
    if (input !== undefined) { p.stdin.write(input); p.stdin.end(); }
    p.on("close", code => res({ code, out }));
  });
}
// Lecture ligne à ligne quand l'entrée n'est pas un terminal (tests) : tampon partagé entre les questions.
let LBUF = "", LWAIT = null, LEND = false;
function nextLine() {
  const si = process.stdin;
  if (!nextLine.on) { nextLine.on = true; si.setEncoding("utf8"); si.on("data", d => { LBUF += d; flush(); }); si.on("end", () => { LEND = true; flush(); }); }
  return new Promise(r => { LWAIT = r; flush(); });
}
function flush() {
  if (!LWAIT) return;
  const i = LBUF.indexOf("\n");
  if (i >= 0) { const l = LBUF.slice(0, i).replace(/\r$/, ""); LBUF = LBUF.slice(i + 1); const w = LWAIT; LWAIT = null; w(l); }
  else if (LEND) { const w = LWAIT; LWAIT = null; w(LBUF); LBUF = ""; }
}
// Saisie masquée : rien ne s'affiche pendant la frappe ; la valeur reste en mémoire puis est transmise à Cloudflare.
function ask(q, hidden) {
  return new Promise(res => {
    process.stdout.write(q);
    const si = process.stdin;
    if (!si.isTTY) return nextLine().then(l => { process.stdout.write("\n"); res(l); });
    let v = ""; si.setRawMode(true); si.resume(); si.setEncoding("utf8");
    const on = ch => {
      for (const c of ch) {
        if (c === "\u0003") { si.setRawMode(false); say("\nAnnulé."); process.exit(1); }
        if (c === "\r" || c === "\n") { si.setRawMode(false); si.off("data", on); si.pause(); process.stdout.write("\n"); return res(v); }
        if (c === "\u007f" || c === "\b") { v = v.slice(0, -1); if (!hidden) process.stdout.write("\b \b"); continue; }
        v += c; if (!hidden) process.stdout.write(c);
      }
    };
    si.on("data", on);
  });
}
async function checks() {
  const o = CFG.origin, r = [];
  const t = async (name, f) => { try { r.push([name, await f()]); } catch (e) { r.push([name, false]); } };
  await t("appel IA sans session refusé (401)", async () => { const x = await fetch(URL0 + "/ai", { method: "POST", headers: { origin: o, "content-type": "application/json" }, body: "{}" }); return x.status === 401; });
  await t("faux jeton Turnstile refusé (401) ; secrets et Durable Object présents (pas de 503)", async () => { const x = await fetch(URL0 + "/session", { method: "POST", headers: { origin: o, "content-type": "application/json" }, body: JSON.stringify({ token: "verification-deploiement" }) }); return x.status === 401; });
  await t("site étranger refusé, sans autorisation CORS", async () => { const x = await fetch(URL0 + "/session", { method: "OPTIONS", headers: { origin: "https://exemple-etranger.invalid", "access-control-request-method": "POST" } }); return x.status === 403 && !x.headers.get("access-control-allow-origin"); });
  await t("pré-vol du site Sobremesa accepté", async () => { const x = await fetch(URL0 + "/ai", { method: "OPTIONS", headers: { origin: o, "access-control-request-method": "POST", "access-control-request-headers": "authorization,content-type" } }); return x.status === 204 && x.headers.get("access-control-allow-origin") === o; });
  return r;
}

let WORK = HERE;
say("Sobremesa — relais IA sécurisé (N4 v3)\nAdresse : " + URL0);
if (VERIF) {
  const r = await checks(); for (const [n, ok] of r) say((ok ? "  ✔ " : "  ✖ ") + n);
  process.exit(r.every(x => x[1]) ? 0 : 1);
}

step(1, "Vérifications locales");
const [maj, min] = process.versions.node.split(".").map(Number);
if (maj < 22 || (maj === 22 && min < 12)) stop(`Node.js ${process.versions.node} est trop ancien. Installe la version « LTS » depuis https://nodejs.org puis relance la commande.`);
const wsrc = [path.join(HERE, "worker.js"), path.join(HERE, "..", "..", "worker.js")].find(existsSync);
if (!wsrc) stop("worker.js introuvable à côté du script.");
const h = createHash("sha256").update(readFileSync(wsrc)).digest("hex");
if (h !== CFG.workerSha256) stop("worker.js ne correspond pas à la version N4 v3 validée (empreinte différente).");
WORK = mkdtempSync(path.join(tmpdir(), "sobremesa-relais-"));
copyFileSync(wsrc, path.join(WORK, "worker.js")); copyFileSync(path.join(HERE, "wrangler.toml"), path.join(WORK, "wrangler.toml"));
process.on("exit", () => { try { rmSync(WORK, { recursive: true, force: true }); } catch (e) {} });
say("  ✔ Node.js " + process.versions.node + " ; worker.js = version N4 v3 validée");
let dry = await run("deploy --dry-run --outdir dist", { quiet: true });
if (dry.code !== 0 || !/BUDGET/.test(dry.out)) stop("La configuration n'a pas pu être validée :\n" + dry.out.slice(-800));
say("  ✔ configuration validée (Worker + Durable Object, offre gratuite)");

step(2, "Connexion à Cloudflare");
const whoami = async () => { const r = await run("whoami --json", { quiet: true }); try { return r.code === 0 ? JSON.parse(r.out.slice(r.out.indexOf("{"))) : null; } catch (e) { return null; } };
let who = await whoami();
if (!who) {
  say("  Ton navigateur va s'ouvrir : connecte-toi à Cloudflare puis clique « Allow ».");
  if ((await run("login")).code !== 0) stop("Connexion à Cloudflare non aboutie.");
  who = await whoami();
  if (!who) stop("Connexion à Cloudflare non confirmée.");
}
const accs = (who.accounts || []).filter(a => a && a.id);
if (!accs.length) stop("Aucun compte Cloudflare trouvé pour cette connexion.");
let acc = accs[0];
if (accs.length > 1) {
  accs.forEach((a, i) => say(`    ${i + 1}. ${a.name}`));
  const n = parseInt(await ask("  Plusieurs comptes : tape le numéro de celui qui contient le relais sobremesa-ia : ", false), 10);
  if (!(n >= 1 && n <= accs.length)) stop("Numéro de compte invalide.");
  acc = accs[n - 1];
}
process.env.CLOUDFLARE_ACCOUNT_ID = acc.id;   // évite toute question de Wrangler pendant la suite
say("  ✔ connecté au compte « " + acc.name + " »");

step(3, "Les 2 clés à coller (rien ne s'affiche pendant la saisie, c'est normal)");
const gk = (await ask("  Clé Gemini (Google AI Studio), puis Entrée : ", true)).trim();
// Formats Google : « AQ. » (clés actuelles d'AI Studio) ou « AIza » (anciennes clés).
if (!/^(AQ\.[A-Za-z0-9._-]{20,200}|AIza[0-9A-Za-z_-]{30,})$/.test(gk) || (gk.match(/AQ\.|AIza/g) || []).length !== 1) stop("Cette clé Gemini n'a pas le format attendu (elle commence par « AQ. » ou « AIza »). Relance la commande et colle-la une seule fois (clic droit), puis Entrée.");
const ts = (await ask("  Clé SECRÈTE Turnstile (Cloudflare, « Secret key »), puis Entrée : ", true)).trim();
if (!/^0x[0-9A-Za-z_-]{20,}$/.test(ts)) stop("Cette clé secrète Turnstile n'a pas le format attendu (elle commence par « 0x »). Attention à ne pas coller la clé publique (« Site key »).");
const vals = { GEMINI_KEY: gk, TURNSTILE_SECRET: ts, SESSION_SECRET: randomBytes(48).toString("base64"), IP_SECRET: randomBytes(48).toString("base64") };
say("  ✔ 2 clés reçues ; 2 secrets internes générés automatiquement (jamais affichés)");

step(4, "Confirmation");
say("  Le relais va être remplacé par la version sécurisée. Jusqu'à la publication de la nouvelle page,");
say("  la conversation et le traducteur de l'ancienne page afficheront une erreur (quelques minutes).");
if ((await ask("  Tape OUI pour continuer : ", false)).trim().toUpperCase() !== "OUI") stop("Annulé à ta demande.");

step(5, "Déploiement");
const dep = await run("deploy", { quiet: true });
if (dep.code !== 0) stop("Le déploiement a échoué (l'ancien relais reste en place) :\n" + dep.out.slice(-800));
const m = dep.out.match(/https:\/\/[a-z0-9.-]+\.workers\.dev/);
if (m && m[0] !== URL0) stop(`Le relais a été déployé à ${m[0]}, mais Sobremesa utilise ${URL0}. Préviens Claude avant toute autre action.`);
say("  ✔ déployé à " + URL0 + " (il refuse tout tant que les secrets ne sont pas enregistrés)");

step(6, "Envoi des 4 secrets à Cloudflare");
for (const k of SECRETS) {
  const r = await run(`secret put ${k}`, { input: vals[k], quiet: true });
  if (r.code !== 0) stop(`Le secret ${k} n'a pas pu être enregistré (le relais reste fermé, aucune dépense possible). Relance simplement la commande.\n` + r.out.replace(/[A-Za-z0-9+/_=-]{30,}/g, "…").slice(-600));
  say("  ✔ " + k);
}
for (const k of Object.keys(vals)) vals[k] = "";

step(7, "Vérifications en ligne");
await new Promise(r => setTimeout(r, 4000));
const lst = await run("secret list --format json", { quiet: true });
const names = (() => { try { return JSON.parse(lst.out.slice(lst.out.indexOf("["))).map(x => x.name); } catch (e) { return []; } })();
let ok = SECRETS.every(k => names.includes(k)); say((ok ? "  ✔ " : "  ✖ ") + "les 4 secrets sont enregistrés chez Cloudflare");
for (const [n, v] of await checks()) { say((v ? "  ✔ " : "  ✖ ") + n); ok = ok && v; }
if (!ok) stop("Le relais est déployé mais une vérification échoue.");
say("\n✔ Relais sécurisé en place.\nDernière étape : dis à Claude « relais déployé » en lui donnant la clé PUBLIQUE Turnstile (Site key).\nElle n'est pas secrète. Claude préparera la page ; la publication attendra ton accord.");
process.exit(0);
