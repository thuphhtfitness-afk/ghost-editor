"""Office set 3: ngồi thẳng như sách giáo khoa cũng đau lưng."""
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

FIX = {**FIX, "cây": "cây", "cầu": "cầu", "Không": "không", "từ": "từ", "gây": "gây", "thằng": "thằng", "Thằng": "thằng"}
ENDCARD = dict(dur=7.0, title="LÀM NGAY", bullets=["Tư thế tốt nhất là tư thế tiếp theo", "Đứng dậy vận động mỗi 45-60 phút"], cta=CTA, question="Bạn ngồi liền bao lâu mới đứng dậy?")
END = TOTAL / FPS + 0.2 + ENDCARD["dur"]
TITLE_END = E(227.05)
HOOK_END = TITLE_END
KICKER = "NGỒI THẲNG NHƯ SÁCH"
TITLE_LINES = ["cũng đau lưng?"]
SECTIONS = [(E(236.25), E(262.10), "ĐĨA ĐỆM", "cần cột sống co duỗi để nhận dinh dưỡng")]
POPS = [(E(234.94), E(235.65), "áp lực", "ser"), (E(261.82), E(262.10), "yếu dần", "ser")]
TAGS = []
FLABELS = [(E(222.94), E(227.05), "ngồi yên một tư thế cả ngày", 690, 1035, "no")]
ZPANELS = [(E(237.24), E(262.10), A + "p_disc.png", A + "p_disc.png", RX, CY, SC, dict(focus=(420, 700), zoom=1.0, zoom_at=None, win=WIN))]
RECAP = (E(262.10), TOTAL / FPS + 0.2)
RECAP_LINES = []
INTRO = dict(top="NGỒI THẲNG", big="CŨNG ĐAU LƯNG?", y=800)
