import json, subprocess, sys
ts = [float(x) for x in sys.argv[1].split(",")]
br = json.load(open("build/broll.json"))
for i, t in enumerate(ts):
    src, ss = "build/plate.mp4", t
    for b in br:
        if b["t0"] <= t < b["t0"] + b["n"] / 30:
            src, ss = b["file"], t - b["t0"]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ss:.3f}", "-i", src, "-frames:v", "1", f"build/snap/{i:02d}.png"], check=True)
