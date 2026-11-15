# HPF talking head, reel 6: lưu ý tập luyện dành cho dân văn phòng (0081 + 0082 ghép, ~90 s)
# Two sources on one virtual clock: 0081 seconds as is, 0082 seconds + B.
import json, os
FPS = 30
B = 10000
SOURCES = [  # (offset, video, transcript, vad)
    (0, "raw/0081.mp4", "tx/0081.json", "build/vad_0081.json"),
    (B, "raw/0082.mp4", "tx/0082.json", "build/vad_0082.json"),
]
SRC, TX, VAD = SOURCES[0][1], SOURCES[0][2], SOURCES[0][3]
PIECES = [
    (268.78, 274.20, 1.18),          # HOOK: thân hình đẹp hơn nhưng stress hơn, làm việc không hiệu quả thì không đáng
    (116.00, 118.65, 1.00),          # thông thường khách của em đa số là dân văn phòng
    (145.55, 151.85, 1.12),          # với khách dân văn phòng thì vốn dĩ họ vận động ít rồi
    (B + 289.40, B + 295.75, 1.00),  # từ không vận động gì đến đi tập đã là một nỗ lực rất lớn rồi
    (152.40, 162.30, 1.18),          # khi họ đi tập, họ đã cố gắng rất nhiều để làm quen một lối sống mới
    (163.10, 167.65, 1.00),          # em không muốn gây quá nhiều áp lực lên bản thân họ
    (B + 279.60, B + 289.40, 1.12),  # với khách mới đi, em cố gắng để mọi người thích nghi làm quen dần
    (B + 305.70, B + 314.90, 1.00),  # không muốn khách vừa vào phát đã vào khuôn khổ; khuôn khổ thì dễ làm
    (B + 315.70, B + 319.55, 1.18),  # dễ đạt kết quả, nhưng không phải ai cũng chịu được áp lực như thế
    (B + 323.50, B + 327.40, 1.32),  # mọi người biết 21 ngày để hình thành một thói quen mới
    (B + 329.10, B + 338.60, 1.00),  # thói quen đi tập gym đều, thành lối sống, thích nghi dần thay vì ép khuôn khổ
    (248.40, 256.05, 1.18),          # tập quan trọng hơn hay đi làm quan trọng hơn: hai cái bổ trợ cho nhau
    (257.90, 264.25, 1.00),          # đánh đổi sức khỏe, ăn uống không đảm bảo, để rồi stress, đi làm không được
    (265.20, 267.45, 1.32),          # thì đi tập cũng không giải quyết vấn đề gì cả
    (274.70, 278.90, 1.00),          # nên mình cố gắng điều chỉnh làm sao để nó thoải mái nhất
    (B + 349.10, B + 351.00, 1.18),  # làm sao mà nó đơn giản nhất
    (B + 352.30, B + 353.60, 1.32),  # back to basic thôi
]
HOOK_PIECES = 1
BROLL = [   # each source once in this reel
    (B + 291.30, B + 295.75, "raw/0091.mp4", 18.5, 1.00, 0.5, 0.5),         # đi tập đã là nỗ lực rất lớn
    (155.60, 159.40, "raw/new3.mp4", 7.0, 1.00, 0.5, 0.5, "ccw"),            # họ đã cố gắng rất nhiều
    (B + 329.10, B + 333.80, "raw/0089.mp4", 12.0, 1.00, 0.5, 0.5),         # thói quen đi tập gym đều
    (274.70, 278.90, "raw/new1.mp4", 12.0, 1.00, 0.5, 0.5, "cw"),            # điều chỉnh cho thoải mái nhất
]
FACE = (0.40, 0.44)
GAP_KEEP = 0.22
PAD_IN, PAD_OUT = 0.09, 0.11
ALT = {1.0: 1.12, 1.06: 1.0, 1.12: 1.0, 1.18: 1.0, 1.32: 1.18}
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
