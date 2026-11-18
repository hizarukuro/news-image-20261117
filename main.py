#!/usr/bin/env python3
"""
news-image-20261117 — entry program (v2).

Renders ONE 1024x1024 PNG: a newspaper front page summing up the news of
Tuesday 17 November 2026 — 43 stories across 6 continents, drawn entirely
with PIL (flat original illustrations, a dotted world map with numbered
pins, numbered briefs, and a data chip on every illustrated cell).

Deterministic: no timestamps, no randomness — same bytes on every run.
Output: $MAKEFUN_OUTPUT_DIR/entry.png (fallback /output/entry.png).
"""
import os

from PIL import Image, ImageDraw, ImageFont

# --------------------------------------------------------------------------
# Canvas + palette
# --------------------------------------------------------------------------
W = H = 1024
MARGIN = 14
CW = W - 2 * MARGIN  # content width = 996

CREAM = (248, 243, 230)
PAPER_EDGE = (240, 233, 214)
INK = (17, 17, 17)
SOFT_INK = (52, 50, 46)
RULE = (17, 17, 17)
RED = (178, 34, 34)
CHIP_BG = (17, 17, 17)
CHIP_FG = (255, 255, 255)

CONTINENT_COLORS = {
    "Europe": (37, 99, 235),
    "Middle East": (217, 119, 6),
    "Asia": (220, 38, 38),
    "Africa": (22, 163, 74),
    "Americas": (124, 58, 237),
    "Oceania": (8, 145, 178),
}

# --------------------------------------------------------------------------
# Fonts (Liberation first — narrow, newspaper-like; DejaVu fallback)
# --------------------------------------------------------------------------
_FONT_DIRS = ["/usr/share/fonts/truetype/liberation",
              "/usr/share/fonts/truetype/dejavu"]


def _font(filename, size, fallback="DejaVuSans.ttf"):
    for d in _FONT_DIRS:
        p = os.path.join(d, filename)
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    for d in _FONT_DIRS:
        p = os.path.join(d, fallback)
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def serif_b(size):
    return _font("LiberationSerif-Bold.ttf", size, "DejaVuSerif-Bold.ttf")


def serif(size):
    return _font("LiberationSerif-Regular.ttf", size, "DejaVuSerif.ttf")


def sans_b(size):
    return _font("LiberationSans-Bold.ttf", size, "DejaVuSans-Bold.ttf")


def sans(size):
    return _font("LiberationSans-Regular.ttf", size, "DejaVuSans.ttf")


F_KICKER = sans_b(11)
F_KICKER_R = sans_b(11)
F_STRIP = sans_b(9)
F_HERO_HEAD = serif_b(17)
F_HERO_SUM = sans(12)
F_GRID_HEAD = serif_b(12)
F_GRID_SUM = sans(12)
F_CHIP = sans_b(10)
F_CHIP_S = sans_b(9)
F_MAP_HEAD = serif_b(13)
F_LEGEND = sans(10)
F_BRIEF = sans(11)
F_BRIEF_B = sans_b(11)
F_BRIEF_CHIP = sans_b(9)
F_FOOT = sans(10)
F_FOOT_B = sans_b(10)

# --------------------------------------------------------------------------
# Story data — headlines and summaries written for this page; every fact
# and figure is from the day's verified wire reports.
# --------------------------------------------------------------------------
# Heroes: (num, continent, kicker, chip, headline, summary, illustration)
HEROES = [
    (1, "Europe", "EUROPE · UKRAINE WAR", "2 STRIKES IN 2 DAYS",
     "Crimean Bridge span crashes into the Kerch Strait",
     "Second strike in two days on the Kerch crossing. Zelenskyy hails an "
     "\u201cunprecedented operation\u201d; the Kremlin vows to rebuild the span.",
     "bridge"),
    (2, "Middle East", "MIDDLE EAST · IRAN WAR", "ALL DRONES DOWNED",
     "Iran fires drones at a US radar site in Bahrain",
     "Bahrain and Washington say every drone was downed. US jets then "
     "strike Qeshm island; Tehran says its tankers hit mines in Hormuz.",
     "mideast"),
    (3, "Asia", "ASIA · DIPLOMACY", "4 NATIONS",
     "Trump convenes his first Quad summit in Manila",
     "The US, India, Japan and Australia unveil critical-minerals deals, "
     "as Putin reaches Shenzhen for Thursday's talks with Trump and Xi.",
     "quad"),
]

# Grid: (num, continent, kicker, chip, headline, summary, illustration)
GRID = [
    (4, "Africa", "AFRICA · HEALTH", "11,000+ CASES",
     "Ebola cases in DR Congo pass 11,000",
     "WHO count more than doubles in three months; some 5,400 dead.",
     "virus"),
    (5, "Middle East", "GLOBAL · CLIMATE", "DRAFT: PHASE OUT",
     "COP31 split over fossil-fuel phase-out",
     "Nations weigh a first draft in Antalya; talks close Friday.",
     "climate"),
    (6, "Americas", "AMERICAS · HEALTH", "MEASLES-FREE STATUS REVOKED",
     "Three countries lose measles-free status",
     "PAHO acts after a year of spread; US cases top 5,700 in 2026.",
     "shield"),
    (7, "Americas", "US · BUSINESS", "$115.8BN · DOW \u2212849",
     "Nvidia sales double to $115.8 billion",
     "Quarterly revenue doubles; earlier, the Dow fell 849 points.",
     "chart"),
    (8, "Middle East", "MIDDLE EAST · GAZA", "1.4M IN ACUTE HUNGER",
     "UN told Gaza truce risks collapse",
     "Peace board reports as agencies say 1.4m face acute hunger.",
     "dove"),
    (9, "Asia", "ASIA · POLITICS", "RESIGNATION",
     "Mongolia's president says he will quit",
     "Kh\u00fcrels\u00fckh denies a $25m bribe claim; parliament must agree.",
     "ger"),
    (10, "Europe", "EUROPE · POLITICS", "140 / 250 SEATS",
     "Serbia's students take their seats",
     "Student List wins 140 of 250; Vu\u010di\u0107's party in opposition.",
     "parliament"),
    (11, "Asia", "ASIA · LABOUR", "TK 30,000 A MONTH",
     "Police tear-gas Dhaka garment workers",
     "They seek Tk 30,000 a month, up from 12,500; 37 plants shut.",
     "factory"),
    (12, "Asia", "RUSSIA · AIR CRASH", "ALL 19 KILLED",
     "Siberia air crash kills all 19 aboard",
     "Air force An-12 down near Kemerovo; a fault is suspected.",
     "crash"),
    (13, "Africa", "AFRICA · JUSTICE", "5 CHARGES",
     "Mozambique tries opposition leader",
     "Mondlane faces five charges over the deadly 2024 protests.",
     "scales"),
]

# Briefs 14-43: (num, bold lead-in, line, continent for the map dot)
BRIEFS = [
    (14, "Russia:", "record 1,441 drones downed overnight", "Asia"),
    (15, "Kyiv:", "missiles hit North and South Dnipro bridges", "Europe"),
    (16, "UN:", "Ukraine civilian deaths this year top 2025", "Europe"),
    (17, "Prague:", "two trains collide; 46 people injured", "Europe"),
    (18, "France:", "strike: 146,000 march; CGT says 500,000", "Europe"),
    (19, "Poland:", "Tusk survives a confidence vote", "Europe"),
    (20, "Germany:", "Deutsche Bank falls after huge data leak", "Europe"),
    (21, "Moldova:", "airspace shut as drone nears Chi\u0219in\u0103u", "Europe"),
    (22, "Turkey:", "seizes opposition broadcaster S\u00f6zc\u00fc TV", "Middle East"),
    (23, "Football:", "Norway win 3\u20132 in Denmark; Haaland 2", "Europe"),
    (24, "Vatican:", "Pope Leo XIV returns from S. America", "Europe"),
    (25, "UK:", "sanctions on 8 settlement firms and Tzav 9", "Europe"),
    (26, "Israel:", "Eisenkot ally Kahana is speaker, 66\u201352", "Middle East"),
    (27, "West Bank:", "settlers kill a woman, 72, near Jericho", "Middle East"),
    (28, "Oman:", "Iran's Araghchi in shipping-safety talks", "Middle East"),
    (29, "India:", "Cyclone Akvan grows; Odisha evacuates", "Asia"),
    (30, "India:", "bus falls into Uttarakhand gorge; 8 dead", "Asia"),
    (31, "Japan:", "protests a Russian airspace intrusion near Fukuoka", "Asia"),
    (32, "China\u2013Canada:", "tariff cuts after Carney\u2013Xi talks", "Asia"),
    (33, "Malaysia:", "Macron visit seals strategic partnership", "Asia"),
    (34, "Thailand:", "pledges to scrap tariffs on US goods", "Asia"),
    (35, "South Korea:", "IMF raises 2026 growth call to 3.9%", "Asia"),
    (36, "Football:", "India beat Pakistan 2\u20131 in SAFF final", "Asia"),
    (37, "Kenya:", "WFP aids 30,000 who fled Ethiopia clashes", "Africa"),
    (38, "Football:", "Togo beat Algeria 3\u20130, AFCON qualifier", "Africa"),
    (39, "Haiti:", "Aristide's party to field no candidates", "Americas"),
    (40, "Senate:", "Van Hollen challenges Schumer for leader", "Americas"),
    (41, "Australia:", "eases planned backpacker visa curbs", "Oceania"),
    (42, "Darwin:", "M6.6 quake off Indonesia; no tsunami", "Oceania"),
    (43, "Apple:", "Pay, iCloud, App Store outage \u2014 not a hack", "Americas"),
]

# --------------------------------------------------------------------------
# Text helpers
# --------------------------------------------------------------------------
def tw(d, s, font):
    """Width of a string in px."""
    return d.textlength(s, font=font)


def wrap(d, text, font, width):
    """Greedy word wrap; returns list of lines fitting `width`."""
    lines, cur = [], ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if tw(d, trial, font) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_block(d, x, y, lines, font, fill, leading):
    for ln in lines:
        d.text((x, y), ln, font=font, fill=fill)
        y += leading
    return y


def data_chip(d, x, y, text, font=F_CHIP, align="left"):
    """Small black chip with white bold text; returns its width."""
    w = int(tw(d, text, font)) + 12
    if align == "right":
        x -= w
    d.rectangle([x, y, x + w, y + 17], fill=CHIP_BG)
    d.text((x + 6, y + 3), text, font=font, fill=CHIP_FG)
    return w


def num_badge(d, cx, cy, num, color, r=9):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color,
              outline=(255, 255, 255), width=2)
    s = str(num)
    w = tw(d, s, F_BRIEF_CHIP)
    d.text((cx - w / 2, cy - 5), s, font=F_BRIEF_CHIP, fill=(255, 255, 255))


def kicker_strip(d, x, y, w, num, kicker, continent):
    d.rectangle([x, y, x + w, y + 15], fill=CONTINENT_COLORS[continent])
    d.text((x + 5, y + 3), "%d · %s" % (num, kicker), font=F_STRIP,
           fill=(255, 255, 255))


# --------------------------------------------------------------------------
# Illustrations — original flat drawings, each rendered into its own box.
# --------------------------------------------------------------------------
def ill_box(w, h, fn):
    img = Image.new("RGB", (w, h), CREAM)
    d = ImageDraw.Draw(img)
    fn(d, w, h)
    return img


def ill_bridge(d, w, h):
    d.rectangle([0, 0, w, h], fill=(203, 226, 240))            # sky
    sea = int(h * 0.62)
    d.rectangle([0, sea, w, h], fill=(46, 109, 164))           # sea
    for i in range(6):                                          # wavelets
        x = 12 + i * (w // 6)
        d.arc([x, sea + 12 + (i % 3) * 9, x + 26, sea + 24 + (i % 3) * 9],
              180, 360, fill=(160, 200, 230), width=2)
    deck = sea - 26
    d.rectangle([0, deck, w, deck + 7], fill=(38, 38, 38))     # deck
    for px in (int(w * 0.22), int(w * 0.72)):                   # pylons
        d.rectangle([px, deck - 44, px + 8, deck], fill=(38, 38, 38))
        for k in range(3):
            d.line([px + 4, deck - 40 + k * 13, px - 52, deck],
                   fill=(90, 90, 90), width=1)
            d.line([px + 4, deck - 40 + k * 13, px + 60, deck],
                   fill=(90, 90, 90), width=1)
    # fallen span: a deck segment tipped into the sea
    d.polygon([(int(w * 0.40), deck + 2), (int(w * 0.60), deck + 4),
               (int(w * 0.63), sea + 26), (int(w * 0.44), sea + 22)],
              fill=(38, 38, 38))
    d.line([int(w * 0.40), deck + 2, int(w * 0.63), sea + 26],
           fill=(120, 120, 120), width=2)
    for cx, cy, r in ((int(w * 0.55), deck - 34, 13),
                      (int(w * 0.63), deck - 48, 18),
                      (int(w * 0.72), deck - 38, 12)):          # smoke
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(150, 150, 150))
    d.ellipse([int(w * 0.06), 12, int(w * 0.06) + 26, 38], fill=(245, 197, 66))


def ill_mideast(d, w, h):
    d.rectangle([0, 0, w, h], fill=(168, 205, 228))            # sea
    d.polygon([(int(w * 0.44), 0), (w, 0), (w, int(h * 0.34)),
               (int(w * 0.68), int(h * 0.44)), (int(w * 0.54), int(h * 0.30)),
               (int(w * 0.47), int(h * 0.12))],
              fill=(232, 216, 168))                             # Iran (NE)
    d.polygon([(int(w * 0.06), int(h * 0.56)), (int(w * 0.34), int(h * 0.46)),
               (int(w * 0.52), int(h * 0.58)), (int(w * 0.60), h),
               (int(w * 0.10), h), (int(w * 0.02), int(h * 0.74))],
              fill=(232, 216, 168))                             # Arabia (SW)
    bx, by = int(w * 0.40), int(h * 0.50)                       # Bahrain dot
    d.ellipse([bx - 4, by - 4, bx + 4, by + 4], fill=RED)
    for i in range(3):                                          # drones inbound
        dx = int(w * (0.60 - 0.07 * i))
        dy = int(h * (0.16 + 0.09 * i))
        d.line([dx - 7, dy, dx + 7, dy], fill=INK, width=2)
        d.line([dx, dy - 5, dx, dy + 5], fill=INK, width=2)
        d.line([dx - 6, dy + 4, bx, by], fill=RED, width=1)
    qx, qy = int(w * 0.60), int(h * 0.42)                       # Qeshm island
    d.ellipse([qx - 7, qy - 3, qx + 7, qy + 3], fill=(214, 196, 144))
    for ang in range(0, 360, 45):                               # strike burst
        import math
        x2 = qx + int(11 * math.cos(math.radians(ang)))
        y2 = qy + int(11 * math.sin(math.radians(ang)))
        d.line([qx, qy, x2, y2], fill=RED, width=2)
    jx, jy = int(w * 0.80), int(h * 0.68)                       # jet
    d.polygon([(jx, jy), (jx + 26, jy + 7), (jx, jy + 14), (jx + 7, jy + 7)],
              fill=INK)
    d.line([jx + 2, jy + 4, qx + 6, qy + 4], fill=RED, width=2)
    data_chip(d, 6, 6, "DRONES DOWNED", F_CHIP_S)
    data_chip(d, w - 6, h - 23, "US STRIKES", F_CHIP_S, align="right")


def _flag_us(d, x, y, w, h):
    for i in range(7):
        c = (178, 34, 34) if i % 2 == 0 else (255, 255, 255)
        d.rectangle([x, y + i * h // 7, x + w, y + (i + 1) * h // 7], fill=c)
    d.rectangle([x, y, x + w * 0.42, y + h * 0.54], fill=(30, 58, 138))
    for r in range(3):
        for cix in range(4):
            d.point((x + 4 + cix * 6, y + 3 + r * 5), fill=(255, 255, 255))


def _flag_in(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h // 3], fill=(240, 140, 40))
    d.rectangle([x, y + h // 3, x + w, y + 2 * h // 3], fill=(255, 255, 255))
    d.rectangle([x, y + 2 * h // 3, x + w, y + h], fill=(30, 130, 60))
    cx, cy = x + w // 2, y + h // 2
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], outline=(30, 58, 138), width=2)


def _flag_jp(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255))
    cx, cy = x + w // 2, y + h // 2
    d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=(188, 0, 45))


def _flag_au(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(20, 40, 120))
    for sx, sy in ((6, 5), (20, 12), (34, 6), (28, 20), (12, 22), (40, 18)):
        d.line([x + sx - 2, y + sy, x + sx + 2, y + sy], fill=(255, 255, 255))
        d.line([x + sx, y + sy - 2, x + sx, y + sy + 2], fill=(255, 255, 255))


def ill_quad(d, w, h):
    d.rectangle([0, 0, w, h], fill=(214, 232, 244))
    d.rectangle([0, int(h * 0.78), w, h], fill=(90, 120, 90))
    flags = (_flag_us, _flag_in, _flag_jp, _flag_au)
    fw, fh = int(w * 0.17), int(h * 0.34)
    for i, fn in enumerate(flags):
        x = int(w * (0.07 + 0.235 * i))
        d.line([x, int(h * 0.14), x, int(h * 0.78)], fill=(60, 60, 60), width=3)
        fn(d, x + 3, int(h * 0.14), fw, fh)
    d.rectangle([0, h - 24, w, h], fill=CHIP_BG)
    label = "QUAD LEADERS' SUMMIT · MANILA"
    d.text(((w - tw(d, label, F_CHIP)) / 2, h - 18), label, font=F_CHIP,
           fill=CHIP_FG)


def ill_virus(d, w, h):
    d.rectangle([0, 0, w, h], fill=(16, 78, 74))
    for cx, cy, r in ((int(w * 0.30), int(h * 0.52), 15),
                      (int(w * 0.58), int(h * 0.38), 11),
                      (int(w * 0.76), int(h * 0.64), 9),
                      (int(w * 0.12), int(h * 0.24), 7)):
        for ang in range(0, 360, 45):
            import math
            x2 = cx + int((r + 6) * math.cos(math.radians(ang)))
            y2 = cy + int((r + 6) * math.sin(math.radians(ang)))
            d.line([cx, cy, x2, y2], fill=(248, 113, 113), width=2)
            d.ellipse([x2 - 2, y2 - 2, x2 + 2, y2 + 2], fill=(248, 113, 113))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(220, 38, 38))


def ill_climate(d, w, h):
    d.rectangle([0, 0, w, h], fill=(250, 224, 178))
    d.ellipse([8, 6, 44, 42], fill=(245, 158, 11))              # sun
    for ang in range(0, 360, 60):
        import math
        x1 = 26 + int(22 * math.cos(math.radians(ang)))
        y1 = 24 + int(22 * math.sin(math.radians(ang)))
        x2 = 26 + int(28 * math.cos(math.radians(ang)))
        y2 = 24 + int(28 * math.sin(math.radians(ang)))
        d.line([x1, y1, x2, y2], fill=(245, 158, 11), width=2)
    fx = int(w * 0.52)                                          # factory
    d.rectangle([fx, int(h * 0.48), fx + int(w * 0.40), h], fill=(87, 83, 78))
    d.rectangle([fx + 8, int(h * 0.22), fx + 20, int(h * 0.48)],
                fill=(87, 83, 78))
    d.rectangle([fx + 30, int(h * 0.30), fx + 40, int(h * 0.48)],
                fill=(87, 83, 78))
    for cx, cy, r in ((fx + 14, int(h * 0.16), 8), (fx + 34, int(h * 0.22), 6),
                      (fx + 24, int(h * 0.10), 10)):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(160, 152, 140))
    ax, ay = int(w * 0.38), int(h * 0.28)                       # down arrow
    d.line([ax, ay, ax, ay + 22], fill=(22, 163, 74), width=4)
    d.polygon([(ax - 6, ay + 18), (ax + 6, ay + 18), (ax, ay + 28)],
              fill=(22, 163, 74))


def ill_shield(d, w, h):
    d.rectangle([0, 0, w, h], fill=(224, 236, 248))
    cx, cy = w // 2, h // 2
    d.polygon([(cx - 26, cy - 20), (cx + 26, cy - 20), (cx + 26, cy + 4),
               (cx, cy + 26), (cx - 26, cy + 4)], fill=(203, 224, 248),
              outline=(30, 90, 160), width=4)
    for dx, dy in ((-10, -6), (8, 0), (-2, 10)):
        d.ellipse([cx + dx - 3, cy + dy - 3, cx + dx + 3, cy + dy + 3],
                  fill=(220, 38, 38))
    d.line([cx - 30, cy + 22, cx + 30, cy - 24], fill=RED, width=5)


def ill_chart(d, w, h):
    d.rectangle([0, 0, w, h], fill=(23, 37, 84))
    base = h - 8
    heights = (0.30, 0.44, 0.60, 0.86)
    for i, hf in enumerate(heights):
        x = int(w * (0.10 + 0.21 * i))
        bw = int(w * 0.14)
        d.rectangle([x, base - int(h * hf), x + bw, base], fill=(34, 197, 94))
    pts = [(int(w * 0.12), base - int(h * 0.34)),
           (int(w * 0.33), base - int(h * 0.48)),
           (int(w * 0.54), base - int(h * 0.64)),
           (int(w * 0.76), base - int(h * 0.90))]
    d.line(pts, fill=(250, 204, 21), width=3)
    d.polygon([(pts[-1][0] - 2, pts[-1][1] - 6), (pts[-1][0] + 10, pts[-1][1] + 1),
               (pts[-1][0] - 4, pts[-1][1] + 3)], fill=(250, 204, 21))


def ill_dove(d, w, h):
    d.rectangle([0, 0, w, h], fill=(226, 232, 240))
    for i, bw in enumerate((26, 38, 20, 30)):                   # skyline
        x = 6 + i * (w // 4)
        d.rectangle([x, h - bw, x + w // 5, h], fill=(120, 128, 140))
    cx, cy = int(w * 0.52), int(h * 0.36)                       # dove
    d.ellipse([cx - 16, cy - 7, cx + 16, cy + 7], fill=(255, 255, 255),
              outline=(100, 116, 139))
    d.ellipse([cx + 12, cy - 12, cx + 22, cy - 2], fill=(255, 255, 255),
              outline=(100, 116, 139))
    d.polygon([(cx - 4, cy - 4), (cx - 22, cy - 18), (cx - 12, cy + 2)],
              fill=(255, 255, 255), outline=(100, 116, 139))
    d.line([cx + 20, cy - 6, cx + 30, cy - 2], fill=(22, 163, 74), width=2)
    d.ellipse([cx + 27, cy - 5, cx + 32, cy], fill=(22, 163, 74))


def ill_ger(d, w, h):
    d.rectangle([0, 0, w, h], fill=(186, 224, 246))
    d.rectangle([0, int(h * 0.66), w, h], fill=(110, 168, 84))  # steppe
    cx, cy = w // 2, int(h * 0.72)
    d.polygon([(cx - 50, cy), (cx - 38, cy - 26), (cx + 38, cy - 26),
               (cx + 50, cy)], fill=(245, 245, 240))
    d.polygon([(cx - 38, cy - 26), (cx, cy - 40), (cx + 38, cy - 26)],
              fill=(203, 213, 225))
    d.rectangle([cx - 7, cy - 17, cx + 7, cy], fill=(146, 64, 14))
    d.line([cx, cy - 40, cx, cy - 50], fill=(100, 60, 20), width=2)
    d.polygon([(cx, cy - 50), (cx + 15, cy - 47), (cx, cy - 44)],
              fill=(220, 38, 38))


def ill_parliament(d, w, h):
    d.rectangle([0, 0, w, h], fill=(219, 228, 240))
    bx, bw = int(w * 0.14), int(w * 0.72)
    by = int(h * 0.30)
    d.polygon([(bx - 6, by), (bx + bw // 2, by - 14), (bx + bw + 6, by)],
              fill=(100, 116, 139))
    d.rectangle([bx, by, bx + bw, h - 6], fill=(226, 220, 204))
    for i in range(5):
        cx = bx + 8 + i * (bw - 12) // 4
        d.rectangle([cx, by + 6, cx + 5, h - 12], fill=(148, 140, 122))
    d.rectangle([bx - 4, h - 8, bx + bw + 4, h - 2], fill=(100, 116, 139))
    dx = bx + bw // 2
    d.pieslice([dx - 10, by - 24, dx + 10, by - 2], 180, 360,
               fill=(100, 116, 139))


def ill_factory(d, w, h):
    d.rectangle([0, 0, w, h], fill=(226, 232, 240))
    d.rectangle([8, int(h * 0.40), w - 30, h - 4], fill=(148, 163, 184))
    for i in range(3):                                          # sawtooth roof
        x = 8 + i * ((w - 38) // 3)
        d.polygon([(x, int(h * 0.40)), (x + 14, int(h * 0.18)),
                   (x + 28, int(h * 0.40))], fill=(100, 116, 139))
    d.rectangle([w - 24, int(h * 0.16), w - 14, h - 4], fill=(100, 116, 139))
    for r in range(2):
        for cix in range(4):
            d.rectangle([16 + cix * 22, int(h * 0.52) + r * 12,
                         28 + cix * 22, int(h * 0.52) + r * 12 + 7],
                        fill=(250, 204, 21))
    tx, ty = int(w * 0.60), int(h * 0.52)                       # t-shirt
    d.polygon([(tx, ty), (tx + 10, ty - 5), (tx + 16, ty), (tx + 26, ty - 5),
               (tx + 36, ty), (tx + 30, ty + 6), (tx + 30, ty + 22),
               (tx + 6, ty + 22), (tx + 6, ty + 6)],
              fill=(236, 72, 153))


def ill_crash(d, w, h):
    d.rectangle([0, 0, w, h], fill=(226, 236, 244))
    d.rectangle([0, int(h * 0.74), w, h], fill=(248, 250, 252))  # snow
    for i in range(5):                                          # pines
        x = 8 + i * (w // 5)
        d.polygon([(x, int(h * 0.74)), (x + 7, int(h * 0.44)),
                   (x + 14, int(h * 0.74))], fill=(22, 101, 52))
    px, py = int(w * 0.52), int(h * 0.40)                       # plane, nose down
    d.polygon([(px, py), (px + 44, py + 16), (px + 40, py + 24),
               (px - 2, py + 10)], fill=(71, 85, 105))
    d.polygon([(px + 16, py + 8), (px + 30, py - 6), (px + 38, py + 12)],
              fill=(100, 116, 139))
    d.polygon([(px - 2, py + 10), (px - 12, py - 2), (px + 4, py + 2)],
              fill=(100, 116, 139))
    for i in range(3):                                          # smoke trail
        sx, sy = px - 16 - i * 14, py - 8 - i * 7
        r = 5 + i * 2
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(156, 163, 175))


def ill_scales(d, w, h):
    d.rectangle([0, 0, w, h], fill=(20, 83, 45))
    cx = w // 2
    d.line([cx, 8, cx, h - 10], fill=(250, 204, 21), width=3)
    d.line([cx - 34, 14, cx + 34, 14], fill=(250, 204, 21), width=3)
    d.ellipse([cx - 4, 4, cx + 4, 12], fill=(250, 204, 21))
    for sx in (cx - 34, cx + 34):
        d.line([sx, 14, sx - 10, 32], fill=(250, 204, 21), width=2)
        d.line([sx, 14, sx + 10, 32], fill=(250, 204, 21), width=2)
        d.arc([sx - 13, 24, sx + 13, 42], 0, 180, fill=(250, 204, 21),
              width=3)
    d.rectangle([cx - 16, h - 10, cx + 16, h - 5], fill=(250, 204, 21))


ILLUSTRATIONS = {
    "bridge": ill_bridge, "mideast": ill_mideast, "quad": ill_quad,
    "virus": ill_virus, "climate": ill_climate, "shield": ill_shield,
    "chart": ill_chart, "dove": ill_dove, "ger": ill_ger,
    "parliament": ill_parliament, "factory": ill_factory,
    "crash": ill_crash, "scales": ill_scales,
}


# --------------------------------------------------------------------------
# World map — dot grid. Segments per row: (first col, last col, land code)
# a=Americas  e=Europe  m=Middle East  s=Asia  f=Africa  o=Oceania
# --------------------------------------------------------------------------
MAP_ROWS = [
    [],
    [(2, 4, "a"), (8, 14, "a"), (22, 24, "a"), (41, 44, "s"), (48, 52, "s")],
    [(1, 20, "a"), (22, 25, "a"), (32, 35, "e"), (39, 58, "s")],
    [(2, 19, "a"), (23, 25, "a"), (30, 36, "e"), (38, 58, "s")],
    [(3, 18, "a"), (28, 29, "e"), (31, 37, "e"), (39, 57, "s")],
    [(4, 17, "a"), (28, 29, "e"), (30, 37, "e"), (38, 56, "s")],
    [(5, 17, "a"), (29, 37, "e"), (38, 53, "s"), (54, 55, "s")],
    [(5, 16, "a"), (28, 36, "e"), (39, 52, "s"), (53, 54, "s")],
    [(6, 15, "a"), (28, 34, "e"), (35, 38, "m"), (40, 52, "s"), (53, 53, "s")],
    [(6, 15, "a"), (29, 33, "e"), (35, 39, "m"), (41, 52, "s")],
    [(7, 13, "a"), (27, 35, "f"), (36, 41, "m"), (43, 51, "s")],
    [(8, 12, "a"), (27, 36, "f"), (37, 41, "m"), (44, 50, "s"), (51, 52, "s")],
    [(10, 12, "a"), (27, 37, "f"), (38, 40, "m"), (45, 49, "s"), (51, 53, "s")],
    [(16, 19, "a"), (28, 38, "f"), (39, 40, "m"), (46, 48, "s"), (51, 53, "s")],
    [(15, 17, "a"), (28, 38, "f"), (51, 53, "s")],
    [(15, 19, "a"), (29, 38, "f"), (52, 54, "s")],
    [(15, 20, "a"), (30, 37, "f"), (51, 55, "s")],
    [(15, 21, "a"), (30, 37, "f"), (50, 56, "s")],
    [(16, 22, "a"), (31, 37, "f"), (51, 57, "s")],
    [(17, 23, "a"), (31, 37, "f"), (57, 58, "s")],
    [(17, 22, "a"), (31, 36, "f"), (39, 39, "f"), (49, 55, "o")],
    [(17, 21, "a"), (32, 36, "f"), (39, 39, "f"), (49, 56, "o")],
    [(18, 21, "a"), (32, 35, "f"), (39, 39, "f"), (50, 56, "o")],
    [(18, 20, "a"), (32, 35, "f"), (39, 39, "f"), (50, 55, "o")],
    [(18, 20, "a"), (33, 34, "f"), (51, 54, "o")],
    [(18, 19, "a"), (52, 53, "o")],
    [(18, 19, "a"), (58, 59, "o")],
]
MAP_CODE = {"a": "Americas", "e": "Europe", "m": "Middle East",
            "s": "Asia", "f": "Africa", "o": "Oceania"}

# Numbered pins for stories 1-13: (num, col, row, continent)
MAP_PINS = [
    (1, 36, 7, "Europe"), (2, 39, 12, "Middle East"), (3, 51, 14, "Asia"),
    (4, 34, 17, "Africa"), (5, 34, 9, "Middle East"), (6, 13, 8, "Americas"),
    (7, 9, 9, "Americas"), (8, 36, 11, "Middle East"), (9, 48, 7, "Asia"),
    (10, 33, 7, "Europe"), (11, 45, 12, "Asia"), (12, 44, 5, "Asia"),
    (13, 36, 21, "Africa"),
]
# Small dots for briefs 14-43: (col, row, continent)
MAP_DOTS = [
    (36, 5, "Asia"), (35, 6, "Europe"), (34, 6, "Europe"), (32, 6, "Europe"),
    (30, 7, "Europe"), (33, 5, "Europe"), (32, 5, "Europe"), (34, 7, "Europe"),
    (35, 8, "Middle East"), (31, 4, "Europe"), (32, 8, "Europe"),
    (30, 6, "Europe"), (35, 10, "Middle East"), (37, 10, "Middle East"),
    (41, 12, "Middle East"), (44, 13, "Asia"), (43, 11, "Asia"),
    (52, 9, "Asia"), (49, 9, "Asia"), (49, 16, "Asia"), (50, 14, "Asia"),
    (51, 9, "Asia"), (43, 13, "Asia"), (37, 17, "Africa"), (30, 15, "Africa"),
    (18, 13, "Americas"), (16, 9, "Americas"), (54, 24, "Oceania"),
    (52, 20, "Oceania"), (8, 10, "Americas"),
]


def draw_map(d, x, y, cell_x=7, cell_y=8):
    """Dot-grid world map; returns (width, height) used."""
    rows = len(MAP_ROWS)
    cols = 60
    for r, segs in enumerate(MAP_ROWS):
        for c0, c1, code in segs:
            color = CONTINENT_COLORS[MAP_CODE[code]]
            for c in range(c0, c1 + 1):
                cx = x + c * cell_x + cell_x // 2
                cy = y + r * cell_y + cell_y // 2
                d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=color)
    for col, row, cont in MAP_DOTS:
        cx = x + col * cell_x + cell_x // 2
        cy = y + row * cell_y + cell_y // 2
        d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3],
                  fill=CONTINENT_COLORS[cont], outline=(255, 255, 255))
    for num, col, row, cont in MAP_PINS:
        cx = x + col * cell_x + cell_x // 2
        cy = y + row * cell_y + cell_y // 2
        num_badge(d, cx, cy, num, CONTINENT_COLORS[cont], r=8)
    return cols * cell_x, rows * cell_y


# --------------------------------------------------------------------------
# Page composition
# --------------------------------------------------------------------------
def draw_brief(d, x, y, num, lead, rest, width):
    """One numbered brief: chip + bold lead-in + wrapped line(s).
    Returns the y just below the brief."""
    d.rectangle([x, y + 1, x + 17, y + 14], fill=CHIP_BG)
    s = str(num)
    d.text((x + (17 - tw(d, s, F_BRIEF_CHIP)) / 2, y + 3), s,
           font=F_BRIEF_CHIP, fill=CHIP_FG)
    tx = x + 22
    right = x + width
    d.text((tx, y), lead, font=F_BRIEF_B, fill=INK)
    cx = tx + tw(d, lead, F_BRIEF_B) + 4
    cy = y
    for word in rest.split():
        ww = tw(d, word, F_BRIEF)
        if cx + ww > right and cx > tx:
            cy += 12.5
            cx = tx
        d.text((cx, cy), word, font=F_BRIEF, fill=INK)
        cx += ww + tw(d, " ", F_BRIEF)
    return cy + 12.5 + 3


def build():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    d.rectangle([5, 5, W - 6, H - 6], outline=INK, width=2)

    # --- kicker row -------------------------------------------------------
    ky = 12
    d.text((MARGIN, ky), "THE WORLD'S NEWS IN ONE PICTURE", font=F_KICKER,
           fill=RED)
    right = "43 STORIES · 6 CONTINENTS · ALL FROM TUESDAY"
    d.text((W - MARGIN - tw(d, right, F_KICKER_R), ky), right,
           font=F_KICKER_R, fill=SOFT_INK)

    # --- masthead ---------------------------------------------------------
    title = "Tuesday 17 November 2026"
    size = 60
    while size > 20 and tw(d, title, serif_b(size)) > 950:
        size -= 2
    f_title = serif_b(size)
    d.text(((W - tw(d, title, f_title)) / 2, 28), title, font=f_title,
           fill=INK)
    d.rectangle([MARGIN, 100, W - MARGIN, 103], fill=RULE)
    d.line([MARGIN, 107, W - MARGIN, 107], fill=RULE, width=1)

    # --- heroes ------------------------------------------------------------
    hy = 114
    hero_w, hero_gap = 325, 10
    ill_h = 128
    for i, (num, cont, kick, chip, head, summ, ill) in enumerate(HEROES):
        x = MARGIN + i * (hero_w + hero_gap)
        img.paste(ill_box(hero_w, ill_h, ILLUSTRATIONS[ill]), (x, hy))
        data_chip(d, x + 6, hy + ill_h - 23, chip)
        sy = hy + ill_h
        kicker_strip(d, x, sy, hero_w, num, kick, cont)
        y = sy + 15 + 5
        y = text_block(d, x, y, wrap(d, head, F_HERO_HEAD, hero_w - 4),
                       F_HERO_HEAD, INK, 20)
        y = text_block(d, x, y + 3, wrap(d, summ, F_HERO_SUM, hero_w - 4),
                       F_HERO_SUM, SOFT_INK, 15)

    # --- grid 4-13 ---------------------------------------------------------
    gy = 356
    cell_w, cell_gap, row_h = 194, 6, 141
    gill_h = 56
    for idx, (num, cont, kick, chip, head, summ, ill) in enumerate(GRID):
        x = MARGIN + (idx % 5) * (cell_w + cell_gap)
        y = gy + (idx // 5) * row_h
        img.paste(ill_box(cell_w, gill_h, ILLUSTRATIONS[ill]), (x, y))
        data_chip(d, x + cell_w - 6, y + gill_h - 21, chip, F_CHIP_S,
                  align="right")
        sy = y + gill_h
        # grid strip is 13px tall
        d.rectangle([x, sy, x + cell_w, sy + 13],
                    fill=CONTINENT_COLORS[cont])
        d.text((x + 4, sy + 2), "%d · %s" % (num, kick), font=F_STRIP,
               fill=(255, 255, 255))
        yy = text_block(d, x, sy + 13 + 3,
                        wrap(d, head, F_GRID_HEAD, cell_w - 4),
                        F_GRID_HEAD, INK, 15)
        text_block(d, x, yy + 2, wrap(d, summ, F_GRID_SUM, cell_w - 4),
                   F_GRID_SUM, SOFT_INK, 14)

    # --- bottom split ------------------------------------------------------
    by = 644
    d.line([MARGIN, by - 4, W - MARGIN, by - 4], fill=RULE, width=2)

    # left: map
    mx = MARGIN
    d.text((mx, by), "WHERE IT HAPPENED", font=F_MAP_HEAD, fill=INK)
    d.line([mx, by + 19, mx + 420, by + 19], fill=RULE, width=1)
    map_y = by + 26
    mw, mh = draw_map(d, mx, map_y)
    ly = map_y + mh + 8
    d.text((mx, ly),
           "Pins 1\u201313: the illustrated stories · Dots: briefs 14\u201343",
           font=F_LEGEND, fill=SOFT_INK)
    ly += 16
    names = list(CONTINENT_COLORS.items())
    for r in range(2):
        for cix in range(3):
            name, color = names[r * 3 + cix]
            lx = mx + cix * 140
            d.rectangle([lx, ly + r * 15 + 2, lx + 9, ly + r * 15 + 11],
                        fill=color)
            d.text((lx + 13, ly + r * 15), name, font=F_LEGEND, fill=INK)

    # right: briefs
    bx = 452
    bw = W - MARGIN - bx  # 558
    d.line([440, by, 440, 968], fill=RULE, width=1)
    d.text((bx, by), "ALSO ON TUESDAY 17 NOVEMBER", font=F_MAP_HEAD, fill=INK)
    d.line([bx, by + 19, W - MARGIN, by + 19], fill=RULE, width=1)
    col_w, col_gap = 270, 18
    col1 = [b for b in BRIEFS if b[0] <= 28]
    col2 = [b for b in BRIEFS if b[0] >= 29]
    for ci, col in enumerate((col1, col2)):
        x = bx + ci * (col_w + col_gap)
        y = by + 27
        for num, lead, rest, _cont in col:
            y = draw_brief(d, x, y, num, lead, rest, col_w)

    # --- footer ------------------------------------------------------------
    d.line([MARGIN, 972, W - MARGIN, 972], fill=RULE, width=1)
    fy = 979
    d.text((MARGIN, fy),
           "Every story above happened, or was first reported, on Tuesday "
           "17 November 2026; contested claims are attributed to those who "
           "made them.", font=F_FOOT, fill=SOFT_INK)
    d.text((MARGIN, fy + 14),
           "Sources: Reuters · AP · AFP · BBC · Al Jazeera · WHO · UN",
           font=F_FOOT_B, fill=INK)
    orig = "Original drawings."
    d.text((W - MARGIN - tw(d, orig, F_FOOT_B), fy + 14), orig,
           font=F_FOOT_B, fill=INK)
    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    img = build()
    img.save(os.path.join(out_dir, "entry.png"), optimize=True)


if __name__ == "__main__":
    main()
