# HPF office set 1: mỏi cổ vai gáy không phải do ngồi nhiều (DJI 0178 = th9)
import json, os
FPS = 30
SRC = "raw/th9.mp4"
VAD = "build/vad_th9.json"
TX = "tx/th9.json"
PIECES = [
    (102.85, 111.30, 1.10),  # HOOK: thực ra cái việc ngồi nhiều chưa phải là cái lý do khiến mọi người gặp những tình trạng như thế
    (56.05, 66.95, 1.00),    # khách của em đa số là dân văn phòng, vấn đề chung là đau mỏi cổ vai gáy
    (91.05, 102.40, 1.10),   # thông thường khách văn phòng đau mỏi cổ vai, lưng dưới; nghĩ là do ngồi nhiều
    (111.72, 125.60, 1.00),  # là bởi vì ngồi khiến vai xoay ra trước nên con này bị co lên, dẫn đến đau mỏi cổ vai gáy
]
BROLL = []
HOOK_PIECES = 1
FACE = (0.45, 0.26)
GAP_KEEP = 0.22
PAD_IN, PAD_OUT = 0.09, 0.11
ALT = {1.0: 1.10, 1.10: 1.0}
def _speech():
    srcs = globals().get("SOURCES") or [(0, SRC, globals().get("TX"), VAD)]
    out = []
    for off, _s, _t, vad in srcs:
        if not os.path.exists(vad):
            return None
        out += [(s + off, e + off) for s, e in json.load(open(vad))]
    return sorted(out)


def subpieces():
    """[(a, b, zoom)] after cutting silences, zoom alternating on every in-sentence cut"""
    sp = _speech()
    out = []
    for pi, (a, b, z) in enumerate(PIECES):
        if not sp:
            out.append((a, b, z, pi)); continue
        regs = []
        for s, e in sp:
            s2, e2 = max(a, s - PAD_IN), min(b, e + PAD_OUT)
            if e2 - s2 > 0.12:
                if regs and s2 - regs[-1][1] < GAP_KEEP:
                    regs[-1][1] = max(regs[-1][1], e2)
                else:
                    regs.append([s2, e2])
        if not regs:
            regs = [[a, b]]
        for i, (s, e) in enumerate(regs):
            out.append((s, e, z if i % 2 == 0 else ALT.get(z, 1.0), pi))
    return out


def timeline():
    """[(a, b_snapped, edit_start, nframes, zoom, piece_index)]; PRE_ROLL seconds of picture come before the first word"""
    out, t = [], round(globals().get("PRE_ROLL", 0) * FPS)
    subs = subpieces()
    for a, b, z, pi in subs:
        n = max(1, round((b - a) * FPS))
        out.append((a, a + n / FPS, t / FPS, n, z, pi))
        t += n
    return out, t


_TL = None


def to_edit(orig_t):
    """original second -> edit second (a time inside a removed silence snaps to the next kept frame);
    "@3.5" is already an edit second (pre-roll graphics, b-roll over the lead-in)"""
    if isinstance(orig_t, str) and orig_t.startswith("@"):
        return float(orig_t[1:])
    global _TL
    if _TL is None:
        _TL = timeline()[0]
    best = None
    for a, b, es, n, z, pi in _TL:
        if a - 1e-6 <= orig_t <= b + 1e-6:
            return es + (orig_t - a)
        if a > orig_t and (best is None or a < best[0]) and a - orig_t < 1.0:
            best = (a, es)
    if best:
        return best[1]
    # nearest end before
    cand = [(orig_t - b, es + n / FPS) for a, b, es, n, z, pi in _TL if b <= orig_t and orig_t - b < 1.0]
    return min(cand)[1] if cand else None


def hook_end():
    tl, _ = timeline()
    return max(es + n / FPS for a, b, es, n, z, pi in tl if pi < HOOK_PIECES)
