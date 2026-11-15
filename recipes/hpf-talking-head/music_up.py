"""Brighter bed for HPF talking head (still under the voice): 108 BPM, soft four-on-the-floor kick, claps on 2 and 4,
off-beat hats, plucked 8th-note chords (Am-F-C-G), bouncing bass. Generated, no licence questions.
Out: audio/bed_up.wav (48 kHz stereo). usage: music_up.py <seconds>"""
import numpy as np, wave, sys
from scipy.signal import butter, lfilter
SR = 48000; BPM = 108; beat = 60 / BPM
dur = float(sys.argv[1]) if len(sys.argv) > 1 else 130
n = int(dur * SR); rng = np.random.default_rng(11)
mid = lambda m: 440 * 2 ** ((m - 69) / 12)
L = np.zeros(n); R = np.zeros(n)
def add(sig, start, pan=0.0):
    i0 = int(start * SR)
    if i0 >= n: return
    m = min(len(sig), n - i0)
    L[i0:i0 + m] += sig[:m] * (1 - pan); R[i0:i0 + m] += sig[:m] * (1 + pan)
def pluck(f, length, amp, bright=1.0):
    t = np.arange(int((length + 0.3) * SR)) / SR
    env = np.minimum(1, t / 0.004) * np.exp(-t / (length * 0.45))
    s = (np.sin(2*np.pi*f*t) + 0.5*bright*np.sin(2*np.pi*2*f*t)*np.exp(-t/0.12) + 0.25*bright*np.sign(np.sin(2*np.pi*f*t))*np.exp(-t/0.05))
    return s * env * amp
chords = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]   # Am F C G
bass = [45, 41, 36, 43]
bar = 4 * beat
t0 = np.arange(int(0.3 * SR)) / SR
kick = np.sin(2*np.pi*(50 + 90*np.exp(-t0/0.025))*t0) * np.exp(-t0/0.11) * 0.55
clap_t = np.arange(int(0.18 * SR)) / SR
clap = rng.standard_normal(len(clap_t)) * (np.exp(-clap_t/0.035) + 0.6*np.exp(-np.maximum(0, clap_t-0.012)/0.03)*(clap_t > 0.012)) * 0.16
b_, a_ = butter(2, [900/(SR/2), 4000/(SR/2)], "band"); clap = lfilter(b_, a_, clap) * 2.2
hat_t = np.arange(int(0.05 * SR)) / SR
hb, ha = butter(2, 7000/(SR/2), "high")
k = 0
while k * bar < dur:
    c = chords[k % 4]; st = k * bar
    for b in range(4):
        add(kick, st + b * beat)
        if b in (1, 3): add(clap, st + b * beat, 0.05)
        h = lfilter(hb, ha, rng.standard_normal(len(hat_t))) * np.exp(-hat_t / 0.012) * 0.10
        add(h, st + b * beat + beat / 2, -0.2)
    for e in range(8):                      # plucked chord stabs on 8ths, accent pattern
        acc = 1.0 if e in (0, 3, 6) else 0.55
        for j, m in enumerate(c):
            add(pluck(mid(m + 12), beat * 0.45, 0.045 * acc), st + e * beat / 2 + j * 0.006, (j - 1) * 0.3)
    for e, off in enumerate([0, 0.75, 1.5, 2.0, 2.75, 3.5]):   # bouncing bass
        add(pluck(mid(bass[k % 4] - 12 + (12 if e in (2, 4) else 0)), beat * 0.5, 0.20, bright=0.25), st + off * beat)
    k += 1
lb, la = butter(2, 9000/(SR/2)); L, R = lfilter(lb, la, L), lfilter(lb, la, R)
t = np.arange(n) / SR
fade = np.minimum(1, t / 0.8) * np.minimum(1, (dur - t) / 1.5)
st = np.stack([L * fade, R * fade], 1); st /= np.abs(st).max() / 0.85
w = wave.open("audio/bed_up.wav", "w"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((st * 32767).astype(np.int16).tobytes()); w.close(); print("ok")
