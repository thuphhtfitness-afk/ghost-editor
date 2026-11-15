"""Soft lo-fi bed, generated (no licence questions): Rhodes-like chords Fmaj7-Em7-Dm7-Cmaj7 at 78 BPM,
brushed kick + soft hat, warm low-pass, vinyl hiss. Out: audio/bed.wav (48 kHz stereo), seconds = argv[1]"""
import numpy as np, wave, sys
SR = 48000; BPM = 78; beat = 60 / BPM
dur = float(sys.argv[1]) if len(sys.argv) > 1 else 90
n = int(dur * SR); t = np.arange(n) / SR
rng = np.random.default_rng(7)
mid = lambda m: 440 * 2 ** ((m - 69) / 12)
chords = [[53, 57, 60, 64], [52, 55, 59, 62], [50, 53, 57, 60], [48, 52, 55, 59]]  # Fmaj7 Em7 Dm7 Cmaj7
bass = [41, 40, 38, 36]
L = np.zeros(n); R = np.zeros(n)
bar = 4 * beat
def note(f, start, length, amp, pan=0.0, bright=1.0):
    i0 = int(start * SR); i1 = min(n, int((start + length + 1.2) * SR))
    if i0 >= n: return
    tt = np.arange(i1 - i0) / SR
    env = np.minimum(1, tt / 0.012) * np.exp(-tt / (length * 0.9))
    trem = 1 + 0.08 * np.sin(2 * np.pi * 4.5 * tt)
    s = (np.sin(2 * np.pi * f * tt) + 0.35 * bright * np.sin(2 * np.pi * 2 * f * tt) * np.exp(-tt / 0.4)
         + 0.12 * bright * np.sin(2 * np.pi * 3 * f * tt) * np.exp(-tt / 0.25)) * env * trem * amp
    L[i0:i1] += s * (1 - pan); R[i0:i1] += s * (1 + pan)
k = 0
while k * bar < dur:
    c = chords[k % 4]
    for j, m in enumerate(c):           # chord on 1, gentle re-strike on the "and" of 3
        note(mid(m), k * bar + j * 0.018, bar * 0.9, 0.11, pan=(j - 1.5) * 0.25)
        note(mid(m + 12) if j == 3 else mid(m), k * bar + 2.5 * beat + j * 0.02, beat * 1.2, 0.05, pan=(1.5 - j) * 0.2, bright=0.6)
    note(mid(bass[k % 4]), k * bar, beat * 1.8, 0.16, bright=0.3)
    note(mid(bass[k % 4]), k * bar + 2.75 * beat, beat * 0.8, 0.10, bright=0.3)
    for b in range(4):                  # soft kick on 1 and 3, brushed hat on offbeats
        st = k * bar + b * beat
        if b in (0, 2):
            i0 = int(st * SR); ln = int(0.25 * SR); tt = np.arange(min(ln, n - i0)) / SR
            kick = np.sin(2 * np.pi * (55 + 60 * np.exp(-tt / 0.03)) * tt) * np.exp(-tt / 0.09) * 0.22
            L[i0:i0 + len(tt)] += kick; R[i0:i0 + len(tt)] += kick
        i0 = int((st + beat / 2) * SR); ln = int(0.08 * SR); m_ = min(ln, n - i0)
        if m_ > 0:
            h = rng.standard_normal(m_) * np.exp(-np.arange(m_) / SR / 0.02) * 0.025
            h = np.diff(np.concatenate([[0], h]))
            L[i0:i0 + m_] += h * 0.8; R[i0:i0 + m_] += h
    k += 1
# warm low-pass (one-pole), hiss, fades
from scipy.signal import butter, lfilter
b_, a_ = butter(2, 3200 / (SR / 2))
L, R = lfilter(b_, a_, L), lfilter(b_, a_, R)
hiss = rng.standard_normal(n) * 0.004
L += hiss; R += hiss
fade = np.minimum(1, t / 1.5) * np.minimum(1, (dur - t) / 2.0)
st = np.stack([L * fade, R * fade], 1)
st /= np.abs(st).max() / 0.8
w = wave.open("audio/bed.wav", "w"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((st * 32767).astype(np.int16).tobytes()); w.close()
# click: camera-shutter style transient for the hook -> scene cut
cl = int(0.12 * SR); tt = np.arange(cl) / SR
c = (rng.standard_normal(cl) * np.exp(-tt / 0.004) * 0.9 + np.sin(2 * np.pi * 2400 * tt) * np.exp(-tt / 0.006) * 0.6)
c[int(0.045 * SR):] += (rng.standard_normal(cl - int(0.045 * SR)) * np.exp(-np.arange(cl - int(0.045 * SR)) / SR / 0.006) * 0.6)
c /= np.abs(c).max() / 0.9
w = wave.open("audio/click.wav", "w"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((c * 32767).astype(np.int16).tobytes()); w.close()
print("ok")
