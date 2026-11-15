"""Blue-essay reel renderer: royal blue / paper white / black pages with grain,
serif keyword + small sans kinetic captions, graded coach footage (cine / bw / duo),
footage cards, simple drawn diagrams. Usage: python3 engine.py spec.json outdir"""
import json, sys, os, math, subprocess, difflib, unicodedata, re
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from multiprocessing import Pool

SCR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(SCR, "fonts")
SRC = os.path.join(SCR, "work", "src1080.mp4")
W, H, FPS = 1080, 1920, 30
PALETTE = json.load(open(os.environ.get("PALETTE", "/home/user/ghost-editor/styles/ht-private-fitness.palette.json")))
def _hex(h): h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
BLUE = _hex(PALETTE["brand_red"])     # accent (name kept: accent colour)
BLUE2 = _hex(PALETTE["red_deep"])
PAPER = _hex(PALETTE["paper"])
INK = _hex(PALETTE["ink"])

_fc = {}
def font(name, size):
    k = (name, int(size))
    if k not in _fc:
        _fc[k] = ImageFont.truetype(os.path.join(FONTS, name), int(size))
    return _fc[k]
SERIF = "PlayfairDisplay-700.ttf"
SERIF_I = "PlayfairDisplay-700i.ttf"
SANS = "InterTight-700.ttf"
KEY_SERIF = "PlayfairDisplay-900i.ttf"
KEY_SANS = "InterTight-800.ttf"

def nfc(s): return unicodedata.normalize("NFC", s)
def norm(s): return re.sub(r"[^\w]", "", nfc(s).lower())
def ease(x): x = min(1, max(0, x)); return 1 - (1 - x) ** 3
def ease_io(x): x = min(1, max(0, x)); return x * x * (3 - 2 * x)

# ---------------- grain / vignette (precomputed) ----------------
rng = np.random.default_rng(7)
GRAIN = [rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32) for _ in range(6)]
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
_r = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
VIG = np.clip(1.0 - 0.55 * np.clip(_r - 0.35, 0, 1) ** 1.6, 0.35, 1)[..., None]
GRAD = (1.0 - 0.10 * (yy / H))[..., None]  # page gradient (top a bit lighter)
del xx, yy, _r

def grain(img, fi, amt):
    g = GRAIN[fi % len(GRAIN)]
    g = np.repeat(np.repeat(g, 2, 0), 2, 1)[..., None]
    return np.clip(img + g * amt, 0, 255)

# ---------------- looks ----------------
def curve_lut(lift, gamma, gain, contrast):
    x = np.arange(256, dtype=np.float32) / 255
    x = 0.5 + (x - 0.5) * contrast
    x = np.clip(x, 0, 1) ** gamma
    x = lift + x * (gain - lift)
    return np.clip(x * 255, 0, 255).astype(np.float32)
LUT_CINE = curve_lut(0.02, 1.12, 0.95, 1.15)
LUT_BW = curve_lut(0.0, 1.35, 0.98, 1.35)

def look(fr, kind):
    f = fr.astype(np.float32)
    if kind == "cine":
        lum = f @ np.array([0.299, 0.587, 0.114], np.float32)
        f = lum[..., None] + (f - lum[..., None]) * 0.55
        f = LUT_CINE[np.clip(f, 0, 255).astype(np.uint8)]
        sh = np.clip(1 - lum / 140, 0, 1)[..., None]
        f = f + sh * np.array([6, 0, -2], np.float32)  # warm-neutral shadows
        f = f * VIG
    elif kind == "bw":
        lum = f @ np.array([0.299, 0.587, 0.114], np.float32)
        f = LUT_BW[np.clip(lum, 0, 255).astype(np.uint8)][..., None].repeat(3, 2)
        f = f * VIG
    elif kind == "duo":  # black -> royal blue -> white
        lum = f @ np.array([0.299, 0.587, 0.114], np.float32) / 255
        lum = np.clip((lum - 0.18) / 0.78, 0, 1) ** 1.55
        lo = np.array(INK, np.float32); mid = np.array(BLUE, np.float32); hi = np.array([255, 250, 248], np.float32)
        a = np.clip(lum * 2, 0, 1)[..., None]; b = np.clip(lum * 2 - 1, 0, 1)[..., None]
        f = lo + (mid - lo) * a + (hi - mid) * b
    elif kind == "dark":
        f = LUT_CINE[f.astype(np.uint8)] * 0.55 * VIG
    return f

# ---------------- footage reader ----------------
class Reader:
    def __init__(self, start, n, w=W, h=H):
        self.w, self.h, self.n = w, h, n
        vf = f"scale={w}:{h}" if (w, h) != (W, H) else "null"
        self.p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{start:.3f}", "-i", SRC, "-frames:v", str(n),
                                   "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
        self.last = None
    def next(self):
        b = self.p.stdout.read(self.w * self.h * 3)
        if len(b) == self.w * self.h * 3:
            self.last = np.frombuffer(b, np.uint8).reshape(self.h, self.w, 3)
        return self.last if self.last is not None else np.zeros((self.h, self.w, 3), np.uint8)
    def close(self):
        self.p.stdout.close(); self.p.wait()

def zoom_frame(fr, z, fx, fy):
    if z <= 1.001: return fr
    cw, ch = W / z, H / z
    x0 = min(max(fx * W - cw / 2, 0), W - cw); y0 = min(max(fy * H - ch / 2, 0), H - ch)
    im = Image.fromarray(fr).resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))
    return np.asarray(im)

# ---------------- text ----------------
def text_w(f, s):
    return f.getlength(s, features=["lnum"])

def wrap(f, words, maxw):
    lines, cur = [], []
    for w in words:
        t = " ".join([x for x, _ in cur] + [w[0]])
        if cur and text_w(f, t) > maxw:
            lines.append(cur); cur = [w]
        else:
            cur.append(w)
    if cur: lines.append(cur)
    return lines

def draw_words(layer, f, line, x, y, t, col, anchor="ls"):
    """line: list of (word, onset). draws word by word with fade-in from onset"""
    d = ImageDraw.Draw(layer)
    sp = text_w(f, " ")
    for w, on in line:
        a = ease((t - on) / 0.14) if on is not None else 1
        if a > 0:
            dy = (1 - a) * 10
            d.text((x, y + dy), w, font=f, fill=col + (int(255 * a),), anchor=anchor)
        x += text_w(f, w) + sp

def caption_layer(layer, cap, t, col, cy, maxw=940):
    """reference layout: small sans line(s) above, big serif keyword, small sans below"""
    pre, key, post = cap["pre"], cap["key"], cap["post"]
    SM = cap.get("small", 56)
    sf = font(SANS, SM)
    lh = SM * 1.18
    KF = cap.get("kfont", KEY_SERIF)
    if key:
        ks = cap.get("size", 0)
        ktxt = " ".join(w for w, _ in key)
        if not ks:
            ks = 210 if KF == KEY_SERIF else 180
            while ks > 80 and text_w(font(KF, ks), ktxt) > maxw: ks -= 4
        kf = font(KF, ks)
        kw = text_w(kf, ktxt)
        kx = W / 2 - kw / 2
        # key appears with a quick settle
        on = key[0][1]
        a = ease((t - on) / 0.18)
        if a > 0:
            tmp = Image.new("L", (W, int(ks * 1.6)), 0)
            ImageDraw.Draw(tmp).text((kx, ks * 1.15), ktxt, font=kf, fill=255, anchor="ls", features=["lnum"])
            sc = 1.06 - 0.06 * a
            if abs(sc - 1) > 0.002:
                tw, th = tmp.size
                tmp = tmp.resize((int(tw * sc), int(th * sc)), Image.BILINEAR)
                tmp = tmp.crop(((tmp.size[0] - tw) // 2, (tmp.size[1] - th) // 2, (tmp.size[0] - tw) // 2 + tw, (tmp.size[1] - th) // 2 + th))
            alpha = tmp.point(lambda v: int(v * a))
            solid = Image.new("RGBA", tmp.size, col + (255,)); solid.putalpha(alpha)
            layer.alpha_composite(solid, (0, int(cy - ks * 1.15)))
        # pre: lines above, the last one ends near the right part of keyword
        plines = wrap(sf, pre, max(kw, 520)) if pre else []
        for i, ln in enumerate(plines):
            lw = text_w(sf, " ".join(w for w, _ in ln))
            y = cy - ks * 0.78 - (len(plines) - 1 - i) * lh
            x = min(kx + kw - lw, W - 90 - lw) if i == len(plines) - 1 else kx
            x = max(x, 90)
            draw_words(layer, sf, ln, x, y, t, col)
        qlines = wrap(sf, post, max(kw, 520)) if post else []
        for i, ln in enumerate(qlines):
            lw = text_w(sf, " ".join(w for w, _ in ln))
            y = cy + ks * 0.22 + (i + 1) * lh * 0.95
            x = max(90, min(kx + kw - lw, W - 90 - lw)) if i == 0 else max(90, kx + kw * 0.15)
            draw_words(layer, sf, ln, x, y, t, col)
    else:
        lines = wrap(sf, pre, 760)
        for i, ln in enumerate(lines):
            lw = text_w(sf, " ".join(w for w, _ in ln))
            y = cy + (i - (len(lines) - 1) / 2) * lh
            draw_words(layer, sf, ln, W / 2 - lw / 2, y, t, col)

# ---------------- gfx ----------------
def gfx_draw(layer, g, t, col, page_arr=None):
    d = ImageDraw.Draw(layer)
    k = g["k"]; t0 = g.get("t", 0); lt = t - t0
    if lt < 0: return
    if k == "ring":
        cx, cy, r = g.get("x", W / 2), g.get("y", 960), g.get("r", 300)
        p = ease_io(lt / g.get("dur", 1.2)) * g.get("to", 1.0)
        wd = g.get("w", 3)
        if g.get("full", True):
            d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=col + (60,), width=2)
        if p > 0.005:
            d.arc((cx - r, cy - r, cx + r, cy + r), -90, -90 + 360 * p, fill=col + (255,), width=wd)
            ang = math.radians(-90 + 360 * p)
            px, py = cx + r * math.cos(ang), cy + r * math.sin(ang)
            d.ellipse((px - 9, py - 9, px + 9, py + 9), fill=col + (255,))
    elif k == "counter":
        a, b = g["from"], g["to"]
        p = ease(lt / g.get("dur", 1.4))
        v = a + (b - a) * p
        s = f"{int(round(v)):,}".replace(",", ".")
        f = font(SERIF, g.get("size", 220))
        al = ease(lt / 0.2)
        d.text((g.get("x", W / 2), g.get("y", 900)), s + g.get("suf", ""), font=f, fill=col + (int(255 * al),), anchor="ms", features=["lnum"])
        if g.get("label"):
            d.text((g.get("x", W / 2), g.get("y", 900) + 80), g["label"], font=font(SANS, 46), fill=col + (int(220 * al),), anchor="ms")
    elif k == "label":
        al = ease(lt / 0.25)
        f = font(g.get("font", SANS), g.get("size", 40))
        d.text((g["x"], g["y"] + (1 - al) * 12), nfc(g["text"]), font=f, fill=col + (int(255 * al * g.get("op", 1)),), anchor=g.get("anchor", "ms"), features=["lnum"])
    elif k == "line":  # line drawn from p0 to p1
        p = ease_io(lt / g.get("dur", 0.6))
        x0, y0 = g["p0"]; x1, y1 = g["p1"]
        d.line((x0, y0, x0 + (x1 - x0) * p, y0 + (y1 - y0) * p), fill=col + (g.get("op", 200),), width=g.get("w", 2))
    elif k == "dot":
        al = ease(lt / 0.2); r = g.get("r", 10) * (0.6 + 0.4 * al)
        d.ellipse((g["x"] - r, g["y"] - r, g["x"] + r, g["y"] + r), fill=col + (int(255 * al),))
    elif k == "bars":  # vertical bars growing; values 0..1
        n = len(g["v"]); bw = g.get("bw", 70); gap = g.get("gap", 34)
        tot = n * bw + (n - 1) * gap; x = W / 2 - tot / 2; base = g.get("y", 1250); hmax = g.get("h", 520)
        for i, v in enumerate(g["v"]):
            p = ease((lt - i * g.get("stag", 0.08)) / 0.6)
            hh = hmax * v * p
            c = col if i not in g.get("hi", []) else g.get("hicol", col)
            d.rectangle((x, base - hh, x + bw, base), fill=tuple(c) + (255 if i in g.get("hi", []) else 150,))
            if g.get("lab"):
                d.text((x + bw / 2, base + 52), g["lab"][i], font=font(SANS, 34), fill=col + (int(200 * p),), anchor="ms")
            x += bw + gap
    elif k == "steps":  # footprints walking up the screen
        n = g.get("n", 10)
        for i in range(n):
            p = ease((lt - i * g.get("stag", 0.12)) / 0.25)
            if p <= 0: continue
            cx = W / 2 + (-50 if i % 2 == 0 else 50); cy = g.get("y0", 1600) - i * g.get("dy", 110)
            rx, ry = 26, 46
            d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=col + (int(230 * p),))
            d.ellipse((cx - 18, cy - ry - 34, cx + 18, cy - ry - 6), fill=col + (int(230 * p),))
    elif k == "orb":
        pass  # handled in page bg
    elif k == "check":  # list item with tick
        al = ease(lt / 0.3)
        x, y = g["x"], g["y"]
        d.ellipse((x - 26, y - 26, x + 26, y + 26), outline=col + (int(255 * al),), width=3)
        if lt > 0.15:
            q = ease((lt - 0.15) / 0.25)
            d.line((x - 12, y, x - 3, y + 10), fill=col + (int(255 * al),), width=4)
            d.line((x - 3, y + 10, x - 3 + 18 * q, y + 10 - 22 * q), fill=col + (int(255 * al),), width=4)
        d.text((x + 50, y + 14 + (1 - al) * 10), nfc(g["text"]), font=font(g.get("font", SANS), g.get("size", 46)), fill=col + (int(255 * al),), anchor="ls")
    elif k == "cross":
        al = ease(lt / 0.3); x, y, r = g["x"], g["y"], g.get("r", 60)
        q = ease(lt / 0.35)
        d.line((x - r, y - r, x - r + 2 * r * q, y - r + 2 * r * q), fill=tuple(g.get("c", col)) + (255,), width=g.get("w", 10))
        if lt > 0.2:
            q2 = ease((lt - 0.2) / 0.35)
            d.line((x + r, y - r, x + r - 2 * r * q2, y - r + 2 * r * q2), fill=tuple(g.get("c", col)) + (255,), width=g.get("w", 10))

ORB = None
def orb_img():
    global ORB
    if ORB is None:
        s = 900
        yy, xx = np.mgrid[0:s, 0:s].astype(np.float32)
        r = np.sqrt((xx - s / 2) ** 2 + (yy - s / 2) ** 2) / (s / 2)
        ORB = np.clip(1 - r, 0, 1) ** 2.2
    return ORB

# ---------------- shot rendering ----------------
def page_bg(kind, fi, t, shot):
    if kind in ("blue", "red"):
        f = np.empty((H, W, 3), np.float32); f[:] = BLUE; g_ = (1 - GRAD) / 0.10; f = f * (1 - g_ * 0.5) + np.array(BLUE2, np.float32) * g_ * 0.5
        if shot.get("glow"): f = add_orb(f, shot, t, (255, 255, 255), 0.35)
        return grain(f, fi, 7)
    if kind == "white":
        f = np.empty((H, W, 3), np.float32); f[:] = PAPER
        if shot.get("glow"): f = add_orb(f, shot, t, BLUE, 0.75)
        return grain(f, fi, 3)
    if kind == "black":
        f = np.empty((H, W, 3), np.float32); f[:] = INK
        if shot.get("glow"): f = add_orb(f, shot, t, BLUE, 0.8)
        return grain(f, fi, 5)

def add_orb(f, shot, t, col, strength):
    o = orb_img(); s = o.shape[0]
    gx, gy = shot.get("gx", W / 2), shot.get("gy", 960)
    sc = shot.get("gs", 1.0) * (1 + 0.04 * math.sin(t * 1.3))
    sz = int(s * sc); oo = np.asarray(Image.fromarray((o * 255).astype(np.uint8)).resize((sz, sz), Image.BILINEAR), np.float32) / 255
    x0, y0 = int(gx - sz / 2), int(gy - sz / 2)
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(W, x0 + sz), min(H, y0 + sz)
    m = oo[ya - y0:yb - y0, xa - x0:xb - x0][..., None] * strength
    f[ya:yb, xa:xb] = f[ya:yb, xa:xb] * (1 - m) + np.array(col, np.float32) * m
    return f

def render_piece(args):
    spec_path, idx = args
    spec = json.load(open(spec_path))
    piece = spec["_pieces"][idx]
    out = os.path.join(spec["_out"], f"seg_{idx:04d}.mp4")
    if os.path.exists(out) and not spec.get("_force"): return out
    t0, t1 = piece["t0"], piece["t1"]
    n = max(1, int(round(t1 * FPS)) - int(round(t0 * FPS)))
    f0 = int(round(t0 * FPS))
    sh = piece["shot"]; kind = sh["type"]
    caps = spec["_caps"]
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                            "-i", "-", "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    rd = None; card_rd = None
    foot = kind in ("coach", "bw", "duo", "dark", "cine")
    if foot:
        rd = Reader(piece["src"], n)
    card = sh.get("card")
    if card:
        cw, ch = card.get("w", 760), card.get("h", 1000)
        cw -= cw % 2; ch -= ch % 2
        card_rd = Reader(card["src"] + (t0 - sh["t"]), n, W, H)
    for i in range(n):
        fi = f0 + i; t = fi / FPS; lt = t - sh["t"]
        if foot:
            fr = rd.next()
            z0, z1 = piece.get("zoom", [1.0, 1.0])
            p = (t - t0) / max(1e-3, (t1 - t0))
            z = z0 + (z1 - z0) * p
            fx, fy = sh.get("focus", [0.6, 0.35])
            fr = zoom_frame(fr, z, fx, fy)
            look_k = {"coach": "cine", "cine": "cine"}.get(kind, kind)
            f = look(fr, look_k)
            f = grain(f, fi, 9 if look_k != "duo" else 7)
            txtcol = (255, 255, 255)
        else:
            f = page_bg(kind, fi, t, sh)
            txtcol = BLUE if kind == "white" else (255, 255, 255)
        img = Image.fromarray(f.astype(np.uint8)).convert("RGBA")
        if card_rd is not None:
            cf = card_rd.next()
            ccx, ccy = card.get("x", W / 2), card.get("y", 960)
            a = ease(lt / 0.35)
            cz = card.get("z", 1.4)
            fr2 = zoom_frame(cf, cz, *card.get("focus", [0.5, 0.4]))
            src_ratio = cw / ch
            # crop center region of frame to card ratio
            if src_ratio > W / H:
                bh = W / src_ratio; box = (0, (H - bh) * card.get("fy", 0.4), W, (H - bh) * card.get("fy", 0.4) + bh)
            else:
                bw_ = H * src_ratio; box = ((W - bw_) / 2, 0, (W + bw_) / 2, H)
            ci = Image.fromarray(look(fr2, card.get("look", "cine")).astype(np.uint8)).resize((cw, ch), Image.BILINEAR, box=box)
            sc = 0.94 + 0.06 * a + 0.02 * (lt / 3)
            ci = ci.resize((int(cw * sc), int(ch * sc)), Image.BILINEAR)
            bd = card.get("border", 6)
            fr_im = Image.new("RGBA", (ci.size[0] + 2 * bd, ci.size[1] + 2 * bd), (245, 245, 248, 255))
            fr_im.paste(ci, (bd, bd))
            if a < 1:
                al = fr_im.getchannel("A").point(lambda v: int(v * a)); fr_im.putalpha(al)
            img.alpha_composite(fr_im, (int(ccx - fr_im.size[0] / 2), int(ccy - fr_im.size[1] / 2 + (1 - a) * 40)))
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gcol = tuple(sh.get("gcol", txtcol))
        for g in sh.get("gfx", []):
            gg = dict(g); gg["t"] = sh["t"] + g.get("t", 0)
            gfx_draw(layer, gg, t, gcol)
        cy = sh.get("cy", 1380 if foot else 960)
        for c in caps:
            if c["t0"] <= t < c["t1"] and sh["t"] - 0.01 <= c["t0"] + 1e9:
                ccol = tuple(c.get("col", txtcol)) if not foot else (255, 255, 255)
                if c.get("col_page") and not foot: ccol = tuple(c["col_page"])
                cyy = c.get("cy", cy)
                if foot:  # soft shadow for legibility
                    sl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                    caption_layer(sl, c, t, (0, 0, 0), cyy + 3)
                    sl = sl.filter(ImageFilter.GaussianBlur(8))
                    a = np.asarray(sl).copy(); a[..., 3] = (a[..., 3] * 0.55).astype(np.uint8)
                    layer.alpha_composite(Image.fromarray(a))
                caption_layer(layer, c, t, ccol, cyy)
        img.alpha_composite(layer)
        # flash at shot start (optional)
        arr = np.asarray(img.convert("RGB"))
        if sh.get("flash") and lt < 0.12 and abs(t0 - sh["t"]) < 1e-6:
            arr = np.clip(arr.astype(np.float32) + 255 * (1 - lt / 0.12) * 0.8, 0, 255).astype(np.uint8)
        enc.stdin.write(arr.tobytes())
    enc.stdin.close(); enc.wait()
    if rd: rd.close()
    if card_rd: card_rd.close()
    return out

STOP = set("""thì là mà cái việc của mọi người có thể nó đấy để cho với trong một những các em chị anh ấy ta đó và nhưng rồi đã
sẽ được này nhé như thế khá rất cũng hơn không phải đúng lại ở từ đến bởi vì tại nè kiểu ví dụ hay hoặc nếu khi xong chứ còn thực
sự chất ra nào gì đâu vậy giờ bảo mới hết lên tầm khoảng ok đây nữa luôn chỉ cả mình nhá ạ hả nhỉ à ừ đi bị""".split())
def _auto_key(toks):
    best = None
    i = 0
    while i < len(toks):
        if norm(toks[i]) in STOP or not norm(toks[i]):
            i += 1; continue
        j = i
        while j < len(toks) and j - i < 3 and norm(toks[j]) not in STOP and norm(toks[j]): j += 1
        span = (i, j)
        if best is None or (j - i) >= (best[1] - best[0]): best = span
        i = j
    return best
def _split(toks, n=5):
    if not toks: return []
    k = math.ceil(len(toks) / n); sz = math.ceil(len(toks) / k)
    return [toks[i:i + sz] for i in range(0, len(toks), sz)]
def chunk_caps(caps):
    out = []; nk = 0
    for c in caps:
        txt = nfc(c["text"]); extra = {k: v for k, v in c.items() if k != "text"}
        if "/" in txt:
            for part in [x.strip() for x in txt.split("/") if x.strip()]:
                d = dict(extra); d["text"] = part
                if "*" in part:
                    nk += 1
                    kt = re.findall(r"\*([^*]+)\*", part)[0]
                    if kt.startswith("!"): d["text"] = part.replace("*!", "*"); d.setdefault("kfont", KEY_SANS)
                    d.setdefault("kfont", KEY_SANS if (nk % 3 == 0 or re.search(r"\d", kt)) else KEY_SERIF)
                out.append(d)
            continue
        parts = re.split(r"(\*[^*]+\*)", txt)
        toks = []
        for p in parts:
            for tok in p.strip("*").split(): toks.append((tok, p.startswith("*")))
        kidx = [i for i, (_, k) in enumerate(toks) if k]
        chunks = []
        if kidx:
            k0, k1 = kidx[0], kidx[-1] + 1
            pre, key, post = toks[:k0], toks[k0:k1], toks[k1:]
            pa = pre[-2:] if len(pre) > 2 else pre; pre_rest = pre[:len(pre) - len(pa)]
            pb = post[:2] if len(post) > 2 else post; post_rest = post[len(pb):]
            chunks += [[(w, False) for w, _ in ch] for ch in _split(pre_rest)]
            chunks.append(pa + key + pb)
            chunks += [[(w, False) for w, _ in ch] for ch in _split(post_rest)]
        else:
            chunks = _split(toks)
        for ch in chunks:
            words = [w for w, _ in ch]
            if not any(k for _, k in ch):
                sp = _auto_key(words)
                if sp: ch = [(w, sp[0] <= i < sp[1]) for i, (w, _) in enumerate(ch)]
            # rebuild text with *key*
            outt = []; inkey = False
            for w, k in ch:
                if k and not inkey: outt.append("*" + w); inkey = True
                elif k: outt.append(w)
                else:
                    if inkey: outt[-1] += "*"; inkey = False
                    outt.append(w)
            if inkey: outt[-1] += "*"
            d = dict(extra); d["text"] = " ".join(outt)
            if any(k for _, k in ch):
                nk += 1
                kt = "".join(w for w, k in ch if k)
                d.setdefault("kfont", KEY_SANS if (nk % 3 == 0 or re.search(r"\d", kt)) else KEY_SERIF)
            out.append(d)
    return out

# ---------------- spec prep ----------------
def build(spec_path, outdir, workers=4, only=None):
    spec = json.load(open(spec_path))
    words = json.load(open(spec["words"]))
    allw = [w for s in words for w in s["words"]]
    cuts = spec["cuts"]
    # out-time map
    segs = []; acc = 0
    for a, b in cuts:
        segs.append((acc, acc + (b - a), a)); acc += b - a
    total = acc
    def src_of(t):
        for o0, o1, a in segs:
            if o0 - 1e-6 <= t < o1: return a + (t - o0)
        return segs[-1][2] + (t - segs[-1][0])
    # words in cuts, remapped
    rw = []
    for o0, o1, a in segs:
        b = a + (o1 - o0)
        for w in allw:
            mid = (w["s"] + w["e"]) / 2
            if a <= mid < b:
                rw.append({"w": nfc(w["w"].strip()), "s": max(o0, w["s"] - a + o0), "e": min(o1, w["e"] - a + o0)})
    # captions: split into short chunks (2-5 words), each with one big keyword
    spec["caps"] = chunk_caps(spec["caps"])
    caps = []
    ctoks = []
    for ci, c in enumerate(spec["caps"]):
        txt = nfc(c["text"])
        parts = re.split(r"(\*[^*]+\*)", txt)
        for p in parts:
            iskey = p.startswith("*")
            for tok in p.strip("*").split():
                ctoks.append((ci, tok, iskey))
    A = [norm(t[1]) for t in ctoks]; B = [norm(w["w"]) for w in rw]
    sm = difflib.SequenceMatcher(None, A, B, autojunk=False)
    times = [None] * len(ctoks)
    for blk in sm.get_matching_blocks():
        for k in range(blk.size): times[blk.a + k] = rw[blk.b + k]["s"]
    # fill gaps by interpolation
    known = [i for i, v in enumerate(times) if v is not None]
    for i in range(len(times)):
        if times[i] is None:
            prev = max([k for k in known if k < i], default=None); nxt = min([k for k in known if k > i], default=None)
            if prev is not None and nxt is not None:
                times[i] = times[prev] + (times[nxt] - times[prev]) * (i - prev) / (nxt - prev)
            elif prev is not None: times[i] = times[prev] + 0.25 * (i - prev)
            elif nxt is not None: times[i] = max(0, times[nxt] - 0.25 * (nxt - i))
            else: times[i] = 0
    unmatched = sum(1 for i in range(len(ctoks)) if i not in set(known))
    for ci, c in enumerate(spec["caps"]):
        toks = [(t[1], times[i], t[2]) for i, t in enumerate(ctoks) if t[0] == ci]
        if not toks: continue
        pre, key, post = [], [], []
        for w, tm, k in toks:
            if k: key.append((w, tm))
            elif key: post.append((w, tm))
            else: pre.append((w, tm))
        cc = {k: v for k, v in c.items() if k != "text"}
        cc.update(pre=pre, key=key, post=post, t0=toks[0][1] - 0.05)
        caps.append(cc)
    for i, c in enumerate(caps):
        last = max(tm for _, tm in c["pre"] + c["key"] + c["post"])
        nxt = caps[i + 1]["t0"] if i + 1 < len(caps) else total
        c["t1"] = min(nxt, c.get("hold", last + 1.2)) if "hold" not in c else c["t0"] + c["hold"]
        c["t1"] = min(c["t1"], nxt)
    # shots -> pieces (split at cut boundaries for synced footage)
    def out_of(src):
        for o0, o1, a in segs:
            if a - 1e-6 <= src < a + (o1 - o0) + 1e-6: return o0 + (src - a)
        # in a removed gap: snap to next segment start
        for o0, o1, a in segs:
            if a > src: return o0
        return total
    shots = spec["shots"]
    for sh in shots:
        if "s" in sh: sh["t"] = round(out_of(sh["s"]), 3)
        if sh.get("card") and sh["card"].get("sync"): sh["card"]["src"] = src_of(sh["t"] + 1e-4)
    shots.sort(key=lambda x: x["t"])
    shots[0]["t"] = 0.0
    gap_at = {}
    for k in range(1, len(segs)):
        gap_at[round(segs[k][0], 4)] = segs[k][2] - (segs[k - 1][2] + segs[k - 1][1] - segs[k - 1][0])
    pieces = []
    bounds = [o0 for o0, _, _ in segs][1:]
    for i, sh in enumerate(shots):
        s0 = sh["t"]; s1 = shots[i + 1]["t"] if i + 1 < len(shots) else total
        sh["end"] = s1
        cutsin = [b for b in bounds if s0 + 0.05 < b < s1 - 0.05] if sh.get("sync", sh["type"] in ("coach",)) else []
        edges = [s0] + cutsin + [s1]
        zbase = sh.get("zoom", [1.0, 1.06])
        state = 0
        for j in range(len(edges) - 1):
            if j > 0 and gap_at.get(round(edges[j], 4), 0) > spec.get("punch_gap", 0.7): state ^= 1
            a, b = edges[j], edges[j + 1]
            if sh["type"] in ("coach", "bw", "duo", "dark", "cine"):
                if sh.get("sync", sh["type"] == "coach"): src = src_of(a + 1e-4)
                else: src = sh["src"] + (a - s0)
            else: src = None
            z = zbase
            if state: z = [zbase[0] * 1.14, zbase[1] * 1.14]  # punch-in on bigger jump cuts
            pieces.append({"t0": a, "t1": b, "shot": sh, "src": src, "zoom": z})
    spec["_pieces"] = pieces; spec["_caps"] = caps; spec["_out"] = outdir; spec["_total"] = total
    os.makedirs(outdir, exist_ok=True)
    sp2 = os.path.join(outdir, "spec.resolved.json"); json.dump(spec, open(sp2, "w"), ensure_ascii=False, indent=1)
    print(f"total {total:.2f}s, {len(pieces)} pieces, {len(caps)} captions, unmatched caption tokens {unmatched}/{len(ctoks)}", flush=True)
    idxs = list(range(len(pieces))) if only is None else only
    with Pool(workers) as pool:
        segfiles = pool.map(render_piece, [(sp2, i) for i in idxs])
    return spec, segs, total

if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
