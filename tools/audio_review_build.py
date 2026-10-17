import csv,json,random,base64,subprocess,collections,re,sys,html
import numpy as np,soundfile as sf
sys.path.insert(0,'/home/claude/work')
R='/home/claude/sobremesa1/';random.seed(11)
rows=[r for r in csv.reader(open('/tmp/q/full_mos.csv',encoding='utf8')) if r[3]]
by=collections.defaultdict(list)
for r in rows:by[(r[0],r[1])].append((float(r[3]),r[2]))
NAME={'es':'Castellano','ca_elia':'Català · Elia ♀','ca_grau':'Català · Grau ♂','va_gina':'Valencià · Gina ♀','va_lluc':'Valencià · Lluc ♂','gl_a':'Galego · voz C ♂','gl_b':'Galego · voz A ♀','gl_c':'Galego · voz B ♂','eu_antton':'Euskara · Antton ♂'}
def clip(v,t):
    ij,base=(R+'a/es.json',R+'a/') if v=='es' else (f'{R}v/{v}/{v}.json',f'{R}v/{v}/')
    ix=json.load(open(ij));pi,o,l=ix['k'][t]
    return open(base+ix['p'][pi],'rb').read()[o:o+l]
items=[]
for (v,c),L in sorted(by.items()):
    L=sorted(L);pick=[L[0],L[1]]+[L[len(L)//2]]+random.sample(L[2:],5)
    seen=set();
    for sc,t in pick:
        if t in seen:continue
        seen.add(t);items.append({'g':v,'c':c,'t':t,'m':round(sc,2),'a':base64.b64encode(clip(v,t)).decode()})
# A/B castillan : original vs Kokoro
from kokoro_onnx import Kokoro
k=Kokoro('/tmp/q/kokoro.onnx','/tmp/q/voices.bin')
orig=[(m,t) for m,t in [(x[0],x[1]) for x in by[('es','orig')]]]
random.shuffle(orig);ab=[]
for m,t in orig[:12]:
    e={'t':t,'o':base64.b64encode(clip('es',t)).decode()}
    for vv in ['ef_dora','em_alex']:
        a,sr=k.create(t,voice=vv,speed=1.0,lang='es');sf.write('/tmp/q/s/r.wav',a,sr)
        e[vv]=base64.b64encode(subprocess.run(['ffmpeg','-loglevel','error','-i','/tmp/q/s/r.wav','-ac','1','-ar','22050','-b:a','32k','-f','mp3','-'],capture_output=True).stdout).decode()
    ab.append(e)
json.dump({'items':items,'ab':ab,'names':NAME},open('/tmp/q/review_data.json','w'),ensure_ascii=False)
print(len(items),len(ab))
