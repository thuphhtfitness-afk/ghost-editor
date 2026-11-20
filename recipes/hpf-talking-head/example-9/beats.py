"""Reel 7 v3 (parents): kid lead-in + big question, hook on 'càng lớn càng ảnh hưởng sinh hoạt', side-column portrait
cards with ligament zoom, end card 'NÊN LÀM GÌ?' (channel text, not the coach's words), logo, channel outro."""
from plan import to_edit as E, hook_end, timeline, FPS, BROLL

FIX = {"trụng": "chụm", "trăng": "chằng", "trắng": "chằng", "tiết": "tiếp", "Ngoạt": "ngoặt"}
TOTAL = timeline()[1]
ENDCARD = None   # owner: no black end card; the host finishes his point, then the channel outro
END = TOTAL / FPS + 0.6
OUTRO = None   # the channel outro clip is appended: final.py --append assets/outro_ht.mp4
WATERMARK = dict(path="assets/logo_ht_white.png", x=955, y=480, width=170, alpha=0.3)
CAP_Y = 1090
TAG_Y = 975
KICKER_Y, TITLE_Y = 95, 190
RECAP_Y, RECAP_DY = 105, 58
FLASH = False
TITLE_SFX = False   # owner: no sound effect on the opening shot

TITLE_T0 = 1.2                     # the freeze, then the photo and the title (silent: only the coach's voice)
TITLE_END = hook_end()
TITLE_CPS = 40
HOOK_END = TITLE_END
KICKER = "PHỤ HUYNH CẦN BIẾT"
TITLE_LINES = ["Con bạn bị", "bàn chân bẹt?"]
SECTIONS = [
    (E(25.45), E(31.65), "1.) BÀN CHÂN BẸT", "trục gót chân đổ vào trong"),
    (E(32.70), E(48.45), "2.) KHỚP GỐI", "chụm vào trong thành chữ X"),
    (E(48.80), E(68.30), "3.) DÂY CHẰNG", "chịu áp lực không phải của nó"),
    (E(68.95), E(87.65), "4.) KHI CHƠI THỂ THAO", "rất dễ gặp chấn thương"),
]
POPS = [
    (E(113.06), E(114.30), "càng lớn", "ser"),
    (E(43.42), E(43.85), "CHỮ X", "osw"),
    (E(54.74), E(55.40), "áp lực", "ser"),
    (E(73.68), E(74.20), "chấn thương", "ser"),
]
TAGS = [
    (E(114.86), E(115.90), "sinh hoạt hằng ngày"),
    (E(77.04), E(79.20), "chỉ cần tiếp đất sai"),
    (E(81.86), E(83.30), "nói đứt thì hơi quá"),
    (E(116.66), E(118.10), "nhất là khi chơi thể thao nhiều"),
    (E(58.58), E(61.25), "chịu áp lực không phải của nó"),
]
EMOJI = [
    (E(73.42), E(74.20), "sweat", 220, 760, 160),
    (E(70.68), E(72.60), "soccer", 220, 760, 150),
]
MARKS = []; CHECKLIST = []; NUMBERS = []; PRICE = None; STRIKE_T = NEW_PRICE_T = 0; CUTOUTS = []; PANELS = []
A = "assets/"
RX, LX, CY, SC = 858, 222, 740, 0.47
WIN = (40, 160, 800, 1160)
ZPANELS = [   # (t0, t1, plain, hot, x, y, scale, {focus, zoom, zoom_at})
    (E(40.80), E(43.85), A + "p_legs.png", A + "p_legs.png", RX, CY, SC, dict(focus=(420, 700), zoom=1.0, zoom_at=None, win=WIN)),
    (E(23.02), E(27.60), A + "p_blank_flat.png", A + "p_blank_flat.png", RX, CY, SC, dict(focus=(420, 700), zoom=1.0, zoom_at=None, win=WIN)),
    (E(27.64), E(31.62), A + "p_heel.png", A + "p_heel.png", RX, CY, SC, dict(focus=(420, 700), zoom=1.0, zoom_at=None, win=WIN)),
    (E(37.72), E(40.40), A + "p_legs.png", A + "p_legs.png", RX, CY, SC, dict(focus=(420, 700), zoom=1.0, zoom_at=None, win=WIN)),
    (E(50.48), E(61.25), A + "p_mcl.png", A + "p_mcl_hot.png", RX, CY, SC, dict(focus=(220, 640), zoom=2.0, zoom_at=E(50.76), win=WIN)),
    (E(64.74), E(68.25), A + "p_inside.png", A + "p_inside_hot.png", RX, CY, SC, dict(focus=(400, 520), zoom=2.0, zoom_at=E(67.10), win=WIN)),
]
# the channel's foot photos, cut out, moving inside the blank portrait card (card centre RX, CY; 395 x 733 on screen)
MOVERS = [   # the channel's foot photos in the blank portrait card; each label sits UNDER its photo, never on it
    (E(23.02), E(25.40), A + "healthy_clean.png", RX, CY - 175, 0.48, dict(slide=(120, 0), zoom=(1.0, 1.03))),
    (E(23.02), E(25.40), A + "flat_clean.png", RX, CY + 150, 0.48, dict(slide=(120, 0), delay=0.25, zoom=(1.0, 1.03))),
    (E(25.45), E(27.60), A + "supported_clean.png", RX, CY - 175, 0.30, dict(slide=(0, 80), zoom=(1.0, 1.03))),
    (E(25.45), E(27.60), A + "collapsed_clean.png", RX, CY + 150, 0.30, dict(slide=(0, 80), delay=0.2, zoom=(1.0, 1.03))),
]
FLABELS = [   # (t0, t1, text, x, y, ok/no, scale)
    (E(23.25), E(25.40), "bình thường", RX, CY - 20, "ok", 0.72),
    (E(23.50), E(25.40), "bàn chân bẹt", RX, CY + 305, "no", 0.72),
    (E(25.60), E(27.60), "có vòm", RX, CY - 45, "ok", 0.72),
    (E(25.80), E(27.60), "vòm sập xuống", RX, CY + 280, "no", 0.72),
]
CAP_X = 540   # captions centred (owner)
RECAP = (E(116.05), END)
RECAP_LINES = ["1.) bàn chân bẹt: gót đổ vào trong", "2.) khớp gối chụm thành chữ X",
               "3.) dây chằng chịu áp lực", "4.) chơi thể thao dễ chấn thương"]

INTRO = dict(kind="two", l1="BÀN CHÂN BẸT", l2="Ở TRẺ EM?", photo="assets/flat_clean.png", photo_until=1.75, y=1060)
