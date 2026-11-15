# HPF talking head, reel 5: tập hay đi làm quan trọng hơn? (DJI 0081, phần không dùng trong V2)
import json, os
FPS = 30
SRC = "raw/0081.mp4"
VAD = "build/vad_0081.json"
TX = "tx/0081.json"
PIECES = [
    (268.60, 274.20, 1.18),  # HOOK: thân hình đẹp hơn nhưng stress hơn, làm việc không hiệu quả thì không đáng
    (145.55, 151.85, 1.00),  # với khách hàng dân văn phòng thì vốn dĩ họ vận động ít rồi
    (152.40, 162.30, 1.12),  # khi họ đi tập, họ đã cố gắng rất nhiều để làm quen với một lối sống mới
    (163.10, 167.65, 1.00),  # em không muốn gây quá nhiều áp lực lên bản thân họ
    (248.40, 256.05, 1.18),  # tập quan trọng hơn hay đi làm quan trọng hơn thì khá khó, hai cái bổ trợ cho nhau
    (257.90, 264.25, 1.00),  # bảo họ đánh đổi sức khỏe, ăn uống không đảm bảo để rồi stress, đi làm không được
    (265.20, 267.45, 1.32),  # thì đi tập cũng không giải quyết vấn đề gì cả
    (274.70, 278.90, 1.00),  # nên mình cố gắng điều chỉnh làm sao để nó thoải mái nhất
]
HOOK_PIECES = 1
BROLL = [
    (155.60, 159.40, "raw/0087.mp4", 4.0, 1.00, 0.5, 0.5),   # họ đã cố gắng rất nhiều -> client on the leg curl
    (274.70, 278.90, "raw/0092.mp4", 5.0, 1.00, 0.5, 0.5),   # điều chỉnh cho thoải mái nhất -> coach adjusting
]
FACE = (0.40, 0.44)
GAP_KEEP = 0.22
PAD_IN, PAD_OUT = 0.09, 0.11
ALT = {1.0: 1.12, 1.06: 1.0, 1.12: 1.0, 1.18: 1.0, 1.32: 1.18}
def _speech():
    return json.load(open(VAD)) if os.path.exists(VAD) else None


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
