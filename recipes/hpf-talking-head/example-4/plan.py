# HPF talking head, reel 4: người mới đi tập, thích nghi dần, đừng ép khuôn khổ (DJI 0082, phần 271-354)
import json, os
FPS = 30
SRC = "raw/0082.mp4"
VAD = "build/vad_0082.json"
TX = "tx/0082.json"
PIECES = [
    (339.00, 345.65, 1.18),  # HOOK: đi lính là nghĩa vụ rồi ... nhưng đây là lựa chọn của mọi người
    (279.60, 289.40, 1.00),  # với khách hàng mới đi, em cố gắng để mọi người thích nghi làm quen dần với việc đi tập
    (289.40, 295.75, 1.18),  # từ không vận động gì đến đi tập đã là một nỗ lực rất lớn rồi
    (296.80, 299.40, 1.00),  # không phải ai cũng chịu được một áp lực lớn
    (305.70, 314.90, 1.12),  # em không muốn khách vừa vào phát đã vào khuôn khổ; khuôn khổ thì dễ làm
    (315.70, 319.55, 1.00),  # dễ đạt kết quả, nhưng không phải ai cũng chịu được áp lực như thế
    (323.50, 327.40, 1.32),  # mọi người biết 21 ngày để hình thành một thói quen mới
    (329.10, 338.60, 1.00),  # hình thành thói quen đi tập gym đều, thích nghi dần thay vì ép vào khuôn khổ
    (345.60, 351.00, 1.18),  # cố gắng để mọi người thích nghi, làm sao đơn giản nhất
    (352.30, 353.60, 1.32),  # back to basic thôi
]
HOOK_PIECES = 1
BROLL = [
    (291.30, 295.75, "raw/0091.mp4", 18.5, 1.00, 0.5, 0.5),  # đi tập đã là nỗ lực rất lớn -> client pulling, coach
    (329.10, 333.80, "raw/0089.mp4", 12.0, 1.00, 0.5, 0.5),  # thói quen đi tập gym đều -> seated row with coach
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
