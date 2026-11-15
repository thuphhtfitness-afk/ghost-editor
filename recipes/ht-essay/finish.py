"""finish.py spec.json outdir final.mp4 : concat video segments, build voice from cuts, music bed, mix."""
import json, sys, os, subprocess, glob
spec_p, outdir, final = sys.argv[1:4]
S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(S, "dl", "src.mp4")
spec = json.load(open(spec_p))
segs = sorted(glob.glob(os.path.join(outdir, "seg_*.mp4")))
with open(os.path.join(outdir, "list.txt"), "w") as f:
    for s in segs: f.write(f"file '{os.path.abspath(s)}'\n")
v = os.path.join(outdir, "video.mp4")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(outdir, "list.txt"), "-c", "copy", v], check=True)
# voice
parts = []; fc = []
for i, (a, b) in enumerate(spec["cuts"]):
    fc.append(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={b - a - 0.03:.3f}:d=0.03[a{i}]")
fc.append("".join(f"[a{i}]" for i in range(len(spec["cuts"]))) + f"concat=n={len(spec['cuts'])}:v=0:a=1[cat]")
fc.append("[cat]highpass=f=80,afftdn=nr=10:nf=-40,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,loudnorm=I=-15:TP=-1.5:LRA=9[vo]")
voice = os.path.join(outdir, "voice.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-filter_complex", ";".join(fc), "-map", "[vo]", "-ac", "2", "-ar", "48000", voice], check=True)
dur = sum(b - a for a, b in spec["cuts"])
mus = os.path.join(outdir, "music.wav")
subprocess.run(["python3", "-I", os.path.join(S, "scripts", "music.py"), mus, str(dur + 1), str(spec.get("seed", 1))], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", v, "-i", voice, "-i", mus, "-filter_complex",
                "[1:a]asplit[v1][v2];[2:a]volume=0.16[m];[m][v1]sidechaincompress=threshold=0.05:ratio=4:attack=20:release=400[md];"
                "[v2][md]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.89[a]",
                "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", final], check=True)
print(final, subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", final], capture_output=True, text=True).stdout.strip())
