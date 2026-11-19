"""Build the cut plate: every (silence-trimmed) sub-piece cut frame-exact from the 3K source with its shot size,
the voice cut at the same snapped times, and the cảnh trám clips as separate layers.
Out: build/plate.mp4 (1080x1920 30 fps), build/voice_raw.wav, build/broll/NN.mp4 + build/broll.json"""
import subprocess, sys, os, json
sys.path.insert(0, os.getcwd())  # the reel project holds plan.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plan import *

W, H = 1080, 1920
os.makedirs("build/seg", exist_ok=True)
os.makedirs("build/broll", exist_ok=True)


def dims(path):
    """display size after ffmpeg's autorotate (a phone clip can carry a 90 degree display matrix)"""
    o = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height:stream_side_data=rotation",
                        "-of", "json", path], capture_output=True, text=True).stdout
    st = json.loads(o)["streams"][0]
    w, h = int(st["width"]), int(st["height"])
    rot = next((abs(int(sd.get("rotation", 0))) for sd in st.get("side_data_list", []) if "rotation" in sd), 0)
    return (h, w) if rot in (90, 270) else (w, h)


def crop_expr(src, z, cx, cy, rot=None):
    SW, SH = dims(src)
    if rot in ("cw", "ccw"):
        SW, SH = SH, SW
    if SW / SH > W / H:  # wider than 9:16 (e.g. a 4K landscape clip): centre-crop to 9:16 first
        SW = int(SH * W / H)
    FW, FH = dims(src)
    if rot in ("cw", "ccw"):
        FW, FH = FH, FW
    cw, ch = round(SW / z / 2) * 2, round(SH / z / 2) * 2
    x = min(max(cx * FW - cw / 2, 0), FW - cw)
    y = min(max(cy * FH - ch / 2, 0), FH - ch)
    pre = {"cw": "transpose=1,", "ccw": "transpose=2,"}.get(rot, "")
    return f"{pre}crop={cw}:{ch}:{int(x)}:{int(y)},scale={W}:{H}:flags=lanczos"


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-2000:]); sys.exit(1)


def cut(src, ss, n, vf, out):
    if os.path.exists(out):
        return
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ss:.6f}", "-i", src,
         "-vf", f"fps={FPS},{vf},format=yuv420p", "-frames:v", str(n), "-an",
         "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-color_primaries", "bt709",
         "-color_trc", "bt709", "-colorspace", "bt709", out])


SOURCES = globals().get("SOURCES") or [(0, SRC, globals().get("TX"), VAD)]


def source_of(t):
    """virtual time -> (source file, time inside it): a reel can cut several clips (offset + source seconds)"""
    off, src = max(((o, s_) for o, s_, *_ in SOURCES if o <= t + 1e-6), key=lambda x: x[0])
    return src, t - off


tl, total = timeline()
lst = []
for i, (a, b, es, n, z, pi) in enumerate(tl):
    out = f"build/seg/{a:.3f}_{n}_{z}.mp4"
    lst.append(out)
    cx, cy = (FACE if z > 1 else (0.5, 0.5))
    src, la = source_of(a)
    out = f"build/seg/{os.path.basename(src)}_{la:.3f}_{n}_{z}.mp4"
    lst[-1] = out
    cut(src, la, n, crop_expr(src, z, cx, cy), out)
PRE = round(globals().get("PRE_ROLL", 0) * FPS)
if PRE:                                    # lead-in: the first piece's first frame held, silent (b-roll covers it)
    a0, _b0, _es0, _n0, z0, _p0 = tl[0]
    src, la = source_of(a0)
    cx, cy = (FACE if z0 > 1 else (0.5, 0.5))
    pre = f"build/seg/pre_{PRE}_{os.path.basename(src)}_{la:.3f}.mp4"
    cut(src, la, 1, crop_expr(src, z0, cx, cy), pre + ".1.mp4")
    if not os.path.exists(pre):
        run(["ffmpeg", "-v", "error", "-y", "-i", pre + ".1.mp4", "-vf", f"tpad=stop_mode=clone:stop={PRE - 1},format=yuv420p",
             "-frames:v", str(PRE), "-c:v", "libx264", "-preset", "medium", "-crf", "14", pre])
    lst.insert(0, pre)
with open("build/seg/list.txt", "w") as f:
    for p in lst:
        f.write(f"file '{os.path.basename(p)}'\n")
run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", "build/seg/list.txt", "-c", "copy", "build/plate.mp4"])

parts, fil = [], []
srcs = [s_[1] for s_ in SOURCES]
for i, (a, b, es, n, z, pi) in enumerate(tl):
    d = n / FPS
    src, la = source_of(a)
    k = srcs.index(src)
    fil.append(f"[{k}:a]atrim={la:.6f}:{la + d:.6f},asetpts=PTS-STARTPTS,aresample=48000,afade=t=in:d=0.008,afade=t=out:st={d - 0.008:.4f}:d=0.008[a{i}]")
    parts.append(f"[a{i}]")
if PRE:
    fil.append(f"anullsrc=r=48000:cl=mono,atrim=duration={PRE / FPS:.6f}[pre]")
    parts.insert(0, "[pre]")
fil.append("".join(parts) + f"concat=n={len(parts)}:v=0:a=1,aresample=48000[v]")
ins = sum((["-i", s_] for s_ in srcs), [])
run(["ffmpeg", "-v", "error", "-y"] + ins + ["-filter_complex", ";".join(fil), "-map", "[v]", "-ac", "1", "build/voice_raw.wav"])

brs = []
for k, br_ in enumerate(BROLL):
    o0, o1, src, ss, bz, bx, by = br_[:7]
    rot = br_[7] if len(br_) > 7 else None
    t0, t1 = to_edit(o0), to_edit(o1)
    n = round((t1 - t0) * FPS)
    out = f"build/broll/{k:02d}_{os.path.basename(src)}_{ss}_{n}_{bx}_{rot}.mp4"
    cut(src, ss, n, crop_expr(src, bz, bx, by, rot), out)
    brs.append({"file": out, "t0": round(t0 * FPS) / FPS, "n": n})
json.dump(brs, open("build/broll.json", "w"), indent=1)
print("subcuts", len(tl), "total", total, "frames", round(total / FPS, 2), "s; broll", [(b["t0"], b["n"]) for b in brs])
