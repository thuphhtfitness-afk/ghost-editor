"""Office set 2: đau lưng dưới mà cứ giãn lưng? gốc có thể ở mông."""
from plan import to_edit as E, hook_end, timeline, FPS, BROLL
FIX = {"gái": "gáy", "vây": "vai", "biển": "ra", "dãn": "giãn", "cuộc": "cột", "Thằng": "cơ", "thằng": "cái", "gây": "kinh", "tọa": "toạ", "bí": "ý", "từ": "kiến", "ruỗi": "duỗi", "Đố": "cột", "rén": "rén", "elit": "elite", "cây": "cột", "cầu": "sống", "Không": "rồi", "Nhấp": "nhấc"}
TOTAL = timeline()[1]
OUTRO = None   # final.py --append assets/outro_ht.mp4
WATERMARK = dict(path="assets/logo_ht_white.png", x=120, y=1690, width=190, alpha=0.25)
CAP_Y = 1150
TAG_Y = 1035
KICKER_Y, TITLE_Y = 95, 190
RECAP_Y, RECAP_DY = 105, 58
CAP_X = 690
A = "assets/"
RX, CY, SC = 200, 760, 0.42   # muscle cards in the LEFT column (owner: never over the face)
WIN = (40, 160, 800, 1160)
MARKS = []; CHECKLIST = []; NUMBERS = []; PRICE = None; STRIKE_T = NEW_PRICE_T = 0; CUTOUTS = []; PANELS = []; EMOJI = []
TITLE_T0 = hook_end()
TITLE_CPS = 36
CTA = "ĐẶT BUỔI THẨM ĐỊNH VỚI HLV HPF"

FIX = {**FIX, "cây": "cây", "cầu": "cầu", "Không": "không", "gây": "kinh", "từ": "kiến", "thằng": "thằng", "Thằng": "cơ", "Dãn": "giãn"}
FIX_AT = {147.07: ""}
ENDCARD = dict(dur=8.0, title="LÀM NGAY", bullets=["Giãn mông 30 giây mỗi bên sau giờ làm", "Đau lan xuống chân, tê chân: đi khám"], cta=CTA, question="Bạn hay đau lưng vào lúc nào trong ngày?")
END = TOTAL / FPS + 0.2 + ENDCARD["dur"]
TITLE_END = E(174.90)
HOOK_END = TITLE_END
KICKER = "ĐAU LƯNG DƯỚI"
TITLE_LINES = ["cứ giãn lưng?", "gốc có thể ở mông"]
SECTIONS = [
    (E(143.15), E(158.30), "1.) CƠ MÔNG CĂNG", "chèn ép dây thần kinh toạ"),
    (E(193.20), E(199.10), "2.) NẾU ĐÃ THOÁT VỊ", "là vấn đề khác: cần bác sĩ"),
]
POPS = [
    (E(164.53), E(164.65), "mông", "ser"),
    (E(174.61), E(174.95), "nhẹ", "ser"),
]
TAGS = [
    (E(145.41), E(149.40), "cơ mông căng là MỘT nguyên nhân có thể gặp"),
    (E(197.19), E(199.10), "đau lan xuống chân, tê chân: đi khám"),
]
EMOJI = [(E(171.11), E(171.40), "weary", 900, 760, 160)]
ZPANELS = [
    (E(162.45), E(164.65), A + "p_glute.png", A + "p_glute_hot.png", RX, CY, SC, dict(focus=(270, 650), zoom=1.8, zoom_at=E(164.40), win=WIN)),
    (E(147.07), E(158.30), A + "p_glute.png", A + "p_glute_hot.png", RX, CY, SC, dict(focus=(300, 830), zoom=1.9, zoom_at=E(150.63), win=WIN)),
]
RECAP = (E(199.10), TOTAL / FPS + 0.2)
RECAP_LINES = []
