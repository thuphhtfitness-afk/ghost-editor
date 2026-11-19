"""Reel 8 content slots (th8: standing, face high; side-on demonstration 48-64 s stays uncovered)."""
from plan import to_edit as E, hook_end, timeline, FPS, BROLL

FIX = {"dày": "giày", "hót": "gót", "giấy": "gây", "hằng": "đằng"}
FIX_AT = {54.94: "ra đằng", 46.7: "", 46.82: "", 67.92: "ấy"}   # (original second of the word): text
TOTAL = timeline()[1]
END = TOTAL / FPS + 0.6
CAP_Y = 1090
TAG_Y = 975
KICKER_Y, TITLE_Y = 95, 190
RECAP_Y, RECAP_DY = 105, 58

TITLE_T0 = hook_end()
TITLE_END = E(28.75)
HOOK_END = TITLE_END
KICKER = "GIÀY CAO GÓT"
TITLE_LINES = ["ảnh hưởng thế nào", "đến tư thế?"]
SECTIONS = [
    (E(31.80), E(42.75), "1.) BẮP CHÂN", "luôn căng vì phải kiễng"),
    (E(42.90), E(47.90), "2.) CƠ GẤP HÔNG", "căng khi ngồi nhiều"),
    (E(48.45), E(60.30), "3.) KHUNG CHẬU", "lật ra đằng trước"),
    (E(60.66), E(72.10), "4.) LƯNG VÕNG", "mỏi lưng, lưng tải quá nhiều"),
    (E(75.30), E(84.10), "5.) KHÔNG PHẢI DO GIÀY", "mà giày + ngồi nhiều"),
]
POPS = [
    (E(74.42), E(74.95), "không sai", "ser"),
    (E(35.60), E(36.25), "căng bắp chân", "ser"),
    (E(46.70), E(47.85), "HIP FLEXOR", "osw"),
    (E(62.62), E(64.10), "lưng võng", "ser"),
    (E(83.30), E(84.10), "đau mỏi lưng", "ser"),
]
TAGS = [
    (E(53.16), E(55.55), "đẩy mông ra sau để giữ thăng bằng"),
    (E(49.08), E(51.35), "đi kiễng, ở trên cao"),
    (E(68.86), E(70.25), "lưng tải quá nhiều"),
]
EMOJI = [
    (E(73.48), E(74.95), "heel", 880, 760, 160),
    (E(44.66), E(45.75), "laptop", 880, 760, 150),
    (E(65.06), E(65.80), "weary", 880, 760, 160),
]
MARKS = []
CHECKLIST = []
NUMBERS = []
PRICE = None
STRIKE_T = NEW_PRICE_T = 0
CUTOUTS = []
A = "assets/"
PY = 1480
PANELS = [   # (t0, t1, card, x, y, scale[, full-screen backdrop])
    (E(35.14), E(42.70), A + "calf_heel.png", 540, PY, 0.98),
    (E(44.88), E(47.90), A + "hip_flexor.png", 540, PY, 0.98),
    (E(58.62), E(60.66), A + "pelvis_tilt.png", 540, PY, 0.98),   # low band: his hips stay visible above it
    (E(65.06), E(72.10), A + "lordosis.png", 540, PY, 0.98),
    (E(76.60), E(84.10), A + "back_chain.png", 540, PY, 0.98),
]
RECAP = (E(81.24), END)
RECAP_LINES = ["1.) kiễng gót: bắp chân căng", "2.) ngồi nhiều: cơ gấp hông căng",
               "3.) khung chậu lật ra trước", "4.) lưng võng, mỏi lưng"]
