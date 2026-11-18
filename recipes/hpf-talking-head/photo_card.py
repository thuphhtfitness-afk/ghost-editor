"""Blank white card (same frame as the anatomy cards) for moving cut-out photos. usage: photo_card.py out.png "KICKER" """
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont
out, kicker = sys.argv[1], sys.argv[2]
F = ImageFont.truetype("/root/.fonts/Montserrat%5Bwght%5D.ttf", 28); F.set_variation_by_axes([800])
c = Image.new("RGBA", (1060, 640)); sh = Image.new("RGBA", c.size)
ImageDraw.Draw(sh).rounded_rectangle((30, 42, 1030, 622), 30, fill=(0, 0, 0, 110)); c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
d = ImageDraw.Draw(c); d.rounded_rectangle((30, 30, 1030, 610), 30, fill=(252, 252, 250, 255), outline=(212, 214, 218, 255), width=4)
bb = F.getbbox(kicker); d.rounded_rectangle((60, 54, 60 + bb[2] + 36, 104), 8, fill=(246, 234, 170, 255))
d.text((78, 79), kicker, font=F, fill=(28, 24, 20, 255), anchor="lm"); c.save(out)
