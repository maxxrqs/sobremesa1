import sys,torch,torchaudio,soundfile as sf,numpy as np
sys.path.insert(0,'/tmp/q/um')
from speechmos.utmos22.strong.model import UTMOS22Strong
m=UTMOS22Strong();m.load_state_dict(torch.load('/tmp/q/utmos.pt',map_location='cpu'));m.eval()
def score(path):
    w,sr=sf.read(path,dtype='float32')
    if w.ndim>1:w=w.mean(1)
    w=torch.from_numpy(w)[None]
    if sr!=16000:w=torchaudio.functional.resample(w,sr,16000)
    with torch.no_grad():return float(m(w,16000))
if __name__=="__main__":
    for p in sys.argv[1:]:print(p,round(score(p),2))
