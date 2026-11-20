# HPF talking head, reel 7 v3 (parents' cut): bàn chân bẹt ảnh hưởng gì đến trẻ khi lớn lên (DJI th7 + kid clip lead-in)
import json, os
FPS = 30
SRC = "raw/th7.mp4"
VAD = "build/vad_th7.json"
TX = "tx/th7.json"
PRE_ROLL = 3.0          # 0-3 s: kid's feet push-in, freeze at 1.2 s (flash + click), photo + title
PIECES = [
    (111.30, 115.95, 1.10),  # HOOK: nhất là khi càng lớn thì mọi người sẽ càng thấy vấn đề đấy ảnh hưởng nhiều đến sinh hoạt hằng ngày
    (40.75, 43.85, 1.00),    # nhưng với bàn chân bẹt thì nó chụm, nó tạo thành chữ X
    (21.85, 23.95, 1.00),    # thì về cái vấn đề bàn chân bẹt nhé
    (25.45, 31.65, 1.10),    # khi bàn chân bị bẹt vào trong, cái trục ở phần gót chân nó bị đổ vào trong
    (32.70, 34.75, 1.00),    # thứ nhất là nó sẽ ảnh hưởng đến cái khớp gối
    (36.20, 40.40, 1.10),    # khớp gối thông thường nó sẽ thẳng, cùng lắm là hơi chụm vào trong
    (45.10, 48.45, 1.00),    # đầu gối nó như thế này, nó không phải bẻ vào trong như thế này
    (48.80, 55.45, 1.10),    # dây chằng bên này đổ vào trong dần, bọn đấy phải chịu áp lực nhiều
    (56.25, 61.30, 1.00),    # bọn đúng ra không phải làm việc đấy lại phải chịu áp lực
    (62.30, 68.30, 1.10),    # về lâu dài ảnh hưởng đến khớp gối, những dây chằng xung quanh khớp gối
    (68.95, 74.25, 1.00),    # thứ hai là khi chơi thể thao, gối như thế rất dễ gặp chấn thương
    (74.65, 87.65, 1.10),    # vốn đổ vào trong rồi, tiếp đất sai, ngoặt phát... nói đứt thì hơi quá, nhưng rất dễ chấn thương
]
HOOK_PIECES = 1
BROLL = [
    ("@0", "@3.0", "raw/kid_feet_freeze.mp4", 0.0, 1.00, 0.5, 0.5),  # lead-in: cu Bo's feet (face out of frame), push-in then freeze
    (84.28, 87.60, "raw/kid_squat.mov", 1.0, 1.10, 0.42, 0.45),  # gối không đủ ổn định -> kid climbing with the coach (back to camera)
]
FACE = (0.45, 0.24)
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
