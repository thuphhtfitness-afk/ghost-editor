"""Render a code-drawn anatomy sheet with the xilo-opus-video renderer and crop it into 1060x640 cards (2 per row).
usage: anatomy_render.py <out dir> [sheet.html name1,name2,...]   (needs ~/.claude/skills/xilo-opus-video and Playwright)"""
import os, sys, subprocess
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
R = os.path.expanduser("~/.claude/skills/xilo-opus-video/scripts/render.py")
SHEETS = {"anatomy.html": ["arch_normal", "arch_flat", "heel_axis", "legs_straight", "legs_x", "knee_mcl", "knee_inside"],
          "heels.html": ["calf_heel", "hip_flexor", "pelvis_tilt", "lordosis", "back_chain"]}
html = sys.argv[2] if len(sys.argv) > 2 else "anatomy.html"
names = SHEETS[html]
rows = (len(names) + 1) // 2
sheet = os.path.join(OUT, "_sheet_" + html.replace(".html", "") + ".png")
env = {**os.environ, "PLAYWRIGHT_BROWSERS_PATH": os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers")}
subprocess.run([sys.executable, R, os.path.join(HERE, html), sheet, "--still", "0", "--size", f"2120x{rows * 640}"], check=True, env=env)
im = Image.open(sheet).convert("RGBA")
for i, n in enumerate(names):
    x, y = (i % 2) * 1060, (i // 2) * 640
    im.crop((x, y, x + 1060, y + 640)).save(os.path.join(OUT, n + ".png"))
print("cards ->", OUT)
