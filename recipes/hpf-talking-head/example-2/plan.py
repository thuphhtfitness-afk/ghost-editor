# HPF talking head, reel 2: "Tự tập được rồi, sao vẫn quay lại?" (DJI 0082, cảnh trám 0087/0089/0092)
import json, os
FPS = 30
SRC = "raw/0082.mp4"
VAD = "build/vad_0082.json"
TX = "tx/0082.json"
PIECES = [
    (134.24, 138.70, 1.18),  # HOOK: làm hết nhiệm vụ ở công ty rồi, về lại có một nhiệm vụ nữa ở phòng gym
    (57.30, 59.75, 1.00),    # ok có thể lấy một case study là khách hàng của em nhé
    (60.40, 68.20, 1.12),    # khách ban đầu đến đây với mục tiêu giảm cân, sau 6 tháng đạt được mục tiêu
    (75.30, 79.50, 1.00),    # khách nắm được technique, tự tập được rồi, tự track được calo
    (80.60, 82.45, 1.18),    # và khách biết phải làm gì
    (86.40, 92.80, 1.00),    # khách tự ra ngoài, mua thẻ 2 năm ở phòng commercial, tự tập
    (93.30, 98.75, 1.32),    # nhưng sau một khoảng thời gian tự tập thì họ vẫn quay lại
    (99.70, 102.90, 1.00),   # quay lại không phải là bởi vì họ không làm được
    (110.50, 113.95, 1.12),  # không phải ai cũng có một hội bạn sporty giống mình
    (117.10, 120.60, 1.00),  # nó khiến cho việc đi tập không vui
    (125.80, 129.70, 1.18),  # nó không phải một dạng lifestyle, không phải lối sống
    (129.86, 133.40, 1.00),  # nên họ đi làm, nó giống như một dạng nhiệm vụ
    (139.00, 141.60, 1.18),  # thì họ sẽ thấy đôi khi nó khá nản, khá mệt
    (152.85, 158.30, 1.00),  # với họ huấn luyện viên như một người đồng hành, một người support
    (221.05, 223.65, 1.18),  # người ta biết người ta cần làm gì
    (223.85, 229.30, 1.32),  # nhưng cảm giác nó cứ thiếu một cái gì đấy, có thể là motivate
    (237.40, 249.50, 1.00),  # gym nên là một dạng lối sống, không phải nhiệm vụ, dễ đồng hành, dễ đi lâu dài
]
HOOK_PIECES = 1
BROLL = [
    (99.70, 102.90, "raw/0087.mp4", 1.0, 1.00, 0.5, 0.5),   # không phải họ không làm được -> client training on her own
    (117.10, 120.60, "raw/0089.mp4", 2.0, 1.00, 0.5, 0.5),  # đi tập không vui -> seated band row
    (155.35, 158.30, "raw/0092.mp4", 0.0, 1.00, 0.5, 0.5),  # người đồng hành, support -> coach beside her
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
