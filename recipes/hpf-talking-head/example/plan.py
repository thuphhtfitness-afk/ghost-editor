# HPF talking head: the edit plan for reel "Dân văn phòng giảm cân" (source DJI 0081, cảnh trám 0087/0091/0092)
import json, os
FPS = 30
SRC = "raw/0081.mp4"
VAD = "build/vad_0081.json"
TX = "tx/0081.json"

# (a, b, zoom) in original seconds of 0081, in EDIT order. zoom: 1.0 as shot, 1.12, 1.18 tight, 1.32 punch.
# Silences inside a piece are cut out automatically (VAD), each sub-cut alternates the shot size.
PIECES = [
    (303.00, 308.84, 1.18),  # HOOK: cả phòng đặt đồ ăn mà mình lại không ăn thì khá dở hơi
    (49.38, 51.98, 1.00),    # Sáng thì thường đá cốc cà phê
    (52.48, 58.88, 1.06),    # Xong rồi chiều trà sữa ... đồng nghiệp rủ
    (59.04, 60.92, 1.12),    # Ăn uống, ăn vặt
    (61.36, 64.56, 1.00),    # Thì em thấy đấy là vấn đề chung của hầu hết dân văn phòng
    (134.00, 141.74, 1.18),  # Nhưng mà với những khách giảm cân ... ngưỡng thâm hụt được
    (167.46, 171.98, 1.00),  # đi tập gây stress lên cơ thể
    (172.44, 174.96, 1.18),  # Và với dân văn phòng thì thực sự là
    (176.60, 178.10, 1.32),  # có rất nhiều stress rồi đúng không
    (180.54, 188.48, 1.00),  # nhiều người ăn là niềm vui ... không muốn quá stress
    (188.86, 197.90, 1.18),  # có thể chấp nhận sáng uống cà phê ... không có bữa xế
    (226.02, 228.60, 1.00),  # Đôi khi mình phải chấp nhận kết quả sẽ đến muộn
    (281.66, 289.30, 1.18),  # giảm cân thì ăn đói đã rất stress ... vừa đói vừa chán
    (311.12, 314.62, 1.00),  # mình sẽ hỗ trợ họ
    (329.52, 332.72, 1.18),  # mọi người hay ăn suất 60-70 nghìn
    (335.68, 339.40, 1.00),  # chỉ cần giảm từ 60-70 nghìn xuống
    (341.96, 344.78, 1.32),  # 50-65 nghìn thôi là đã ít hơn rồi
    (349.16, 356.80, 1.00),  # tối mình điều chỉnh ở bữa tối
]
HOOK_PIECES = 1          # the first N pieces are the cold-open hook; a flash + click lands after them
# cảnh trám: full screen over the talking head between two ORIGINAL times of 0081 (voice keeps running)
# (orig_from, orig_to, file, src_start, zoom, cx, cy)
BROLL = [
    (134.00, 137.40, "raw/0091.mp4", 5.0, 1.00, 0.5, 0.5),   # khách giảm cân -> coach behind a client on the band pull
    (167.46, 171.98, "raw/0087.mp4", 20.5, 1.00, 0.5, 0.5),  # đi tập = stress lên cơ thể -> leg curl, coach watching
    (311.12, 314.62, "raw/0092.mp4", 13.4, 1.00, 0.5, 0.5),  # mình sẽ hỗ trợ họ -> coach adjusting her form
]
FACE = (0.40, 0.44)
GAP_KEEP = 0.22          # a silence shorter than this stays; longer ones are cut to PAD_IN + PAD_OUT
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
