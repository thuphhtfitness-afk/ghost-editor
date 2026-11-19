# HPF office merged (3+4): đĩa đệm yếu dần -> case chị khách thoát vị -> tập lại: chị khách thoát vị, từ thói quen ngồi đến lúc dám tập lại (th9). Interviewer lines cut:
# 300.0-304.4 (ambiguous voice), 326.3-364.3, 372.4-374.5.
import json, os
FPS = 30
SRC = "raw/th9.mp4"
VAD = "build/vad_th9.json"
TX = "tx/th9.json"
PIECES = [
    (294.45, 299.90, 1.10),  # HOOK: có một chị khách thoát vị nhưng mà bị thoát sang bên trái
    (219.60, 227.10, 1.00),  # với việc chị ngồi cả ngày và ngồi thẳng, ngồi thẳng được như này (demo)
    (228.45, 235.70, 1.10),  # ngồi như sách giáo khoa, ngồi thẳng lâu như thế vẫn gây áp lực lên cột sống
    (236.25, 239.95, 1.00),  # chưa kể đĩa đệm nhá, bọn này không lấy được dinh dưỡng...
    (245.50, 250.00, 1.10),  # ...bọn này lấy dinh dưỡng khi cột sống co duỗi
    (258.00, 262.15, 1.00),  # mà ngồi nhiều như thế bọn đấy không nhận được dinh dưỡng, bắt đầu yếu dần
    (305.30, 312.95, 1.10),  # thói quen chị ngồi bàn chữ L, chị hay ngồi như này (demo)
    (313.75, 325.90, 1.00),  # cột sống nghiêng ra, ngồi quá lâu, còn gác chân, chậu nghiêng, lệch dần
    (364.35, 372.45, 1.10),  # khách tập ở đây rồi, nghỉ ra ngoài tập xong quay lại
    (374.55, 380.60, 1.00),  # chị quay lại tập ở đây vì thực ra chị biết tập rồi
    (381.25, 384.35, 1.10),  # nhưng khi chị phát hiện ra chị bị thoát vị
    (385.00, 393.20, 1.00),  # chị rất rén những bài compound nặng, deadlift, Romanian deadlift
    (393.65, 397.75, 1.10),  # chị cảm thấy lưng khi tập bài đấy
    (399.80, 409.00, 1.00),  # em chỉnh lại technique, chị lại thấy mông, bắt đầu không rén những bài đấy nữa
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
