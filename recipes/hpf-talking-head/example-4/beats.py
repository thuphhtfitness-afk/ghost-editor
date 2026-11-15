"""Reel 4 content slots. Times: E(<original second of 0082>)."""
from plan import to_edit as E, hook_end, timeline, FPS, BROLL

FIX = {"Người": "thì", "dream": "", "Back": "back"}
TOTAL = timeline()[1]
END = TOTAL / FPS + 0.6

TITLE_T0 = hook_end()
TITLE_END = E(283.00)
HOOK_END = TITLE_END
KICKER = "NGƯỜI MỚI ĐI TẬP"
TITLE_LINES = ["thích nghi dần,", "đừng ép khuôn khổ"]
SECTIONS = [
    (E(283.90), E(299.35), "1.) VỚI NGƯỜI MỚI", "đi tập đã là nỗ lực rất lớn"),
    (E(305.70), E(319.50), "2.) KHÔNG ÉP VÀO", "khuôn khổ ngay từ đầu"),
    (E(323.50), E(338.55), "3.) 21 NGÀY", "để hình thành một thói quen mới"),
    (E(345.80), E(352.20), "4.) THÍCH NGHI DẦN", "làm sao đơn giản nhất"),
]
POPS = [
    (E(341.43), E(342.20), "nghĩa vụ", "ser"),
    (E(344.89), E(345.60), "lựa chọn", "ser"),
    (E(294.87), E(295.70), "nỗ lực rất lớn", "ser"),
    (E(312.31), E(312.62), "khuôn khổ", "ser"),
    (E(319.09), E(319.50), "áp lực", "ser"),
    (E(333.59), E(334.25), "lối sống", "ser"),
    (E(350.21), E(351.00), "đơn giản nhất", "ser"),
    (E(352.41), E(353.60), "BACK TO BASIC", "osw"),
]
TAGS = [
    (E(340.41), E(342.95), "đi lính = nghĩa vụ"),
    (E(343.55), E(345.60), "đi tập = lựa chọn"),
    (E(297.21), E(299.35), "không phải ai cũng chịu được áp lực"),
]
EMOJI = [
    (E(339.60), TITLE_T0, "helmet", 150, 800, 135),
    (E(286.75), E(289.35), "seedling", 150, 800, 135),
    (E(296.89), E(299.35), "sweat", 860, 640, 165),
    (E(325.51), E(327.40), "calendar", 160, 470, 130),
    (E(335.35), E(338.55), "seedling", 150, 800, 135),
]
MARKS = []
CHECKLIST = []
NUMBERS = [
    (E(325.51), E(327.40), "21 NGÀY", 600, 470),
]
PRICE = (E(291.35), E(295.70), "KHÔNG VẬN ĐỘNG", "ĐI TẬP")   # strike on "đến", new on "đi tập"
STRIKE_T = E(293.33)
NEW_PRICE_T = E(293.99)
RECAP = (E(349.20), END)
RECAP_LINES = ["1.) đi tập đã là nỗ lực rất lớn", "2.) đừng ép vào khuôn khổ ngay",
               "3.) 21 ngày để thành thói quen", "4.) thích nghi dần, back to basic"]
