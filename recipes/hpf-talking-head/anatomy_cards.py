"""Anatomy cards for HPF talking head (white card, marker annotations in Vietnamese, source credit on the card).
Pictures: public-domain plates (Gray's Anatomy 1918 via Wikimedia Commons) or a drawn schematic when no plate fits.
Each card is a PNG for beats.PANELS. usage: anatomy_cards.py <anat dir> <out dir>"""
import sys, os, math
from PIL import Image, ImageDraw, ImageFilter, ImageFont

A, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
FD = "/root/.fonts/"
def font(n, s, w=None):
    f = ImageFont.truetype(FD + n, s)
    if w:
        try: f.set_variation_by_axes([w])
        except Exception: pass
    return f
HAND = font("PatrickHand-Regular.ttf", 58)
HAND_S = font("PatrickHand-Regular.ttf", 44)
KICK = font("BeVietnamPro-ExtraBold.ttf", 30)
CRED = font("BeVietnamPro-Medium.ttf", 20)
INK = (29, 53, 87, 255); RED = (220, 45, 55, 255); GREEN = (40, 160, 80, 255); GREY = (120, 124, 130, 255)
W, H = 1000, 580


def card(kicker, credit=None):
    c = Image.new("RGBA", (W + 60, H + 60))
    sh = Image.new("RGBA", c.size); ImageDraw.Draw(sh).rounded_rectangle((30, 42, 30 + W, 42 + H), 30, fill=(0, 0, 0, 110))
    c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle((30, 30, 30 + W, 30 + H), 30, fill=(252, 252, 250, 255), outline=(210, 212, 216, 255), width=4)
    bb = KICK.getbbox(kicker); d.rounded_rectangle((60, 54, 60 + bb[2] + 36, 54 + bb[3] + 22), 8, fill=(246, 234, 170, 255))
    d.text((78, 63), kicker, font=KICK, fill=(28, 24, 20, 255))
    if credit:
        cb = CRED.getbbox(credit); d.text((30 + W - cb[2] - 26, 30 + H - 36), credit, font=CRED, fill=GREY)
    return c, d


def place(c, img, box):
    """fit img into box (x0, y0, x1, y1) on the card, return the pixel transform"""
    x0, y0, x1, y1 = box
    s = min((x1 - x0) / img.width, (y1 - y0) / img.height)
    im = img.resize((int(img.width * s), int(img.height * s)), Image.LANCZOS)
    ox, oy = x0 + (x1 - x0 - im.width) // 2, y0 + (y1 - y0 - im.height) // 2
    c.alpha_composite(im.convert("RGBA"), (ox, oy))
    return lambda u, v: (ox + u * im.width, oy + v * im.height)


def curve(d, pts, fill, width=9):
    d.line(pts, fill=fill, width=width, joint="curve")


def bezier(p0, p1, p2, n=40):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in [i / n for i in range(n + 1)]]


def label(d, xy, txt, f=HAND, fill=INK, anchor="mm"):
    d.text(xy, txt, font=f, fill=fill, anchor=anchor)


def label_tick(d, xy, txt, f, fill, ok):
    """centred label with its tick placed just left of the text, never on it"""
    w = f.getbbox(txt)[2]
    label(d, xy, txt, f, fill)
    tick(d, xy[0] - w / 2 - 36, xy[1] + 4, ok)


def tick(d, x, y, ok):
    d.ellipse((x - 26, y - 26, x + 26, y + 26), fill=GREEN if ok else RED)
    if ok: d.line((x - 12, y + 1, x - 3, y + 11, x + 13, y - 10), fill=(255, 255, 255), width=6, joint="curve")
    else: d.line((x - 10, y - 10, x + 10, y + 10), fill=(255, 255, 255), width=6); d.line((x + 10, y - 10, x - 10, y + 10), fill=(255, 255, 255), width=6)


# 1a. foot skeleton with the normal arch (Gray 290)
foot = Image.open(f"{A}/Gray290.png").convert("RGBA")
c, d = card("VÒM BÀN CHÂN", "Gray's Anatomy (1918), public domain")
P = place(c, foot, (70, 120, 990, 500))
curve(d, bezier(P(0.08, 0.97), P(0.46, 0.52), P(0.80, 0.93)), GREEN, 10)
label(d, (P(0.47, 0.70)[0], P(0.47, 0.70)[1] + 150), "vòm bàn chân", fill=GREEN)
c.save(f"{OUT}/arch_normal.png")

# 1b. normal arch vs flat foot (photo, PD)
flat = Image.open(f"{A}/Flatfoot.jpg").convert("RGBA")
c, d = card("BÀN CHÂN BẸT", "Gray's Anatomy (1918); Flatfoot.jpg, Wikimedia Commons, public domain")
P1 = place(c, foot, (60, 150, 520, 430))
curve(d, bezier(P1(0.08, 0.97), P1(0.46, 0.52), P1(0.80, 0.93)), GREEN, 8)
label_tick(d, (300, 480), "bình thường: có vòm", HAND_S, GREEN, True)
P2 = place(c, flat, (545, 140, 985, 430))
curve(d, [P2(0.06, 0.86), P2(0.95, 0.84)], RED, 8)
label_tick(d, (785, 480), "bẹt: vòm sập xuống", HAND_S, RED, False)
c.save(f"{OUT}/arch_flat.png")


# 2. heel axis from behind (drawn schematic)
def heel(d, cx, base, tilt, col):
    a = math.radians(tilt)
    top = (cx + math.sin(a) * 250, base - math.cos(a) * 250)
    d.line((cx - 34, base - 250, cx - 26, base - 60), fill=(150, 150, 150, 255), width=10)       # lower leg outline
    d.line((cx + 34, base - 250, cx + 26, base - 60), fill=(150, 150, 150, 255), width=10)
    hx = cx + math.sin(a) * 40
    d.ellipse((hx - 62, base - 70, hx + 62, base + 40), outline=(150, 150, 150, 255), width=10)  # heel
    d.line((cx - 120, base + 52, cx + 120, base + 52), fill=(180, 180, 180, 255), width=6)        # floor
    d.line((cx + math.sin(a) * -60, base + 40 + math.cos(a) * 20, top[0], top[1]), fill=col, width=9)
c, d = card("TRỤC GÓT CHÂN (NHÌN TỪ SAU)")
heel(d, 300, 420, 0, GREEN); heel(d, 740, 420, -16, RED)
label_tick(d, (300, 520), "thẳng", HAND, GREEN, True)
label_tick(d, (760, 520), "đổ vào trong", HAND, RED, False)
c.save(f"{OUT}/heel_axis.png")


# 3. legs straight vs knock-knee (drawn schematic, front view)
def legs(d, cx, knock, col):
    hipL, hipR = (cx - 70, 150), (cx + 70, 150)
    kin = 38 if knock else 0
    kL, kR = (cx - 62 + kin, 320), (cx + 62 - kin, 320)
    aL, aR = (cx - 66, 480), (cx + 66, 480)
    for h, k, a in ((hipL, kL, aL), (hipR, kR, aR)):
        d.line((h, k), fill=(120, 120, 120, 255), width=14); d.line((k, a), fill=(120, 120, 120, 255), width=14)
        d.ellipse((k[0] - 18, k[1] - 18, k[0] + 18, k[1] + 18), fill=col)
        d.line((a[0] - 30 if a[0] < cx else a[0] - 10, a[1] + 12, a[0] + 10 if a[0] < cx else a[0] + 30, a[1] + 12), fill=(120, 120, 120, 255), width=12)
    d.ellipse((cx - 90, 120, cx + 90, 175), outline=(170, 170, 170, 255), width=8)               # pelvis
c, d = card("KHỚP GỐI (NHÌN TỪ TRƯỚC)")
legs(d, 300, False, GREEN); label_tick(d, (300, 535), "thẳng", HAND, GREEN, True)
c.save(f"{OUT}/legs_straight.png")
legs(d, 740, True, RED); label_tick(d, (760, 535), "chụm vào: chữ X", HAND, RED, False)
c.save(f"{OUT}/legs_x.png")

# 4. knee ligament under load (Gray 345, medial collateral highlighted)
knee = Image.open(f"{A}/Gray345.png").convert("RGBA")
c, d = card("DÂY CHẰNG BÊN TRONG GỐI", "Gray's Anatomy (1918), public domain")
P = place(c, knee, (330, 110, 640, 590))
hl = Image.new("RGBA", c.size); ImageDraw.Draw(hl).polygon([P(0.86, 0.40), P(0.99, 0.44), P(0.87, 0.98), P(0.70, 0.96)], fill=(220, 45, 55, 120))
c.alpha_composite(hl.filter(ImageFilter.GaussianBlur(3)))
d = ImageDraw.Draw(c)
tx, ty = P(0.95, 0.62)
d.line((tx + 18, ty, 730, ty - 40), fill=RED, width=7)
label(d, (845, ty - 80), "dây chằng", HAND, RED); label(d, (845, ty - 25), "bên này", HAND, RED)
label(d, (845, ty + 50), "chịu áp lực", HAND_S, INK)
c.save(f"{OUT}/knee_mcl.png")

# 5. ligaments around the knee (Gray 347, inside view)
k2 = Image.open(f"{A}/Gray347.png").convert("RGBA")
c, d = card("DÂY CHẰNG QUANH KHỚP GỐI", "Gray's Anatomy (1918), public domain")
P = place(c, k2, (300, 110, 700, 590))
hl = Image.new("RGBA", c.size); hd = ImageDraw.Draw(hl)
for (u, v) in ((0.48, 0.42), (0.53, 0.55)):
    x, y = P(u, v); hd.ellipse((x - 40, y - 60, x + 40, y + 60), fill=(220, 45, 55, 90))
c.alpha_composite(hl.filter(ImageFilter.GaussianBlur(8)))
d = ImageDraw.Draw(c)
label(d, (160, 330), "ảnh hưởng", HAND_S, INK); label(d, (160, 380), "lâu dài", HAND_S, RED)
c.save(f"{OUT}/knee_inside.png")
print("cards ->", OUT, sorted(os.listdir(OUT)))
