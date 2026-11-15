"""Generate a soft ambient piano + pad bed (original, procedural). music.py out.wav seconds [seed]"""
import sys, numpy as np, wave
SR = 48000
dur = float(sys.argv[2]); seed = int(sys.argv[3]) if len(sys.argv) > 3 else 1
rng = np.random.default_rng(seed)
n = int(SR * (dur + 3))
L = np.zeros(n); R = np.zeros(n)
def hz(m): return 440 * 2 ** ((m - 69) / 12)
progs = [[[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]],   # Am F C G
         [[50, 53, 57], [46, 50, 53], [53, 57, 60], [48, 52, 55]]]   # Dm Bb F C
prog = progs[seed % 2]
bar = 4.0
t_all = np.arange(n) / SR
# pad
for i in range(int(dur / bar) + 2):
    ch = prog[i % 4]; s0 = int(i * bar * SR); ln = int((bar + 1.5) * SR)
    t = np.arange(ln) / SR
    env = np.minimum(t / 1.2, 1) * np.exp(-np.maximum(t - bar, 0) / 0.6)
    for m in ch + [ch[0] - 12]:
        for det, pan in ((-0.12, 0.3), (0.12, 0.7)):
            sig = np.sin(2 * np.pi * (hz(m) + det) * t + rng.uniform(0, 6)) * 0.018 * env
            e = min(n, s0 + ln)
            L[s0:e] += sig[:e - s0] * (1 - pan); R[s0:e] += sig[:e - s0] * pan
# piano arpeggio
step = bar / 8
for i in range(int(dur / step) + 1):
    ch = prog[int(i * step / bar) % 4]
    pat = [0, 1, 2, 1, 0, 2, 1, 2]
    if rng.random() < 0.18: continue
    m = ch[pat[i % 8]] + 12 + (12 if (i % 8 == 5 and rng.random() < 0.5) else 0)
    s0 = int(i * step * SR); ln = int(2.5 * SR); t = np.arange(ln) / SR
    f = hz(m)
    sig = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) * np.exp(-t * 3) + 0.12 * np.sin(6 * np.pi * f * t) * np.exp(-t * 5))
    sig *= np.exp(-t * 1.6) * np.minimum(t / 0.005, 1) * 0.07 * (0.75 + 0.25 * rng.random())
    pan = 0.35 + 0.3 * rng.random(); e = min(n, s0 + ln)
    L[s0:e] += sig[:e - s0] * (1 - pan); R[s0:e] += sig[:e - s0] * pan
# reverb
ir_n = int(2.2 * SR); ir_t = np.arange(ir_n) / SR
def verb(x, s):
    ir = np.random.default_rng(s).normal(0, 1, ir_n) * np.exp(-ir_t / 0.55); ir[0] = 0
    N = 1 << int(np.ceil(np.log2(len(x) + ir_n)))
    y = np.fft.irfft(np.fft.rfft(x, N) * np.fft.rfft(ir, N), N)[:len(x)]
    return x * 0.7 + y * 0.03
L = verb(L, 11); R = verb(R, 12)
out = np.stack([L, R], 1)[: int(SR * dur)]
fade = int(SR * 2); out[-fade:] *= np.linspace(1, 0, fade)[:, None]; out[:int(SR * 0.5)] *= np.linspace(0, 1, int(SR * 0.5))[:, None]
out = out / (np.abs(out).max() + 1e-9) * 0.8
w = wave.open(sys.argv[1], "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((out * 32767).astype(np.int16).tobytes()); w.close()
