#!/usr/bin/env python3
"""Apply a patch made in the HPF Reel Fixer page to a reel spec, then (optionally) re-render.

    patch_apply.py <spec.json> <patch.json> [--render]

patch.json (downloaded from the page): {"reel": "H3", "beats": {"<index>": {"text": "...", "shift": 0.3, "dur": 0.5,
"cx": 500, "cy": 900, "r": 120, "delete": true, ...}}, "phrases": {"wrong caption": "right caption"}}
Times shift in seconds; no token is spent: this is plain JSON editing. --render runs hpf_reel.py (the whole reel again, no LLM).
"""
import json, os, subprocess, sys
spec_p, patch_p = sys.argv[1], sys.argv[2]
spec = json.load(open(spec_p)); patch = json.load(open(patch_p))
beats = spec["beats"]
for k, ch in patch.get("beats", {}).items():
    b = beats[int(k)]
    if ch.get("delete"): b["_del"] = True; continue
    for key in ("text", "title", "tag", "big", "sub", "y", "cx", "cy", "rx", "ry"):
        if key in ch and key in b: b[key] = ch[key]
    if b["type"] == "title" and "text" in ch and b.get("style") != "card": b["text"] = ch["text"]
    if b["type"] == "anatomy" and "title" in ch: b["title"] = ch["title"]
    if b["type"] == "hiprot":
        if "a_title" in ch: b["a"]["title"] = ch["a_title"]
        if "b_title" in ch: b["b"]["title"] = ch["b_title"]
    if b["type"] == "compare2":
        if "top_label" in ch: b["top"]["label"] = ch["top_label"]
        if "bottom_label" in ch: b["bottom"]["label"] = ch["bottom_label"]
    if b["type"] == "guide" and "cx" in ch:
        c = next((s for s in b["shapes"] if s["type"] == "circle"), None)
        if c: c.update(cx=ch["cx"], cy=ch["cy"], r=ch.get("r", c["r"]))
    if b["type"] == "glow":
        for key in ("cx", "cy", "rx", "ry"):
            if key in ch: b[key] = ch[key]
    sh, du = ch.get("shift", 0), ch.get("dur", 0)
    if (sh or du) and isinstance(b.get("at"), (int, float)):
        b["at"] = round(b["at"] + sh, 2)
        if isinstance(b.get("to"), (int, float)): b["to"] = round(b["to"] + sh + du, 2)
spec["beats"] = [b for b in beats if not b.get("_del")]
spec.setdefault("phrases", {}).update({k: v for k, v in patch.get("phrases", {}).items() if k and v})
json.dump(spec, open(spec_p, "w"), ensure_ascii=False, indent=1)
print(f"patched {spec_p}: {len(patch.get('beats', {}))} beat edits, {len(patch.get('phrases', {}))} caption fixes")
if "--render" in sys.argv:
    subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "hpf_reel.py"), spec_p], check=True)
