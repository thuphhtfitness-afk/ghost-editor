# HPF office set 2: đau lưng dưới mà cứ giãn lưng? gốc có thể ở mông (th9). Cut on purpose: 188.0-193.0 (nói quá).
import json, os
FPS = 30
SRC = "raw/th9.mp4"
VAD = "build/vad_th9.json"
TX = "tx/th9.json"
PIECES = [
    (159.60, 164.65, 1.10),  # HOOK: đau mỏi lưng dưới nhưng mọi người cứ cố giãn lưng, không biết cái gốc nằm ở mông
    (165.45, 174.95, 1.00),  # có khách đi làm về đau lưng, em cho thử giãn mông, giãn 5 cái khách bảo nhẹ
    (143.15, 158.35, 1.10),  # lưng dưới còn vì ngồi nhiều, cơ mông căng chèn ép dây thần kinh toạ...
    (193.20, 199.15, 1.00),  # nếu đã thoát vị thì là vấn đề khác, lúc đấy cần ý kiến bác sĩ
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
