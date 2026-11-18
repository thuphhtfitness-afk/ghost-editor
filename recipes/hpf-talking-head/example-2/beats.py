"""Reel 2 content slots. Times: E(<original second of 0082>)."""
from plan import to_edit as E, hook_end, timeline, FPS, BROLL

FIX = {"cây": "case", "Bàn": "ban", "dưới": "đến", "calor": "calo", "sporty": "sporty"}
TOTAL = timeline()[1]
END = TOTAL / FPS + 0.6

TITLE_T0 = hook_end()
TITLE_END = E(60.85)
TITLE_CPS = 42
HOOK_END = TITLE_END
KICKER = "CASE STUDY"
TITLE_LINES = ["tự tập được rồi,", "sao vẫn quay lại?"]
SECTIONS = [
    (E(63.77), E(92.75), "1.) KHÁCH CỦA EM", "6 tháng, đạt mục tiêu giảm cân"),
    (E(93.30), E(141.55), "2.) VÌ SAO VẪN QUAY LẠI", "gym thành một nhiệm vụ"),
    (E(152.85), E(229.25), "3.) HUẤN LUYỆN VIÊN LÀ", "một người đồng hành"),
    (E(244.85), E(246.80), "4.) KHI GYM LÀ LỐI SỐNG", "dễ đồng hành, dễ đi lâu dài"),
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
    (E(135.48), E(136.30), "office", 150, 800, 135),
    (E(138.10), E(138.65), "lifting", 150, 980, 135),
    (E(140.70), E(141.55), "exhale", 860, 640, 170),
    (E(226.79), E(229.25), "thinking", 860, 640, 170),
    (E(246.52), E(249.45), "heart", 860, 640, 160),
    (E(241.68), E(244.50), "seedling", 150, 800, 135),
]
MARKS = []
CHECKLIST = [  # ticked lines on the plain wall, left of the head
    (E(76.96), E(82.40), 70, 760, "tự tập được"),
    (E(78.46), E(82.40), 70, 870, "tự track calo"),
    (E(81.50), E(82.40), 70, 980, "biết phải làm gì"),
]
NUMBERS = [
    (E(90.12), E(92.75), "THẺ 2 NĂM", 330, 470),
]
PRICE = None
CUTOUTS = []
BOARD = dict(   # whiteboard: before -> 6 tháng -> after (khách cũ, faces covered)
    t0=E(60.95), t1=E(76.50), box=(40, 130, 1040, 680),
    before=("assets/sticker2.png", E(61.28), 255, 390, 0.56, 2),
    after=("assets/sticker1.png", E(67.12), 835, 385, 0.50, -3),
    arrow=(E(64.44), E(66.24), (430, 410, 655)),
    labels=[(E(61.28), "ban đầu", 255, 640, "S"), (E(64.84), "6 tháng", 542, 330, "L"),
            (E(67.12), "đạt mục tiêu", 835, 640, "S")],
)
STRIKE_T = NEW_PRICE_T = 0
RECAP = (E(246.90), END)
RECAP_LINES = ["1.) khách đã tự tập được", "2.) vẫn quay lại vì gym thành nhiệm vụ",
               "3.) huấn luyện viên là người đồng hành", "4.) gym nên là một lối sống"]
