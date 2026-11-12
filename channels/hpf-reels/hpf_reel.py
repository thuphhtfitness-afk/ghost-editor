#!/usr/bin/env python3
"""HPF training reels: one spec -> a finished reel (coaching labels, drawn guides, B&W fault replays, punch-ins),
on the core pipeline (build.mjs + HyperFrames). Same spec as founder-reels/make_reel.py; HPF defaults below.

    make_reel.py <spec.json> [--no-render]

The spec names a BASE project that was prepped once per recording (prep.sh -> assets/talk.mp4, transcribe.py ->
build/words.whisper.json, face_track.py or a measured box -> build/face.json) and lists the reel:

  {"name": "2B", "base": "/path/base", "out": "/path/reel_2B.mp4",
   "segments": [[73.7, 76.2], [64.1, 73.7], ...],      # ORIGINAL seconds, in edit order (a hook may come from later)
   "origin": "45% 31%",                                 # zoom origin = the face
   "beats": [...],                                      # reel.json beats; times are snapped to the nearest word
   "phrases": {...}, "keywords": [...],                 # captions.phrases / captions.keywords
   "crack": 13.5,                                       # optional: the word "vỡ" -> glass crack + quiet glass break
   "frame": {"zoom": 1.2, "x": 0.3}}                    # optional: punch the plate (speaker at a frame edge)

Rules it applies (README.md, the client's briefs): every segment is split at pauses > 0.6 s and cut on word times
(a - 0.12, b + 0.25); snaps alternate 1.0 / 1.08 at each cut; captions highlighter, y 1400; cards never carry a
default SFX; voice -14 LUFS; the glass break sits ~8 dB under the voice.
"""
import json, os, subprocess, sys, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.expanduser(os.environ.get("GHOST_EDITOR_SKILL", "~/.claude/skills/ghost-editor"))
os.environ.setdefault("GHOST_TASTE", os.path.join(HERE, "taste.json"))  # this channel's own taste, never ghost-editor's
GAP = 0.6


PROFANITY = {"vãi", "vã", "đéo", "đếch", "địt", "đm", "đmm", "dm", "vl", "vcl", "vkl", "cặc", "lồn", "buồi", "ngu", "đĩ"}
MUSIC = ["lo-fi-02", "a-baby-story", "chillax"]  # light, warm beds under a coaching voice (HPF)


def core(w):
    return w.strip().strip(".,!?;:\"'…").lower()


def normalize_case(words, proper=()):
    """captions: capital only at a sentence start (and proper nouns); whisper capitalises every segment start"""
    prop = {p.lower() for p in proper}
    prev_end = True
    for w in words:
        t = w["word"]; lead = t[:len(t) - len(t.lstrip())]; body = t.strip()
        if body:
            if core(body) in prop: body = body[0].upper() + body[1:]
            elif prev_end: body = body[0].upper() + body[1:]
            elif body.upper() != body or len(body) == 1: body = body[0].lower() + body[1:]
            prev_end = body[-1:] in ".?!"
        w["word"] = lead + body
    return words


def words_of(base):
    r = json.load(open(os.path.join(base, "build", "words.whisper.json")))
    segs = r["segments"] if isinstance(r, dict) else r
    return [w for s in segs for w in s.get("words", [])]


def takes_for(segments, words):
    takes = []
    for a0, b0 in segments:
        ws = [w for w in words if w["start"] >= a0 - 0.1 and w["end"] <= b0 + 0.15]
        if not ws:
            raise SystemExit(f"no words in segment {a0}-{b0}")
        drop = set()
        for i, w in enumerate(ws):  # non-standard words are cut (with the "ra" of "vãi ra")
            if core(w["word"]) in PROFANITY:
                drop.add(i); print(f"  cut non-standard word '{w['word'].strip()}' at {w['start']:.2f}")
                if i + 1 < len(ws) and core(ws[i + 1]["word"]) == "ra" and core(w["word"]) in ("vã", "vãi"): drop.add(i + 1)
        if drop:
            parts, cur = [], []
            for i, w in enumerate(ws):
                if i in drop:
                    if cur: parts.append(cur); cur = []
                else: cur.append(w)
            if cur: parts.append(cur)
        else:
            parts = [ws]
        for ws in parts:
            takes.extend(_runs(ws, words))
    return _unoverlap(takes)


def _runs(ws, words):
    if True:
        idx = {id(w): i for i, w in enumerate(words)}
        def edge(run):  # a - 0.12 / b + 0.25, but never into the neighbouring words that are not in this take
            i0, i1 = idx[id(run[0])], idx[id(run[-1])]
            a = run[0]["start"] - 0.12; b = run[-1]["end"] + 0.25
            if i0 > 0: a = max(a, words[i0 - 1]["end"] + 0.02)
            if i1 + 1 < len(words): b = min(b, words[i1 + 1]["start"] - 0.02)
            return [a, b]
        takes = []
        run = [ws[0]]
        for w in ws[1:]:
            if w["start"] - run[-1]["end"] > GAP:
                takes.append(edge(run)); run = [w]
            else:
                run.append(w)
        takes.append(edge(run))
        return takes


def _unoverlap(takes):
    # neighbours from one stretch of source must not overlap (that would play the same audio twice)
    for i in range(len(takes) - 1):
        if 0 < takes[i][1] - takes[i + 1][0] < 1.0 and takes[i][0] < takes[i + 1][0]:
            m = (takes[i][1] + takes[i + 1][0]) / 2; takes[i][1] = m; takes[i + 1][0] = m
    return [[round(max(0, a), 2), round(b, 2)] for a, b in takes]


def snap(t, words, key="start", within=0.8):
    """starts snap FORWARD to a word that begins at or after t (- 0.15), ends snap BACK to one that ends by t (+ 0.15):
    a card time never slides into the neighbouring take"""
    if key == "start":
        c = [w for w in words if w["start"] >= t - 0.15 and w["start"] - t <= within]
    else:
        c = [w for w in words if w["end"] <= t + 0.15 and t - w["end"] <= within]
    if not c: return t
    best = min(c, key=lambda w: abs(w[key] - t))
    return round(best[key], 2)


def snap_beat(b, words):
    if isinstance(b.get("at"), (int, float)): b["at"] = snap(b["at"], words)
    if isinstance(b.get("to"), (int, float)): b["to"] = snap(b["to"], words, "end")
    for l in b.get("lines", []):
        if isinstance(l, dict) and isinstance(l.get("at"), (int, float)): l["at"] = snap(l["at"], words)
    for c in b.get("cols", []):
        if isinstance(c.get("at"), (int, float)): c["at"] = snap(c["at"], words)
        for l in c.get("lines", []):
            if isinstance(l.get("at"), (int, float)): l["at"] = snap(l["at"], words)
    b.setdefault("sfx", "none")
    for l in b.get("lines", []):
        if isinstance(l, dict): l.setdefault("sfx", "none")
    return b


def clamp_to(b, takes):
    """a snapped `to` can land just past its take's last frame: pull it back inside the take that holds `at`"""
    if isinstance(b.get("at"), (int, float)) and isinstance(b.get("to"), (int, float)):
        for a, e in takes:
            if a <= b["at"] <= e:
                if not any(a2 <= b["to"] <= e2 for a2, e2 in takes):
                    ends = [e2 for a2, e2 in takes if b["at"] <= e2 <= b["to"]]  # the last take end before `to`
                    b["to"] = round((max(ends) if ends else e) - 0.05, 2)
                break
    return b


def chain_broll(beats, takes):
    """client rule: B-roll after B-roll is a straight cut. Two B-roll beats less than 1.5 s apart in the edit are
    joined: the first runs to the end of its take, the next starts at the head of its take, both hard-cut"""
    def take_of(t):
        for i, (a, e) in enumerate(takes):
            if a - 0.01 <= t <= e + 0.01: return i
    def et(t):
        acc = 0.0
        for a, e in takes:
            if a <= t <= e: return acc + t - a
            acc += e - a
    br = sorted([b for b in beats if b["type"] == "broll"], key=lambda b: et(b["at"]) or 0)
    for p, q in zip(br, br[1:]):
        if et(q["at"]) - et(p["to"]) < 1.5:
            ip, iq = take_of(p["to"]), take_of(q["at"])
            if iq == ip + 1:
                p["to"] = round(takes[ip][1] - 0.005, 3); q["at"] = round(takes[iq][0] + 0.005, 3)
            elif iq == ip:
                p["to"] = q["at"]
            p["cutOut"] = True; q["cutIn"] = True


def text_layout(beats):
    """client rule: no text ever sits on other text. Zones: titles top, labels near the middle, notes beside their
    point, captions at the bottom. A note that hits a label moves below it; a label that hits a title moves under the
    title; a label never shows during an anatomy scene (the scene carries its own words)."""
    def box(b):
        if b["type"] == "label":
            sz = b.get("size", 42); x = b.get("x", 70); y = b.get("y", 600)
            return (x, y, x + len(b["text"]) * sz * 0.58 + 90, y + sz * 1.4)
        if b["type"] == "note":
            sz = b.get("size", 64); w = len(b["text"]) * sz * 0.6; tx = b.get("tx", 540); ty = b.get("ty", 760)
            return (tx - w / 2, ty - sz * 1.25, tx + w / 2, ty)
        if b["type"] == "glow":  # an on-body highlight is not text, but words must not hide it
            return (b["cx"] - b["rx"], b["cy"] - b["ry"], b["cx"] + b["rx"], b["cy"] + b["ry"])
        if b["type"] == "title":
            sz = b.get("size", 96); y = b.get("y", 190)
            return (60, y, 1020, y + sz * 1.25)
    def hit(a, b): return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]
    def overlap_t(a, b):
        ta, tb = (a["at"], a["to"]), (b["at"], b["to"])
        return isinstance(ta[1], (int, float)) and isinstance(tb[1], (int, float)) and ta[0] < tb[1] and tb[0] < ta[1]
    anat = [b for b in beats if b["type"] == "anatomy"]
    for l in [b for b in beats if b["type"] == "label"]:
        for a in anat:
            if overlap_t(l, a):
                if l["at"] < a["at"]: l["to"] = round(a["at"] - 0.02, 3)
                else: l["at"] = round(min(a["to"] + 0.02, l["to"] - 0.3), 3)
    for _ in range(3):
        for p in beats:
            for q in beats:
                if p is q or not overlap_t(p, q): continue
                bp, bq = box(p), box(q)
                if not bp or not bq or not hit(bp, bq): continue
                if p["type"] == "note" and q["type"] in ("label", "title"):
                    p["ty"] = round(bq[3] + p.get("size", 64) * 1.25 + 30)
                elif p["type"] == "label" and q["type"] == "title":
                    p["y"] = round(bq[3] + 30)
                elif p["type"] in ("label", "note") and q["type"] == "glow":  # move the words off the highlighted part
                    key = "y" if p["type"] == "label" else "ty"
                    above = bq[1] - (bp[3] - bp[1]) - 30
                    p[key] = round(above if above > 260 else bq[3] + 30 + (bp[3] - bp[1] if p["type"] == "note" else 0))
        for p in beats:
            if p["type"] == "note" and p.get("ty", 760) > 1480: p["ty"] = 1480  # keep clear of the captions
    return beats


def edit_time(t, takes):
    acc = 0.0
    for a, b in takes:
        if a <= t <= b: return acc + (t - a)
        acc += b - a
    raise SystemExit(f"{t} is not in kept material")


def lufs(path, a, b):
    out = subprocess.run(["ffmpeg", "-v", "info", "-ss", str(a), "-to", str(b), "-i", path, "-vn", "-af", "ebur128=framelog=quiet",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    vals = [l.split()[1] for l in out.splitlines() if l.strip().startswith("I:")]
    return float(vals[-1]) if vals else -70.0


def boosted_plate(src, base, ranges, target=-16.0):
    """the user's rule: a voice that the mic barely caught (the client asking off-mic) is lifted to the listener's level.
    ranges: [[a, b]] (auto gain to `target` LUFS, max +20 dB) or [[a, b, dB]]; source seconds. Video is copied."""
    parts = []
    for r in ranges:
        a, b = r[0], r[1]
        g = r[2] if len(r) > 2 else max(0.0, min(20.0, target - lufs(src, a, b)))
        parts.append((a, b, round(g, 1))); print(f"  boost {a:.2f}-{b:.2f}: +{g:.1f} dB")
    tag = "_".join(f"{a:g}-{b:g}-{g:g}" for a, b, g in parts)
    import hashlib
    dst = os.path.join(base, "assets", f"talk.boost.{hashlib.md5(tag.encode()).hexdigest()[:8]}.mp4")
    if not os.path.exists(dst):
        # 80 ms ramps at each edge so the lift never clicks; a limiter keeps the lifted noise from peaking
        expr = "+".join(f"(pow(10,{g}/20)-1)*clip(min((t-{a})/0.08,({b}-t)/0.08),0,1)" for a, b, g in parts)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-c:v", "copy",
                        "-af", f"volume='1+{expr}':eval=frame,alimiter=limit=0.89:level=false",
                        "-c:a", "aac", "-b:a", "256k", dst + ".part.mp4"], check=True)
        os.replace(dst + ".part.mp4", dst)
    return dst


def main():
    spec = json.load(open(sys.argv[1]))
    base, name = spec["base"], spec["name"]
    P = os.path.join(os.path.dirname(os.path.abspath(sys.argv[1])), f"reel-{name}")
    os.makedirs(os.path.join(P, "assets"), exist_ok=True); os.makedirs(os.path.join(P, "build"), exist_ok=True)
    src = os.path.join(base, "assets", "talk.mp4")
    pv = spec.get("privacy")
    if pv:  # client rule: never show eyes, nose or mouth. Crop the RAW recording below the mouth line (base coords)
        raw = spec["raw"]
        rw, rh = map(int, subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                                           "-of", "csv=p=0", raw], capture_output=True, text=True).stdout.strip().split(",")[:2])
        k = rw / 1080; top = pv["top"]; ch = int((1920 - top) * k) // 2 * 2; cw = int(ch * 9 / 16) // 2 * 2
        cx = int(min(max(pv.get("cx", 540) * k - cw / 2, 0), rw - cw)); cy = int(top * k)
        names = spec.get("names", [])
        tag = f"top{top}cx{pv.get('cx', 540)}n{len(names)}"
        dst = os.path.join(base, "assets", f"talk.private.{tag}.mp4")
        if not os.path.exists(dst):
            # names are beeped in the plate: mute the word, a 1 kHz tone under it (captions show ***)
            bw = [w for w in words_of(base) if names and core(w["word"]) in {n.lower() for n in names}]
            af = "anull"
            if bw:
                mute = "+".join(f"between(t,{w['start'] - 0.03:.2f},{w['end'] + 0.05:.2f})" for w in bw)
                af = f"volume=0:enable='{mute}'"
            beep = "+".join(f"between(t,{w['start'] - 0.03:.2f},{w['end'] + 0.05:.2f})" for w in bw) or "0"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-i", os.path.join(base, "assets", "talk.mp4"),
                            "-f", "lavfi", "-i", "sine=frequency=1000:sample_rate=48000",
                            "-filter_complex", f"[0:v]crop={cw}:{ch}:{cx}:{cy},scale=1080:1920:flags=lanczos,fps=30,format=yuv420p[v];"
                                               f"[1:a]{af}[va];[2:a]volume=0.18,volume=0:enable='not({beep})'[bp];[va][bp]amix=inputs=2:normalize=0:duration=first[a]",
                            "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-threads", "4", "-preset", "medium", "-crf", "14", "-g", "30",
                            "-c:a", "aac", "-b:a", "256k", "-shortest", dst + ".part.mp4"], check=True)
            os.replace(dst + ".part.mp4", dst)  # atomic: an interrupted run never leaves a broken plate behind
        src = dst
    elif spec.get("frame"):  # punch the plate once: speaker at a frame edge, cups in the foreground
        fr = spec["frame"]; z = fr.get("zoom", 1.2); w, h = int(1080 / z) // 2 * 2, int(1920 / z) // 2 * 2
        x, y = int((1080 - w) * fr.get("x", 0.5)), int((1920 - h) * fr.get("y", 0.35))
        dst = os.path.join(base, "assets", f"talk.z{z}x{fr.get('x', 0.5)}y{fr.get('y', 0.35)}.mp4")
        if not os.path.exists(dst):
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vf", f"crop={w}:{h}:{x}:{y},scale=1080:1920:flags=lanczos",
                            "-c:v", "libx264", "-threads", "4", "-preset", "medium", "-crf", "16", "-g", "30", "-c:a", "copy", dst], check=True)
        src = dst
    if spec.get("boost"):  # quiet off-mic voice (the client asking): lift each [a, b] range to the coach's level
        src = boosted_plate(src, base, spec["boost"])
    dp = os.path.join(P, "assets", "talk.mp4")
    if os.path.lexists(dp): os.remove(dp)
    os.symlink(os.path.abspath(src), dp)
    # this reel's own words file: sentence-case captions, names as ***
    wj = json.load(open(os.path.join(base, "build", "words.whisper.json")))
    segs = wj["segments"] if isinstance(wj, dict) else wj
    flat = [w for sg in segs for w in sg.get("words", [])]
    normalize_case(flat, spec.get("proper", []))
    for w in flat:
        if core(w["word"]) in {n.lower() for n in spec.get("names", [])}: w["word"] = w["word"].replace(w["word"].strip(), "***")
    json.dump(wj, open(os.path.join(P, "build", "words.whisper.json"), "w"), ensure_ascii=False)
    fj = os.path.join(P, "build", "face.json")
    if pv:  # the plate shows no face: only the chin at the top edge
        d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src], capture_output=True, text=True).stdout)
        json.dump({"fps": 5, "w": 1080, "h": 1920, "samples": [[round(i * 0.2, 2), 0, 160, 240, 840, 40, 120] for i in range(int(d / 0.2) + 1)]}, open(fj, "w"))
    else:
        if os.path.lexists(fj): os.remove(fj)
        os.symlink(os.path.join(base, "build", "face.json"), fj)
    for dst, src_ in spec.get("assets", {}).items():  # B-roll the client sent: {"broll/mats.mp4": "/abs/path.mp4"}
        dp = os.path.join(P, "assets", dst); os.makedirs(os.path.dirname(dp), exist_ok=True); shutil.copy2(src_, dp)
    words = words_of(base)
    takes = takes_for(spec["segments"], words)
    # snap card times only to words the reel keeps: a word just outside a take would fail the build
    kept = [w for w in words if any(a <= w["start"] and w["end"] <= b for a, b in takes)]
    snaps = [[a, 1.08 if i % 2 else 1.0] for i, (a, b) in enumerate(takes) if i]
    reel = {
        "title": spec.get("title", name), "source": "assets/talk.mp4", "words": "build/words.whisper.json", "fps": 30,
        "outro": 0.5, "platform": "all", "style": "clean", "sfxProfile": "restrained",
        "takes": [{"a": a, "b": b} for a, b in takes],
        "captions": {"style": "mini", "group": spec.get("captionGroup", 2), "size": 48, "weight": 700, "stroke": 3, "y": spec.get("captionY", 1560), "splitY": 985, "phrases": spec.get("phrases", {}),
                     "fixes": spec.get("fixes", {}), **({"keywords": spec["keywords"]} if spec.get("keywords") else {})},
        "zoom": {"origin": spec.get("origin", "45% 31%"), "snaps": snaps,
                 "pushes": [{"at": takes[0][0] + 0.05, "z": 1.06, "up": max(1.0, takes[0][1] - takes[0][0] - 0.4), "until": takes[0][1] - 0.1, "down": 0.1}]},
        "beats": [clamp_to(snap_beat(b, kept), takes) for b in spec.get("beats", [])], "sfx": [],
        "music": {"id": spec.get("music", MUSIC[sum(map(ord, name)) % len(MUSIC)]), "db": spec.get("musicDb", -18)},
    }
    if spec.get("origin") is None and pv: reel["zoom"]["origin"] = "50% 40%"
    chain_broll(reel["beats"], takes)
    text_layout(reel["beats"])
    reel["beats"].sort(key=lambda b: b["type"] != "broll")  # B-roll at the bottom: labels, guides and cards draw over it
    total = sum(b - a for a, b in takes)
    if total < 30: print(f"WARNING: {total:.1f} s of speech: under the 30 s minimum, merge it with another story line")
    json.dump(reel, open(os.path.join(P, "reel.json"), "w"), ensure_ascii=False, indent=1)
    post_only = "--post-only" in sys.argv  # re-export from the existing render (new export settings), no rebuild
    out = subprocess.run(["true"] if post_only else ["node", os.path.join(SKILL, "scripts", "build.mjs"), P], capture_output=True, text=True)
    print("\n".join(l for l in out.stdout.splitlines() if "WARN" in l or "speech" in l or l.startswith("  ") and "s " in l[:12]))
    if out.returncode: print(out.stdout[-2000:], out.stderr[-2000:]); raise SystemExit("build failed")
    warns = out.stdout.split("WARNINGS:")[1] if "WARNINGS:" in out.stdout else ""
    if warns.strip(): print("WARNINGS:", warns.strip()[:1500])
    if "--no-render" in sys.argv: return
    r = subprocess.run(["true"] if post_only else ["bash", os.path.join(SKILL, "scripts", "hf.sh"), "render", "-o", "build/reel.mp4"], cwd=P, capture_output=True, text=True)
    if r.returncode: print(r.stdout[-1500:]); raise SystemExit("render failed")
    # post: glass crack on "vỡ", and the hook -> main cut gets a white flash + a click (client rule, Refined Ambition)
    inputs, vchain, achain, n = ["-i", "build/reel.mp4"], "[0:v]", "[0:a]", 1
    vf, af, extra_a = [], [], []
    if spec.get("crack") is not None:
        crack_dir = os.path.join(P, "build", "crack")
        if not os.path.isdir(crack_dir):
            os.makedirs(crack_dir); subprocess.run([sys.executable, os.path.join(HERE, "crack_fx.py"), crack_dir], check=True)
        t = edit_time(snap(spec["crack"], kept), takes) - 0.03
        inputs += ["-framerate", "30", "-itsoffset", f"{t:.3f}", "-i", os.path.join(crack_dir, "c%03d.png")]
        vf.append((n, "overlay=0:0:eof_action=pass")); n += 1
        inputs += ["-i", os.path.join(SKILL, "library", "sfx", "cc0-glass-break.wav")]
        extra_a.append((n, int((t - 0.02) * 1000), 0.22)); n += 1
    if spec.get("hookCut", True) and len(spec["segments"]) > 1:
        n_hook = len(takes_for([spec["segments"][0]], words))
        th = sum(b - a for a, b in takes[:n_hook])
        inputs += ["-f", "lavfi", "-i", "color=white:s=1080x1920:r=30:d=0.32,format=rgba,fade=t=in:st=0:d=0.06:alpha=1,fade=t=out:st=0.08:d=0.24:alpha=1"]
        vf.append((n, f"overlay=0:0:eof_action=pass:enable='between(t,{th - 0.06:.3f},{th + 0.3:.3f})'", th - 0.06)); n += 1
        click = os.path.join(SKILL, "library", "sfx", "click-1.wav")
        if os.path.exists(click):
            inputs += ["-i", click]; extra_a.append((n, int(max(0, th - 0.04) * 1000), 0.5)); n += 1
        print(f"  hook cut at {th:.2f} s: flash + click")
    g, cur = [], "[0:v]"
    for k, item in enumerate(vf):
        idx, ov = item[0], item[1]
        src_v = f"[{idx}:v]" if len(item) == 2 else f"[{idx}:v]setpts=PTS+{item[2]:.3f}/TB[f{k}];"
        if len(item) == 2: g.append(f"{cur}{src_v}{ov}[v{k}]")
        else: g.append(f"{src_v}{cur}[f{k}]{ov}[v{k}]")
        cur = f"[v{k}]"
    g.append(f"{cur}format=yuv420p[v]")
    mix = ["[0:a]"]
    for k, (idx, d, vol) in enumerate(extra_a):
        g.append(f"[{idx}:a]volume={vol},adelay={d}|{d},apad[s{k}]"); mix.append(f"[s{k}]")
    g.append(f"{''.join(mix)}amix=inputs={len(mix)}:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11[a]" if len(mix) > 1 else "[0:a]loudnorm=I=-14:TP=-1.5:LRA=11[a]")
    fc = ";".join(g); vin, extra = inputs, []
    subprocess.run(["ffmpeg", "-v", "error", "-y", *vin, *extra, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-threads", "4", "-preset", "medium", "-crf", "15", "-maxrate", "20M", "-bufsize", "40M",
                    "-profile:v", "high", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-c:a", "aac", "-b:a", "256k",
                    "-ar", "48000", spec["out"]], cwd=P, check=True)
    dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", spec["out"]], capture_output=True, text=True).stdout.strip()
    print(f"-> {spec['out']} ({float(dur):.1f} s)")


if __name__ == "__main__":
    main()
