import sys, json, wave, numpy as np
clip=sys.argv[1]; lo,hi=float(sys.argv[2]),float(sys.argv[3])
w=wave.open(f"wav/{clip}.wav"); a=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768
sp=json.load(open(f"build/vad_{clip}.json"))
def f0(x):
    x=x-x.mean(); 
    if np.sqrt((x**2).mean())<0.01: return None
    c=np.correlate(x,x,'full')[len(x)-1:]; c/=c[0]+1e-9
    lmin,lmax=int(16000/350),int(16000/70); k=lmin+np.argmax(c[lmin:lmax])
    return 16000/k if c[k]>0.4 else None
for s,e in sp:
    if s<lo or s>hi: continue
    fs=[f0(a[int(t*16000):int(t*16000)+640]) for t in np.arange(s,e-0.04,0.02)]
    fs=[f for f in fs if f]
    if fs: print(f"{s:7.2f}-{e:7.2f}  f0 {np.median(fs):5.0f} Hz  {'NỮ' if np.median(fs)>175 else 'nam'}")
