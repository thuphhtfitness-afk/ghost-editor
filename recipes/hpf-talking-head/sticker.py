"""Paper cut-out sticker of a person (HPF talking head, ref: magazine cut-out collage):
person cut from the photo (rembg BiRefNet-portrait), face covered by a 3D emoji (privacy), white paper border, soft shadow.
usage: sticker.py photo.jpg out.png --face cx,cy,r --emoji smile --height 760 [--border 16]"""
import argparse, os
from PIL import Image, ImageFilter
ap = argparse.ArgumentParser()
ap.add_argument("photo"); ap.add_argument("out")
ap.add_argument("--face", action="append", default=[], help="cx,cy,r in photo pixels (repeat for several faces)")
ap.add_argument("--emoji", default="smile"); ap.add_argument("--height", type=int, default=760)
ap.add_argument("--border", type=int, default=16); ap.add_argument("--cut", help="existing cut-out PNG")
a = ap.parse_args()
HERE = os.path.dirname(os.path.abspath(__file__))
if a.cut:
    im = Image.open(a.cut).convert("RGBA")
else:
    from rembg import remove, new_session
    im = remove(Image.open(a.photo).convert("RGB"), session=new_session("birefnet-portrait")).convert("RGBA")
alpha = im.split()[3].point(lambda v: 255 if v > 128 else int(v * 1.6))
im.putalpha(alpha)
emo = Image.open(f"{HERE}/emoji/{a.emoji}.png").convert("RGBA")
for f in a.face:
    cx, cy, r = [float(x) for x in f.split(",")]
    sz = int(r * 2.55)
    e = emo.resize((sz, sz), Image.LANCZOS).rotate(-6, resample=Image.BICUBIC, expand=True)
    im.alpha_composite(e, (int(cx - e.width / 2), int(cy - e.height / 2 - r * 0.05)))
bb = im.split()[3].getbbox(); im = im.crop(bb)
s = a.height / im.height; im = im.resize((int(im.width * s), a.height), Image.LANCZOS)
pad = a.border * 2 + 30
canvas = Image.new("RGBA", (im.width + pad * 2, im.height + pad * 2)); canvas.alpha_composite(im, (pad, pad))
al = canvas.split()[3]
ring = al.filter(ImageFilter.MaxFilter(3))
for _ in range(a.border // 2):
    ring = ring.filter(ImageFilter.MaxFilter(5))
ring = ring.filter(ImageFilter.GaussianBlur(1.2)).point(lambda v: 255 if v > 90 else 0).filter(ImageFilter.GaussianBlur(0.8))
paper = Image.new("RGBA", canvas.size, (250, 248, 242, 0)); paper.putalpha(ring)
shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0)); shadow.putalpha(ring.point(lambda v: int(v * 0.45)))
shadow = shadow.filter(ImageFilter.GaussianBlur(10))
out = Image.new("RGBA", canvas.size); out.alpha_composite(shadow, (6, 12)); out.alpha_composite(paper); out.alpha_composite(canvas)
out.save(a.out); print(a.out, out.size)
