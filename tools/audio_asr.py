import sys,json,random,subprocess,unicodedata,difflib,time,numpy as np,os
import sherpa_onnx
vid,N,seed=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]) if len(sys.argv)>3 else 1
D=sys.argv[4] if len(sys.argv)>4 else f'/tmp/au/out/{vid}';IDX=sys.argv[5] if len(sys.argv)>5 else 'gap.json'
lang={'eu':'eu','gl':'gl','va':'ca','ca':'ca','es':'es'}[vid.split('_')[0]]
M='/tmp/asr/sherpa-onnx-whisper-small/small'
rec=sherpa_onnx.OfflineRecognizer.from_whisper(encoder=M+'-encoder.onnx',decoder=M+'-decoder.int8.onnx',tokens=M+'-tokens.txt',language=lang,task='transcribe',num_threads=1)
d=json.load(open(f'{D}/{IDX}'));ks=list(d['k']);random.seed(seed)
sel=random.sample(ks,min(N,len(ks))) if N>0 else ks
norm=lambda s:''.join(c for c in unicodedata.normalize('NFD',s.lower()) if c.isalnum() or c==' ').strip()
packs={};out=[];t0=time.time()
for k in sel:
    p,o,l=d['k'][k]
    if p not in packs:packs[p]=open(f'{D}/{d["p"][p]}','rb').read()
    pcm=np.frombuffer(subprocess.run(['ffmpeg','-loglevel','error','-i','-','-f','s16le','-ac','1','-ar','16000','-'],input=packs[p][o:o+l],capture_output=True).stdout,'<i2').astype(np.float32)/32768
    s=rec.create_stream();s.accept_waveform(16000,np.concatenate([np.zeros(4000,np.float32),pcm,np.zeros(8000,np.float32)]));rec.decode_stream(s)
    tx=s.result.text;r=difflib.SequenceMatcher(None,norm(k),norm(tx)).ratio()
    out.append({'k':k,'tx':tx,'r':round(r,2),'dur':round(len(pcm)/16000,2),'pk':round(float(np.abs(pcm).max()),2)})
json.dump(out,open(f'/tmp/au/asr_{vid}_{seed}.json','w'),ensure_ascii=False)
rs=np.array([x['r'] for x in out])
print(vid,len(out),'moy',rs.mean().round(3),'méd',np.median(rs).round(3),'<0.6:',int((rs<0.6).sum()),'<0.8:',int((rs<0.8).sum()),'temps',round(time.time()-t0),'s')
for x in sorted(out,key=lambda x:x['r'])[:6]:print('  ',x)
