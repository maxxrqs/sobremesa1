// Réserve n°4 : l'appli (index.html + shim.js) avec le relais sécurisé (worker.js) servi localement par Miniflare.
// Gemini et Turnstile sont simulés ; aucun secret réel. Vérifie :
//  - que les invites RÉELLES de l'appli (conversation et traduction, toutes langues, niveaux, mascottes, scénarios)
//    sont acceptées par le relais (sinon une modification de l'appli casserait l'IA en silence) ;
//  - conversation et traduction de bout en bout ; renouvellement de session sur 401 ; messages sur 429 et refus ;
//  - aucun secret dans le navigateur ; l'ancienne adresse du relais n'est jamais contactée.
// Usage : MINIFLARE_DIR=<dossier contenant node_modules/miniflare> node tests/relais_app.mjs
import { createRequire } from "node:module";
import { readFileSync } from "node:fs";
import { spawn } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";
const ROOT = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
const req = createRequire(path.join(process.env.MINIFLARE_DIR || ROOT, "noop.js"));
const { Miniflare } = req("miniflare");
const { chromium } = createRequire(import.meta.url)("playwright");
const WEB = 8792, AIP = 8793, PAGE = `http://127.0.0.1:${WEB}/`, AI = `http://127.0.0.1:${AIP}`;
const SECRETS = { GEMINI_KEY: "test-gemini-key-NE-DOIT-JAMAIS-SORTIR-7f3a", TURNSTILE_SECRET: "test-turnstile-secret-NE-DOIT-JAMAIS-SORTIR-91c2", SESSION_SECRET: "test-session-secret-0123456789abcdef-NE-DOIT-JAMAIS-SORTIR", IP_SECRET: "test-ip-secret-0123456789abcdef0123-NE-DOIT-JAMAIS-SORTIR" };
const R = []; const ck = (n, c, info = "") => { R.push(!!c); console.log((c ? "OK   " : "FAIL ") + n + (c ? "" : "  " + String(info).slice(0, 500))); };
const M = { gem: [], ts: 0 };
async function outbound(request) {
  const u = new URL(request.url);
  if (u.hostname === "challenges.cloudflare.com") {
    M.ts++; const f = await request.formData(); const tok = f.get("response");
    const ok = f.get("secret") === SECRETS.TURNSTILE_SECRET && tok.startsWith("local-");
    return Response.json(ok ? { success: true, hostname: "127.0.0.1", action: "sobremesa-ia", challenge_ts: new Date().toISOString() } : { success: false });
  }
  if (u.hostname === "generativelanguage.googleapis.com") {
    const body = await request.json(); const p = body.contents[0].parts[0].text; M.gem.push(p);
    const text = p.startsWith("You are an expert professional translator") ? '{"src":"fr","t":"Hola, ¿qué tal estás hoy?","alt":[],"note":""}'
      : '{"r":"¡Hola! ¿Qué te pongo hoy?","tr":"Bonjour ! Je vous sers quoi aujourd\'hui ?","fix":"","hints":["Un café","Un café con leche","Un café con leche, por favor"]}';
    return Response.json({ candidates: [{ content: { parts: [{ text }] } }] });
  }
  return new Response("blocked", { status: 599 });
}
const srv = spawn("python3", ["-B", "tests/rangesrv.py", String(WEB), "."], { cwd: ROOT, stdio: "ignore" });
const mf = new Miniflare({ modules: true, script: readFileSync(path.join(ROOT, "worker.js"), "utf8"), compatibilityDate: "2025-06-01", host: "127.0.0.1", port: AIP,
  bindings: { ...SECRETS, ALLOWED_ORIGIN: `http://127.0.0.1:${WEB}`, ALLOWED_HOSTNAME: "127.0.0.1", REQ_SESSION: "100000", REQ_SESSION_MIN: "100000", REQ_IP_DAY: "100000", REQ_DAY: "100000", CHARS_DAY: "900000000", SESS_IP_DAY: "1000" },
  durableObjects: { BUDGET: "Budget" }, outboundService: outbound });
await mf.ready;
await new Promise(r => setTimeout(r, 1200));
const b = await chromium.launch();
const errs = [], seen = [], oldRelay = [];
async function newPage({ ts = "test-sitekey", token = "local", routeAi } = {}) {
  const ctx = await b.newContext({ locale: "fr-FR" });
  const pg = await ctx.newPage();
  pg.on("pageerror", e => errs.push(String(e)));
  pg.on("response", async r => { try { if (r.url().startsWith(AI)) seen.push(r.url() + " " + (await r.text()) + JSON.stringify(r.headers())); } catch (e) {} });
  await ctx.route(/workers\.dev/, r => { oldRelay.push(r.request().url()); r.abort(); });
  await ctx.route(/challenges\.cloudflare\.com/, r => r.abort());
  await ctx.route(/config\.js(\?|$)/, r => r.fulfill({ contentType: "application/javascript", body: `window.SOB_AI=${JSON.stringify(AI)};window.SOB_PUSH="";window.SOB_TS=${JSON.stringify(ts)};` }));
  if (routeAi) await ctx.route(new RegExp("^" + AI.replace(/\./g, "\\.") + "/ai"), routeAi);
  await pg.addInitScript(tok => { window.__ts = []; window.turnstile = { render(el, o) { window.__ts.push({ sitekey: o.sitekey, action: o.action, inDom: document.body.contains(el) }); setTimeout(() => o.callback(tok + "-" + Math.random().toString(36).slice(2)), 20); return window.__ts.length; }, remove() {} }; }, token);
  await pg.goto(PAGE + "index.html"); await pg.waitForTimeout(2500);
  return { ctx, pg };
}
const reqs = pg => { const a = []; pg.on("request", r => { if (r.url().startsWith(AI)) a.push(new URL(r.url()).pathname); }); return a; };

// ---------- 1. invites réelles de l'appli acceptées par le relais ----------
{
  const { ctx, pg } = await newPage();
  const P = await pg.evaluate(async () => {
    const out = { conv: [], trad: [] }, UIL = ["fr", "en", "it", "de", "pt"], mas = Object.keys(FX.A), L = ["es", "va", "ca", "gl", "eu"];
    const hists = [[], [{ w: "npc", t: "¡Hola! ¿Qué tal?" }], [{ w: "npc", t: "Bon dia!" }, { w: "me", t: "Vull un cafè amb llet, «si us plau» — 3€ ${x} `y` 😀" }],
      Array.from({ length: 20 }, (_, i) => ({ w: i % 2 ? "me" : "npc", t: "Frase número " + i + " con \"comillas\" y acentos: ñ, ç, à." }))];
    let i = 0;
    for (const l of L) for (let lvl = 1; lvl <= 5; lvl++) for (const h of hists) {
      i++; S.lang = l; S.lvl = lvl; S.mas = mas[i % mas.length]; UI = UIL[i % 5];
      try { build(); xens(); } catch (e) {}
      CV = { s: CVS[i % CVS.length], msgs: h.slice(), busy: 0, n: 0, auto: false, tq: 0, rec: 0, guided: i % 2 === 0 };
      out.conv.push(cvPrompt());
    }
    for (const s of CVS) { CV = { s, msgs: [], guided: false }; S.lang = "es"; UI = "fr"; out.conv.push(cvPrompt()); }
    CV = null;
    const keep = TSAMP; const srcs = ["auto", ...Object.keys(TLP)], texts = ["Bonjour, ça va ?", "Ligne 1\nLigne 2\n\nFin.", 'Il a dit : "${non}" `code` </text> <text> 100 %', "x".repeat(2999) + "y", "Hola"];
    let j = 0;
    for (const src of srcs) for (const dst of Object.keys(TLP)) {
      if (src === dst) continue; j++; if (j % 3) continue;
      TS.src = src; TS.dst = dst; UI = UIL[j % 5];
      TSAMP = async p => { out.trad.push(p); return { text: '{"t":"ok"}' }; };
      try { await tsClaude(texts[j % texts.length]); } catch (e) {}
    }
    TSAMP = keep; return out;
  });
  const sres = await fetch(AI + "/session", { method: "POST", headers: { origin: `http://127.0.0.1:${WEB}`, "content-type": "application/json" }, body: JSON.stringify({ token: "local-direct" }) });
  const { s } = await sres.json();
  const bad = [];
  for (const [mode, list] of Object.entries(P)) for (const p of list) {
    const r = await fetch(AI + "/ai", { method: "POST", headers: { origin: `http://127.0.0.1:${WEB}`, authorization: "Bearer " + s, "content-type": "application/json" }, body: JSON.stringify({ mode, prompt: p }) });
    if (r.status !== 200) bad.push(mode + " " + r.status + " " + p.slice(0, 120));
  }
  ck(`invites réelles de l'appli acceptées : ${P.conv.length} conversations (5 langues × 5 niveaux × 3 mascottes, 10 scénarios, 5 langues d'interface, historiques avec guillemets, emoji, \${}, 20 messages) et ${P.trad.length} traductions (11 sources dont détection auto, 10 cibles, 2 999 caractères, </text> dans le texte)`, bad.length === 0 && P.conv.length >= 100 && P.trad.length >= 30, bad.slice(0, 3));
  await ctx.close();
}
// ---------- 2. conversation et traduction de bout en bout ----------
{
  const { ctx, pg } = await newPage(); const rq = reqs(pg);
  const n0 = M.gem.length;
  await pg.evaluate(() => cvStart("cafe"));
  await pg.waitForFunction(() => document.getElementById("cvc") && document.getElementById("cvc").textContent.includes("Qué te pongo hoy"), null, { timeout: 15000 }).catch(() => {});
  const c1 = await pg.evaluate(() => ({ txt: (document.getElementById("cvc") || {}).textContent || "", hints: (document.getElementById("cvhints") || {}).textContent || "", err: CV && CV.err }));
  ck("conversation : la mascotte ouvre la discussion via le relais sécurisé, indices affichés", c1.txt.includes("¡Hola! ¿Qué te pongo hoy?") && c1.hints.includes("Un café") && !c1.err, JSON.stringify(c1));
  await pg.evaluate(() => cvSend("Un café con leche, por favor"));
  await pg.waitForFunction(() => CV && !CV.busy && CV.msgs.filter(m => m.w === "npc").length >= 2, null, { timeout: 15000 }).catch(() => {});
  const c2 = await pg.evaluate(() => ({ n: CV.msgs.length, err: CV.err, ts: window.__ts }));
  ck("conversation : réponse au message de l'apprenant, une seule vérification Turnstile (session réutilisée)", c2.n >= 3 && !c2.err && c2.ts.length === 1 && c2.ts[0].sitekey === "test-sitekey" && c2.ts[0].action === "sobremesa-ia" && c2.ts[0].inDom, JSON.stringify(c2));
  ck("le navigateur appelle /session une fois puis /ai, et Gemini reçoit les invites", rq.filter(x => x === "/session").length === 1 && rq.filter(x => x === "/ai").length === 2 && M.gem.length - n0 === 2, rq.join());
  await pg.evaluate(() => { cvQuit && cvQuit(); trad(); });
  await pg.fill("#tin", "Bonjour, comment ça va aujourd'hui ?"); await pg.dispatchEvent("#tin", "input");
  await pg.waitForFunction(() => (document.getElementById("tout") || {}).textContent && document.getElementById("tout").textContent.includes("Hola, ¿qué tal"), null, { timeout: 15000 }).catch(() => {});
  const t1 = await pg.evaluate(() => ({ out: (document.getElementById("tout") || {}).textContent, ts: window.__ts.length }));
  ck("traduction : résultat affiché, même session (pas de nouvelle vérification)", t1.out && t1.out.includes("Hola, ¿qué tal estás hoy?") && t1.ts === 1, JSON.stringify(t1));
  const st = await pg.evaluate(() => ({ ls: JSON.stringify(localStorage), ss: JSON.stringify(sessionStorage), cfg: [window.SOB_AI, window.SOB_TS].join() }));
  const blob = JSON.stringify(st) + seen.join("\n");
  ck("aucun secret (clé Gemini, secret Turnstile, secret de session) dans le navigateur : réponses, stockage, configuration", !Object.values(SECRETS).some(v => blob.includes(v)));
  await ctx.close();
}
// ---------- 3. 401 : session expirée ou refusée ----------
{
  let first = true;
  const { ctx, pg } = await newPage({ routeAi: r => { if (first) { first = false; return r.fulfill({ status: 401, body: "unauthorized", headers: { "access-control-allow-origin": `http://127.0.0.1:${WEB}` } }); } return r.continue(); } });
  const rq = reqs(pg);
  await pg.evaluate(() => trad());
  await pg.fill("#tin", "Je voudrais réserver une table pour deux."); await pg.dispatchEvent("#tin", "input");
  await pg.waitForFunction(() => (document.getElementById("tout") || {}).textContent.includes("Hola, ¿qué tal"), null, { timeout: 15000 }).catch(() => {});
  const r1 = await pg.evaluate(() => ({ out: document.getElementById("tout").textContent, ts: window.__ts.length }));
  ck("401 sur /ai (session expirée ou clé tournée) : nouvelle session obtenue et requête rejouée une fois, sans erreur visible", r1.out.includes("Hola, ¿qué tal") && r1.ts === 2 && rq.filter(x => x === "/session").length === 2, JSON.stringify(r1) + " " + rq.join());
  await ctx.close();
}
{
  const { ctx, pg } = await newPage({ token: "fail" }); const rq = reqs(pg);
  await pg.evaluate(() => trad());
  await pg.fill("#tin", "Où se trouve la gare, s'il vous plaît ?"); await pg.dispatchEvent("#tin", "input");
  await pg.waitForFunction(() => /impossible|code/i.test((document.getElementById("tout") || {}).textContent || ""), null, { timeout: 20000 }).catch(() => {});
  const r2 = await pg.evaluate(() => document.getElementById("tout").textContent);
  ck("vérification Turnstile refusée : message d'erreur clair (code http401), aucun appel /ai", /Traduction impossible/.test(r2) && /http401/.test(r2) && !rq.includes("/ai"), r2 + " " + rq.join());
  await ctx.close();
}
// ---------- 4. 429 ----------
{
  const { ctx, pg } = await newPage({ routeAi: r => r.fulfill({ status: 429, body: "rate_limited", headers: { "access-control-allow-origin": `http://127.0.0.1:${WEB}` } }) });
  await pg.evaluate(() => trad());
  await pg.fill("#tin", "Pouvez-vous répéter plus lentement ?"); await pg.dispatchEvent("#tin", "input");
  await pg.waitForFunction(() => /Trop de demandes/.test((document.getElementById("tout") || {}).textContent || ""), null, { timeout: 25000 }).catch(() => {});
  const t = await pg.evaluate(() => document.getElementById("tout").textContent);
  ck("429 en traduction : message « Trop de demandes… attends quelques secondes » après les nouvelles tentatives prévues", /Trop de demandes/.test(t), t);
  await pg.evaluate(() => cvStart("amigos"));
  await pg.waitForFunction(() => CV && !CV.busy && CV.err, null, { timeout: 15000 }).catch(() => {});
  const c = await pg.evaluate(() => ({ err: CV && CV.err, busy: CV && CV.busy, box: (document.getElementById("cverr") || {}).textContent }));
  ck("429 en conversation : erreur « rate_limited » signalée, saisie de nouveau disponible", c.err === "rate_limited" && !c.busy, JSON.stringify(c));
  await ctx.close();
}
// ---------- 5. configuration incomplète ----------
{
  const { ctx, pg } = await newPage({ ts: "" }); const rq = reqs(pg);
  await pg.evaluate(() => trad());
  await pg.fill("#tin", "Merci beaucoup pour votre aide."); await pg.dispatchEvent("#tin", "input");
  await pg.waitForFunction(() => /impossible/i.test((document.getElementById("tout") || {}).textContent || ""), null, { timeout: 15000 }).catch(() => {});
  const t = await pg.evaluate(() => document.getElementById("tout").textContent);
  ck("clé publique Turnstile absente de config.js : erreur explicite (http503), aucune requête au relais", /impossible/i.test(t) && /http503/.test(t) && rq.length === 0, t + " " + rq.join());
  await ctx.close();
}
// ---------- 6. page de diagnostic ----------
{
  const { ctx, pg } = await newPage();
  await pg.goto(PAGE + "diag.html"); await pg.waitForTimeout(500);
  await pg.click("#b");
  await pg.waitForFunction(() => /Terminé en/.test(document.getElementById("o").textContent), null, { timeout: 30000 }).catch(() => {});
  const d = await pg.evaluate(() => ({ o: document.getElementById("o").textContent, ts: window.__ts }));
  ck("diag.html : configuration affichée, « 401 → OK » sans session, jeton Turnstile, session, traduction de test en 200",
    /Clé publique Turnstile : présente/.test(d.o) && /Statut 401 .*OK, le relais refuse/.test(d.o) && /Session valable jusqu'à/.test(d.o) && /4\. Appel IA[\s\S]*Statut 200[\s\S]*Hola, ¿qué tal/.test(d.o) && d.ts.length === 1 && d.ts[0].action === "sobremesa-ia", d.o);
  ck("diag.html : la session n'apparaît jamais dans le résultat (capture partageable)", !/eyJ|Bearer|\.[A-Za-z0-9_-]{40,}/.test(d.o) && !Object.values(SECRETS).some(v => d.o.includes(v)));
  await ctx.close();
  const p2 = await newPage({ ts: "" }); await p2.pg.goto(PAGE + "diag.html"); await p2.pg.waitForTimeout(300); await p2.pg.click("#b"); await p2.pg.waitForTimeout(300);
  const d2 = await p2.pg.evaluate(() => document.getElementById("o").textContent);
  ck("diag.html sans clé publique Turnstile : « ABSENTE » et arrêt explicite", /ABSENTE/.test(d2) && /ARRÊT : configuration incomplète/.test(d2), d2);
  await p2.ctx.close();
}
ck("l'ancienne adresse du relais (workers.dev) n'est jamais contactée par l'appli testée", oldRelay.length === 0, oldRelay);
ck("aucune erreur JavaScript", errs.length === 0, errs.slice(0, 3));
await b.close(); await mf.dispose(); srv.kill();
console.log(`\n${R.filter(Boolean).length}/${R.length} contrôles OK`);
process.exit(R.every(Boolean) ? 0 : 1);
