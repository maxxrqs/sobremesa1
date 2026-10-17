import sys,json,re
from playwright.sync_api import sync_playwright
BASE="http://localhost:8772/"
N=int(sys.argv[1]) if len(sys.argv)>1 else 150
GEN="""(a)=>{const lang=a.lang,N=a.n,SRC={};const add=(s,t)=>{if(typeof t!=="string")return;t=t.replace(/\\s+/g," ").trim();if(!t||/^[a-z]:/.test(t))return;(SRC[t]=SRC[t]||new Set()).add(s)};
 S.lang=lang;S.pthAll=1;build();try{xens()}catch(e){};
 ALL.forEach(w=>add("word",w[0]));PH.forEach(p=>add("phrase",p[0]));
 TX.forEach(t=>{add("text",t[0]);(t[0].match(/[^.!?]+[.!?]+\\s*/g)||[t[0]]).forEach(s=>add("textsent",s))});
 try{xdP(lang).forEach(z=>{add("dlg-npc",z.n);add("dlg-model",z.m);z.va.forEach(v=>add("dlg-model",v))})}catch(e){}
 for(let L=1;L<=5;L++){S.lang=lang;S.lvl=L;S.pth={};S.rat={};S.rq={};S.md={};build();try{xens()}catch(e){};PLC=null;
 for(const st of pathPlanMain().flat){if(st.test)continue;
  R={mode:'lesson',t:st.t||'Chunk',n:0,ok:0,xp:0,cat:null,pid:st.id,pt:st.pt||null,ws:st.ws||null,dp:st.dp||null,gp:st.gp||null,go:st.go||null,xs:st.xs||null,qs:st.qs||null,vs:st.vs||null,pp:st.pp||null};
  for(let i=0;i<N;i++){R.n=i%12;S.rq={};try{const q=mkQ(pickType(),0);const arr=(q.sa||(q.say?[q.say]:[])).slice();if(["speak","rep","speakF","speakC","speakQ","replyQ"].includes(q.ty)&&q.es)arr.push(q.es);
   arr.forEach(t=>add("ex:"+q.ty,t))}catch(e){}}}}
 const o={};for(const k in SRC)o[k]=[...SRC[k]];return o}"""
out={}
with sync_playwright() as p:
    b=p.chromium.launch();c=b.new_context(locale="fr-FR");pg=c.new_page();pg.goto(BASE+"index.html");pg.wait_for_timeout(2500)
    for l in ["es","va","ca","gl","eu"]:
        r=pg.evaluate(GEN,{"lang":l,"n":N});out[l]=r;print(l,len(r),flush=True)
    b.close()
json.dump(out,open("/tmp/au/all_texts.json","w"),ensure_ascii=False)
