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


def env(t, t0, t1, fin=0.12, fout=0.15):
    """alpha envelope and pop scale for an element living t0..t1"""
    if t < t0 or t > t1:
        return 0, 0
    a = min(1, (t - t0) / fin) if fin else 1
    a = min(a, (t1 - t) / fout) if fout else a
    s = 0.6 + 0.4 * ease_back((t - t0) / 0.28)
    return a, s


# ---------------- words ----------------
FIX = {"đá": "đá", "công": "cốc", "calor": "calo", "-70": "-70", "-65": "-65"}


def load_words():
    d = json.load(open("tx/0081.json"))
    tl, total = timeline()
    words = []
    for a, b, es, n, z, pi in tl:
        for s in d:
            for w in s["words"]:
                if w["e"] > a + 0.1 and w["s"] < b - 0.05:
                    words.append([es + max(0, w["s"] + WORD_LAG - a), es + (min(w["e"] + WORD_LAG, b) - a), w["w"], w["s"]])
    # merge "60" "-70" style number pairs, apply fixes, strip punctuation
    out = []
    for w in words:
        txt = FIX.get(w[2].strip(",.?"), w[2].strip(",.?"))
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

# ---------------- beats ----------------
TITLE_T0 = hook_end()          # cold-open hook ends: flash + click, the title starts
TITLE_END = E(64.50)
HOOK_END = TITLE_END
SECTIONS = [  # (t0, t1, line1, line2)
    (E(134.00), E(141.70), "1.) KHÁCH GIẢM CÂN", "ăn trong ngưỡng thâm hụt"),
    (E(167.46), E(197.86), "2.) ĐỪNG ĐỂ VIỆC ĂN UỐNG", "thành thêm một nỗi stress"),
    (E(226.02), E(289.28), "3.) CHẤP NHẬN", "kết quả sẽ đến muộn hơn"),
    (E(311.12), E(353.15), "4.) ĐIỀU CHỈNH", "các bữa còn lại trong ngày"),
]
# keyword pops in the caption zone: (t0, t1, text, style)  style: ser / osw
POPS = [
    (E(62.70), E(63.86), "vấn đề chung", "ser"),
    (E(137.66), E(138.50), "CALO", "osw"),
    (E(140.90), E(141.70), "thâm hụt", "ser"),
    (E(177.20), E(177.95), "STRESS", "osw"),
    (E(183.80), E(184.60), "niềm vui", "ser"),
    (E(283.36), E(283.95), "ăn đói", "ser"),
    (E(286.20), E(288.40), "vừa đói\nvừa chán", "ser"),
    (E(308.26), E(308.80), "dở hơi", "ser"),
]
TAGS = [  # (t0, t1, text)
    (E(169.40), E(171.95), "đi tập = stress lên cơ thể"),
    (E(227.50), E(228.58), "kết quả đến muộn"),
    (E(303.60), E(306.00), "cả phòng đặt đồ ăn"),
]
# emoji stickers: (t0, t1, name, x, y, size)
EMOJI = [
    (E(51.28), HOOK_END, "coffee", 150, 780, 135),
    (E(54.28), HOOK_END, "bubbletea", 150, 945, 135),
    (E(60.20), HOOK_END, "fries", 150, 1110, 135),
    (E(177.20), E(178.08), "sweat", 860, 640, 170),
    (E(183.80), E(184.60), "yum", 860, 640, 170),
    (E(192.36), E(197.86), "coffee", 400, 480, 160),
    (E(196.30), E(197.86), "cookie", 680, 480, 160),
    (E(227.50), E(228.58), "hourglass", 860, 640, 160),
    (E(286.20), E(288.40), "weary", 860, 640, 170),
    (E(308.26), E(308.80), "zany", 860, 640, 170),
    (E(330.52), E(344.76), "bento", 880, 470, 150),
    (E(342.06), E(344.76), "down", 170, 650, 110),
    (E(354.24), E(356.78), "plate", 860, 640, 160),
]
MARKS = [  # check / cross badges on emoji: (t0, t1, x, y, kind)
    (E(192.70), E(197.86), 455, 540, "ok"),
    (E(196.60), E(197.86), 735, 540, "no"),
]
PRICE = (E(331.58), E(344.76))      # price card
STRIKE_T = E(338.74)
NEW_PRICE_T = E(342.06)
RECAP = (E(353.20), END)
RECAP_LINES = ["1.) ăn trong ngưỡng thâm hụt", "2.) ăn uống không thành stress",
               "3.) chấp nhận kết quả đến muộn", "4.) điều chỉnh các bữa còn lại"]
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
        k = kicker_img("✦ DÂN VĂN PHÒNG ✦")
        paste(c, k, W / 2, 150, 0.9 + 0.1 * ease_back(t / 0.25), a * min(1, t / 0.12))
        hc = Image.new("RGBA", (W, H))
        draw_typed(hc, "giảm cân sao cho", F_SER_XL, CREAM, W / 2, 265, t, 0.10, 24, cursor=False)
        draw_typed(hc, "đỡ stress?", F_SER_XL, CREAM, W / 2, 385, t, 0.10 + 16 / 24, 24)
        if a < 1:
            hc.putalpha(hc.split()[3].point(lambda v: int(v * a)))
        c.alpha_composite(hc)
        if t > 1.3:
            tw = 0.85 + 0.15 * math.sin(t * 6)
            paste(c, emoji("sparkles", 90), 905, 330, tw, a)
            paste(c, emoji("star", 60), 170, 225, 1.1 - tw * 0.2, a)
    t = t_abs
    # ---- section headers ----
    for t0, t1, l1, l2 in SECTIONS:
        if t0 <= t <= t1 + 0.2:
            a = min(1, (t1 + 0.2 - t) / 0.2)
            hc = Image.new("RGBA", (W, H))
            paste(hc, text_img(N(l1), F_HEAD, WHITE), W / 2, 200, 1, min(1, (t - t0) / 0.15))
            draw_typed(hc, l2, F_SER_M, CREAM, W / 2, 285, t, t0 + 0.15, 30, cursor=False)
            if a < 1:
                hc.putalpha(hc.split()[3].point(lambda v: int(v * a)))
            c.alpha_composite(hc)
    # ---- recap ----
    if RECAP[0] <= t:
        y = 175
        for i, line in enumerate(RECAP_LINES):
            tt = RECAP[0] + i * 0.18
            if t >= tt:
                a = min(1, (t - tt) / 0.15)
                im = text_img(line, F_RECAP, CREAM if i % 2 == 0 else WHITE)
                paste(c, im, W / 2, y + i * 72, 0.9 + 0.1 * a, a)
    # ---- emoji ----
    for t0, t1, name, x, y, sz in EMOJI:
        a, s = env(t, t0, t1)
        if a:
            bob = 6 * math.sin((t - t0) * 4)
            paste(c, emoji(name, sz), x, y + bob, s, a)
    for t0, t1, x, y, kind in MARKS:
        a, s = env(t, t0, t1)
        if a:
            b = Image.new("RGBA", (84, 84))
            d = ImageDraw.Draw(b)
            d.ellipse((4, 4, 80, 80), fill=(60, 180, 90, 255) if kind == "ok" else RED, outline=WHITE, width=5)
            if kind == "ok":
                d.line((24, 44, 38, 58, 62, 28), fill=WHITE, width=9, joint="curve")
            else:
                d.line((28, 28, 56, 56), fill=WHITE, width=9); d.line((56, 28, 28, 56), fill=WHITE, width=9)
            paste(c, b, x, y, s, a)
    # ---- price card ----
    if PRICE[0] <= t <= PRICE[1]:
        a, s = env(t, *PRICE)
        old = text_img("60-70K", F_OSW, WHITE)
        paste(c, old, W / 2 - 40, 470, s, a)
        if t >= STRIKE_T:
            p = min(1, (t - STRIKE_T) / 0.3)
            d = ImageDraw.Draw(c)
            x0 = W / 2 - 40 - old.width / 2 + 40
            x1 = x0 + (old.width - 80) * p
            d.line((x0, 480, x1, 460), fill=RED, width=14)
        if t >= NEW_PRICE_T:
            a2, s2 = env(t, NEW_PRICE_T, PRICE[1])
            paste(c, text_img("50-65K", F_OSW_M, CREAM, glow=True), W / 2 + 40, 630, s2, a2)
    # ---- tags ----
    for t0, t1, txt in TAGS:
        a, s = env(t, t0, t1)
        if a:
            paste(c, tag_img(txt), W / 2, 1290, 0.85 + 0.15 * s, a)
    # ---- keyword pops ----
    for t0, t1, txt, st in POPS:
        a, s = env(t, t0, t1, 0.08, 0.12)
        if a:
            lines = txt.split("\n")
            for i, ln in enumerate(lines):
                f = F_OSW if st == "osw" else (F_SER_L if len(lines) > 1 else F_SER_XL)
                im = text_img(ln, f, CREAM if st == "ser" else WHITE, glow=True)
                yy = CAP_Y - (len(lines) - 1) * 55 + i * 110
                paste(c, im, W / 2, yy, s, a)
    # ---- word captions ----
    if not caption_zone_busy(t):
        cy = CAP_Y
        for s0, s1, txt, _ in WORDS:
            if s0 <= t < s1:
                k = min(1, (t - s0) / 0.06)
                paste(c, text_img(txt.lower(), F_CAP, WHITE), W / 2, cy, 0.92 + 0.08 * k, 1)
                break
    # ---- flash on the hook -> scene cut (white, 0.35 s) ----
    if TITLE_T0 - 0.04 <= t_abs < TITLE_T0 + 0.35:
        k = (t_abs - TITLE_T0 + 0.04) / 0.39
        fl = Image.new("RGBA", (W, H), (255, 255, 255, int(235 * (1 - k) ** 1.7)))
        c.alpha_composite(fl)
    return c


def sfx_events():
    ev = [(TITLE_T0 - 0.03, "@click", -6), (TITLE_T0 + 0.05, "cc0-whoosh-reverse", -18)]
    for t0, *_ in SECTIONS:
        ev.append((t0, "cc0-paper-flip", -14))
    for o0, *_ in BROLL:
        ev.append((max(0, E(o0) - 0.22), "cc0-whoosh-reverse", -20))
    ev.append((STRIKE_T, "cc0-cartoon-zip", -18))
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
