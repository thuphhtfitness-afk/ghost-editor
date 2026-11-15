# HPF talking head: the edit plan for reel "Dân văn phòng giảm cân" (source DJI 0081 + B-roll 0084)
FPS = 30
SRC = "raw/0081.mp4"
BROLL = "raw/0084.mp4"

# (a, b, zoom, broll) in original seconds of 0081. zoom: 1.0 wide as shot, 1.18 tight, 1.32 punch.
# broll: (start in 0084, zoom, cx, cy) -> full-screen cảnh trám, voice keeps running underneath.
PIECES = [
    (49.20, 51.98, 1.00, None),   # Sáng thì thường đá cốc cà phê
    (52.48, 58.88, 1.18, None),   # Xong rồi chiều trà sữa ... đồng nghiệp rủ
    (59.04, 60.92, 1.32, None),   # Ăn uống, ăn vặt
    (61.36, 64.56, 1.00, None),   # Thì em thấy đấy là vấn đề chung của hầu hết dân văn phòng
    (134.00, 141.74, 1.18, None), # Nhưng mà với những khách giảm cân ... ngưỡng thâm hụt được
    (167.46, 171.98, 1.00, (24.0, 1.15, 0.45, 0.55)),  # đi tập gây stress lên cơ thể -> client on treadmill
    (172.44, 174.96, 1.18, None), # Và với dân văn phòng thì thực sự là
    (176.60, 178.10, 1.32, None), # có rất nhiều stress rồi đúng không
    (180.54, 188.48, 1.00, None), # nhiều người ăn là niềm vui ... không muốn quá stress
    (188.86, 197.90, 1.18, None), # có thể chấp nhận sáng uống cà phê ... không có bữa xế
    (226.02, 228.60, 1.00, None), # Đôi khi mình phải chấp nhận kết quả sẽ đến muộn
    (281.66, 289.30, 1.18, None), # giảm cân thì ăn đói đã rất stress ... vừa đói vừa chán
    (303.00, 308.84, 1.00, None), # cả phòng đặt đồ ăn ... khá dở hơi
    (311.12, 314.62, 1.18, (15.2, 1.10, 0.55, 0.5)),  # mình sẽ hỗ trợ họ -> coach guiding client
    (329.52, 332.72, 1.00, None), # mọi người hay ăn suất 60-70 nghìn
    (335.68, 339.40, 1.18, None), # chỉ cần giảm từ 60-70 nghìn xuống
    (341.96, 344.78, 1.32, None), # 50-65 nghìn thôi là đã ít hơn rồi
    (349.16, 356.80, 1.00, None), # tối mình điều chỉnh ở bữa tối
]
# face centre in the source frame (normalised); punch-ins zoom towards it
FACE = (0.40, 0.44)


def frames(p):
    a, b = p[0], p[1]
    return round((b - a) * FPS)


def timeline():
    """[(a, b_snapped, edit_start, nframes, zoom, broll)]"""
    out, t = [], 0
    for p in PIECES:
        n = frames(p)
        out.append((p[0], p[0] + n / FPS, t / FPS, n, p[2], p[3]))
        t += n
    return out, t


def to_edit(orig_t):
    tl, _ = timeline()
    for a, b, es, n, z, br in tl:
        if a - 1e-6 <= orig_t <= b + 1e-6:
            return es + (orig_t - a)
    return None
