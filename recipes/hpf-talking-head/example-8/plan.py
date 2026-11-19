# HPF talking head, reel 8: giày cao gót ảnh hưởng thế nào đến tư thế (DJI th8, standing, demonstrates side-on 48-64 s)
import json, os
FPS = 30
SRC = "raw/th8.mp4"
VAD = "build/vad_th8.json"
TX = "tx/th8.json"
PIECES = [
    (73.10, 75.00, 1.10),   # HOOK: nên là thực ra cái việc đi giày cao gót không sai
    (24.60, 28.80, 1.00),   # với việc nữ đi giày cao gót nhiều ảnh hưởng đến tư thế
    (31.80, 42.80, 1.10),   # thứ nhất: khá căng bắp chân vì luôn phải kiễng; một nhóm cơ thôi thì không ảnh hưởng nhiều
    (42.90, 47.95, 1.00),   # nhưng làm văn phòng ngồi nhiều, nó căng hip flexor
    (48.45, 55.60, 1.00),   # đi kiễng ở cao, để giữ thăng bằng thì đẩy cái mông ra đằng sau
    (55.95, 64.15, 1.00),   # gây ra tình trạng lật cái chậu về đằng trước, dẫn đến lưng võng
    (65.05, 72.15, 1.10),   # mỏi lưng; đứng tình trạng ấy lâu ngày, lưng tải quá nhiều, ảnh hưởng đến cả cuộc sống
    (75.30, 84.15, 1.00),   # đi giày cao gót cùng với ngồi nhiều dẫn đến bọn này bị căng, nên mới đau mỏi lưng
]
HOOK_PIECES = 1
BROLL = []
FACE = (0.55, 0.22)
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
    """[(a, b_snapped, edit_start, nframes, zoom, piece_index)]"""
    out, t = [], 0
    subs = subpieces()
    for a, b, z, pi in subs:
        n = max(1, round((b - a) * FPS))
        out.append((a, a + n / FPS, t / FPS, n, z, pi))
        t += n
    return out, t


_TL = None


def to_edit(orig_t):
    """original second -> edit second (a time inside a removed silence snaps to the next kept frame)"""
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
