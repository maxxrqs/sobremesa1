# Génère les clips manquants de la voix es_dora (Kokoro ef_dora) au format des paquets Sobremesa
import json,os,subprocess,sys,numpy as np
from kokoro_onnx import Kokoro
k=Kokoro('kokoro-v1.0.onnx','voices-v1.0.bin')
texts=json.load(open('texts/full_es.json'));V='es_dora';os.makedirs(f'out/{V}',exist_ok=True)
def trim(x,SR):
    x=x.astype(np.float32);pk=np.abs(x).max()
    if pk<1e-4:return None
    th=max(0.004,pk*0.02);nz=np.where(np.abs(x)>th)[0]
    a=max(0,nz[0]-int(0.09*SR));b=min(len(x),nz[-1]+int(0.2*SR));y=x[a:b].copy()
    y*=min(6.0,0.8/np.abs(y).max());f=int(0.012*SR);y[:f]*=np.linspace(0,1,f);y[-f:]*=np.linspace(1,0,f);return y
def enc(y,sr):
    b=(np.clip(y,-1,1)*32767).astype('<i2').tobytes()
    return subprocess.run(['ffmpeg','-loglevel','error','-f','s16le','-ar',str(sr),'-ac','1','-i','-','-codec:a','libmp3lame','-b:a','32k','-ar','22050','-ac','1','-f','mp3','-'],input=b,capture_output=True,check=True).stdout
pack=bytearray();K={};bad=[]
for t in texts:
    try:
        a,sr=k.create(t,voice='ef_dora',speed=1.0,lang='es');y=trim(a,sr)
        if y is None or len(y)<0.1*sr:raise ValueError('vide')
        c=enc(y,sr);K[t]=[0,len(pack),len(c)];pack+=c
    except Exception as e:bad.append([t,str(e)[:80]])
open(f'out/{V}/{V}_g9.mp3','wb').write(pack)
json.dump({'p':[f'{V}_g9.mp3'],'k':K},open(f'out/{V}/gap.json','w'),ensure_ascii=False)
json.dump(bad,open('out/bad.json','w'),ensure_ascii=False)
print(V,len(K),'clips',len(bad),'échecs',len(pack)//1000,'ko')
