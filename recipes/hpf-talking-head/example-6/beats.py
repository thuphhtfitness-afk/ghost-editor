"""Reel 6 content slots. Times: E(<0081 second>) or E(B + <0082 second>)."""
from plan import to_edit as E, hook_end, timeline, FPS, BROLL, B

FIX = {"thải": "giải", "áo": "áp", "calor": "calo", "Người": "thì", "dream": "", "Back": "back"}
TOTAL = timeline()[1]
END = TOTAL / FPS + 0.6

TITLE_T0 = hook_end()
TITLE_END = E(151.80)
HOOK_END = TITLE_END
KICKER = "DÂN VĂN PHÒNG"
TITLE_LINES = ["lưu ý tập luyện", "dành cho dân văn phòng"]
SECTIONS = [
    (E(B + 289.40), E(162.25), "1.) ĐI TẬP ĐÃ LÀ", "một nỗ lực rất lớn"),
    (E(163.10), E(B + 319.50), "2.) ĐỪNG ÉP VÀO KHUÔN KHỔ", "không phải ai cũng chịu được áp lực"),
    (E(B + 323.50), E(B + 338.55), "3.) 21 NGÀY", "để hình thành một thói quen mới"),
    (E(248.40), E(267.40), "4.) TẬP HAY ĐI LÀM?", "hai cái bổ trợ cho nhau"),
    (E(274.70), E(B + 353.60), "5.) ĐIỀU CHỈNH", "làm sao thoải mái, đơn giản nhất"),
]
POPS = [
    (E(273.80), E(274.15), "không đáng", "ser"),
    (E(151.20), E(151.80), "vận động ít", "ser"),
    (E(B + 294.87), E(B + 295.70), "nỗ lực rất lớn", "ser"),
    (E(164.28), E(165.30), "áp lực", "ser"),
    (E(B + 312.31), E(B + 312.62), "khuôn khổ", "ser"),
    (E(B + 333.59), E(B + 334.25), "lối sống", "ser"),
    (E(255.20), E(256.00), "bổ trợ", "ser"),
    (E(266.42), E(267.40), "không giải quyết", "ser"),
    (E(278.14), E(278.85), "thoải mái nhất", "ser"),
    (E(B + 350.21), E(B + 351.00), "đơn giản nhất", "ser"),
    (E(B + 352.41), E(B + 353.60), "BACK TO BASIC", "osw"),
]
TAGS = [
    (E(160.92), E(162.25), "một lối sống, một thói quen mới"),
    (E(B + 317.79), E(B + 319.50), "không phải ai cũng chịu được áp lực"),
]
EMOJI = [
    (E(117.60), E(118.60), "office", 150, 800, 135),
    (E(147.08), E(151.80), "laptop", 150, 800, 135),
    (E(B + 286.75), E(B + 289.35), "seedling", 150, 800, 135),
    (E(B + 325.51), E(B + 327.40), "calendar", 160, 470, 130),
    (E(B + 335.35), E(B + 338.55), "seedling", 150, 800, 135),
    (E(250.48), E(256.00), "lifting", 330, 470, 140),
    (E(252.18), E(256.00), "briefcase", 750, 470, 140),
    (E(255.20), E(256.00), "scale", 540, 620, 130),
    (E(262.84), E(264.20), "weary", 860, 640, 165),
]
MARKS = []
CHECKLIST = [
    (E(269.46), E(274.15), 70, 800, "thân hình đẹp hơn", "ok"),
    (E(270.58), E(274.15), 70, 900, "stress hơn, làm việc kém", "no"),
]
NUMBERS = [
    (E(B + 325.51), E(B + 327.40), "21 NGÀY", 600, 470),
    (E(251.92), E(256.00), "VS", 540, 470),
]
PRICE = (E(B + 291.35), E(B + 295.70), "KHÔNG VẬN ĐỘNG", "ĐI TẬP")
STRIKE_T = E(B + 293.33)
NEW_PRICE_T = E(B + 293.99)
RECAP = (E(B + 349.20), END)
RECAP_LINES = ["1.) đi tập đã là nỗ lực rất lớn", "2.) đừng ép vào khuôn khổ ngay", "3.) 21 ngày để thành thói quen",
               "4.) tập và đi làm bổ trợ cho nhau", "5.) điều chỉnh cho thoải mái nhất"]
