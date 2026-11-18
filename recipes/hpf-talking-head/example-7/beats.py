"""Reel 7 content slots (th7: standing, face high -> titles above the head, captions at the waist, anatomy cards low)."""
from plan import to_edit as E, hook_end, timeline, FPS, BROLL

FIX = {"trụng": "chụm", "trăng": "chằng", "trắng": "chằng", "tiết": "tiếp", "Ngoạt": "ngoặt", "tè": "toè"}
TOTAL = timeline()[1]
END = TOTAL / FPS + 0.6
CAP_Y = 1090
TAG_Y = 975
KICKER_Y, TITLE_Y = 95, 190
RECAP_Y, RECAP_DY = 105, 58

TITLE_T0 = hook_end()
TITLE_END = E(23.95)
HOOK_END = TITLE_END
KICKER = "BÀN CHÂN BẸT"
TITLE_LINES = ["ảnh hưởng thế nào", "đến tư thế?"]
SECTIONS = [
    (E(25.45), E(31.65), "1.) BÀN CHÂN BẸT", "trục gót chân đổ vào trong"),
    (E(32.70), E(48.45), "2.) KHỚP GỐI", "chụm vào trong thành chữ X"),
    (E(48.80), E(68.30), "3.) DÂY CHẰNG", "chịu áp lực không phải của nó"),
    (E(68.95), E(87.65), "4.) KHI CHƠI THỂ THAO", "rất dễ gặp chấn thương"),
    (E(88.85), E(120.60), "5.) DÁNG ĐI ĐỨNG", "trông sẽ rất xấu"),
]
POPS = [
    (E(79.96), E(80.70), "đứt dây chằng?", "ser"),
    (E(43.42), E(43.85), "CHỮ X", "osw"),
    (E(54.74), E(55.40), "áp lực", "ser"),
    (E(73.68), E(74.20), "chấn thương", "ser"),
    (E(95.20), E(95.85), "rất xấu", "ser"),
    (E(105.64), E(106.40), "không mạnh mẽ", "ser"),
]
TAGS = [
    (E(77.04), E(79.20), "chỉ cần tiếp đất sai"),
    (E(58.58), E(61.25), "chịu áp lực không phải của nó"),
    (E(116.66), E(118.10), "nhất là khi chơi thể thao nhiều"),
    (E(114.96), E(115.90), "sinh hoạt hằng ngày"),
    (E(103.74), E(105.60), "với nam: nhìn không khỏe"),
]
EMOJI = [
    (E(73.42), E(74.20), "sweat", 880, 760, 160),
    (E(81.86), E(83.30), "thinking", 880, 760, 160),
    (E(70.68), E(72.60), "soccer", 880, 760, 150),
    (E(93.58), E(95.85), "walking", 880, 760, 160),
    (E(101.70), E(102.50), "laugh", 880, 760, 160),
]
MARKS = []
CHECKLIST = []
NUMBERS = []
PRICE = None
STRIKE_T = NEW_PRICE_T = 0
CUTOUTS = []
A = "assets/"
PY = 1480   # anatomy band centre (legs area)
PANELS = [   # (t0, t1, card png, x, y, scale)
    (E(79.96), E(80.74), A + "knee_mcl.png", 540, PY, 0.98),
    (E(23.02), E(23.95), A + "arch_normal.png", 540, PY, 0.98),
    (E(25.86), E(27.60), A + "arch_flat.png", 540, PY, 0.98),
    (E(27.64), E(31.62), A + "heel_axis.png", 540, PY, 0.98),
    (E(37.72), E(40.70), A + "legs_straight.png", 540, PY, 0.98),
    (E(40.80), E(48.40), A + "legs_x.png", 540, PY, 0.98),
    (E(50.48), E(61.25), A + "knee_mcl.png", 540, PY, 0.98),
    (E(64.74), E(68.25), A + "knee_inside.png", 540, PY, 0.98),
    (E(99.26), E(102.40), A + "legs_x.png", 540, PY, 0.98),
]
RECAP = (E(116.10), END)
RECAP_LINES = ["1.) bàn chân bẹt: gót đổ vào trong", "2.) khớp gối chụm thành chữ X",
               "3.) dây chằng chịu áp lực", "4.) chơi thể thao dễ chấn thương", "5.) dáng đi đứng trông xấu"]
