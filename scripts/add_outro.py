#!/usr/bin/env python3
"""Append the channel's outro to finished reels: "<name>.mp4" -> "<name> (outro).mp4" next to it.

    add_outro.py <final.mp4> [<final.mp4> ...] [--outro FILE] [--gain-db N] [--out DIR]
    add_outro.py --check                         # print the configured outro and its facts

The outro is set once in library/outro/outro.json ({"enabled": true, "file": "<clip in library/outro>", "gain_db": 0}).
`finals.py render` calls this by itself after the final (and its no-music version) whenever the config is enabled, so
every reel ends on the outro without anyone remembering it; the "(outro)" file is the one to post.

The final itself stays as rendered (QA, the no-music pass and deliver all compare it to the composition, so it must keep
the composition's length). The outro is conformed to the reel (size, 30 fps, SAR 1, 48 kHz stereo), joined with a hard
cut and encoded once with the delivery settings of finals.py (H.264 High@4.2, CRF 16 capped at 20 Mbit/s, BT.709, AAC 256k).
Its own sound is kept at its own level (gain_db 0): a logo sting ends quieter than the voice by design.
"""
import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
CFG = os.path.join(SKILL, "library", "outro", "outro.json")
sys.path.insert(0, HERE)
from x264 import THREADS as X264_THREADS  # noqa: E402

H264 = ["-c:v", "libx264", "-threads", X264_THREADS, "-preset", "slow", "-crf", "16", "-maxrate", "20M", "-bufsize", "40M",
        "-profile:v", "high", "-level", "4.2", "-g", "60",
        "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv",
        "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "2", "-movflags", "+faststart"]


def config():
    """{"enabled", "file" (absolute), "gain_db"} or None when no outro is set up"""
    if not os.path.exists(CFG):
        return None
    c = json.load(open(CFG, encoding="utf-8"))
    c["file"] = os.path.join(os.path.dirname(CFG), c["file"]) if not os.path.isabs(c["file"]) else c["file"]
    return c


def probe(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height:format=duration",
                          "-of", "json", p], capture_output=True, text=True, check=True).stdout
    d = json.loads(out)
    v = next(s for s in d["streams"] if s["codec_type"] == "video")
    return {"w": v["width"], "h": v["height"], "dur": float(d["format"]["duration"]),
            "audio": any(s["codec_type"] == "audio" for s in d["streams"])}


def outro_name(src):
    return src[:-4] + " (outro).mp4"


def append(src, dst=None, outro=None, gain_db=None):
    """src reel + outro -> dst (default "<src> (outro).mp4"); returns dst"""
    c = config() or {}
    outro = outro or c.get("file")
    if not outro or not os.path.exists(outro):
        raise SystemExit(f"no outro clip ({outro or 'set library/outro/outro.json'})")
    gain = c.get("gain_db", 0) if gain_db is None else gain_db
    dst = dst or outro_name(src)
    a, o = probe(src), probe(outro)
    W, H = a["w"], a["h"]
    conform = (f"scale={W}:{H}:force_original_aspect_ratio=decrease:flags=lanczos,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:black,"
               f"fps=30,setsar=1,format=yuv420p")
    va = "[0:v]fps=30,setsar=1,format=yuv420p[v0];"
    aa = "[0:a]aresample=48000,aformat=channel_layouts=stereo[a0];" if a["audio"] else \
        f"anullsrc=r=48000:cl=stereo,atrim=0:{a['dur']:.3f}[a0];"
    ob = (f"[1:a]aresample=48000,aformat=channel_layouts=stereo,volume={gain}dB,apad,atrim=0:{o['dur']:.3f}[a1];" if o["audio"]
          else f"anullsrc=r=48000:cl=stereo,atrim=0:{o['dur']:.3f}[a1];")
    fc = va + f"[1:v]{conform}[v1];" + aa + ob + "[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]"
    tmp = dst + ".part.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-i", outro, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
                    *H264, tmp], check=True)
    os.replace(tmp, dst)
    got = probe(dst)["dur"]
    want = a["dur"] + o["dur"]
    if abs(got - want) > 0.15:
        raise SystemExit(f"outro join: {got:.2f} s, expected {want:.2f} s ({dst})")
    print(f"outro {os.path.basename(src)} + {os.path.basename(outro)} ({o['dur']:.1f} s) -> {dst} ({got:.2f} s)")
    return dst


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("finals", nargs="*")
    ap.add_argument("--outro", help="outro clip (default: library/outro/outro.json)")
    ap.add_argument("--gain-db", type=float, help="gain on the outro's own sound (default: the config's, 0)")
    ap.add_argument("--out", help="folder for the outro versions (default: next to each final)")
    ap.add_argument("--check", action="store_true", help="print the configured outro")
    a = ap.parse_args()
    if a.check or not a.finals:
        c = config()
        if not c:
            return print(f"no outro configured ({CFG} missing)")
        f = probe(c["file"]) if os.path.exists(c["file"]) else None
        return print(f"outro {'ENABLED' if c.get('enabled') else 'disabled'}: {c['file']} "
                     + (f"{f['w']}x{f['h']} {f['dur']:.2f} s, sound {'yes' if f['audio'] else 'no'}" if f else "(file missing)")
                     + f", gain {c.get('gain_db', 0)} dB")
    for f in a.finals:
        dst = os.path.join(a.out, os.path.basename(outro_name(f))) if a.out else None
        append(f, dst, a.outro, a.gain_db)


if __name__ == "__main__":
    main()
