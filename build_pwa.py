#!/usr/bin/env python3
# Génère la PWA à partir de ../castellano.html (même code que l'artefact)
import shutil,os,re,time
here=os.path.dirname(os.path.abspath(__file__));src=os.path.join(here,"..","castellano.html")
s=open(src,encoding="utf-8").read()
head='''<link rel="manifest" href="manifest.webmanifest">
<meta name="theme-color" content="#CFE9DC">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Sobremesa">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<link rel="icon" href="icon-192.png"><link rel="apple-touch-icon" href="icon-192.png">
<script src="config.js"></script><script src="shim.js"></script>
'''
assert "<head>" in s
s=s.replace("<head>","<head>\n"+head,1)
reg='''<script>if("serviceWorker"in navigator&&location.protocol!=="file:"){addEventListener("load",()=>navigator.serviceWorker.register("sw.js").then(r=>{r.addEventListener("updatefound",()=>{const w=r.installing;w&&w.addEventListener("statechange",()=>{if(w.state==="installed"&&navigator.serviceWorker.controller&&document.getElementById("splash"))location.reload()})})}).catch(()=>{}))}</script>
'''
s=s.replace("</body>",reg+"</body>",1)
open(os.path.join(here,"index.html"),"w",encoding="utf-8").write(s)
tr=os.path.join(here,"tr");shutil.rmtree(tr,ignore_errors=True)
shutil.copytree(os.path.join(here,"..","tr"),tr)
v=str(int(time.time()))
sw=open(os.path.join(here,"sw.template.js")).read().replace("__VERSION__",v)
open(os.path.join(here,"sw.js"),"w").write(sw)
print("PWA ok, version",v,len(s)//1024,"Ko")
