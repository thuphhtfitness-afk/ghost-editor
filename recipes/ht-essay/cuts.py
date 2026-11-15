"""cuts.py ranges.json -> prints cuts: energy VAD islands within each source range, pauses trimmed."""
import sys, json, wave, numpy as np
S = sys.argv[2] if len(sys.argv) > 2 else None
wf = wave.open(S); a = np.frombuffer(wf.readframes(wf.getnframes()), np.int16).astype(np.float32) / 32768
sr = 16000; hop = 320  # 20 ms
nfr = len(a) // hop
rms = np.sqrt((a[:nfr * hop].reshape(nfr, hop) ** 2).mean(1) + 1e-12)
db = 20 * np.log10(rms)
noise = np.percentile(db, 15)
def islands(r0, r1, thr_off=10, maxgap=0.38, lead=0.10, tail=0.16, minlen=0.12):
    i0, i1 = int(r0 * 50), int(r1 * 50)
    seg = db[i0:i1]
    sm = np.convolve(seg, np.ones(3) / 3, mode="same")
    on = sm > noise + thr_off
    isl = []; st = None
    for k, v in enumerate(on):
        if v and st is None: st = k
        if not v and st is not None: isl.append([st, k]); st = None
    if st is not None: isl.append([st, len(on)])
    isl = [[(i0 + s) / 50, (i0 + e) / 50] for s, e in isl if (e - s) / 50 >= 0.06]
    merged = []
    for s, e in isl:
        if merged and s - merged[-1][1] < maxgap: merged[-1][1] = e
        else: merged.append([s, e])
    merged = [[max(r0, s - lead), min(r1, e + tail)] for s, e in merged if e - s >= minlen]
    out = []
    for s, e in merged:
        if out and s <= out[-1][1] + 0.02: out[-1][1] = e
        else: out.append([s, e])
    return out
if __name__ == "__main__":
    ranges = json.load(open(sys.argv[1]))
    cuts = []
    for r in ranges:
        cuts += islands(r[0], r[1])
    cuts = [[round(s, 3), round(e, 3)] for s, e in cuts]
    print(json.dumps(cuts))
    print("noise", round(float(noise), 1), "total", round(sum(e - s for s, e in cuts), 2), "raw", round(sum(r[1] - r[0] for r in ranges), 2), file=sys.stderr)
