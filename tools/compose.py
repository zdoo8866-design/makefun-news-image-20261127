#!/usr/bin/env python3
"""Draw the Friday 27 November 2026 front page: 'The World in One Day'.

A single-file PIL renderer. Everything on the page -- masthead, tally bar,
numbers strip, thirteen story cards with small spot illustrations, the
locator map with numbered pins, the briefs column, the date-check box --
is drawn in code; there are no photographs and no pasted assets.

Usage:  python3 compose.py [output.png]     (default: entry.png next to
the repository root, i.e. one level above this script's folder)
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from worldmap_data import LANDMASSES  # noqa: E402

# ---------------------------------------------------------------- palette
PAPER = (246, 241, 230)
CARD = (252, 250, 244)
INK = (24, 28, 38)
NAVY = (18, 38, 84)
RED = (178, 32, 38)
GOLD = (176, 132, 40)
GREEN = (74, 140, 74)
GREY = (105, 105, 100)
LINE = (60, 60, 60)
SKY = (214, 226, 238)
NIGHT = (26, 34, 58)

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")


def font(name, size):
    return ImageFont.truetype(str(FONT_DIR / name), size)


SERIF = "DejaVuSerif.ttf"
SERIF_B = "DejaVuSerif-Bold.ttf"
SERIF_I = "DejaVuSerif.ttf"  # no serif italic shipped; regular serif stands in
SANS = "DejaVuSans.ttf"
SANS_B = "DejaVuSans-Bold.ttf"

W, H = 1024, 1024
MARGIN = 24
CW = W - 2 * MARGIN  # 976 usable width

# ------------------------------------------------------------------- data
CARDS = [
    dict(n=1, city="WELLINGTON", tag="ELECTION", scene="ballot",
         head="Final count leaves New Zealand hung at 65–65",
         body="Special votes erase the coalition's majority: 65 seats each, and Luxon needs Opportunity's seven.",
         src="1News"),
    dict(n=2, city="NEW YORK", tag="WEATHER", scene="storm",
         head="Thanksgiving storm: 400 flights cut, 724,000 in the dark",
         body="Nearly 400 flights cancelled, 2,000 delayed, mostly in the east; 724,000 homes without power.",
         src="NDTV"),
    dict(n=3, city="NEW DELHI", tag="CRIME", scene="cuffs",
         head="Delhi police smash a cyber-slavery ring; 164 freed",
         body="Raids free 164 foreigners — 92 Indonesians, 72 Malaysians — held by a cyber-slavery ring.",
         src="NDTV"),
    dict(n=4, city="HORMUZ", tag="GULF", scene="tanker",
         head="Blasts hit three tankers in the Strait of Hormuz",
         body="Explosions aboard three tankers as the Gulf campaign widens.",
         src="QT"),
    dict(n=5, city="KYIV", tag="WAR", scene="drone",
         head="Zelensky warns of a new mass strike",
         body="New mass strike feared as attacks run daily since September.",
         src="NDTV"),
    dict(n=6, city="TOKYO", tag="ECONOMY", scene="inflation",
         head="Tokyo core prices rise 2.9%, past forecasts",
         body="Core prices up 2.9% on the year, from 2.6% in October.",
         src="NDTV"),
    dict(n=7, city="BUENOS AIRES", tag="ECONOMY", scene="press",
         head="Argentina bars its bank from printing money",
         body="Buenos Aires bans the bank from printing money for the state.",
         src="ET"),
    dict(n=8, city="BERLIN", tag="MIGRATION", scene="flag",
         head="Berlin offers more to return Syrians",
         body="Berlin readies a bigger return plan, with higher cash bonuses.",
         src="QT"),
    dict(n=9, city="BRUSSELS", tag="EUROPE", scene="coins",
         head="EU split over a $49bn loan for Ukraine",
         body="Leaders split as a $49bn loan for Ukraine is weighed.",
         src="ET"),
    dict(n=10, city="MINNEAPOLIS", tag="FRAUD", scene="seal",
         head="'Ghost daycares' aired at a House hearing",
         body="A House hearing airs fraud claims at Minnesota daycares.",
         src="ET"),
    dict(n=11, city="SEOUL", tag="FILM", scene="screen",
         head="Dune: Part Three leads advance sales",
         body="Advance bookings near 105,000 ahead of the Dec 16 opening.",
         src="AJP"),
    dict(n=12, city="CHRISTCHURCH", tag="CRICKET", scene="cricket",
         head="Debutant strikes as India face New Zealand",
         body="Debutant Gurnoor Brar strikes late; New Zealand 77 for 1.",
         src="NDTV"),
    dict(n=13, city="GENEVA", tag="TRADE", scene="tariff",
         head="Global maritime trade set for zero growth",
         body="UN sees zero growth in 2026 as Gulf attacks snarl shipping.",
         src="ET"),
]

BRIEFS = [
    (14, "WASHINGTON", "Trump: Putin can come to G20", "ET"),
    (15, "WASHINGTON", "Trump urges Putin to end aggression", "ET"),
    (16, "WASHINGTON", "Senators grill Hegseth on Iran war", "ET"),
    (17, "WASHINGTON", "USAID 'weaponised': 248 files out", "ET"),
    (18, "CALIFORNIA", "El Niño, king tides flood the coast", "ET"),
    (19, "WASHINGTON", "Trump: Huang is no security threat", "NDTV"),
    (20, "DHAKA", "Hasina's ex-press aide arrested", "ET"),
    (21, "BALKH", "Women renamed 'Bibi', 'goat', 'cow'", "ET"),
    (22, "GLOBAL", "Chess worlds: game three drawn", "NDTV"),
    (23, "COLOMBO", "UN urges Sri Lanka wartime apology", "Scoop"),
    (24, "PORT MORESBY", "PNG: five women 'buried alive'", "Scoop"),
    (25, "WASHINGTON", "Hawley: healthcare costs 'outrageous'", "ET"),
    (26, "ABU DHABI", "Adnoc curbs tanker entry after attacks", "ET"),
    (27, "DUBAI", "Gulf war dents winter hotel bookings", "ET"),
    (28, "NEW DELHI", "Opposition marches over vote 'fraud'", "QT"),
    (29, "KYIV", "Ukraine, Russia swap soldiers' remains", "QT"),
    (30, "KYIV", "Russian strikes kill 5, cut power", "QT"),
    (31, "BRUSSELS", "NATO's Rutte praises Trump on Putin", "QT"),
    (32, "PYONGYANG", "Kim calls for nuclear expansion", "QT"),
    (33, "SEOUL", "'White Blast' tops Korean box office", "AJP"),
    (34, "MUMBAI", "'Ramayana' day 22 leads the charts", "TOI"),
    (35, "LONDON", "Brent nears $97 after Gulf attacks", "NDTV"),
    (36, "THE HAGUE", "ICC urged to centre Afghan victims", "Scoop"),
]

# (number, lon, lat, badge nudge in px) -- nudges keep close pins apart.
PINS = [
    (1, 174.78, -41.29, (15, -11)),
    (2, -74.01, 40.71, (0, 0)),
    (3, 77.21, 28.61, (0, 0)),
    (4, 56.50, 26.60, (11, 9)),
    (5, 30.52, 50.45, (-15, -9)),
    (6, 139.69, 35.68, (13, -7)),
    (7, -58.38, -34.60, (0, 0)),
    (8, 13.40, 52.52, (3, -15)),
    (9, 4.35, 50.85, (-15, 5)),
    (10, -93.27, 44.98, (0, 0)),
    (11, 126.98, 37.57, (-13, 9)),
    (12, 172.64, -43.53, (-15, 13)),
    (13, 6.14, 46.20, (13, 11)),
]

TALLY = [
    ("AMERICAS 10", 10, (42, 120, 110)),
    ("ASIA 10", 10, (58, 90, 150)),
    ("EUROPE 9", 9, (90, 110, 140)),
    ("MIDDLE EAST 3", 3, (140, 90, 60)),
    ("OCEANIA 3", 3, (30, 90, 90)),
    ("GLOBAL 1", 1, (110, 110, 110)),
]

NUMBERS = [
    ("724,000", "without power in the storm"),
    ("400", "Thanksgiving flights cancelled"),
    ("65", "seats a side in a hung House"),
    ("164", "rescued in the Delhi bust"),
    ("2.9%", "Tokyo core inflation"),
    ("248", "files in the USAID dump"),
]

DATE_CHECK = (
    "Every story on this page happened, or was first reported, on Friday 27 November 2026.  "
    "NOT FRIDAY — Thu 26 Nov: drones kill two Italians at a Kuwait air base, Iran denies it; "
    "UK net migration falls to 77,000; Spain's Pablo Hernández de Cos is picked to lead the ECB; "
    "a diesel tanker capsizes off Ibiza, one dead; Trump signs Florida flood aid; "
    "Macy's 100th parade marches. Wed 25 Nov: troops free all hostages in Cartagena. "
    "NOT YET: Eisenkot's deadline (Dec 6) · Hasina's flight home (Dec 16) · "
    "Dune: Part Three opens (Dec 16)."
)


# ------------------------------------------------------------- text utils
def wrap(d, text, fnt, width):
    """Greedy word wrap; returns a list of lines that fit `width`."""
    lines, cur = [], ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if d.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_lines(d, lines, x, y, fnt, fill, leading):
    for i, line in enumerate(lines):
        d.text((x, y + i * leading), line, font=fnt, fill=fill)
    return y + len(lines) * leading


def centre(d, cx, y, text, fnt, fill):
    d.text((cx - d.textlength(text, font=fnt) / 2, y), text, font=fnt, fill=fill)


# ------------------------------------------------------- spot illustrations
def _cloud(d, x, y, s, fill):
    d.ellipse([x, y, x + s, y + s * 0.7], fill=fill)
    d.ellipse([x + s * 0.3, y - s * 0.25, x + s * 1.1, y + s * 0.5], fill=fill)
    d.ellipse([x + s * 0.7, y, x + s * 1.4, y + s * 0.7], fill=fill)


def _star(d, cx, cy, r, fill):
    pts = []
    import math
    for i in range(10):
        ang = math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy - rr * math.sin(ang)))
    d.polygon(pts, fill=fill)


def scene_ballot(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(226, 232, 240))
    bx, by, bw, bh = x + w * 0.32, y + h * 0.42, w * 0.42, h * 0.42
    d.rectangle([bx, by, bx + bw, by + bh], fill=NAVY)
    d.rectangle([bx - 4, by - 6, bx + bw + 4, by + 2], fill=NAVY)
    px, py = bx + bw * 0.3, by - h * 0.34
    d.polygon([(px, py), (px + w * 0.16, py + h * 0.05), (px + w * 0.13, py + h * 0.36),
               (px - w * 0.03, py + h * 0.31)], fill=(250, 250, 246),
              outline=INK)
    for i in range(2):
        d.line([px + 4, py + 10 + i * 6, px + w * 0.12, py + 10 + i * 6], fill=GREY, width=1)
    _star(d, x + w * 0.86, y + h * 0.22, 7, GOLD)
    d.text((x + 8, y + 6), "65 – 65", font=font(SANS_B, 15), fill=RED)


def scene_storm(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NIGHT)
    _cloud(d, x + w * 0.08, y + h * 0.12, w * 0.2, (120, 130, 150))
    _cloud(d, x + w * 0.42, y + h * 0.06, w * 0.24, (140, 150, 168))
    _cloud(d, x + w * 0.72, y + h * 0.16, w * 0.18, (110, 120, 140))
    d.polygon([(x + w * 0.55, y + h * 0.38), (x + w * 0.48, y + h * 0.62),
               (x + w * 0.56, y + h * 0.62), (x + w * 0.50, y + h * 0.85),
               (x + w * 0.62, y + h * 0.55), (x + w * 0.55, y + h * 0.55)],
              fill=(240, 200, 60))
    for i, rx in enumerate((0.12, 0.28, 0.70, 0.86)):
        d.line([x + w * rx, y + h * 0.55, x + w * (rx - 0.04), y + h * 0.95],
               fill=(150, 180, 220), width=2)


def scene_cuffs(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 234, 238))
    cy = y + h * 0.52
    for cx in (x + w * 0.28, x + w * 0.72):
        d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], outline=NAVY, width=5)
        d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=NAVY)
    d.line([x + w * 0.28, cy, x + w * 0.72, cy], fill=NAVY, width=4)
    d.ellipse([x + w * 0.47, cy - 6, x + w * 0.53, cy + 6], outline=RED, width=3)


def scene_tanker(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(200, 222, 236))
    d.polygon([(x + w * 0.10, y + h * 0.55), (x + w * 0.90, y + h * 0.55),
               (x + w * 0.82, y + h * 0.82), (x + w * 0.18, y + h * 0.82)],
              fill=(40, 48, 66))
    d.rectangle([x + w * 0.55, y + h * 0.32, x + w * 0.72, y + h * 0.55], fill=(240, 240, 235))
    d.rectangle([x + w * 0.60, y + h * 0.20, x + w * 0.64, y + h * 0.32], fill=RED)
    for i in range(3):
        yy = y + h * (0.86 + i * 0.05)
        d.arc([x + w * 0.08, yy - 6, x + w * 0.92, yy + 10], 0, 180, fill=NAVY, width=2)
    _star(d, x + w * 0.80, y + h * 0.22, 9, (240, 170, 40))


def scene_drone(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NIGHT)
    d.polygon([(x + w * 0.30, y + h * 0.85), (x + w * 0.62, y + h * 0.30),
               (x + w * 0.72, y + h * 0.34), (x + w * 0.48, y + h * 0.88)],
              fill=(240, 230, 150))
    cx, cy = x + w * 0.55, y + h * 0.30
    d.ellipse([cx - 12, cy - 7, cx + 12, cy + 7], fill=(200, 200, 195))
    for dx, dy in ((-26, -12), (26, -12), (-26, 12), (26, 12)):
        d.line([cx, cy, cx + dx, cy + dy], fill=(160, 160, 155), width=2)
        d.ellipse([cx + dx - 6, cy + dy - 3, cx + dx + 6, cy + dy + 3],
                  outline=(200, 200, 195), width=2)
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=RED)


def scene_inflation(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(240, 234, 214))
    d.polygon([(x + w * 0.18, y + h * 0.45), (x + w * 0.50, y + h * 0.45),
               (x + w * 0.45, y + h * 0.85), (x + w * 0.23, y + h * 0.85)],
              fill=(170, 120, 60))
    for i, (ox, col) in enumerate(((0.22, (220, 80, 60)), (0.30, (90, 160, 90)),
                                   (0.38, (230, 170, 50)))):
        d.ellipse([x + w * ox, y + h * 0.28, x + w * (ox + 0.08), y + h * 0.44],
                  fill=col)
    d.line([x + w * 0.55, y + h * 0.70, x + w * 0.88, y + h * 0.25], fill=RED, width=3)
    d.polygon([(x + w * 0.88, y + h * 0.25), (x + w * 0.76, y + h * 0.25),
               (x + w * 0.88, y + h * 0.38)], fill=RED)


def scene_press(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(228, 228, 222))
    d.rectangle([x + w * 0.15, y + h * 0.30, x + w * 0.85, y + h * 0.45], fill=(90, 90, 95))
    d.ellipse([x + w * 0.18, y + h * 0.22, x + w * 0.34, y + h * 0.52], fill=(150, 150, 150))
    d.ellipse([x + w * 0.66, y + h * 0.22, x + w * 0.82, y + h * 0.52], fill=(150, 150, 150))
    d.rectangle([x + w * 0.30, y + h * 0.55, x + w * 0.70, y + h * 0.82], fill=(250, 250, 246),
                outline=GREY)
    d.line([x + w * 0.35, y + h * 0.64, x + w * 0.65, y + h * 0.64], fill=GREY, width=1)
    d.line([x + w * 0.35, y + h * 0.72, x + w * 0.65, y + h * 0.72], fill=GREY, width=1)
    d.ellipse([x + w * 0.80, y + h * 0.12, x + w * 0.92, y + h * 0.28], outline=RED, width=3)
    d.line([x + w * 0.80, y + h * 0.12, x + w * 0.92, y + h * 0.28], fill=RED, width=3)


def scene_flag(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(222, 232, 240))
    d.line([x + w * 0.22, y + h * 0.12, x + w * 0.22, y + h * 0.88], fill=INK, width=3)
    d.polygon([(x + w * 0.22, y + h * 0.12), (x + w * 0.72, y + h * 0.20),
               (x + w * 0.22, y + h * 0.38)], fill=(220, 60, 50))
    d.polygon([(x + w * 0.22, y + h * 0.38), (x + w * 0.72, y + h * 0.20),
               (x + w * 0.60, y + h * 0.52), (x + w * 0.22, y + h * 0.52)],
              fill=(250, 210, 60))
    d.rectangle([x + w * 0.62, y + h * 0.58, x + w * 0.88, y + h * 0.88], fill=NAVY)
    d.polygon([(x + w * 0.60, y + h * 0.58), (x + w * 0.90, y + h * 0.58),
               (x + w * 0.75, y + h * 0.46)], fill=RED)


def scene_coins(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 234, 218))
    for i, cx in enumerate((0.24, 0.44, 0.64)):
        for j in range(3):
            yy = y + h * (0.78 - j * 0.16)
            d.ellipse([x + w * cx - 13, yy - 7, x + w * cx + 13, yy + 7], fill=GOLD,
                      outline=(140, 105, 30))
    d.text((x + w * 0.78, y + h * 0.18), "€", font=font(SERIF_B, 26), fill=NAVY)


def scene_seal(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 230, 224))
    d.rectangle([x + w * 0.16, y + h * 0.18, x + w * 0.62, y + h * 0.82], fill=(250, 250, 246),
                outline=GREY)
    for i in range(4):
        d.line([x + w * 0.22, y + h * (0.30 + i * 0.14), x + w * 0.56, y + h * (0.30 + i * 0.14)],
               fill=GREY, width=1)
    d.ellipse([x + w * 0.58, y + h * 0.30, x + w * 0.88, y + h * 0.68], outline=NAVY, width=4)
    d.line([x + w * 0.84, y + h * 0.62, x + w * 0.96, y + h * 0.82], fill=NAVY, width=4)
    d.text((x + w * 0.66, y + h * 0.40), "?", font=font(SERIF_B, 20), fill=RED)


def scene_screen(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(30, 28, 40))
    d.rectangle([x + w * 0.18, y + h * 0.14, x + w * 0.82, y + h * 0.58], fill=(240, 240, 235),
                outline=GOLD)
    d.polygon([(x + w * 0.30, y + h * 0.22), (x + w * 0.30, y + h * 0.50),
               (x + w * 0.62, y + h * 0.36)], fill=RED)
    for i in range(4):
        d.ellipse([x + w * (0.20 + i * 0.20), y + h * 0.68, x + w * (0.32 + i * 0.20),
                   y + h * 0.86], fill=(90, 85, 110))


def scene_cricket(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(206, 226, 190))
    d.line([x + w * 0.30, y + h * 0.20, x + w * 0.62, y + h * 0.72], fill=(160, 110, 60),
           width=7)
    d.ellipse([x + w * 0.66, y + h * 0.62, x + w * 0.78, y + h * 0.78], fill=RED)
    for i, ox in enumerate((0.14, 0.19, 0.24)):
        d.line([x + w * ox, y + h * 0.55, x + w * ox, y + h * 0.85], fill=(230, 200, 120),
               width=3)
    d.ellipse([x + w * 0.80, y + h * 0.14, x + w * 0.94, y + h * 0.32], fill=(250, 250, 246),
              outline=GREY)


def scene_tariff(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(210, 226, 236))
    d.polygon([(x + w * 0.12, y + h * 0.55), (x + w * 0.62, y + h * 0.55),
               (x + w * 0.55, y + h * 0.80), (x + w * 0.19, y + h * 0.80)],
              fill=(40, 48, 66))
    d.rectangle([x + w * 0.30, y + h * 0.30, x + w * 0.44, y + h * 0.55], fill=(240, 240, 235))
    d.ellipse([x + w * 0.66, y + h * 0.18, x + w * 0.94, y + h * 0.58], fill=RED)
    d.text((x + w * 0.71, y + h * 0.24), "%", font=font(SANS_B, 22), fill=(255, 255, 255))


SCENES = {
    "ballot": scene_ballot, "storm": scene_storm, "cuffs": scene_cuffs,
    "tanker": scene_tanker, "drone": scene_drone, "inflation": scene_inflation,
    "press": scene_press, "flag": scene_flag, "coins": scene_coins,
    "seal": scene_seal, "screen": scene_screen, "cricket": scene_cricket,
    "tariff": scene_tariff,
}


# ------------------------------------------------------------- page pieces
def draw_reported_badge(d, right, y, size=9):
    """Green REPORTED pill, right-aligned so its right edge is `right`."""
    label = "REPORTED"
    fnt = font(SANS_B, size)
    tw = d.textlength(label, font=fnt)
    pad = 5
    bw = tw + pad * 2
    x = right - bw
    d.rounded_rectangle([x, y, x + bw, y + size + 7], radius=2, fill=GREEN)
    d.text((x + pad, y + 1), label, font=fnt, fill=(255, 255, 255))
    return bw


def draw_card(d, card, x, y, w, h, hero):
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=INK, width=1)
    ill_h = 76 if hero else 52
    SCENES[card["scene"]](d, x + 1, y + 1, w - 2, ill_h)
    strip_y = y + ill_h + 1
    strip_h = 18 if hero else 16
    d.rectangle([x, y + ill_h + 1, x + w, strip_y + strip_h], fill=NAVY)
    lab_f = font(SANS_B, 11 if hero else 9)
    strip_label = f"{card['city']} · {card['tag']}" if hero else card["city"]
    d.text((x + 6, strip_y + 3 if hero else strip_y + 2),
           strip_label, font=lab_f, fill=(255, 255, 255))
    draw_reported_badge(d, x + w - 4, strip_y + 3 if hero else strip_y + 2,
                        size=9 if hero else 8)
    # body block
    bx = x + 6
    by = strip_y + strip_h + 5
    num = str(card["n"])
    nf = font(SANS_B, 13 if hero else 11)
    nw = d.textlength(num, font=nf) + 8
    d.rectangle([bx, by, bx + nw, by + 16], fill=RED)
    d.text((bx + 4, by + 1), num, font=nf, fill=(255, 255, 255))
    city_f = font(SANS_B, 12 if hero else 10)
    d.text((bx + nw + 5, by + 1), f"{card['city']} · {card['tag']}",
           font=city_f, fill=NAVY)
    hy = by + 21
    head_f = font(SERIF_B, 17 if hero else 13)
    head_lead = 20 if hero else 16
    head_lines = wrap(d, card["head"], head_f, w - 12)
    draw_lines(d, head_lines, bx, hy, head_f, INK, head_lead)
    body_f = font(SANS, 11 if hero else 9.5)
    body_lead = 13 if hero else 12
    body = card["body"] + " — " + card["src"]
    body_lines = wrap(d, body, body_f, w - 12)
    draw_lines(d, body_lines, bx, hy + len(head_lines) * head_lead + 3,
               body_f, (50, 50, 55), body_lead)


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    lon0, lon1, lat0, lat1 = -170.0, 190.0, 84.0, -58.0

    def project(lon, lat):
        px = x + (lon - lon0) / (lon1 - lon0) * w
        py = y + (lat0 - lat) / (lat0 - lat1) * h
        return px, py

    for land in LANDMASSES:
        pts = [project(lon, lat) for lon, lat in land]
        d.polygon(pts, fill=(238, 232, 210))
    for n, lon, lat, (dx, dy) in PINS:
        px, py = project(lon, lat)
        bx, by = px + dx, py + dy
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(255, 255, 255))
        if dx or dy:
            d.line([px, py, bx, by], fill=(255, 255, 255), width=1)
        d.ellipse([bx - 7, by - 7, bx + 7, by + 7], fill=RED, outline=(255, 255, 255))
        nf = font(SANS_B, 9)
        label = str(n)
        d.text((bx - d.textlength(label, font=nf) / 2, by - 6),
               label, font=nf, fill=(255, 255, 255))


# ------------------------------------------------------------------- build
def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    x0 = MARGIN

    # kicker row
    d.text((x0, 14), "THE WORLD IN ONE DAY", font=font(SANS_B, 15), fill=RED)
    right = "36 STORIES · ALL FROM THIS ONE DAY"
    rf = font(SANS_B, 13)
    d.text((x0 + CW - d.textlength(right, font=rf), 15), right, font=rf, fill=NAVY)

    # masthead + standfirst
    d.text((x0, 30), "Friday 27 November 2026", font=font(SERIF_B, 54), fill=INK)
    d.text((x0, 94), "A hung parliament in Wellington · a Thanksgiving storm strands America · Delhi busts a cyber-slavery ring.",
           font=font(SERIF_I, 16), fill=RED)
    d.line([x0, 118, x0 + CW, 118], fill=INK, width=2)
    d.line([x0, 122, x0 + CW, 122], fill=INK, width=1)

    # region tally bar
    widths = [262, 262, 236, 78, 78, 60]
    tx = x0
    for (label, _count, colour), tw in zip(TALLY, widths):
        d.rectangle([tx, 128, tx + tw, 148], fill=colour)
        centre(d, tx + tw / 2, 132, label, font(SANS_B, 10), (255, 255, 255))
        tx += tw

    # day in numbers
    ny = 154
    d.rectangle([x0, ny, x0 + 118, ny + 56], fill=RED)
    centre(d, x0 + 59, ny + 10, "THE DAY IN", font(SANS_B, 13), (255, 255, 255))
    centre(d, x0 + 59, ny + 28, "NUMBERS", font(SANS_B, 13), (255, 255, 255))
    stat_w = (CW - 118) / len(NUMBERS)
    for i, (big, small) in enumerate(NUMBERS):
        cx = x0 + 118 + stat_w * (i + 0.5)
        centre(d, cx, ny + 2, big, font(SERIF_B, 25), RED)
        for j, line in enumerate(wrap(d, small, font(SANS, 10), stat_w - 12)):
            centre(d, cx, ny + 32 + j * 12, line, font(SANS, 10), (60, 60, 60))
    d.line([x0, ny + 62, x0 + CW, ny + 62], fill=INK, width=1)

    # hero cards
    hy = 222
    hw = (CW - 20) // 3
    for i, card in enumerate(CARDS[:3]):
        draw_card(d, card, x0 + i * (hw + 10), hy, hw, 196, hero=True)

    # small cards, two rows of five
    sy = 426
    sw = (CW - 32) // 5
    for row in range(2):
        for col in range(5):
            card = CARDS[3 + row * 5 + col]
            draw_card(d, card, x0 + col * (sw + 8), sy + row * 166, sw, 158, hero=False)

    # section headers
    hy2 = 758
    d.text((x0, hy2), "WHERE IT HAPPENED", font=font(SANS_B, 13), fill=INK)
    d.text((x0 + 340, hy2), "ALSO ON FRIDAY — 23 MORE STORIES", font=font(SANS_B, 13), fill=INK)
    hint = "place · what happened · source"
    hf = font(SANS, 9)
    d.text((x0 + CW - d.textlength(hint, font=hf), hy2 + 2), hint, font=hf, fill=GREY)

    # map + briefs
    my = 778
    draw_map(d, x0, my, 328, 126)
    d.text((x0, my + 130), "Pins 1–13 are the card stories above.",
           font=font(SANS, 10), fill=GREY)
    bx0 = x0 + 340
    col_w = 318
    bf_num = font(SANS_B, 9.5)
    bf_city = font(SANS_B, 9.5)
    bf_txt = font(SANS, 9.5)
    bf_src = font(SANS, 9.5)
    for col in range(2):
        col_briefs = BRIEFS[col * 12:(col + 1) * 12]
        for row, (n, city, text, src) in enumerate(col_briefs):
            ry = my + row * 11
            cx = bx0 + col * (col_w + 12)
            d.text((cx, ry), str(n), font=bf_num, fill=RED)
            num_w = d.textlength(str(n), font=bf_num) + 4
            d.text((cx + num_w, ry), city, font=bf_city, fill=INK)
            city_w = d.textlength(city, font=bf_city)
            d.text((cx + num_w + city_w + 4, ry), "— " + text, font=bf_txt, fill=INK)
            txt_w = d.textlength("— " + text, font=bf_txt)
            d.text((cx + num_w + city_w + 4 + txt_w + 4, ry), "· " + src,
                   font=bf_src, fill=GREY)

    # date check box: label runs inline at the start of the first line,
    # so the body wraps with a narrower first line.
    dy = 918
    box_h = 56
    d.rectangle([x0, dy, x0 + CW, dy + box_h], outline=RED, width=2)
    lab_f = font(SANS_B, 11)
    label = "✓ DATE CHECK  "
    lab_w = d.textlength(label, font=lab_f)
    body_f = font(SANS, 10)
    inner_w = CW - 24
    first = wrap(d, DATE_CHECK, body_f, inner_w - lab_w)
    rest = []
    if first:
        # re-wrap: first line holds what fits after the label, the rest
        # flows at full width.
        first_line = first[0]
        remaining = DATE_CHECK[len(first_line):].strip()
        rest = wrap(d, remaining, body_f, inner_w) if remaining else []
        all_lines = [first_line] + rest
    else:
        all_lines = []
    d.text((x0 + 12, dy + 8), label, font=lab_f, fill=RED)
    for i, line in enumerate(all_lines):
        lx = x0 + 12 + (lab_w if i == 0 else 0)
        d.text((lx, dy + 8 + i * 12), line, font=body_f, fill=INK)

    # footer
    fy = 996
    d.text((x0, fy), "Sources: 1News · NDTV · Economic Times · Qatar Tribune · Scoop · AJP · Times of India · Dawn — every story above happened, or was first reported, on Friday 27 November 2026.",
           font=font(SANS, 10), fill=GREY)
    foot2 = "Pictures and map drawn in code, not photographs"
    ff = font(SANS, 9)
    d.text((x0 + CW - d.textlength(foot2, font=ff), fy + 13), foot2, font=ff, fill=GREY)

    return img


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "entry.png"
    img = build()
    img.save(out, format="PNG")
    print(f"wrote {out} ({img.size[0]}x{img.size[1]})")


if __name__ == "__main__":
    main()
