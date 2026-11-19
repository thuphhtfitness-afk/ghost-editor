"""Office set 1: mỏi cổ vai gáy không phải do ngồi nhiều."""
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

FIX = {**FIX, "Thằng": "thằng", "thằng": "thằng", "cuộc": "cuộc", "cây": "cây", "cầu": "cầu", "Không": "không", "từ": "từ", "gây": "gây"}
ENDCARD = dict(dur=7.0, title="LÀM NGAY", bullets=["Kéo 2 vai ra sau, thu cằm: 10 lần mỗi giờ"], cta=CTA, question="Bạn ngồi máy tính mấy tiếng mỗi ngày?")
END = TOTAL / FPS + 0.2 + ENDCARD["dur"]
TITLE_END = E(66.90)
HOOK_END = TITLE_END
KICKER = "DÂN VĂN PHÒNG"
TITLE_LINES = ["mỏi cổ vai gáy", "không phải do ngồi nhiều"]
SECTIONS = [
    (E(91.05), E(101.95), "1.) MỌI NGƯỜI HAY NGHĨ", "do ngồi nhiều"),
    (E(111.72), E(125.55), "2.) THỰC RA", "vai xoay ra trước, cơ thang co lên"),
]
POPS = [
    (E(108.27), E(111.00), "chưa phải lý do", "ser"),
    (E(122.19), E(122.60), "CO LÊN", "osw"),
]
TAGS = [
    (E(62.49), E(64.30), "vấn đề chung: đau mỏi cổ vai gáy"),
    (E(118.77), E(120.50), "vai xoay ra trước"),
]
EMOJI = [(E(58.25), E(59.20), "laptop", 900, 760, 150), (E(124.99), E(125.55), "weary", 900, 760, 160)]
ZPANELS = [(E(111.77), E(125.55), A + "p_trap.png", A + "p_trap_hot.png", RX, CY, SC, dict(focus=(420, 560), zoom=1.9, zoom_at=E(122.10), win=WIN))]
RECAP = (E(125.55), TOTAL / FPS + 0.2)
RECAP_LINES = []
INTRO = dict(top="VÌ SAO BẠN HAY", big="MỎI CỔ - VAI - GÁY")
