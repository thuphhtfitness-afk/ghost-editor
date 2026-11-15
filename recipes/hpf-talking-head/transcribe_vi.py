import sys, json, wave, numpy as np
def load(p):
    w=wave.open(p); a=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768; return a
from faster_whisper import WhisperModel
m = WhisperModel(sys.argv[1], device="cpu", compute_type="int8", cpu_threads=4)
for n in sys.argv[2:]:
    segs, info = m.transcribe(load(f"wav/{n}.wav"), language="vi", word_timestamps=True, vad_filter=True, condition_on_previous_text=False, beam_size=5)
    out=[]
    with open(f"tx/{n}.txt","w") as t:
        for s in segs:
            out.append({"s":s.start,"e":s.end,"text":s.text.strip(),"words":[{"w":w.word.strip(),"s":w.start,"e":w.end,"p":w.probability} for w in s.words]})
            t.write(f"[{s.start:7.2f}-{s.end:7.2f}] {s.text.strip()}\n"); t.flush()
    json.dump(out, open(f"tx/{n}.json","w"), ensure_ascii=False)
    print("done", n, flush=True)
