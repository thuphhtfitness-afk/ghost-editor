"""Reel 2 content slots. Times: E(<original second of 0082>)."""
from plan import to_edit as E, hook_end, timeline, FPS, BROLL

FIX = {"cây": "case", "Bàn": "ban", "dưới": "đến", "calor": "calo", "sporty": "sporty"}
TOTAL = timeline()[1]
END = TOTAL / FPS + 0.6

TITLE_T0 = hook_end()
TITLE_END = E(63.25)
HOOK_END = TITLE_END
KICKER = "CASE STUDY"
TITLE_LINES = ["tự tập được rồi,", "sao vẫn quay lại?"]
SECTIONS = [
    (E(63.77), E(92.75), "1.) KHÁCH CỦA EM", "6 tháng, đạt mục tiêu giảm cân"),
    (E(93.30), E(141.55), "2.) VÌ SAO VẪN QUAY LẠI", "gym thành một nhiệm vụ"),
    (E(152.85), E(229.25), "3.) HUẤN LUYỆN VIÊN LÀ", "một người đồng hành"),
    (E(237.40), E(246.50), "4.) GYM NÊN LÀ", "một lối sống"),
]
POPS = [
    (E(137.54), E(138.55), "nhiệm vụ", "ser"),
    (E(97.56), E(98.70), "vẫn quay lại", "ser"),
    (E(119.10), E(120.55), "không vui", "ser"),
    (E(127.80), E(128.30), "LIFESTYLE", "osw"),
    (E(129.02), E(129.65), "lối sống", "ser"),
    (E(132.84), E(133.35), "nhiệm vụ", "ser"),
    (E(140.70), E(141.55), "nản, mệt", "ser"),
    (E(228.05), E(228.95), "MOTIVATE", "osw"),
    (E(241.68), E(242.55), "lối sống", "ser"),
]
TAGS = [
    (E(134.64), E(136.30), "nhiệm vụ ở công ty"),
    (E(111.00), E(113.90), "không phải ai cũng có hội bạn sporty"),
    (E(221.20), E(223.60), "người ta biết cần làm gì rồi"),
    (E(157.00), E(158.25), "người đồng hành, người support"),
]
EMOJI = [
    (E(135.48), TITLE_T0, "office", 150, 800, 135),
    (E(138.10), TITLE_T0, "lifting", 150, 980, 135),
    (E(63.80), E(68.15), "target", 150, 800, 135),
    (E(64.84), E(68.15), "calendar", 150, 970, 135),
    (E(140.70), E(141.55), "exhale", 860, 640, 170),
    (E(226.79), E(229.25), "thinking", 860, 640, 170),
    (E(246.52), E(249.45), "heart", 860, 640, 160),
]
MARKS = []
CHECKLIST = [  # ticked lines on the plain wall, left of the head
    (E(76.96), E(82.40), 70, 760, "tự tập được"),
    (E(78.46), E(82.40), 70, 870, "tự track calo"),
    (E(81.50), E(82.40), 70, 980, "biết phải làm gì"),
]
NUMBERS = [
    (E(64.84), E(68.15), "6 THÁNG", 640, 470),
    (E(90.12), E(92.75), "THẺ 2 NĂM", 540, 470),
]
PRICE = None
STRIKE_T = NEW_PRICE_T = 0
RECAP = (E(246.50), END)
RECAP_LINES = ["1.) khách đã tự tập được", "2.) vẫn quay lại vì gym thành nhiệm vụ",
               "3.) huấn luyện viên là người đồng hành", "4.) gym nên là một lối sống"]
