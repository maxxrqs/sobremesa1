import sys,os,json,subprocess,time,numpy as np
sys.path.insert(0,'/home/claude/work')
from strip import strip
from kokoro_onnx import Kokoro
k=Kokoro('/tmp/q/kokoro.onnx','/tmp/q/voices.bin')
SIL=open('/home/claude/work/sil80.mp3','rb').read()
OUT='/tmp/q/kes';os.makedirs(OUT,exist_ok=True)
texts=json.load(open('/tmp/q/es_gap_texts.json'))
def trim(x,SR):
    x=x.astype(np.float32);pk=np.abs(x).max()
    if pk<1e-4:return None
    th=max(0.004,pk*0.02);nz=np.where(np.abs(x)>th)[0]
    a=max(0,nz[0]-int(0.09*SR));b=min(len(x),nz[-1]+int(0.2*SR));y=x[a:b].copy()
    y*=min(6.0,0.8/np.abs(y).max());f=int(0.012*SR);y[:f]*=np.linspace(0,1,f);y[-f:]*=np.linspace(1,0,f);return y
def enc(y,sr):
    b=(np.clip(y,-1,1)*32767).astype('<i2').tobytes()
    m=subprocess.run(['ffmpeg','-loglevel','error','-f','s16le','-ar',str(sr),'-ac','1','-i','-','-codec:a','libmp3lame','-b:a','32k','-ar','22050','-f','mp3','-'],input=b,capture_output=True).stdout
    return strip(m)[0]+SIL
done={};bad=[];t0=time.time()
for i,t in enumerate(texts):
    try:
        a,sr=k.create(t,voice='ef_dora',speed=1.0,lang='es');y=trim(a,sr)
        if y is None or len(y)<0.1*sr:raise ValueError
        done[t]=enc(y,sr)
    except Exception:bad.append(t)
    if i%100==0:print(i,len(texts),len(bad),round(time.time()-t0),flush=True)
PM=4_800_000;packs=[];K={};cur=None;cl=0
for t,b in done.items():
    if cur is None or cl+len(b)>PM:
        if cur:cur.close()
        n=f'es_k{len(packs)}.mp3';packs.append(n);cur=open(f'{OUT}/{n}','wb');cl=0
    K[t]=[len(packs)-1,cl,len(b)];cur.write(b);cl+=len(b)
cur.close()
json.dump({'p':packs,'k':K},open(f'{OUT}/gap.json','w'),ensure_ascii=False,separators=(',',':'))
json.dump(bad,open(f'{OUT}/bad.json','w'),ensure_ascii=False);print('FIN',len(K),len(bad))
