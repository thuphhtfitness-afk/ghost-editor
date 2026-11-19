"""HPF talking head overlay: renders every graphic as RGBA frames to stdout (1080x1920, 30 fps).
House look (from the references):
  * one spoken word at a time, white Be Vietnam Pro ExtraBold, lowercase, soft shadow, on the chest (ref 2-6)
  * hook: small white caps kicker + big cream Playfair Display Italic typed on with a cursor and sparkles (ref 1, 6)
  * section header held at the top: white "1.) ..." + cream italic second line (ref 6)
  * keyword pops: cream Playfair italic or Oswald caps with glow, replacing the word caption (ref 1)
  * tags: cream box, ink text (ref 1 'edit style' box, ref 3-4 label tags)
  * 3D emoji stickers that pop on the word and collect in a row (ref 3 tier icons, ref 6 emoji)
Usage: overlay.py --frames N  > rgba stream ; overlay.py --still t1,t2 out.png ; overlay.py --events
"""
import sys, os, json, math, unicodedata
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, os.getcwd())  # the reel project holds plan.py
from plan import *

W, H = 1080, 1920
CREAM = (246, 234, 170, 255)
WHITE = (255, 255, 255, 255)
INK = (28, 24, 20, 255)
RED = (230, 57, 70, 255)
FD = "/root/.fonts/"
EMO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "emoji/")
CAP_Y = 1420          # word caption centre (chest)
TITLE_CPS = 24                 # typing speed of the title (a short title window types faster)
KICKER_Y, TITLE_Y = 150, 265   # hook title (a reel with the face high in frame moves them up)
RECAP_Y, RECAP_DY = 175, 72
CAP_X = TAG_X = W / 2   # horizontal centre of captions / pops and of tags (a reel with a side column moves them)
TAG_Y = 1290          # tag pill centre (a reel can override CAP_Y / TAG_Y in beats.py)


def font(name, size, wght=None):
    f = ImageFont.truetype(FD + name, size)
    if wght:
        try:
            f.set_variation_by_axes([wght])
        except Exception:
            pass
    return f


F_CAP = font("BeVietnamPro-ExtraBold.ttf", 66)
F_KICK = font("BeVietnamPro-ExtraBold.ttf", 40)
F_HEAD = font("BeVietnamPro-ExtraBold.ttf", 50)
F_TAG = font("BeVietnamPro-SemiBold.ttf", 42)
F_SER_XL = font("PlayfairDisplay-Italic%5Bwght%5D.ttf", 112, 500)
F_SER_L = font("PlayfairDisplay-Italic%5Bwght%5D.ttf", 92, 500)
F_SER_M = font("PlayfairDisplay-Italic%5Bwght%5D.ttf", 72, 600)
F_HAND = font("PatrickHand-Regular.ttf", 62)  # full Vietnamese (Caveat lacks ơ ư ẳ ...)
F_HAND_L = font("PatrickHand-Regular.ttf", 82)
INKB = (29, 53, 87, 255)       # marker blue
F_SER_S = font("PlayfairDisplay-Italic%5Bwght%5D.ttf", 58, 600)
F_OSW = font("Oswald%5Bwght%5D.ttf", 150, 600)
F_OSW_M = font("Oswald%5Bwght%5D.ttf", 120, 600)
F_RECAP = font("BeVietnamPro-ExtraBold.ttf", 46)

N = lambda s: unicodedata.normalize("NFC", s)
_cache = {}
WORD_LAG = 0.08   # whisper word onsets run early on this mic


def text_img(txt, f, fill, shadow=True, glow=False, stroke=0):
    key = (txt, id(f), fill, shadow, glow, stroke)
    if key in _cache:
        return _cache[key]
    txt = N(txt)
    bb = f.getbbox(txt, stroke_width=stroke)
    pad = 40
    w, h = bb[2] - bb[0] + pad * 2, bb[3] - bb[1] + pad * 2
    im = Image.new("RGBA", (w, h))
    d = ImageDraw.Draw(im)
    d.text((pad - bb[0], pad - bb[1]), txt, font=f, fill=fill, stroke_width=stroke, stroke_fill=fill)
    out = Image.new("RGBA", (w, h))
    if shadow:
        a = im.split()[3]
        sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        sh.putalpha(a.point(lambda v: v * 0.55))
        sh = sh.filter(ImageFilter.GaussianBlur(7))
        out.alpha_composite(sh, (0, 5))
    if glow:
        g = Image.new("RGBA", (w, h), fill[:3] + (0,))
        g.putalpha(im.split()[3].point(lambda v: v * 0.6))
        out.alpha_composite(g.filter(ImageFilter.GaussianBlur(16)))
    out.alpha_composite(im)
    _cache[key] = out
    return out


def tag_img(txt):
    key = ("tag", txt)
    if key in _cache:
        return _cache[key]
    txt = N(txt)
    bb = F_TAG.getbbox(txt)
    px, py = 26, 16
    w, h = bb[2] - bb[0] + px * 2, bb[3] - bb[1] + py * 2
    im = Image.new("RGBA", (w + 30, h + 30))
    sh = Image.new("RGBA", im.size)
    ImageDraw.Draw(sh).rounded_rectangle((15, 21, 15 + w, 21 + h), 14, fill=(0, 0, 0, 110))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((15, 15, 15 + w, 15 + h), 14, fill=CREAM)
    d.text((15 + px - bb[0], 15 + py - bb[1]), txt, font=F_TAG, fill=INK)
    _cache[key] = im
    return im


def kicker_img(txt):
    key = ("kick", txt)
    if key in _cache:
        return _cache[key]
    txt = N(txt)
    bb = F_KICK.getbbox(txt)
    px, py = 24, 14
    w, h = bb[2] - bb[0] + px * 2, bb[3] - bb[1] + py * 2
    im = Image.new("RGBA", (w + 30, h + 30))
    sh = Image.new("RGBA", im.size)
    ImageDraw.Draw(sh).rectangle((15, 21, 15 + w, 21 + h), fill=(0, 0, 0, 120))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    d = ImageDraw.Draw(im)
    d.rectangle((15, 15, 15 + w, 15 + h), fill=CREAM)
    d.text((15 + px - bb[0], 15 + py - bb[1]), txt, font=F_KICK, fill=INK)
    _cache[key] = im
    return im


F_MONT = font("Montserrat%5Bwght%5D.ttf", 44, 700)


def flabel_img(txt, kind=None):
    """Montserrat label on a white pill, with a ✓/✗ badge (photo and anatomy call-outs)"""
    key = ("flab", txt, kind)
    if key in _cache:
        return _cache[key]
    txt = N(txt); bb = F_MONT.getbbox(txt)
    badge = 58 if kind else 0
    w, h = bb[2] - bb[0] + 44 + badge, bb[3] - bb[1] + 30
    im = Image.new("RGBA", (w + 30, h + 30))
    sh = Image.new("RGBA", im.size); ImageDraw.Draw(sh).rounded_rectangle((15, 21, 15 + w, 21 + h), h // 2, fill=(0, 0, 0, 100))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((15, 15, 15 + w, 15 + h), h // 2, fill=(255, 255, 255, 255))
    col = (40, 160, 80, 255) if kind == "ok" else RED if kind == "no" else INK
    if kind:
        cx, cy = 15 + 22 + 18, 15 + h // 2
        d.ellipse((cx - 22, cy - 22, cx + 22, cy + 22), fill=col)
        if kind == "ok":
            d.line((cx - 10, cy + 1, cx - 3, cy + 9, cx + 11, cy - 8), fill=WHITE, width=6, joint="curve")
        else:
            d.line((cx - 8, cy - 8, cx + 8, cy + 8), fill=WHITE, width=6); d.line((cx + 8, cy - 8, cx - 8, cy + 8), fill=WHITE, width=6)
    d.text((15 + 22 + badge - bb[0], 15 + 15 - bb[1]), txt, font=F_MONT, fill=col if kind else INK)
    _cache[key] = im
    return im


def emoji(name, size):
    key = ("emo", name, size)
    if key not in _cache:
        im = Image.open(EMO + name + ".png").convert("RGBA")
        im = im.resize((size, size), Image.LANCZOS)
        out = Image.new("RGBA", (size + 30, size + 30))
        sh = Image.new("RGBA", out.size)
        sh.paste((0, 0, 0, 90), (15, 22), im)
        out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
        out.alpha_composite(im, (15, 15))
        _cache[key] = out
    return _cache[key]


def ease_back(x):
    x = min(max(x, 0), 1)
    c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def paste(canvas, im, cx, cy, scale=1.0, alpha=1.0, anchor="c"):
    if alpha <= 0.01 or scale <= 0.01:
        return
    if abs(scale - 1) > 0.01:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BILINEAR)
    if alpha < 0.999:
        a = im.split()[3].point(lambda v: int(v * alpha))
        im = im.copy(); im.putalpha(a)
    x = int(cx - im.width / 2) if anchor == "c" else int(cx - 40)
    canvas.alpha_composite(im, (x, int(cy - im.height / 2))) if 0 <= x and x + im.width <= W else _safe(canvas, im, x, int(cy - im.height / 2))


def _safe(canvas, im, x, y):
    tmp = Image.new("RGBA", canvas.size)
    tmp.paste(im, (x, y))
    canvas.alpha_composite(tmp)


# closed-form spring (from xilo-opus-video craft rules): a pure function of time, no state between frames.
# One preset per kind of element, the same preset for the same kind across the reel.
SPRING = {"sticker": (18, 0.45),   # emoji, cut-out people, badges: lively, visible bounce
          "card": (15, 0.72),      # tags, checklist pills: default
          "heavy": (10, 0.90)}     # big words, numbers, keyword pops: settles with almost no bounce


def spring(x, w=15, z=0.72):
    if x <= 0:
        return 0.0
    wd = w * math.sqrt(1 - z * z)
    return 1 - math.exp(-z * w * x) * (math.cos(wd * x) + (z * w / wd) * math.sin(wd * x))


def env(t, t0, t1, fin=0.12, fout=0.15, kind="card"):
    """alpha envelope and pop scale for an element living t0..t1"""
    if t < t0 or t > t1:
        return 0, 0
    a = min(1, (t - t0) / fin) if fin else 1
    a = min(a, (t1 - t) / fout) if fout else a
    w, z = SPRING.get(kind, SPRING["card"])
    s = 0.6 + 0.4 * spring(t - t0, w, z)
    return a, s


# ---------------- words ----------------
from beats import FIX  # caption fixes for mis-heard words
try:
    from beats import FIX_AT
except ImportError:
    FIX_AT = {}


def load_words():
    import plan as _plan
    d = []
    for off, _src, tx, _vad in getattr(_plan, "SOURCES", [(0, None, TX, None)]):
        for seg in json.load(open(tx)):
            d.append({**seg, "words": [{**w, "s": w["s"] + off, "e": w["e"] + off} for w in seg["words"]]})
    tl, total = timeline()
    words, seen = [], set()
    for a, b, es, n, z, pi in tl:
        for s in d:
            for w in s["words"]:
                if w["e"] > a + 0.1 and w["s"] < b - 0.05 and (w["s"], w["w"]) not in seen:
                    seen.add((w["s"], w["w"]))   # a word straddling a silence cut belongs to the first piece only
                    words.append([es + max(0, w["s"] + WORD_LAG - a), es + (min(w["e"] + WORD_LAG, b) - a), w["w"], w["s"]])
    # merge "60" "-70" style number pairs, apply fixes, strip punctuation
    out = []
    for w in words:
        txt = FIX.get(w[2].strip(",.?"), w[2].strip(",.?"))
        fa = globals().get('FIX_AT', {}).get(round(w[3], 2))   # a fix for one word at one moment
        if fa is not None:
            txt = fa
        if not txt:
            continue
        if txt.startswith("-") and out:
            out[-1][2] += txt; out[-1][1] = w[1]; continue
        if txt.isdigit() or txt[0].isdigit():
            txt = txt
        out.append([w[0], w[1], txt, w[3]])
    for i, w in enumerate(out):
        nxt = out[i + 1][0] if i + 1 < len(out) else w[1] + 0.4
        w[1] = min(max(w[1], w[0] + 0.18), nxt, w[0] + 1.2)
    return out, total


WORDS, TOTAL = load_words()
E = to_edit  # original second -> edit second
TL, _ = timeline()
END = TOTAL / FPS + 0.6   # held tail

from beats import *  # the reel's content slots (beats.py in the reel project)
SFX = []  # filled by frame 0 pass


def typed(txt, t, t0, cps=22):
    n = int(max(0, (t - t0)) * cps)
    return txt[:n], n < len(txt)


def draw_typed(c, txt, f, fill, cx, cy, t, t0, cps=22, cursor=True):
    full = text_img(txt, f, fill, glow=True)
    s, typing = typed(txt, t, t0, cps)
    if not s:
        return
    im = text_img(s, f, fill, glow=True)
    x0 = cx - full.width / 2
    c.alpha_composite(im, (int(x0), int(cy - im.height / 2)))
    if cursor and (typing or (t - t0) % 0.8 < 0.4) and t - t0 < len(txt) / cps + 0.9:
        d = ImageDraw.Draw(c)
        xe = x0 + im.width - 34
        d.rectangle((xe, cy - f.size * 0.42, xe + 4, cy + f.size * 0.42), fill=WHITE)


def cap_x(t):
    """captions sit opposite a side-column card: CAP_X_AT = [(t0, t1, x), ...] in beats.py, else CAP_X"""
    for t0, t1, x in globals().get("CAP_X_AT", []):
        if t0 - 0.1 <= t <= t1 + 0.1:
            return x
    return CAP_X


def caption_zone_busy(t):
    for t0, t1, *_ in POPS:
        if t0 <= t <= t1:
            return True
    return False


def _grad():
    g = Image.new("RGBA", (W, H))
    d = ImageDraw.Draw(g)
    for y in range(0, 820):
        d.line((0, y, W, y), fill=(0, 0, 0, int(165 * (1 - y / 820) ** 1.35)))
    return g


GRAD = _grad()


def frame(t):
    t_abs = t
    c = GRAD.copy()
    # ---- hook (ref 1 + ref 6 title) ----
    if TITLE_T0 <= t < HOOK_END:
        a = min(1, (HOOK_END - t) / 0.2)
        t = t - TITLE_T0  # title clock
        k = kicker_img(f"✦ {KICKER} ✦")
        paste(c, k, W / 2, KICKER_Y, 0.9 + 0.1 * ease_back(t / 0.25), a * min(1, t / 0.12))
        hc = Image.new("RGBA", (W, H))
        t_line = 0.10
        tf = F_SER_XL if all(text_img(l, F_SER_XL, CREAM, glow=True).width - 80 < W - 90 for l in TITLE_LINES) else F_SER_L
        for li, line in enumerate(TITLE_LINES):
            draw_typed(hc, line, tf, CREAM, W / 2, TITLE_Y + li * (120 if tf is F_SER_XL else 104), t, t_line, TITLE_CPS, cursor=li == len(TITLE_LINES) - 1)
            t_line += len(line) / TITLE_CPS
        if a < 1:
            hc.putalpha(hc.split()[3].point(lambda v: int(v * a)))
        c.alpha_composite(hc)
        if t > 1.3:
            tw = 0.85 + 0.15 * math.sin(t * 6)
            paste(c, emoji("sparkles", 90), 905, 330, tw, a)
            paste(c, emoji("star", 60), 170, 225, 1.1 - tw * 0.2, a)
    t = t_abs
    # ---- section headers ----
    for si, (t0, t1, l1, l2) in enumerate(SECTIONS):
        t1 = min(t1, RECAP[0] - 0.25)   # the recap owns the top band: never two blocks of text at once
        nxt = [s_[0] for s_ in SECTIONS if s_[0] > t0]
        if nxt:
            t1 = min(t1, min(nxt) - 0.22)  # the old header is gone before the next one types in
        bd_ = globals().get("BOARD")
        if bd_ and bd_["t0"] - 0.1 <= t <= bd_["t1"]:
            continue                    # the whiteboard owns the top band too
        if t0 <= t <= t1 + 0.2:
            a = min(1, (t1 + 0.2 - t) / 0.2)
            hc = Image.new("RGBA", (W, H))
            paste(hc, text_img(N(l1), F_HEAD, WHITE), W / 2, 200, 1, min(1, (t - t0) / 0.15))
            f2 = F_SER_M if text_img(l2, F_SER_M, CREAM, glow=True).width - 80 < W - 90 else F_SER_S
            draw_typed(hc, l2, f2, CREAM, W / 2, 285, t, t0 + 0.15, 30, cursor=False)
            if a < 1:
                hc.putalpha(hc.split()[3].point(lambda v: int(v * a)))
            c.alpha_composite(hc)
    # ---- recap ----
    if RECAP[0] <= t:
        y = RECAP_Y
        for i, line in enumerate(RECAP_LINES):
            tt = RECAP[0] + i * 0.18
            if t >= tt:
                a = min(1, (t - tt) / 0.15)
                im = text_img(line, F_RECAP, CREAM if i % 2 == 0 else WHITE)
                paste(c, im, W / 2, y + i * RECAP_DY, 0.9 + 0.1 * a, a)
    # ---- emoji ----
    for t0, t1, name, x, y, sz in EMOJI:
        a, s = env(t, t0, t1, kind="sticker")
        if a:
            bob = 6 * math.sin((t - t0) * 4)
            paste(c, emoji(name, sz), x, y + bob, s, a)
    for t0, t1, x, y, kind in MARKS:
        a, s = env(t, t0, t1, kind="sticker")
        if a:
            b = Image.new("RGBA", (84, 84))
            d = ImageDraw.Draw(b)
            d.ellipse((4, 4, 80, 80), fill=(60, 180, 90, 255) if kind == "ok" else RED, outline=WHITE, width=5)
            if kind == "ok":
                d.line((24, 44, 38, 58, 62, 28), fill=WHITE, width=9, joint="curve")
            else:
                d.line((28, 28, 56, 56), fill=WHITE, width=9); d.line((56, 28, 28, 56), fill=WHITE, width=9)
            paste(c, b, x, y, s, a)
    # ---- checklist on the plain wall (lines tick in on their words) ----
    for item in CHECKLIST:
        t0, t1, x, y, line = item[:5]
        kind = item[5] if len(item) > 5 else "ok"
        a, s = env(t, t0, t1)
        if a:
            b = Image.new("RGBA", (64, 64)); d = ImageDraw.Draw(b)
            d.ellipse((2, 2, 62, 62), fill=(60, 180, 90, 255) if kind == "ok" else RED, outline=WHITE, width=4)
            if kind == "ok":
                d.line((18, 33, 28, 44, 47, 21), fill=WHITE, width=7, joint="curve")
            else:
                d.line((21, 21, 43, 43), fill=WHITE, width=7); d.line((43, 21, 21, 43), fill=WHITE, width=7)
            paste(c, b, x, y, s, a)
            im = tag_img(line)
            paste(c, im, x + 44 + im.width / 2 - 15, y, 0.9 + 0.1 * s, a)
    # ---- whiteboard: before -> marker arrow + time benchmark -> after (beats.BOARD) ----
    bd = globals().get("BOARD")
    if bd and bd["t0"] <= t <= bd["t1"]:
        a = min(1, (t - bd["t0"]) / 0.18, (bd["t1"] - t) / 0.2)
        x0, y0, x1, y1 = bd["box"]
        slide = (1 - ease_back(min(1, (t - bd["t0"]) / 0.35))) * 60
        layer = Image.new("RGBA", (W, H))
        sh = Image.new("RGBA", (W, H)); ImageDraw.Draw(sh).rounded_rectangle((x0, y0 + 14, x1, y1 + 14), 26, fill=(0, 0, 0, 90))
        layer.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
        d = ImageDraw.Draw(layer)
        d.rounded_rectangle((x0, y0, x1, y1), 26, fill=(252, 252, 250, 255), outline=(205, 208, 212, 255), width=6)
        d.rounded_rectangle((x0 + (x1 - x0) * 0.3, y1 - 4, x0 + (x1 - x0) * 0.7, y1 + 14), 6, fill=(170, 175, 182, 255))  # marker tray
        for lt, txt, lx, ly, f in bd.get("labels", []):
            f = F_HAND_L if f == "L" else F_HAND
            if t >= lt:
                s_, typing = typed(txt, t, lt, 26)
                if s_:
                    im = text_img(s_, f, INKB, shadow=False)
                    full = text_img(txt, f, INKB, shadow=False)
                    layer.alpha_composite(im, (int(lx - full.width / 2), int(ly - im.height / 2)))
        for key in ("before", "after"):
            path, pt, px, py, sc, ang = bd[key]
            if t >= pt:
                k_ = ("cut", path, sc, ang)
                if k_ not in _cache:
                    im = Image.open(path).convert("RGBA")
                    im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
                    _cache[k_] = im.rotate(ang, resample=Image.BICUBIC, expand=True)
                paste(layer, _cache[k_], px, py, 0.6 + 0.4 * ease_back((t - pt) / 0.3), min(1, (t - pt) / 0.1))
        at0, at1, (ax0, ay, ax1) = bd["arrow"]
        if t >= at0:
            p = min(1, (t - at0) / max(0.05, at1 - at0))
            pts = [(ax0 + (ax1 - ax0) * u, ay + 10 * math.sin(u * math.pi * 1.5)) for u in [i / 40 * p for i in range(41)]]
            d.line(pts, fill=INKB, width=10, joint="curve")
            if p >= 1:
                ex, ey = pts[-1]
                d.line((ex - 34, ey - 22, ex, ey, ex - 34, ey + 24), fill=INKB, width=10, joint="curve")
        if a < 1:
            layer.putalpha(layer.split()[3].point(lambda v: int(v * a)))
        c.alpha_composite(layer, (0, int(slide)))
    # ---- zoom-and-pulse cards: whole figure first, then on the spoken muscle the window zooms into it and it glows ----
    for t0, t1, plain, hot, x, y, sc, o in globals().get("ZPANELS", []):
        a, s = env(t, t0, t1, 0.12, 0.18, kind="card")
        if not a:
            continue
        key = ("zp", plain, hot)
        if key not in _cache:
            _cache[key] = (Image.open(plain).convert("RGBA"), Image.open(hot).convert("RGBA"))
        P0, P1 = _cache[key]
        card = P0.copy()
        tz = o.get("zoom_at")
        if tz is not None and t >= tz:
            u = t - tz
            z = 1 + (o.get("zoom", 2.0) - 1) * spring(u, 9, 0.9)
            ha = min(1, u / 0.25) * (0.6 + 0.4 * math.sin(2 * math.pi * 1.3 * u))
            src = Image.blend(P0, P1, max(0, min(1, ha)))
            wx0, wy0, wx1, wy1 = o.get("win", (40, 160, 800, 1160))
            fx, fy = o["focus"]
            ww, wh = (wx1 - wx0) / z, (wy1 - wy0) / z
            cx0 = min(max(fx - ww / 2, wx0), wx1 - ww); cy0 = min(max(fy - wh / 2, wy0), wy1 - wh)
            card.paste(src.crop((int(cx0), int(cy0), int(cx0 + ww), int(cy0 + wh))).resize((wx1 - wx0, wy1 - wy0), Image.LANCZOS), (wx0, wy0))
        card = card.resize((int(card.width * sc), int(card.height * sc)), Image.LANCZOS)
        paste(c, card, x, y, 0.94 + 0.06 * s, a)
    # ---- illustration cards (anatomy_cards.py etc.): steady, card spring ----
    for item in globals().get("PANELS", []):
        t0, t1, path, x, y, sc = item[:6]
        bg = item[6] if len(item) > 6 else None      # e.g. (244, 244, 242): full-screen card over the footage
        a, s = env(t, t0, t1, 0.10, 0.15, kind="card")
        if a and bg:
            c.alpha_composite(Image.new("RGBA", (W, H), tuple(bg) + (int(255 * a),)))
        if a:
            key = ("panel", path, sc)
            if key not in _cache:
                im = Image.open(path).convert("RGBA")
                _cache[key] = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
            paste(c, _cache[key], x, y, 0.92 + 0.08 * s, a)
    # ---- moving cut-out photos (slide in on a spring, slow drift / zoom while held) ----
    for item in globals().get("MOVERS", []):
        t0, t1, path, x, y, sc = item[:6]
        o = item[6] if len(item) > 6 else {}
        if not (t0 <= t <= t1):
            continue
        key = ("mover", path, sc)
        if key not in _cache:
            im = Image.open(path).convert("RGBA")
            im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
            sh = Image.new("RGBA", (im.width + 60, im.height + 60))
            sh.paste((0, 0, 0, 110), (30, 42), im)
            out = sh.filter(ImageFilter.GaussianBlur(12)); out.alpha_composite(im, (30, 30))
            _cache[key] = out
        u = t - t0 - o.get("delay", 0)
        if u < 0:
            continue
        k = spring(u, 15, 0.72)
        dx, dy = o.get("slide", (0, 120))
        life = max(0.01, t1 - t0)
        ddx, ddy = o.get("drift", (0, 0))
        z0, z1 = o.get("zoom", (1.0, 1.0))
        a = min(1, u / 0.12, (t1 - t) / 0.15)
        paste(c, _cache[key], x + dx * (1 - k) + ddx * (t - t0) / life, y + dy * (1 - k) + ddy * (t - t0) / life,
              z0 + (z1 - z0) * (t - t0) / life, a)
    for item in globals().get("FLABELS", []):
        t0, t1, txt, x, y = item[:5]
        kind = item[5] if len(item) > 5 else None
        a, s = env(t, t0, t1, kind="card")
        if a:
            paste(c, flabel_img(txt, kind), x, y, 0.9 + 0.1 * s, a)
    # ---- paper cut-out stickers of people (sticker.py), pop in with a small tilt ----
    for t0, t1, path, x, y, sc, ang in globals().get("CUTOUTS", []):
        a, s = env(t, t0, t1, 0.10, 0.18, kind="sticker")
        if a:
            key = ("cut", path, sc, ang)
            if key not in _cache:
                im = Image.open(path).convert("RGBA")
                im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
                _cache[key] = im.rotate(ang, resample=Image.BICUBIC, expand=True)
            wob = 1.5 * math.sin((t - t0) * 2.2)
            im = _cache[key]
            if abs(wob) > 0.3:
                im = im.rotate(wob, resample=Image.BILINEAR, expand=True)
            paste(c, im, x, y, s, a)
    # ---- big numbers (Oswald, cream) ----
    for t0, t1, txt, x, y in NUMBERS:
        a, s = env(t, t0, t1, kind="heavy")
        if a:
            paste(c, text_img(txt, F_OSW_M, CREAM, glow=True), x, y, s, a)
    # ---- price card ----
    if PRICE and PRICE[0] <= t <= PRICE[1]:
        a, s = env(t, PRICE[0], PRICE[1], kind="heavy")
        old = text_img(PRICE[2], F_OSW, WHITE)
        fit = min(1.0, 980 / old.width)
        if fit < 1:
            old = old.resize((int(old.width * fit), int(old.height * fit)), Image.LANCZOS)
        paste(c, old, W / 2 - 40, 470, s, a)
        if t >= STRIKE_T:
            p = min(1, (t - STRIKE_T) / 0.3)
            d = ImageDraw.Draw(c)
            x0 = W / 2 - 40 - old.width / 2 + 40
            x1 = x0 + (old.width - 80) * p
            d.line((x0, 480, x1, 460), fill=RED, width=14)
        if t >= NEW_PRICE_T:
            a2, s2 = env(t, NEW_PRICE_T, PRICE[1], kind="heavy")
            paste(c, text_img(PRICE[3], F_OSW_M, CREAM, glow=True), W / 2 + 40, 630, s2, a2)
    # ---- tags ----
    for t0, t1, txt in TAGS:
        a, s = env(t, t0, t1)
        if a:
            paste(c, tag_img(txt), cap_x(t) if TAG_X == W / 2 else TAG_X, TAG_Y, 0.85 + 0.15 * s, a)
    # ---- keyword pops ----
    for t0, t1, txt, st in POPS:
        a, s = env(t, t0, t1, 0.08, 0.12, kind="heavy")
        if a:
            lines = txt.split("\n")
            for i, ln in enumerate(lines):
                f = F_OSW if st == "osw" else (F_SER_L if len(lines) > 1 else F_SER_XL)
                im = text_img(ln, f, CREAM if st == "ser" else WHITE, glow=True)
                yy = CAP_Y - (len(lines) - 1) * 55 + i * 110
                paste(c, im, cap_x(t), yy, s, a)
    # ---- word captions ----
    if not caption_zone_busy(t):
        cy = CAP_Y
        for s0, s1, txt, _ in WORDS:
            if s0 <= t < s1:
                k = min(1, (t - s0) / 0.06)
                paste(c, text_img(txt.lower(), F_CAP, WHITE), cap_x(t), cy, 0.92 + 0.08 * k, 1)
                break
    # ---- brand watermark (faint logo), hidden under the outro ----
    wm = globals().get("WATERMARK")
    ot = globals().get("OUTRO")
    t_out = (TOTAL / FPS + 0.3) if ot else 1e9
    if wm and t_abs < t_out + 0.3:
        key = ("wm", wm["path"], wm["width"])
        if key not in _cache:
            im = Image.open(wm["path"]).convert("RGBA")
            _cache[key] = im.resize((wm["width"], int(im.height * wm["width"] / im.width)), Image.LANCZOS)
        paste(c, _cache[key], wm["x"], wm["y"], 1, wm.get("alpha", 0.35))
    # ---- end card after the last word (advice the host did not say: shown as the channel's text) ----
    ec = globals().get("ENDCARD")
    if ec and t_abs >= TOTAL / FPS + 0.2:
        u = t_abs - TOTAL / FPS - 0.2
        a = min(1, u / 0.3)
        bgc = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(bgc)
        for yy in range(0, H, 4):
            k = yy / H
            d.rectangle((0, yy, W, yy + 4), fill=(int(22 + 26 * k), int(15 + 2 * k), int(17 + 3 * k), int(250 * a)))
        c.alpha_composite(bgc)
        hc = Image.new("RGBA", (W, H))
        y0 = ec.get("top", 560)
        draw_typed(hc, ec["title"], F_SER_XL, CREAM, W / 2, y0, u, 0.15, 30, cursor=False)
        c.alpha_composite(hc)
        y = y0 + 170
        for i, line in enumerate(ec["bullets"]):
            tb = 0.6 + i * 0.5
            if u < tb:
                break
            al = min(1, (u - tb) / 0.25)
            words, rows, cur = line.split(), [], ""
            for wd in words:                        # wrap to 820 px
                trial = (cur + " " + wd).strip()
                if F_MONT.getbbox(N(trial))[2] > 820 and cur:
                    rows.append(cur); cur = wd
                else:
                    cur = trial
            rows.append(cur)
            dot = Image.new("RGBA", (40, 40)); ImageDraw.Draw(dot).ellipse((4, 4, 36, 36), fill=RED)
            paste(c, dot, 95, y + 26, 0.8 + 0.2 * spring(u - tb, 15, .7), al)
            for r_ in rows:
                im = text_img(r_, F_MONT, WHITE)
                paste(c, im, 140 + im.width / 2 - 40, y + 26, 1, al)
                y += 62
            y += 34
        tc = 0.6 + len(ec["bullets"]) * 0.5 + 0.4
        if ec.get("cta") and u >= tc:
            al = min(1, (u - tc) / 0.25)
            paste(c, kicker_img(ec["cta"]), W / 2, y + 60, 0.9 + 0.1 * spring(u - tc, 15, .7), al)
        if ec.get("question") and u >= tc + 0.5:
            paste(c, text_img(ec["question"], F_SER_M, CREAM, glow=True), W / 2, y + 190, 1, min(1, (u - tc - 0.5) / 0.3))
    # ---- outro: brand screen after the last word ----
    if ot and t_abs >= t_out:
        u = t_abs - t_out
        a = min(1, u / 0.3)
        bgc = Image.new("RGBA", (W, H))
        d = ImageDraw.Draw(bgc)
        for yy in range(0, H, 4):
            k = yy / H
            d.rectangle((0, yy, W, yy + 4), fill=(int(20 + 30 * k), int(14 + 2 * k), int(16 + 4 * k), int(255 * a)))
        c.alpha_composite(bgc)
        key = ("outro", ot["logo"])
        if key not in _cache:
            im = Image.open(ot["logo"]).convert("RGBA")
            _cache[key] = im.resize((640, int(im.height * 640 / im.width)), Image.LANCZOS)
        lg = _cache[key]
        s_ = 0.7 + 0.3 * spring(u - 0.15, 12, 0.7)
        paste(c, lg, W / 2, 860, s_, min(1, max(0, (u - 0.15) / 0.2)))
        dl = ImageDraw.Draw(c)
        lw = 260 * min(1, max(0, (u - 0.5) / 0.4))
        dl.line((W / 2 - lw, 860 + lg.height / 2 + 60, W / 2 + lw, 860 + lg.height / 2 + 60), fill=(220, 45, 55, 255), width=6)
        if ot.get("line") and u > 0.7:
            paste(c, text_img(ot["line"], F_MONT, WHITE), W / 2, 860 + lg.height / 2 + 140, 1, min(1, (u - 0.7) / 0.25))
    # ---- flash on the hook -> scene cut (white, 0.35 s) ----
    if globals().get("FLASH", True) and TITLE_T0 - 0.04 <= t_abs < TITLE_T0 + 0.35:
        k = (t_abs - TITLE_T0 + 0.04) / 0.39
        fl = Image.new("RGBA", (W, H), (255, 255, 255, int(235 * (1 - k) ** 1.7)))
        c.alpha_composite(fl)
    return c


def sfx_events():
    ev = [(TITLE_T0 - 0.03, "@click", -6), (TITLE_T0 + 0.05, "cc0-whoosh-reverse", -18)] if globals().get("FLASH", True) else [(max(0, TITLE_T0) + 0.05, "cc0-whoosh-reverse", -18)]
    for t0, *_ in SECTIONS:
        ev.append((t0, "cc0-paper-flip", -14))
    for o0, *_ in BROLL:
        if E(o0) > 0.3:
            ev.append((max(0, E(o0) - 0.22), "cc0-whoosh-reverse", -20))
    if PRICE:
        ev.append((STRIKE_T, "cc0-cartoon-zip", -18))
    if globals().get("BOARD"):
        bd = BOARD
        ev.append((bd["t0"], "cc0-paper-flip", -15))
        ev.append((bd["arrow"][0], "cc0-whoosh-reverse", -20))
        ev.append((bd["after"][1], "cc0-paper-riffle", -18))
    if globals().get("OUTRO"):
        ev.append((TOTAL / FPS + 0.25, "cc0-swell-short", -12))
    if globals().get("ENDCARD"):
        ev.append((TOTAL / FPS + 0.2, "cc0-paper-flip", -15))
    for p_ in globals().get("PANELS", []):
        ev.append((p_[0], "cc0-paper-flip", -17))
    for p_ in globals().get("ZPANELS", []):
        ev.append((p_[0], "cc0-paper-flip", -17))
        if p_[7].get("zoom_at") is not None:
            ev.append((p_[7]["zoom_at"], "cc0-whoosh-reverse", -22))
    for t0, *_ in globals().get("CUTOUTS", []):
        ev.append((t0, "cc0-paper-flip", -15))
    ev.append((RECAP[0], "cc0-paper-riffle", -16))
    return ev


if __name__ == "__main__":
    if sys.argv[1] == "--events":
        print(json.dumps({"total": TOTAL, "end": END, "sfx": sfx_events(),
                          "words": [(round(a, 2), w) for a, b, w, _ in WORDS]}, ensure_ascii=False))
    elif sys.argv[1] == "--still":
        ts = [float(x) for x in sys.argv[2].split(",")]
        ims = []
        bg = sys.argv[4] if len(sys.argv) > 4 else None
        for t in ts:
            ims.append(frame(t))
        sheet = Image.new("RGBA", (W * len(ims) // 3, H // 3), (40, 40, 40, 255))
        for i, im in enumerate(ims):
            fr = Image.open(f"build/snap/{i:02d}.png").convert("RGBA").resize((W, H)) if bg else Image.new("RGBA", (W, H), (90, 90, 90, 255))
            fr.alpha_composite(im)
            sheet.paste(fr.resize((W // 3, H // 3)), (i * W // 3, 0))
        sheet.convert("RGB").save(sys.argv[3], quality=88)
    else:
        nfr = int(round(END * FPS))
        out = sys.stdout.buffer
        for i in range(nfr):
            out.write(frame(i / FPS).tobytes())
