# Mesure du délai entre l'appui et le début réel du son (premier AudioBufferSource.start / <audio>.play), réseau bridé, sans cache.
import sys,json,time,statistics
from playwright.sync_api import sync_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else "http://127.0.0.1:8773/"
LANG=sys.argv[2] if len(sys.argv)>2 else "es"
PROF={"4G":(9*125000,60),"3G rapide":(1.6*125000,150),"3G lente":(0.4*125000,400)}
INIT="""window.__st=[];const P=AudioBufferSourceNode.prototype.start;AudioBufferSourceNode.prototype.start=function(){window.__st.push(performance.now());return P.apply(this,arguments)};
const PP=HTMLMediaElement.prototype.play;HTMLMediaElement.prototype.play=function(){window.__st.push(performance.now());return PP.apply(this,arguments)};
Object.defineProperty(navigator,'serviceWorker',{value:undefined,configurable:true});"""
def run(b,prof,texts,lang):
    c=b.new_context(locale="fr-FR");pg=c.new_page();pg.add_init_script(INIT);pg.goto(BASE+"index.html");pg.wait_for_timeout(2500)
    cdp=c.new_cdp_session(pg);cdp.send("Network.enable");bw,rtt=PROF[prof]
    cdp.send("Network.emulateNetworkConditions",{"offline":False,"latency":rtt,"downloadThroughput":bw,"uploadThroughput":bw})
    pg.evaluate("l=>{S.lang=l;build()}",lang);out=[]
    for t in texts:
        pg.evaluate("window.__st=[]");t0=pg.evaluate("performance.now()");pg.evaluate("t=>{aud('m'+Math.random(),[t])}",t)
        d=None
        for _ in range(400):
            st=pg.evaluate("window.__st");
            if st:d=st[0]-t0;break
            pg.wait_for_timeout(50)
        out.append(None if d is None else round(d));pg.evaluate("stopSp()");pg.wait_for_timeout(100)
    c.close();return out
if __name__=="__main__":
    T=json.load(open("/tmp/au/lat_texts.json"))[LANG]
    with sync_playwright() as p:
        b=p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
        for prof in sys.argv[3].split(",") if len(sys.argv)>3 else ["4G","3G rapide"]:
            for kind in ("enregistré","non enregistré"):
                r=run(b,prof,T[kind],LANG);ok=[x for x in r if x is not None]
                print(f"{LANG} {prof:10} {kind:15} démarre {len(ok)}/{len(r)} | médiane {statistics.median(ok) if ok else '-'} ms | max {max(ok) if ok else '-'} ms | détail {r}",flush=True)
        b.close()
