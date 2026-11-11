import math, random, sys
from PIL import Image, ImageDraw, ImageFilter
W, H, FPS = 1080, 1920, 30
out = sys.argv[1]
random.seed(7)
cx, cy = 790, 560  # impact point: upper right, away from the face (x 190-570)
# radial cracks: jagged polylines from the impact point
rays = []
for i in range(17):
    a = i / 17 * 2 * math.pi + random.uniform(-0.15, 0.15)
    L = random.uniform(700, 1500)
    pts, r, x, y = [(cx, cy)], 0, cx, cy
    while r < L:
        step = random.uniform(40, 110); r += step
        a += random.uniform(-0.22, 0.22)
        x, y = x + step * math.cos(a), y + step * math.sin(a)
        pts.append((x, y))
    rays.append(pts)
# concentric rings: broken arcs joining neighbouring rays
rings = [70, 150, 260, 400]
def ray_point(pts, d):
    acc = 0
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        seg = math.hypot(x1 - x0, y1 - y0)
        if acc + seg >= d:
            t = (d - acc) / seg; return (x0 + t * (x1 - x0), y0 + t * (y1 - y0))
        acc += seg
    return None
def frame(grow, alpha):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dark, light = ImageDraw.Draw(im), None
    maxd = grow * 1500
    for pts in rays:
        acc, keep = 0, [pts[0]]
        for p0, p1 in zip(pts, pts[1:]):
            seg = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
            if acc + seg > maxd:
                t = max(0, (maxd - acc) / seg); keep.append((p0[0] + t * (p1[0] - p0[0]), p0[1] + t * (p1[1] - p0[1]))); break
            keep.append(p1); acc += seg
        if len(keep) > 1:
            dark.line(keep, fill=(0, 0, 0, int(120 * alpha)), width=5)
            dark.line(keep, fill=(255, 255, 255, int(235 * alpha)), width=2)
    for rr in rings:
        if rr > maxd: continue
        for k in range(len(rays)):
            if random.Random(rr * 31 + k).random() < 0.35: continue
            p, q = ray_point(rays[k], rr * random.Random(k + rr).uniform(0.85, 1.15)), ray_point(rays[(k + 1) % len(rays)], rr * random.Random(k * 7 + rr).uniform(0.85, 1.15))
            if p and q:
                dark.line([p, q], fill=(0, 0, 0, int(100 * alpha)), width=4)
                dark.line([p, q], fill=(255, 255, 255, int(200 * alpha)), width=2)
    # impact spot
    dark.ellipse([cx - 18, cy - 18, cx + 18, cy + 18], fill=(255, 255, 255, int(160 * alpha)))
    return im.filter(ImageFilter.GaussianBlur(0.6))
n = int(1.6 * FPS)
for f in range(n):
    t = f / FPS
    grow = min(1.0, (t / 0.14) ** 0.6)          # cracks race out in ~0.14 s
    alpha = 1.0 if t < 1.0 else max(0.0, 1 - (t - 1.0) / 0.6)
    im = frame(grow, alpha)
    if f < 2:  # impact flash
        fl = Image.new("RGBA", (W, H), (255, 255, 255, 110 if f == 0 else 45)); im = Image.alpha_composite(fl, im)
    im.save(f"{out}/c{f:03d}.png")
print("frames", n)
