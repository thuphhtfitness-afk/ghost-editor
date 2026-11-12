#!/usr/bin/env python3
"""zoomed 9:16 plate that follows the speaker's face: a W x 16/9*W window around the tracked face, Lanczos up to
1080x1920 + light unsharp. plate_zoom.py src.mov track.json cut.json out.mp4 [W=450] [face_y_frac=0.40]"""
import json, subprocess, sys
import cv2, numpy as np

src, track, cutf, out = sys.argv[1:5]
W = int(sys.argv[5]) if len(sys.argv) > 5 else 450
FY = float(sys.argv[6]) if len(sys.argv) > 6 else 0.40
H = round(W * 16 / 9)
tr = [r for r in json.load(open(track)) if r[1] is not None]
T = np.array([r[0] for r in tr]); X = np.array([r[1] for r in tr], float); Y = np.array([r[2] for r in tr], float)


def smooth(v, k=5):           # median of +-1 s, then a light moving average: steady, follows the pan
    m = np.array([np.median(v[max(0, i - k // 2 - 1):i + k // 2 + 2]) for i in range(len(v))])
    return np.convolve(np.pad(m, 1, mode="edge"), [0.25, 0.5, 0.25], "valid")


X, Y = smooth(X), smooth(Y)
segs = json.load(open(cutf))["segs"]
cap = cv2.VideoCapture(src)
fps_src = cap.get(cv2.CAP_PROP_FPS)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", "1080x1920", "-r", "30",
                        "-i", "-", "-vf", "unsharp=5:5:0.6,tpad=stop_mode=clone:stop_duration=1.0", "-c:v", "libx264",
                        "-preset", "medium", "-crf", "15", "-pix_fmt", "yuv420p", "-g", "30", out], stdin=subprocess.PIPE)
n = 0
for s in segs:
    a, b = s["src"]
    nf = int(round((b - a) * 30))
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(round(a * fps_src)))
    for k in range(nf):
        t = a + k / 30
        ok, f = cap.read()
        if not ok:
            break
        cx, cy = np.interp(t, T, X), np.interp(t, T, Y)
        x0 = int(np.clip(cx - W / 2, 0, f.shape[1] - W))
        y0 = int(np.clip(cy - FY * H, 0, f.shape[0] - H))
        crop = f[y0:y0 + H, x0:x0 + W]
        enc.stdin.write(cv2.resize(crop, (1080, 1920), interpolation=cv2.INTER_LANCZOS4).tobytes())
        n += 1
enc.stdin.close(); enc.wait()
print(f"{n} frames -> {out}")
