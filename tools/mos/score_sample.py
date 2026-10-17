import json,random,subprocess,os,sys,re,csv
sys.path.insert(0,'/tmp/q/um');import mos,torch
torch.set_num_threads(3)
R='/home/claude/sobremesa1/'
sets={'es':(R+'a/es.json',R+'a/')}
for v in os.listdir(R+'v'):
    if v!='voices.json':sets[v]=(f'{R}v/{v}/{v}.json',f'{R}v/{v}/')
w=csv.writer(open('/tmp/q/full_mos.csv','a',newline='',encoding='utf8'))
done=set()
try:
    for r in csv.reader(open('/tmp/q/full_mos.csv',encoding='utf8')):done.add((r[0],r[2]))
except:pass
for name,(ij,base) in sets.items():
    ix=json.load(open(ij));P=ix['p']
    gi={i for i,p in enumerate(P) if re.search(r'_g\d+\.mp3$',p)}
    for t,(pi,off,ln) in ix['k'].items():
        if (name,t) in done:continue
        fn=f'/tmp/q/s/f_{name}.mp3';open(fn,'wb').write(open(base+P[pi],'rb').read()[off:off+ln])
        subprocess.run(['ffmpeg','-y','-loglevel','quiet','-i',fn,'-ar','22050',f'/tmp/q/s/f_{name}.wav'])
        try:sc=round(mos.score(f'/tmp/q/s/f_{name}.wav'),3)
        except Exception:sc=''
        w.writerow([name,'gap' if pi in gi else 'orig',t,sc])
