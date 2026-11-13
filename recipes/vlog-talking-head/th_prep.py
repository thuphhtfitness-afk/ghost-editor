#!/usr/bin/env python3
"""talking-head prep: segments -> pauses removed -> pieces; caption words (edit s); zoomed face-following plate;
a firm, warm voice; B-roll clips.  th_prep.py reel.json [--skip-plate]

reel.json: project, src, clean (DF ~20 dB wav), nr_ref (full-strength DF wav, only for pause detection), whisper,
           track (face track json), segs [[a, b, text]], broll_src, broll [[name, src_start, dur]]"""
import difflib, json, os, re, subprocess, sys, unicodedata

R = json.load(open(sys.argv[1], encoding="utf-8"))
P = R["project"]
os.makedirs(f"{P}/assets/broll", exist_ok=True)
os.makedirs(f"{P}/build/segs", exist_ok=True)
SKIP_PLATE = "--skip-plate" in sys.argv
KEEP = R.get("keep_pause", 0.12)          # air left on each side of a removed pause
MINP = R.get("min_pause", 0.32)           # pauses longer than this are cut


def sh(*a):
    subprocess.run(a, check=True)


# ---- 1. pauses from the full-strength denoised voice (its floor is silent, so silence = no speech)
def silences(a, b):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", R["nr_ref"],
                          "-af", f"silencedetect=noise={R.get('sil_db', -38)}dB:d={MINP}", "-f", "null", "-"], capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
    return [(a + s, a + e) for s, e in zip(st, en)]


pieces = []                                # [src a, src b, seg index]
SILENT = {si for si, sg in enumerate(R["segs"]) if len(sg) > 3 and sg[3].get("silent")}
for si, sg in enumerate(R["segs"]):
    a, b = sg[0], sg[1]
    if si in SILENT:                       # a montage gap: the plate runs (under B-roll), no voice, no pause cut
        pieces.append([round(a, 3), round(b, 3), si])
        continue
    cur = a
    for s, e in silences(a, b):
        if s - a < 0.05 or b - e < 0.05:   # edge silences: trim the segment
            if s - a < 0.05:
                cur = max(cur, e - KEEP)
            else:
                b = min(b, s + KEEP)
            continue
        if s + KEEP > cur:
            pieces.append([round(cur, 3), round(s + KEEP, 3), si])
        cur = e - KEEP
    if b - cur > 0.06:
        pieces.append([round(cur, 3), round(b, 3), si])
edit, plan = 0.0, []
for a, b, si in pieces:
    plan.append({"src": [a, b], "edit": [round(edit, 3), round(edit + b - a, 3)], "seg": si})
    edit += b - a
DUR = round(edit, 3)
src_total = sum(sg[1] - sg[0] for sg in R["segs"])
print(f"{len(R['segs'])} segments {src_total:.2f} s -> {len(pieces)} pieces {DUR:.2f} s (cut {src_total - DUR:.2f} s of pauses)")


def to_edit(x, si):
    """source seconds of segment si -> edit seconds; a time inside a removed pause snaps to the next piece"""
    for p in [q for q in plan if q["seg"] == si]:
        a, b = p["src"]
        if x < a:
            return p["edit"][0]
        if x <= b:
            return p["edit"][0] + x - a
    return [q for q in plan if q["seg"] == si][-1]["edit"][1]


# ---- 2. caption words: corrected syllables aligned to whisper onsets per segment, then mapped to edit time
norm = lambda s: unicodedata.normalize("NFC", re.sub(r"[^\w]", "", s.lower()))
WH = [(w["word"].strip(), w["start"], w["end"]) for s in json.load(open(R["whisper"], encoding="utf-8"))["segments"] for w in s["words"]]
words = []
for si, sg in enumerate(R["segs"]):
    a, b, text = sg[0], sg[1], sg[2]
    if not text.strip():
        continue
    ws = [w for w in WH if a - 0.05 <= w[1] < b]
    toks = text.split()
    syl = [(ti, s) for ti, tk in enumerate(toks) for s in tk.split("_")]
    sm = difflib.SequenceMatcher(None, [norm(s) for _, s in syl], [norm(w[0]) for w in ws], autojunk=False)
    t_of = [None] * len(syl)
    for blk in sm.get_matching_blocks():
        for k in range(blk.size):
            t_of[blk.a + k] = ws[blk.b + k][1]
    anchors = [(-1, a + 0.05)] + [(k, x) for k, x in enumerate(t_of) if x is not None] + [(len(syl), b - 0.25)]
    for (k0, t0), (k1, t1) in zip(anchors, anchors[1:]):
        for k in range(k0 + 1, k1):
            t_of[k] = t0 + (t1 - t0) * (k - k0) / (k1 - k0)
    last = a
    for k in range(len(syl)):
        t_of[k] = min(max(t_of[k], last), b - 0.08)
        last = t_of[k] + 0.04
    for ti, tk in enumerate(toks):
        ks = [k for k, (tj, _) in enumerate(syl) if tj == ti]
        words.append({"word": tk.replace("_", " "), "start": round(to_edit(t_of[ks[0]], si), 3),
                      "end": round(to_edit(t_of[ks[-1]] + 0.2, si), 3)})
for x, y in zip(words, words[1:]):
    y["start"] = max(y["start"], x["start"] + 0.03)
    x["end"] = min(max(x["end"], x["start"] + 0.05), y["start"])
json.dump({"words": words}, open(f"{P}/build/words.cut.json", "w"), ensure_ascii=False, indent=0)
json.dump({"dur": DUR, "segs": plan}, open(f"{P}/build/cut.json", "w"), indent=1)
for k in range(0, len(words), 12):
    print(" ".join(f"{i}:{w['word']}@{w['start']:.2f}" for i, w in list(enumerate(words))[k:k + 12]))

# ---- 3. voice: a light denoise (~20 dB, the room stays faintly), then body + presence + firm compression
ins = []
for i, p in enumerate(plan):
    a, b = p["src"]
    w = f"{P}/build/segs/a{i}.wav"
    fd = min(0.012, (b - a) / 4)
    if p["seg"] in SILENT:
        sh("ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t", f"{b - a:.3f}", w)
    else:
        sh("ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", R["clean"],
           "-af", f"afade=t=in:d={fd},afade=t=out:st={b - a - fd:.3f}:d={fd}", "-ar", "48000", "-ac", "1", w)
    ins += ["-i", w]
CHAIN = ("highpass=f=70,lowpass=f=11500,afftdn=nr=6:nf=-42:tn=1,"
         "agate=threshold=0.012:ratio=2:range=0.35:attack=6:release=250,"
         "equalizer=f=120:t=q:w=0.9:g=4,equalizer=f=250:t=q:w=1.0:g=1.5,equalizer=f=500:t=q:w=1.4:g=-2.5,"
         "equalizer=f=2200:t=q:w=1.0:g=2,equalizer=f=6500:t=q:w=1.6:g=-3.5,"
         "acompressor=threshold=-30dB:ratio=4:attack=5:release=120:knee=4:makeup=6,"
         "alimiter=limit=0.89:attack=3:release=50:level=disabled,loudnorm=I=-15:TP=-1.5:LRA=6")
sh("ffmpeg", "-v", "error", "-y", *ins, "-filter_complex",
   "".join(f"[{i}:a]" for i in range(len(plan))) + f"concat=n={len(plan)}:v=0:a=1,{CHAIN}[o]",
   "-map", "[o]", "-ar", "48000", "-ac", "2", f"{P}/assets/voice.wav")

# ---- 4. plate + B-roll
if not SKIP_PLATE:
    sh("python3", os.path.join(os.path.dirname(__file__), "plate_zoom.py"), R["src"], R["track"], f"{P}/build/cut.json",
       f"{P}/assets/talk.mp4", str(R.get("zoom_w", 450)), str(R.get("face_y", 0.40)))
for name, s, d in R.get("broll", []):
    sh("ffmpeg", "-v", "error", "-y", "-ss", f"{s}", "-t", f"{d}", "-i", R["broll_src"], "-an",
       "-vf", "scale=1080:1920:flags=lanczos,fps=30,setsar=1", "-c:v", "libx264", "-preset", "medium", "-crf", "15",
       "-pix_fmt", "yuv420p", "-g", "30", f"{P}/assets/broll/{name}.mp4")
print(f"duration {DUR:.2f} s")
