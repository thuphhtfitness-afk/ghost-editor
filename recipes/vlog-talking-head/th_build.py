"""talking head in the reference's vlog style: big lowercase titles + a 1-2-3 list, small two-line notes, hand-drawn
white arrows, keyword-highlighted captions near the middle, the user's B-roll on chosen lines; jump cuts alternate two
zoom levels; no SFX, a quiet bed.  build(P, cfg) -> index.html

cfg: title (page title), titles [(from word | 0, hold s | to word "w123", [lines], sub)], broll [(clip, from w, to w)],
     notes [(from w, to w, [l1, l2], (x, y))], arrows [(from w, to w, body path, head path)], key {word indices},
     punch [(from w, to w | None, scale)], bed_vol"""
import json, os, shutil
from PIL import ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(os.path.dirname(HERE))
GSAP = os.environ.get("GSAP_JS", "")      # a local gsap.min.js (npm pack gsap@3.14.2) when the CDN is blocked
FPS = 30
fr = lambda x: round(round(x * FPS) / FPS, 4)
esc = lambda s: s.replace("&", "&amp;").replace("<", "&lt;")
F800 = ImageFont.truetype(f"{HERE}/fonts/inter-tight.woff2", 100)
F800.set_variation_by_axes([800])


STROKE = (".cin, .note { -webkit-text-stroke: 9px rgba(0,0,0,.55); paint-order: stroke fill; } "
          ".ts { -webkit-text-stroke: 6px rgba(0,0,0,.5); paint-order: stroke fill; }")


def fit(text, maxw=960, size=104, track=-0.045):
    w = F800.getlength(text) * size / 100 + track * size * (len(text) - 1)
    return min(size, size * maxw / w)


def build(P, cfg):
    W = json.load(open(f"{P}/build/words.cut.json", encoding="utf-8"))["words"]
    cut = json.load(open(f"{P}/build/cut.json"))
    VOICE_DUR = cut["dur"]
    DUR = round(VOICE_DUR + 0.6, 2)
    t = lambda i: W[i]["start"] if isinstance(i, int) else (DUR if i == "end" else float(i))
    os.makedirs(f"{P}/assets/fonts", exist_ok=True)
    os.makedirs(f"{P}/assets/js", exist_ok=True)
    for f in ("inter-tight", "inter-tight-italic"):
        shutil.copy(f"{HERE}/fonts/{f}.woff2", f"{P}/assets/fonts/{f}.woff2")
    if GSAP:
        shutil.copy(GSAP, f"{P}/assets/js/gsap.min.js")
    # bed_up [(from, to, gain)]: the bed rises (e.g. x6 over a wordless montage), 0.4 s ramps
    BEDUP = f",volume={cfg.get('bed_base', 1)}" + "".join(f",volume='1+({g}-1)*clip(min((t-{t(a)})/0.4\\,({t(b)}-t)/0.4)\\,0\\,1)':eval=frame"
                    for a, b, g in cfg.get("bed_up", []))
    os.system(f'ffmpeg -v error -y -i {SKILL}/library/music/{cfg.get("bed", "lo-fi-02")}.mp3 -t {DUR} '
              f'-af "afade=t=in:d=0.6,afade=t=out:st={DUR - 1.5}:d=1.5{BEDUP}" -ar 48000 -ac 2 {P}/assets/bed.wav')
    H, JS = [], []
    tset = lambda sel, props, at: JS.append(f'tl.set("{sel}", {json.dumps(props)}, {fr(at)});')
    tween = lambda sel, a, b, at: JS.append(f'tl.fromTo("{sel}", {json.dumps(a)}, {json.dumps({**b, "immediateRender": False})}, {fr(at)});')

    # B-roll
    vids = []
    for k, (b, i, j) in enumerate(cfg.get("broll", [])):
        a, e = t(i), t(j)
        vids.append(f'<video id="{b}" class="full" src="assets/broll/{b}.mp4" data-start="{fr(a)}" data-duration="{fr(e) - fr(a):.4f}" '
                    f'data-track-index="{10 + k}" muted playsinline style="z-index:3;object-fit:cover"></video>')

    # plate: every jump cut alternates two zoom levels (hides the jump), punch-ins on payoff words
    JS.append("gsap.set('#cam', {transformOrigin: '540px 760px'});")
    for k, p in enumerate(cut["segs"]):
        tset("#cam", {"scale": 1.0 if k % 2 == 0 else 1.07}, p["edit"][0])
    for i, j, s in cfg.get("punch", []):
        tset("#cam", {"scale": s}, t(i))
        if j is not None:
            nxt = [p for p in cut["segs"] if p["edit"][0] <= t(j) < p["edit"][1]]
            k = cut["segs"].index(nxt[0]) if nxt else 0
            tset("#cam", {"scale": 1.0 if k % 2 == 0 else 1.07}, t(j))

    # titles
    starts = sorted(t(x[0]) for x in cfg.get("titles", []))
    for k, (a, e, lines, sub) in enumerate(cfg.get("titles", [])):
        a = t(a)
        e = a + e if isinstance(e, (int, float)) else (DUR if e == "wend" else t(int(e[1:])))
        nxt = [x for x in starts if x > a + 1e-3]
        if nxt:                                   # a title never overlaps the next one
            e = min(e, nxt[0] - 0.05)
        size = min(fit(l) for l in lines)
        body = "".join(f'<div class="tl" style="font-size:{size:.0f}px">{esc(l)}</div>' for l in lines)
        H.append(f'<div id="ti{k}" class="title"><div class="tin">{body}<div class="ts">{esc(sub)}</div></div></div>')
        tset(f"#ti{k}", {"opacity": 1}, a)
        tween(f"#ti{k} .tl", {"y": 40, "opacity": 0}, {"y": 0, "opacity": 1, "ease": "power3.out", "duration": 0.45, "stagger": 0.08}, a)
        tween(f"#ti{k} .ts", {"x": 30, "opacity": 0}, {"x": 0, "opacity": 1, "ease": "power2.out", "duration": 0.4}, a + 0.25)
        tween(f"#ti{k}", {"opacity": 1}, {"opacity": 0, "ease": "power1.in", "duration": 0.3}, e - 0.3)

    # notes
    for k, (i, j, lines, (x, y)) in enumerate(cfg.get("notes", [])):
        H.append(f'<div id="no{k}" class="note" style="left:{x}px;top:{y}px">' + "<br>".join(esc(l) for l in lines) + "</div>")
        tset(f"#no{k}", {"opacity": 1}, t(i) + 0.2)
        tween(f"#no{k}", {"y": 16, "opacity": 0}, {"y": 0, "opacity": 1, "ease": "power2.out", "duration": 0.3}, t(i) + 0.2)
        tset(f"#no{k}", {"opacity": 0}, t(j))

    # arrows
    svg = ['<svg id="arrows" class="full" viewBox="0 0 1080 1920" style="z-index:6">']
    for k, (i, j, body, head) in enumerate(cfg.get("arrows", [])):
        svg.append(f'<g id="ar{k}" opacity="0"><path id="ar{k}b" d="{body}" class="ar" pathLength="1"/>'
                   f'<path id="ar{k}h" d="{head}" class="ar" pathLength="1"/></g>')
        tset(f"#ar{k}", {"opacity": 1}, t(i) + 0.12)
        tween(f"#ar{k}b", {"strokeDashoffset": 1}, {"strokeDashoffset": 0, "ease": "power2.inOut", "duration": 0.42}, t(i) + 0.12)
        tween(f"#ar{k}h", {"strokeDashoffset": 1}, {"strokeDashoffset": 0, "ease": "power2.out", "duration": 0.16}, t(i) + 0.52)
        tset(f"#ar{k}", {"opacity": 0}, t(j))
    svg.append("</svg>")

    # hook: the hook line as big stacked type over a darkened face, line by line on the spoken words, then a white flash
    HK = cfg.get("hook")
    n_hook = 0
    if HK:
        n_hook = HK["n"]
        hook_end = next(p["edit"][0] for p in cut["segs"] if p["seg"] >= HK.get("segs", 1))
        H.append('<div id="hkdim" class="full" style="background:linear-gradient(180deg,rgba(0,0,0,.62) 0%,rgba(0,0,0,.35) 55%,rgba(0,0,0,0) 80%);opacity:0"></div>')
        rows = []
        starts = []
        for k, ln in enumerate(HK["lines"]):
            if isinstance(ln, dict):          # a short summary line of the hook, shown when token `at` is spoken
                plain = ln["text"]
                txt = esc(plain)
                for kw in ln.get("key", []):
                    txt = txt.replace(esc(kw), f'<span class="hkw">{esc(kw)}</span>')
                starts.append(ln["at"])
            else:
                i, j = ln
                plain = " ".join(W[q]["word"] for q in range(i, j))
                txt = " ".join(f'<span class="{"hkw" if q in HK.get("key", set()) else ""}">{esc(W[q]["word"].rstrip(",.:"))}</span>' for q in range(i, j))
                starts.append(i)
            size = fit(plain, 980, 116)
            rows.append(f'<div id="hl{k}" class="hl" style="font-size:{size:.0f}px">{txt}</div>')
        si, sj = HK.get("sub") or (None, None)
        if si is not None:
            rows.append(f'<div id="hls" class="hls">{esc(" ".join(W[q]["word"] for q in range(si, sj)))}</div>')
        H.append(f'<div id="hook" class="hook">{"".join(rows)}</div>')
        tset("#hkdim", {"opacity": 1}, 0.0)
        tset("#hook", {"opacity": 1}, 0.0)
        for k, i in enumerate(starts):
            tween(f"#hl{k}", {"y": 60, "opacity": 0, "scale": 1.08}, {"y": 0, "opacity": 1, "scale": 1, "ease": "power3.out", "duration": 0.32}, max(0.0, t(i) - 0.04))
        if si is not None:
            tween("#hls", {"y": 20, "opacity": 0}, {"y": 0, "opacity": 1, "ease": "power2.out", "duration": 0.25}, t(si))
        tset("#hook", {"opacity": 0}, hook_end)
        tset("#hkdim", {"opacity": 0}, hook_end)
        # flash into the main video + a small punch on the plate
        H.append('<div id="flash" class="full" style="background:#fff;opacity:0;z-index:9"></div>')
        tween("#flash", {"opacity": 0}, {"opacity": 0.95, "ease": "power2.in", "duration": 0.1}, hook_end - 0.1)
        tween("#flash", {"opacity": 0.95}, {"opacity": 0, "ease": "power2.out", "duration": 0.35}, hook_end)
        tween("#cam", {"scale": 1.12}, {"scale": 1.0, "ease": "power3.out", "duration": 0.5}, hook_end)

    # captions
    KEY = cfg.get("key", set())
    chunks, cur = [], []
    for i, w in enumerate(W):
        if i < n_hook or i in cfg.get("nocap", ()):
            continue
        if cur and (len(" ".join(W[k]["word"] for k in cur + [i])) > 24 or w["start"] - W[cur[-1]]["end"] > 0.5):
            chunks.append(cur); cur = []
        cur.append(i)
        if w["word"][-1] in ",.!?:":
            chunks.append(cur); cur = []
    if cur:
        chunks.append(cur)
    for k, c in enumerate(chunks):
        a = t(c[0])
        e = min(t(chunks[k + 1][0]) if k + 1 < len(chunks) else DUR, W[c[-1]]["end"] + 1.0)
        ws = " ".join(f'<span class="{"kw" if i in KEY else "w"}">{esc(W[i]["word"].rstrip(",.:"))}</span>' for i in c)
        H.append(f'<div id="cp{k}" class="cap"><div class="cin">{ws}</div></div>')
        tset(f"#cp{k}", {"opacity": 1}, a)
        tween(f"#cp{k} .cin", {"scale": 0.92, "y": 10}, {"scale": 1, "y": 0, "ease": "back.out(2)", "duration": 0.18}, a)
        tset(f"#cp{k}", {"opacity": 0}, e)

    html = f"""<!doctype html>
<html lang="vi">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<title>{esc(cfg["title"])}</title>
<script src="{"assets/js/gsap.min.js" if GSAP else "https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"}"></script>
<style>
@font-face {{ font-family: 'Inter Tight'; src: url('assets/fonts/inter-tight.woff2') format('woff2'); font-weight: 100 900; font-style: normal; }}
@font-face {{ font-family: 'Inter Tight'; src: url('assets/fonts/inter-tight-italic.woff2') format('woff2'); font-weight: 100 900; font-style: italic; }}
html, body {{ margin: 0; background: #000; }}
#root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; background: #000; font-family: 'Inter Tight', sans-serif; }}
.full {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; }}
video.full {{ object-fit: cover; }}
#ov {{ z-index: 5; pointer-events: none; }}
.title {{ position: absolute; left: 0; top: {cfg.get("title_y", 150)}px; width: 1080px; opacity: 0; display: flex; justify-content: center; }}
.tin {{ display: inline-flex; flex-direction: column; align-items: flex-start; }}
.tl {{ color: #fff; font-weight: 800; letter-spacing: -0.045em; line-height: 0.98;
       text-shadow: 0 2px 18px rgba(0,0,0,.35); white-space: nowrap; }}
.ts {{ align-self: flex-end; color: #fff; font-style: italic; font-weight: 400; font-size: 44px; letter-spacing: -0.02em;
       margin-top: 6px; text-shadow: 0 1px 10px rgba(0,0,0,.6); }}
.note {{ position: absolute; white-space: nowrap; opacity: 0; color: #fff; font-weight: 500; font-size: 46px; line-height: 1.12;
        letter-spacing: -0.01em; text-shadow: 0 1px 2px rgba(0,0,0,.9), 0 0 14px rgba(0,0,0,.55); }}
.ar {{ fill: none; stroke: #fff; stroke-width: 9; stroke-linecap: round; stroke-linejoin: round; stroke-dasharray: 1; stroke-dashoffset: 1;
      filter: drop-shadow(0 1px 3px rgba(0,0,0,.6)); }}
.cap {{ position: absolute; left: 70px; width: 940px; top: {cfg.get("cap_y", 1180)}px; opacity: 0; text-align: center; }}
.cin {{ display: inline-block; font-weight: 700; font-size: 66px; line-height: 1.15; letter-spacing: -0.015em; color: #fff;
       text-shadow: 0 2px 2px rgba(0,0,0,.85), 0 0 16px rgba(0,0,0,.6); }}
.kw {{ color: #FFE14A; font-weight: 800; }}
{STROKE if cfg.get("cap_stroke") else ""}
.hook {{ position: absolute; left: 0; top: 230px; width: 1080px; opacity: 0; text-align: center; z-index: 6; }}
.hl {{ color: #fff; font-weight: 800; letter-spacing: -0.045em; line-height: 1.0; white-space: nowrap;
      text-shadow: 0 3px 22px rgba(0,0,0,.45); opacity: 0; }}
.hkw {{ color: #FFE14A; }}
.hls {{ color: #fff; font-style: italic; font-weight: 400; font-size: 52px; margin-top: 14px; opacity: 0;
       text-shadow: 0 1px 10px rgba(0,0,0,.6); }}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-width="1080" data-height="1920" data-duration="{DUR:.2f}" data-fps="{FPS}">
<div id="cam" class="full" style="z-index:1">
<video id="plate" class="full" src="assets/talk.mp4" data-start="0" data-duration="{DUR:.2f}" data-track-index="0" muted playsinline></video>
</div>
{chr(10).join(vids)}
<div id="ov" class="full">
{chr(10).join(H)}
</div>
{chr(10).join(svg)}
<audio id="vo" src="assets/voice.wav" data-start="0" data-duration="{VOICE_DUR:.2f}" data-track-index="40" data-volume="1"></audio>
<audio id="bed" src="assets/bed.wav" data-start="0" data-duration="{DUR:.2f}" data-track-index="41" data-volume="{cfg.get("bed_vol", 0.06)}"></audio>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(JS)}
tl.set({{}}, {{}}, {DUR:.2f});
window.__timelines["main"] = tl;
</script>
</div>
</body>
</html>
"""
    open(f"{P}/index.html", "w", encoding="utf-8").write(html)
    br = sum(t(j) - t(i) for _, i, j in cfg.get("broll", []))
    print(f"{cfg['title']}: {DUR:.2f} s, captions {len(chunks)}, titles {len(cfg.get('titles', []))}, "
          f"b-roll {len(cfg.get('broll', []))} ({br:.1f} s), notes {len(cfg.get('notes', []))}, arrows {len(cfg.get('arrows', []))}")
