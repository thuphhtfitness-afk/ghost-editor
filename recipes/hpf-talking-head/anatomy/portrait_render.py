"""Render a portrait anatomy sheet (cards 840x1560 px in one row) twice: plain muscles and highlighted muscles, and crop
each card into <name>.png and <name>_hot.png for the zoom-and-pulse panels (beats.ZPANELS).
usage: portrait_render.py <out dir> [heels_portrait.html]"""
import os, sys, subprocess
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
html = sys.argv[2] if len(sys.argv) > 2 else "heels_portrait.html"
NAMES = {"heels_portrait.html": ["p_calf", "p_hip", "p_pelvis", "p_lordosis", "p_chain"]}[html]
R = os.path.expanduser("~/.claude/skills/xilo-opus-video/scripts/render.py")
env = {**os.environ, "PLAYWRIGHT_BROWSERS_PATH": os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers")}
src = open(os.path.join(HERE, html)).read()
first = src.split("\n")[[i for i, l in enumerate(src.split("\n")) if "window.HOT =" in l][0]]
for mode, val in (("plain", "false"), ("hot", "true")):
    tmp = os.path.join(HERE, f"_{mode}_{html}")
    open(tmp, "w").write(src.replace(first, f"<script>window.HOT = {val};</script>"))
    sheet = os.path.join(OUT, f"_sheet_{mode}.png")
    subprocess.run([sys.executable, R, tmp, sheet, "--still", "0", "--size", f"{840 * len(NAMES)}x1560"], check=True, env=env)
    os.remove(tmp)
    im = Image.open(sheet).convert("RGBA")
    for i, n in enumerate(NAMES):
        im.crop((i * 840, 0, i * 840 + 840, 1560)).save(os.path.join(OUT, n + ("_hot" if mode == "hot" else "") + ".png"))
print("portrait cards ->", OUT)
