"""Reel 3 content slots. Times: E(<original second of 0083>)."""
from plan import to_edit as E, hook_end, timeline, FPS, BROLL

FIX = {"sổm": "xổm", "squad": "squat", "Squat": "squat"}
TOTAL = timeline()[1]
END = TOTAL / FPS + 0.6

TITLE_T0 = hook_end()
TITLE_END = E(36.80)
HOOK_END = TITLE_END
KICKER = "SQUAT ĐỂ LÀM GÌ?"
TITLE_LINES = ["không chỉ để", "tập nhóm cơ"]
SECTIONS = [
    (E(37.11), E(40.75), "1.) MỌI NGƯỜI HAY NGHĨ", "squat để tập nhóm cơ"),
    (E(41.40), E(50.35), "2.) THỰC CHẤT BÀI TẬP", "giả lập hành động hằng ngày"),
    (E(53.40), E(67.70), "3.) MỖI NGƯỜI MỘT MỤC TIÊU", "không chỉ một nhóm cơ"),
    (E(104.00), E(201.40), "4.) SQUAT TRONG ĐỜI SỐNG", "bê vác đồ, ngồi, ngồi xổm"),
]
POPS = [
    (E(119.35), E(120.15), "ngồi", "ser"),
    (E(120.20), E(121.20), "ngồi xổm", "ser"),
    (E(39.30), E(40.70), "nhóm cơ", "ser"),
    (E(48.10), E(49.20), "hằng ngày", "ser"),
    (E(66.90), E(67.70), "bổ trợ", "ser"),
    (E(108.70), E(109.60), "bê vác đồ", "ser"),
    (E(204.30), E(205.65), "chuyển động\ntrong ngày", "ser"),
]
TAGS = [
    (E(119.40), E(121.20), "ngồi bình thường = squat"),
    (E(37.40), E(39.20), "squat = nhóm cơ này?"),
]
EMOJI = [
    (E(119.40), TITLE_T0, "chair", 150, 520, 135),
    (E(37.40), E(40.70), "leg", 150, 520, 135),
    (E(104.60), E(109.60), "package", 150, 520, 140),
    (E(112.30), E(114.30), "house", 150, 520, 135),
    (E(201.40), E(205.65), "relieved", 900, 560, 150),
]
MARKS = []
CHECKLIST = [
    (E(59.90), E(67.70), 60, 480, "lift nặng hơn"),
    (E(62.30), E(67.70), 60, 570, "target nhóm cơ"),
    (E(67.00), E(67.70), 60, 660, "chỉ để bổ trợ"),
]
NUMBERS = []
PRICE = None
STRIKE_T = NEW_PRICE_T = 0
RECAP = (E(202.80), END)
RECAP_LINES = ["1.) không chỉ để tập nhóm cơ", "2.) bài tập giả lập hành động hằng ngày",
               "3.) mỗi người một mục tiêu", "4.) squat = bê vác đồ, ngồi xổm"]
