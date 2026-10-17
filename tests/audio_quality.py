# Qualité du signal des clips ajoutés (paquets *_gN.mp3) : durée, débit par caractère, niveau, écrêtage, silences en tête/queue.
# Mesure objective seulement : elle ne dit rien du caractère naturel de la voix (à juger à l'écoute).
# Usage : audio_quality.py [dossier_dépôt] [voix …]
import sys,os,json,subprocess,numpy as np
ROOT=sys.argv[1] if len(sys.argv)>1 else os.path.join(os.path.dirname(os.path.abspath(__file__)),"..")
VO=json.load(open(ROOT+"/v/voices.json"));ALLV=[v["id"] for l in VO for v in VO[l]]+["es"]
voices=sys.argv[2:] or ALLV;bad_total=0
for v in voices:
    ip,d=(ROOT+"/a/es.json",ROOT+"/a") if v=="es" else (ROOT+f"/v/{v}/{v}.json",ROOT+f"/v/{v}")
    ix=json.load(open(ip));import re;gp=[i for i,n in enumerate(ix["p"]) if re.search(r"_g\d+\.mp3$",n)]
    if not gp:print(v,"aucun clip ajouté");continue
    packs={i:open(f"{d}/{ix['p'][i]}","rb").read() for i in gp};R=[];bad=[]
    for k,(pi,o,l) in ix["k"].items():
        if pi not in packs:continue
        pcm=np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i","-","-f","s16le","-ac","1","-ar","22050","-"],input=packs[pi][o:o+l],capture_output=True).stdout,"<i2").astype(np.float32)/32768
        if len(pcm)<2200:bad.append((k,"trop court"));continue
        dur=len(pcm)/22050;pk=float(np.abs(pcm).max());clip=float((np.abs(pcm)>=.999).mean())
        th=max(.01,pk*.04);nz=np.where(np.abs(pcm)>th)[0];lead=nz[0]/22050 if len(nz) else 9;tail=(len(pcm)-nz[-1])/22050 if len(nz) else 9
        spc=(dur-.08)/max(1,len(k));R.append((k,dur,spc,pk,clip,lead,tail))
        why=[]
        if not .0225<=spc<=.32:why.append(f"débit {spc:.3f} s/car")
        if pk<.3 or pk>1.0:why.append(f"niveau {pk:.2f}")
        if clip>.001:why.append(f"écrêtage {clip*100:.2f} %")
        if lead>.4:why.append(f"silence initial {lead:.2f}s")
        if tail>.9:why.append(f"silence final {tail:.2f}s")
        if dur>45:why.append("trop long")
        if why:bad.append((k,", ".join(why)))
    a=np.array([[r[1],r[2],r[3]] for r in R])
    print(f"{v}: {len(R)} clips ajoutés | durée moy {a[:,0].mean():.1f}s | débit {np.median(a[:,1])*1000:.0f} ms/car | pic médian {np.median(a[:,2]):.2f} | hors normes {len(bad)}")
    for k,w in bad[:8]:print("    ",repr(k[:60]),w)
    bad_total+=len(bad)
sys.exit(0 if bad_total==0 else 1)
