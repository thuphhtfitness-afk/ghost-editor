# HPF talking head, reel 3: squat không chỉ để tập nhóm cơ (DJI 0083). Không dùng phần thoát vị / ngã.
import json, os
FPS = 30
SRC = "raw/0083.mp4"
VAD = "build/vad_0083.json"
TX = "tx/0083.json"
PIECES = [
    (119.20, 121.25, 1.18),  # HOOK: ngồi bình thường là squat, ngồi xổm là squat mà
    (31.25, 40.80, 1.00),    # mọi người hình dung squat là để tập trung cho nhóm cơ này, nhóm cơ này
    (41.40, 50.40, 1.18),    # nhưng thực chất các bài tập đang giả lập lại hành động hằng ngày
    (53.40, 67.75, 1.00),    # mỗi người một target: lift nặng hơn, target nhóm cơ, hay chỉ bổ trợ
    (104.00, 109.65, 1.18),  # cái squat này mọi người đã thấy rõ khi bê vác đồ
    (110.15, 114.35, 1.00),  # hoặc làm một cái chuyển động gì đấy
    (199.05, 205.70, 1.32),  # với con squat thì nó giả lập cho việc chuyển động trong ngày
]
HOOK_PIECES = 1
BROLL = [
    (43.50, 48.90, "raw/new4.mp4", 0.5, 1.00, 0.5, 0.5, "ccw"),   # bài tập giả lập hành động hằng ngày -> squat with the coach
    (61.20, 64.00, "raw/new2.mp4", 10.0, 1.00, 0.5, 0.5, "cw"),   # target nhóm cơ này -> machine work
]
FACE = (0.52, 0.40)
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
