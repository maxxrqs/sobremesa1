// Test du kit de déploiement du relais (deploiement/relais/deployer.mjs), sans Cloudflare réel :
// Wrangler est simulé (journal des appels et des secrets reçus) et le relais tourne en local (Miniflare, worker.js réel).
// Usage : MINIFLARE_DIR=<dossier contenant node_modules/miniflare> node tests/deploiement_relais.mjs
import { createRequire } from "node:module";
import { readFileSync, writeFileSync, mkdtempSync, existsSync, readdirSync, cpSync } from "node:fs";
import { spawn } from "node:child_process";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
const ROOT = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
const KIT = path.join(ROOT, "deploiement", "relais");
const req = createRequire(path.join(process.env.MINIFLARE_DIR || ROOT, "noop.js"));
const { Miniflare } = req("miniflare");
const R = []; const ck = (n, c, i = "") => { R.push(!!c); console.log((c ? "OK   " : "FAIL ") + n + (c ? "" : "  " + String(i).slice(0, 500))); };
const TMP = mkdtempSync(path.join(tmpdir(), "kit-test-"));

// ---- Wrangler simulé ----
const FAKE = path.join(TMP, "fake-wrangler.mjs");
writeFileSync(FAKE, `
import { appendFileSync, readFileSync, existsSync } from "node:fs";
const a = process.argv.slice(2), mode = process.env.FAKE_MODE || "ok", log = process.env.FAKE_LOG;
let input = ""; if (a[0] === "secret" && a[1] === "put") { try { input = readFileSync(0, "utf8"); } catch (e) {} }   // le vrai Wrangler ne lit l'entrée que pour « secret put »
appendFileSync(log, JSON.stringify({ a, input: a[0] === "secret" && a[1] === "put" ? input : undefined, acc: process.env.CLOUDFLARE_ACCOUNT_ID || null, cwd: process.cwd(), files: existsSync("worker.js") && existsSync("wrangler.toml") }) + "\\n");
const cmd = a.join(" ");
if (cmd.startsWith("deploy --dry-run")) { console.log("Your Worker has access to the following bindings:\\nenv.BUDGET (Budget)  Durable Object\\n--dry-run: exiting now."); process.exit(0); }
if (cmd === "whoami --json") { if (mode === "logout" && !existsSync(process.env.FAKE_LOG + ".login")) process.exit(1);
  console.log(JSON.stringify({ loggedIn: true, accounts: mode === "multi" ? [{ name: "Perso", id: "a".repeat(32) }, { name: "Sobremesa", id: "b".repeat(32) }] : [{ name: "Max", id: "c".repeat(32) }] })); process.exit(0); }
if (cmd === "login") { appendFileSync(process.env.FAKE_LOG + ".login", "1"); process.exit(0); }
if (cmd === "deploy") { if (mode === "deployfail") { console.error("Authentication error [code: 10000]"); process.exit(1); } console.log("Uploaded sobremesa-ia\\nDeployed sobremesa-ia triggers"); process.exit(0); }
if (a[0] === "secret" && a[1] === "put") { if (mode === "secretfail" && a[2] === "TURNSTILE_SECRET") { console.error("échec simulé " + input); process.exit(1); } console.log("✨ Success! Uploaded secret " + a[2]); process.exit(0); }
if (cmd === "secret list --format json") { console.log(JSON.stringify(["GEMINI_KEY","TURNSTILE_SECRET","SESSION_SECRET","IP_SECRET"].map(name => ({ name, type: "secret_text" })))); process.exit(0); }
process.exit(2);
`);
// ---- relais local (worker.js réel, Turnstile simulé : tout jeton est refusé) ----
const PORT = 8794, RELAIS = "http://127.0.0.1:" + PORT;
const mkRelay = async (script, bindings) => { const mf = new Miniflare({ modules: true, script, compatibilityDate: "2025-06-01", host: "127.0.0.1", port: PORT, bindings, durableObjects: script.includes("class Budget") ? { BUDGET: "Budget" } : undefined,
  outboundService: async r => new URL(r.url).hostname === "challenges.cloudflare.com" ? Response.json({ success: false }) : new Response("blocked", { status: 599 }) }); await mf.ready; return mf; };
const SEC = { GEMINI_KEY: "k-test", TURNSTILE_SECRET: "t-test", SESSION_SECRET: "s".repeat(40), IP_SECRET: "i".repeat(40), ALLOWED_ORIGIN: "https://maxxrqs.github.io", ALLOWED_HOSTNAME: "maxxrqs.github.io" };
let relay = await mkRelay(readFileSync(path.join(ROOT, "worker.js"), "utf8"), SEC);

// Valeurs factices construites à l'exécution (aucune chaîne au format d'une vraie clé dans ce fichier).
const GK = ["AQ", ".Ab"].join("") + "Faux-Faux_".repeat(4), GK_OLD = ["AI", "za"].join("") + "Faux".repeat(8) + "123", TS = ["0", "x"].join("") + "FauxSecretTurnstile".repeat(2);
let n = 0;
function runKit(lines, { mode = "ok", kit = KIT, args = [] } = {}) {
  const log = path.join(TMP, "log" + (++n) + ".jsonl"); writeFileSync(log, "");
  return new Promise(res => {
    const p = spawn(process.execPath, [path.join(kit, "deployer.mjs"), ...args], { env: { ...process.env, SOB_WRANGLER: `"${process.execPath}" "${FAKE}"`, SOB_RELAIS_URL: RELAIS, FAKE_LOG: log, FAKE_MODE: mode, CLOUDFLARE_ACCOUNT_ID: "" }, stdio: ["pipe", "pipe", "pipe"] });
    let out = ""; p.stdout.on("data", d => out += d); p.stderr.on("data", d => out += d);
    p.stdin.write(lines.map(x => x + "\n").join("")); p.stdin.end();
    p.on("close", code => { const calls = readFileSync(log, "utf8").trim().split("\n").filter(Boolean).map(JSON.parse); res({ code, out, calls }); });
  });
}
const cmds = c => c.calls.map(x => x.a.join(" "));
const tmpLeft = () => readdirSync(tmpdir()).filter(x => x.startsWith("sobremesa-relais-")).length;

{ // 1. parcours normal
  const t0 = tmpLeft();
  const r = await runKit([GK, TS, "OUI"]);
  const puts = r.calls.filter(x => x.a[0] === "secret" && x.a[1] === "put");
  const got = Object.fromEntries(puts.map(x => [x.a[2], x.input]));
  ck("parcours normal : code 0, message final « Relais sécurisé en place »", r.code === 0 && /Relais sécurisé en place/.test(r.out), r.out.slice(-600));
  ck("ordre : validation à blanc, connexion, déploiement, PUIS les 4 secrets, puis contrôle de la liste", cmds(r).join("|") === "deploy --dry-run --outdir dist|whoami --json|deploy|secret put GEMINI_KEY|secret put TURNSTILE_SECRET|secret put SESSION_SECRET|secret put IP_SECRET|secret list --format json", cmds(r).join("|"));
  ck("les 2 clés saisies sont transmises telles quelles ; les 2 secrets internes sont générés (64 car. base64, différents)", got.GEMINI_KEY === GK && got.TURNSTILE_SECRET === TS && /^[A-Za-z0-9+/]{64}$/.test(got.SESSION_SECRET) && /^[A-Za-z0-9+/]{64}$/.test(got.IP_SECRET) && got.SESSION_SECRET !== got.IP_SECRET, JSON.stringify(Object.keys(got)));
  ck("aucun secret n'apparaît à l'écran (ni les clés saisies, ni les secrets générés)", ![GK, TS, got.SESSION_SECRET, got.IP_SECRET].some(v => v && r.out.includes(v)));
  ck("secrets transmis par l'entrée standard, jamais en argument de commande", r.calls.every(x => !x.a.some(y => [GK, TS, got.SESSION_SECRET, got.IP_SECRET].includes(y))));
  ck("compte Cloudflare fixé pour toute la suite (aucune question de Wrangler)", r.calls.filter(x => x.a[0] !== "whoami" && !x.a.includes("--dry-run")).every(x => x.acc === "c".repeat(32)));
  ck("Wrangler travaille dans un dossier temporaire contenant worker.js et wrangler.toml, supprimé à la fin", r.calls.every(x => x.files && x.cwd.includes("sobremesa-relais-")) && tmpLeft() === t0);
  ck("les 4 contrôles en ligne passent contre le vrai worker.js (401 sans session, faux jeton 401, CORS étranger refusé, pré-vol accepté)", (r.out.match(/  ✔ /g) || []).length >= 9 && !/  ✖ /.test(r.out), r.out.slice(-700));
}
{ // 2. refus et erreurs : rien n'est modifié
  let r = await runKit(["AIzaTropCourt", TS, "OUI"]);
  ck("clé Gemini au mauvais format : arrêt AVANT tout déploiement ou envoi de secret", r.code === 1 && /format attendu/.test(r.out) && !cmds(r).some(c => c === "deploy" || c.startsWith("secret")), cmds(r));
  r = await runKit([GK, "1x00000000AAAAAAAAAAAAAAAAAAAAAAAA", "OUI"]);
  ck("clé publique Turnstile collée à la place de la secrète : arrêt avant toute modification", r.code === 1 && /Site key/.test(r.out) && !cmds(r).some(c => c === "deploy" || c.startsWith("secret")), cmds(r));
  r = await runKit([GK_OLD, TS, "non"]);
  ck("ancien format de clé Gemini (AIza) toujours accepté", /2 clés reçues/.test(r.out), r.out.slice(-300));
  r = await runKit([GK + GK, TS, "non"]);
  ck("clé Gemini collée deux fois : refusée (aucune espace, longueur bornée) avant toute modification", r.code === 1 && /format attendu/.test(r.out) && !cmds(r).some(c => c === "deploy" || c.startsWith("secret")), r.out.slice(-200));
  r = await runKit([GK, TS, "non"]);
  ck("confirmation refusée : rien n'est déployé, aucun secret envoyé", r.code === 1 && !cmds(r).some(c => c === "deploy" || c.startsWith("secret")), cmds(r));
  r = await runKit([GK, TS, "OUI"], { mode: "deployfail" });
  ck("échec du déploiement : arrêt, aucun secret envoyé, l'ancien relais reste en place", r.code === 1 && /ancien relais reste en place/.test(r.out) && !cmds(r).some(c => c.startsWith("secret")), cmds(r));
  r = await runKit([GK, TS, "OUI"], { mode: "secretfail" });
  ck("échec d'un secret : arrêt explicite, la valeur du secret n'est jamais affichée", r.code === 1 && /TURNSTILE_SECRET n'a pas pu/.test(r.out) && !r.out.includes(TS), r.out.slice(-300));
  r = await runKit(["2", GK, TS, "OUI"], { mode: "multi" });
  ck("plusieurs comptes Cloudflare : choix par numéro, le compte choisi est utilisé partout", r.code === 0 && r.calls.filter(x => x.a[0] === "deploy" && x.a.length === 1).every(x => x.acc === "b".repeat(32)), r.out.slice(-300));
  r = await runKit([GK, TS, "OUI"], { mode: "logout" });
  ck("pas encore connecté : la connexion Cloudflare est lancée puis le déploiement continue", r.code === 0 && cmds(r).includes("login"), cmds(r));
  const k2 = path.join(TMP, "kit-modifie"); cpSync(KIT, k2, { recursive: true }); writeFileSync(path.join(k2, "worker.js"), readFileSync(path.join(ROOT, "worker.js"), "utf8") + "\n// modifié");
  r = await runKit([GK, TS, "OUI"], { kit: k2 });
  ck("worker.js différent de la version N4 v3 validée : refus immédiat, aucun appel à Wrangler", r.code === 1 && /ne correspond pas/.test(r.out) && r.calls.length === 0, r.out.slice(-300));
}
{ // 3. mode vérification seule
  let r = await runKit([], { args: ["--verifier"] });
  ck("--verifier contre le relais N4 v3 : tout est vert, aucun appel à Wrangler", r.code === 0 && r.calls.length === 0 && (r.out.match(/  ✔ /g) || []).length === 4, r.out);
  await relay.dispose();
  const old = `export default { async fetch(req) { const o = req.headers.get("origin") || ""; const h = { "access-control-allow-origin": o || "*", "access-control-allow-headers": "content-type" };
    if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: h }); return new Response("réponse de l'ancien relais", { status: 200, headers: h }); } };`;
  relay = await mkRelay(old, {});
  r = await runKit([], { args: ["--verifier"] });
  ck("--verifier contre un relais à l'ancienne (sans session) : signalé en échec", r.code === 1 && /✖ appel IA sans session refusé/.test(r.out), r.out);
  await relay.dispose();
  relay = await mkRelay(readFileSync(path.join(ROOT, "worker.js"), "utf8"), { ...SEC, IP_SECRET: "" });
  r = await runKit([], { args: ["--verifier"] });
  ck("--verifier contre le relais N4 v3 sans IP_SECRET (503) : signalé en échec", r.code === 1 && /✖ faux jeton Turnstile/.test(r.out), r.out);
  await relay.dispose();
}
{ // 4. cohérence du kit
  const cfg = JSON.parse(readFileSync(path.join(KIT, "relais.json"), "utf8"));
  const { createHash } = await import("node:crypto");
  const conf = readFileSync(path.join(ROOT, "config.js"), "utf8");
  ck("relais.json : empreinte = worker.js du dépôt ; adresse = SOB_AI de config.js", cfg.workerSha256 === createHash("sha256").update(readFileSync(path.join(ROOT, "worker.js"))).digest("hex") && conf.includes(`window.SOB_AI="${cfg.url}"`));
  const toml = readFileSync(path.join(KIT, "wrangler.toml"), "utf8");
  ck("wrangler.toml : nom sobremesa-ia, Durable Object SQLite BUDGET, origine Sobremesa, aucun limiteur payant, aucun secret", /name = "sobremesa-ia"/.test(toml) && /class_name = "Budget"/.test(toml) && /new_sqlite_classes = \["Budget"\]/.test(toml) && /ALLOWED_ORIGIN = "https:\/\/maxxrqs.github.io"/.test(toml) && !/^\[\[ratelimits\]\]/m.test(toml) && !/(GEMINI_KEY|TURNSTILE_SECRET|SESSION_SECRET|IP_SECRET)\s*=/.test(toml));
  const all = ["deployer.mjs", "wrangler.toml", "relais.json", "LISEZ-MOI.txt"].map(f => readFileSync(path.join(KIT, f), "utf8")).join("\n");
  ck("aucune clé ni secret dans le kit", !/AIza[0-9A-Za-z_-]{30}|0x4AAA[0-9A-Za-z_-]{10,}/.test(all));
}
console.log(`\n${R.filter(Boolean).length}/${R.length} contrôles OK`);
process.exit(R.every(Boolean) ? 0 : 1);
