"""HPF talking head: the content slots of ONE reel (overlay.py imports this from the reel project).
Every time is E(<original second of the source clip>), so it follows the cut."""
from plan import to_edit as E, hook_end, timeline, FPS, BROLL

FIX = {"đá": "đá", "công": "cốc", "calor": "calo", "-70": "-70", "-65": "-65"}
TOTAL = timeline()[1]
END = TOTAL / FPS + 0.6   # held tail
# ---------------- beats ----------------
TITLE_T0 = hook_end()          # cold-open hook ends: flash + click, the title starts
TITLE_END = E(64.50)
HOOK_END = TITLE_END
SECTIONS = [  # (t0, t1, line1, line2)
    (E(134.00), E(141.70), "1.) KHÁCH GIẢM CÂN", "ăn trong ngưỡng thâm hụt"),
    (E(167.46), E(197.86), "2.) ĐỪNG ĐỂ VIỆC ĂN UỐNG", "thành thêm một nỗi stress"),
    (E(226.02), E(289.28), "3.) CHẤP NHẬN", "kết quả sẽ đến muộn hơn"),
    (E(311.12), E(353.15), "4.) ĐIỀU CHỈNH", "các bữa còn lại trong ngày"),
]
# keyword pops in the caption zone: (t0, t1, text, style)  style: ser / osw
POPS = [
    (E(62.70), E(63.86), "vấn đề chung", "ser"),
    (E(137.66), E(138.50), "CALO", "osw"),
    (E(140.90), E(141.70), "thâm hụt", "ser"),
    (E(177.20), E(177.95), "STRESS", "osw"),
    (E(183.80), E(184.60), "niềm vui", "ser"),
    (E(283.36), E(283.95), "ăn đói", "ser"),
    (E(286.20), E(288.40), "vừa đói\nvừa chán", "ser"),
    (E(308.26), E(308.80), "dở hơi", "ser"),
]
TAGS = [  # (t0, t1, text)
    (E(169.40), E(171.95), "đi tập = stress lên cơ thể"),
    (E(227.50), E(228.58), "kết quả đến muộn"),
    (E(303.60), E(306.00), "cả phòng đặt đồ ăn"),
]
# emoji stickers: (t0, t1, name, x, y, size)
EMOJI = [
    (E(51.28), HOOK_END, "coffee", 150, 780, 135),
    (E(54.28), HOOK_END, "bubbletea", 150, 945, 135),
    (E(60.20), HOOK_END, "fries", 150, 1110, 135),
    (E(177.20), E(178.08), "sweat", 860, 640, 170),
    (E(183.80), E(184.60), "yum", 860, 640, 170),
    (E(192.36), E(197.86), "coffee", 400, 480, 160),
    (E(196.30), E(197.86), "cookie", 680, 480, 160),
    (E(227.50), E(228.58), "hourglass", 860, 640, 160),
    (E(286.20), E(288.40), "weary", 860, 640, 170),
    (E(308.26), E(308.80), "zany", 860, 640, 170),
    (E(330.52), E(344.76), "bento", 880, 470, 150),
    (E(342.06), E(344.76), "down", 170, 650, 110),
    (E(354.24), E(356.78), "plate", 860, 640, 160),
]
MARKS = [  # check / cross badges on emoji: (t0, t1, x, y, kind)
    (E(192.70), E(197.86), 455, 540, "ok"),
    (E(196.60), E(197.86), 735, 540, "no"),
]
PRICE = (E(331.58), E(344.76), "60-70K", "50-65K")      # price card: (t0, t1, old, new)
STRIKE_T = E(338.74)
NEW_PRICE_T = E(342.06)
RECAP = (E(353.20), END)
RECAP_LINES = ["1.) ăn trong ngưỡng thâm hụt", "2.) ăn uống không thành stress",
               "3.) chấp nhận kết quả đến muộn", "4.) điều chỉnh các bữa còn lại"]
KICKER = "DÂN VĂN PHÒNG"
TITLE_LINES = ["giảm cân sao cho", "đỡ stress?"]
CHECKLIST = []   # (t0, t1, x, y, text) ticked lines on the plain wall
NUMBERS = []     # (t0, t1, text, x, y) big Oswald cream numbers in the top zone
