"""Reel 5 content slots. Times: E(<original second of 0081>)."""
from plan import to_edit as E, hook_end, timeline, FPS, BROLL

FIX = {"thải": "giải", "áo": "áp", "calor": "calo"}
TOTAL = timeline()[1]
END = TOTAL / FPS + 0.6

TITLE_T0 = hook_end()
TITLE_END = E(151.80)
HOOK_END = TITLE_END
KICKER = "DÂN VĂN PHÒNG"
TITLE_LINES = ["tập hay đi làm", "quan trọng hơn?"]
SECTIONS = [
    (E(152.40), E(167.60), "1.) KHI DÂN VĂN PHÒNG ĐI TẬP", "họ đã cố gắng rất nhiều"),
    (E(248.40), E(256.00), "2.) TẬP HAY ĐI LÀM?", "hai cái bổ trợ cho nhau"),
    (E(257.90), E(267.40), "3.) ĐÁNH ĐỔI SỨC KHỎE", "thì đi tập cũng không giải quyết"),
    (E(274.70), E(276.90), "4.) ĐIỀU CHỈNH", "làm sao thoải mái nhất"),
]
POPS = [
    (E(273.80), E(274.15), "không đáng", "ser"),
    (E(151.20), E(151.80), "vận động ít", "ser"),
    (E(157.40), E(158.25), "cố gắng rất nhiều", "ser"),
    (E(164.28), E(165.30), "áp lực", "ser"),
    (E(255.20), E(256.00), "bổ trợ", "ser"),
    (E(266.42), E(267.40), "không giải quyết", "ser"),
    (E(278.14), E(278.85), "thoải mái nhất", "ser"),
]
TAGS = [
    (E(269.46), E(270.50), "thân hình đẹp hơn"),
    (E(270.58), E(272.20), "nhưng stress hơn, làm việc kém"),
    (E(160.92), E(162.25), "một lối sống, một thói quen mới"),
]
EMOJI = [
    (E(250.48), E(256.00), "lifting", 330, 470, 140),
    (E(252.18), E(256.00), "briefcase", 750, 470, 140),
    (E(255.20), E(256.00), "scale", 540, 620, 130),
    (E(262.84), E(264.20), "weary", 860, 640, 165),
    (E(147.08), E(151.80), "office", 150, 800, 135),
]
MARKS = [
    (E(269.70), E(274.15), 150, 800, "ok"),
    (E(270.58), E(274.15), 150, 900, "no"),
]
CHECKLIST = []
NUMBERS = [(E(251.92), E(256.00), "VS", 540, 470)]
PRICE = None
STRIKE_T = NEW_PRICE_T = 0
RECAP = (E(276.90), END)
RECAP_LINES = ["1.) đi tập đã là cố gắng rất nhiều", "2.) tập và đi làm bổ trợ cho nhau",
               "3.) đánh đổi sức khỏe thì không đáng", "4.) điều chỉnh cho thoải mái nhất"]
