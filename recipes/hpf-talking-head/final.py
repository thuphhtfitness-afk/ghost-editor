"""Compose the reel: plate (+ held tail) + cảnh trám layers + overlay RGBA stream + voice + ducked music bed + SFX.
usage: final.py OUT.mp4 [--bed audio/bed.wav] [--bed-db -17]"""
import json, subprocess, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
S = os.environ.get("GHOST", os.path.abspath(os.path.join(HERE, "..", "..")))
out = sys.argv[1]
bed = sys.argv[sys.argv.index("--bed") + 1] if "--bed" in sys.argv else "audio/bed.wav"
CRF = int(sys.argv[sys.argv.index("--crf") + 1]) if "--crf" in sys.argv else 15
bed_db = float(sys.argv[sys.argv.index("--bed-db") + 1]) if "--bed-db" in sys.argv else -17
os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
ev = json.loads(subprocess.run([sys.executable, f"{HERE}/overlay.py", "--events"], capture_output=True, text=True, check=True).stdout)
END = ev["end"]
br = json.load(open("build/broll.json"))

inp = ["-i", "build/plate.mp4", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", "1080x1920", "-r", "30", "-i", "-",
       "-i", "build/voice_raw.wav", "-i", bed]
k = 4
fv, fa = [], []
fv.append(f"[0:v]tpad=stop_mode=clone:stop_duration={max(1.0, END - ev['total'] / 30 + 0.5):.2f}[p0]")   # held tail covers an outro too
last = "p0"
for i, b in enumerate(br):
    inp += ["-i", b["file"]]
    t0, t1 = b["t0"], b["t0"] + b["n"] / 30
    fv.append(f"[{k}:v]setpts=PTS-STARTPTS+{t0:.6f}/TB[b{i}]")
    fv.append(f"[{last}][b{i}]overlay=0:0:enable='between(t,{t0:.4f},{t1 - 0.001:.4f})':eof_action=pass[p{i + 1}]")
    last = f"p{i + 1}"; k += 1
fv.append(f"[{last}][1:v]overlay=0:0:format=auto,trim=duration={END:.4f},format=yuv420p[v]")

fa.append("[2:a]aformat=sample_rates=48000:channel_layouts=mono,highpass=f=80,"
          "acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120,apad,asplit=2[vo][sc]")
fa.append(f"[3:a]aformat=sample_rates=48000:channel_layouts=mono,volume={bed_db}dB[bd0]")
fa.append("[bd0][sc]sidechaincompress=threshold=0.015:ratio=6:attack=25:release=450:makeup=1[bd]")
mix = ["[vo]", "[bd]"]
for i, (t, name, db) in enumerate(ev["sfx"]):
    f = "audio/click.wav" if name == "@click" else f"{S}/library/sfx/{name}.wav"
    inp += ["-i", f]
    fa.append(f"[{k}:a]aformat=sample_rates=48000:channel_layouts=mono,volume={db}dB,adelay={int(t * 1000)}[s{i}]")
    mix.append(f"[s{i}]"); k += 1
fa.append("".join(mix) + f"amix=inputs={len(mix)}:normalize=0:duration=first,atrim=duration={END:.4f},"
          "afade=t=out:st=" + f"{END - 0.5:.3f}" + ":d=0.5,loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000[a]")

cmd = ["ffmpeg", "-v", "error", "-stats", "-y"] + inp + ["-filter_complex", ";".join(fv + fa), "-map", "[v]", "-map", "[a]",
       "-c:v", "libx264", "-preset", "slow", "-crf", str(CRF), "-profile:v", "high", "-level", "4.2", "-maxrate", "20M",
       "-bufsize", "30M", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
       "-movflags", "+faststart", "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "2", out]
gen = subprocess.Popen([sys.executable, f"{HERE}/overlay.py", "--frames"], stdout=subprocess.PIPE)
r = subprocess.run(cmd, stdin=gen.stdout)
gen.wait()
sys.exit(r.returncode)
