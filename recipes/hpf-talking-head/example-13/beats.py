"""Office set 4 (case): chị khách thoát vị, từ thói quen ngồi đến lúc dám tập lại."""
from plan import to_edit as E, hook_end, timeline, FPS, BROLL
FIX = {"gái": "gáy", "vây": "vai", "biển": "ra", "dãn": "giãn", "cuộc": "cột", "Thằng": "cơ", "thằng": "cái", "gây": "kinh", "tọa": "toạ", "bí": "ý", "từ": "kiến", "ruỗi": "duỗi", "Đố": "cột", "rén": "rén", "elit": "elite", "cây": "cột", "cầu": "sống", "Không": "rồi", "Nhấp": "nhấc"}
TOTAL = timeline()[1]
OUTRO = None   # final.py --append assets/outro_ht.mp4
WATERMARK = dict(path="assets/logo_ht_white.png", x=955, y=390, width=170, alpha=0.3)   # top right, on the wood slats (owner)
CAP_Y = 1150
TAG_Y = 1035
KICKER_Y, TITLE_Y = 95, 190
RECAP_Y, RECAP_DY = 105, 58
CAP_X = 540   # captions centred (owner)
A = "assets/"
RX, CY, SC = 200, 760, 0.42   # muscle cards in the LEFT column (owner: never over the face)
WIN = (40, 160, 800, 1160)
MARKS = []; CHECKLIST = []; NUMBERS = []; PRICE = None; STRIKE_T = NEW_PRICE_T = 0; CUTOUTS = []; PANELS = []; EMOJI = []
TITLE_T0 = hook_end()
TITLE_CPS = 36
CTA = "ĐẶT BUỔI THẨM ĐỊNH VỚI HLV HPF"

FIX = {**FIX, "từ": "từ", "gây": "gây", "thằng": "thằng", "Thằng": "thằng", "Nhấp": "nhấc", "Không": "rồi", "người": "người"}
FIX_AT = {322.78: "người", 322.58: "rồi", 313.82: "cái", 314.14: "cột", 314.38: "sống", 314.54: "", 323.44: "như"}
ENDCARD = dict(dur=7.5, title="BỊ ĐAU ≠ BỎ TẬP", bullets=["Bị đau không có nghĩa là phải bỏ tập, mà là tập đúng với cơ thể mình"], cta=CTA, question="Bạn từng phải nghỉ tập vì đau lưng chưa?")
END = TOTAL / FPS + 0.2 + ENDCARD["dur"]
TITLE_END = E(309.10)
HOOK_END = TITLE_END
KICKER = "CASE STUDY"
TITLE_LINES = ["chị khách thoát vị", "dám tập lại"]
SECTIONS = [
    (E(309.20), E(325.85), "1.) VÌ SAO THOÁT VỊ MỘT BÊN", "thói quen ngồi lệch lâu ngày"),
    (E(364.35), E(408.95), "2.) SỢ DEADLIFT", "chỉnh technique, tập lại"),
]
POPS = [
    (E(389.88), E(390.30), "DEADLIFT", "osw"),
    (E(406.58), E(406.80), "mông", "ser"),
]
TAGS = [
    (E(320.48), E(325.85), "thói quen ngồi lệch lâu ngày là MỘT yếu tố"),
    (E(399.86), E(408.95), "đã được bác sĩ cho phép · HLV điều chỉnh riêng"),
]
FLABELS = [(E(309.56), E(312.90), "ngồi lệch một bên", 540, 930, "no"), (E(319.12), E(320.40), "gác chân", 540, 930, "no")]
ZPANELS = [(E(313.82), E(320.40), A + "p_lean.png", A + "p_lean.png", RX, CY, SC, dict(focus=(420, 700), zoom=1.0, zoom_at=None, win=WIN))]
RECAP = (E(408.95), TOTAL / FPS + 0.2)
RECAP_LINES = []
INTRO = dict(top="TẬP GYM CHO NGƯỜI", big="THOÁT VỊ ĐĨA ĐỆM?", y=800, big_size=170)
