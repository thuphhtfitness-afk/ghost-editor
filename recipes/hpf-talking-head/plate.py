"""Build the cut plate: every piece trimmed frame-exact from the 3K source, punch-in crop, B-roll swaps.
Video and voice are cut at the same snapped times. Output: build/plate.mp4 (1080x1920 30fps) + build/voice.wav"""
import subprocess, sys, os
sys.path.insert(0, os.getcwd())  # the reel project holds plan.py
from plan import *

W, H = 1080, 1920
SW, SH = 1728, 3072
os.makedirs("build/seg", exist_ok=True)


def crop_expr(z, cx, cy):
    cw, ch = round(SW / z / 2) * 2, round(SH / z / 2) * 2
    x = min(max(cx * SW - cw / 2, 0), SW - cw)
    y = min(max(cy * SH - ch / 2, 0), SH - ch)
    return f"crop={cw}:{ch}:{int(x)}:{int(y)},scale={W}:{H}:flags=lanczos"


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-2000:]); sys.exit(1)


tl, total = timeline()
lst = []
for i, (a, b, es, n, z, br) in enumerate(tl):
    out = f"build/seg/{i:02d}.mp4"
    lst.append(out)
    if os.path.exists(out) and "--force" not in sys.argv:
        continue
    if br:
        bs, bz, bx, by = br
        src, ss, vf = BROLL, bs, crop_expr(bz, bx, by)
    else:
        cx = FACE[0] if z > 1 else 0.5
        cy = FACE[1] if z > 1 else 0.5
        src, ss, vf = SRC, a, crop_expr(z, cx, cy)
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ss:.6f}", "-i", src,
         "-vf", f"fps={FPS},{vf},format=yuv420p", "-frames:v", str(n), "-an",
         "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-color_primaries", "bt709",
         "-color_trc", "bt709", "-colorspace", "bt709", out])
    print("seg", i, n, "frames", "broll" if br else f"z{z}", flush=True)

with open("build/seg/list.txt", "w") as f:
    for p in lst:
        f.write(f"file '{os.path.basename(p)}'\n")
run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", "build/seg/list.txt", "-c", "copy", "build/plate.mp4"])

# voice: same snapped windows, 8 ms fades at every cut against clicks
parts, fil = [], []
for i, (a, b, es, n, z, br) in enumerate(tl):
    d = n / FPS
    fil.append(f"[0:a]atrim={a:.6f}:{a + d:.6f},asetpts=PTS-STARTPTS,afade=t=in:d=0.008,afade=t=out:st={d - 0.008:.4f}:d=0.008[a{i}]")
    parts.append(f"[a{i}]")
fil.append("".join(parts) + f"concat=n={len(parts)}:v=0:a=1,aresample=48000[v]")
run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-filter_complex", ";".join(fil), "-map", "[v]", "-ac", "1", "build/voice_raw.wav"])
print("total", total, "frames", total / FPS, "s")
