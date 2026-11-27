#!/usr/bin/env python3
"""Compose the 27 November 2026 front page: one 1024x1024 newspaper
sheet summing up a single day of world news in 36 stories.

Everything is drawn with PIL primitives -- masthead, region bar,
numbers strip, thirteen story cards with small spot illustrations, a
schematic world map with numbered pins, a briefs block, the red DATE
CHECK box and the footer. No photographs, no outside assets.

Every story on the page happened, or was first reported, on Friday
27 November 2026. Stories from Thursday 26 November that the wires
carried again today are listed in the DATE CHECK box instead.
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from worldmap_data import OUTLINES, ISLANDS

SIDE = 1024
EDGE = 26

PAPER = (246, 241, 230)
INK = (24, 28, 38)
NAVY = (18, 38, 84)
RED = (178, 32, 38)
GOLD = (176, 132, 40)
GREY = (96, 98, 104)
CARD = (252, 250, 244)
SCENE = (238, 233, 219)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def load_font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def serif_b(size):
    return load_font("DejaVuSerif-Bold.ttf", size)


def serif_r(size):
    return load_font("DejaVuSerif.ttf", size)


def sans_r(size):
    return load_font("DejaVuSans.ttf", size)


def sans_b(size):
    return load_font("DejaVuSans-Bold.ttf", size)


def text_w(d, s, fnt):
    return d.textlength(s, font=fnt)


def wrap(d, s, fnt, width, limit=None):
    """Greedy wrap; over-long words are split by character."""
    out = []
    for chunk in s.split("\n"):
        words = chunk.split(" ")
        cur = ""
        for w in words:
            trial = (cur + " " + w).strip()
            if text_w(d, trial, fnt) <= width:
                cur = trial
                continue
            if cur:
                out.append(cur)
                cur = ""
            while text_w(d, w, fnt) > width and len(w) > 1:
                cut = len(w)
                while cut > 1 and text_w(d, w[:cut], fnt) > width:
                    cut -= 1
                out.append(w[:cut])
                w = w[cut:]
            cur = w
        out.append(cur)
    if limit and len(out) > limit:
        out = out[:limit]
    return out


def para(d, xy, s, fnt, fill, width, leading, limit=None):
    x, y = xy
    for ln in wrap(d, s, fnt, width, limit):
        d.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


def centred(d, cx, y, s, fnt, fill):
    d.text((cx - text_w(d, s, fnt) / 2, y), s, font=fnt, fill=fill)


def hline(d, x0, x1, y, fill=INK, w=2):
    d.line([(x0, y), (x1, y)], fill=fill, width=w)


def box(d, coords, fill=None, outline=None, width=1):
    d.rectangle(coords, fill=fill, outline=outline, width=width)


def round_box(d, coords, radius, fill=None, outline=None, width=1):
    d.rounded_rectangle(coords, radius=radius, fill=fill, outline=outline,
                        width=width)


def starburst(d, cx, cy, r, fill):
    """Eight-point flash."""
    pts = []
    for i in range(16):
        ang = math.pi * i / 8
        rad = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    d.polygon(pts, fill=fill)


def smoke(d, x, y, scale=1.0, tone=(150, 148, 142)):
    """A rising smoke column: four growing circles."""
    for dx, dy, r in [(0, 0, 9), (6, -10, 12), (14, -22, 15), (24, -36, 18)]:
        d.ellipse([x + dx * scale - r * scale, y + dy * scale - r * scale,
                   x + dx * scale + r * scale, y + dy * scale + r * scale],
                  fill=tone)


# ---------------------------------------------------------------- content
KICKER = "THE WORLD IN ONE DAY"
MASTHEAD = "Friday 27 November 2026"
STAND = ("A hung parliament in Wellington · a Thanksgiving storm "
         "strands America · Delhi busts a cyber-slavery ring")

HEROES = [
    dict(n=1, city="WELLINGTON", tag="ELECTION", scene="ballot",
         head="Final count leaves New Zealand hung at 65–65",
         src="1News"),
    dict(n=2, city="NEW YORK", tag="WEATHER", scene="storm",
         head="Thanksgiving storm: 400 flights cut, 724,000 in the dark",
         src="NDTV"),
    dict(n=3, city="NEW DELHI", tag="CRIME", scene="cuffs",
         head="Delhi police smash a cyber-slavery ring; 164 freed",
         src="NDTV"),
]

SMALLS = [
    dict(n=4, city="HORMUZ", tag="GULF", scene="tanker",
         head="Blasts hit three tankers in the Strait of Hormuz",
         src="QT"),
    dict(n=5, city="KYIV", tag="WAR", scene="drone",
         head="Zelensky warns of a new mass strike",
         src="NDTV"),
    dict(n=6, city="TOKYO", tag="ECONOMY", scene="inflation",
         head="Tokyo core prices rise 2.9%, past forecasts",
         src="NDTV"),
    dict(n=7, city="BUENOS AIRES", tag="ECONOMY", scene="press",
         head="Argentina bars its bank from printing money",
         src="ET"),
    dict(n=8, city="BERLIN", tag="MIGRATION", scene="flag",
         head="Berlin offers more to return Syrians",
         src="QT"),
    dict(n=9, city="BRUSSELS", tag="EUROPE", scene="coins",
         head="EU split over a $49bn loan for Ukraine",
         src="ET"),
    dict(n=10, city="MINNEAPOLIS", tag="FRAUD", scene="seal",
         head="'Ghost daycares' aired at a House hearing",
         src="ET"),
    dict(n=11, city="SEOUL", tag="FILM", scene="screen",
         head="Dune: Part Three leads advance sales",
         src="AJP"),
    dict(n=12, city="CHRISTCHURCH", tag="CRICKET", scene="cricket",
         head="Debutant strikes as India face New Zealand",
         src="NDTV"),
    dict(n=13, city="GENEVA", tag="TRADE", scene="tariff",
         head="Global maritime trade set for zero growth",
         src="ET"),
]

BODY = {
    1: ("Special votes erase the coalition's majority: 65 seats each, "
        "and Luxon needs Opportunity's seven."),
    2: ("Nearly 400 flights cancelled, 2,000 delayed, mostly in the "
        "east; 724,000 homes without power."),
    3: ("Raids free 164 foreigners — 92 Indonesians, 72 Malaysians — "
        "held by a cyber-slavery ring."),
    4: "Explosions aboard three tankers as the Gulf campaign widens.",
    5: "New mass strike feared as attacks run daily since September.",
    6: "Core prices up 2.9% on the year, from 2.6% in October.",
    7: "Buenos Aires bans the bank from printing money for the state.",
    8: "Berlin readies a bigger return plan, with higher cash bonuses.",
    9: "Leaders split as a $49bn loan for Ukraine is weighed.",
    10: "A House hearing airs fraud claims at Minnesota daycares.",
    11: "Advance bookings near 105,000 ahead of the Dec 16 opening.",
    12: "Debutant Gurnoor Brar strikes late; New Zealand 77 for 1.",
    13: "UN sees zero growth in 2026 as Gulf attacks snarl shipping.",
}

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

NUMBERS = [
    ("724,000", "without power in the storm"),
    ("400", "Thanksgiving flights cancelled"),
    ("65", "seats a side in a hung House"),
    ("164", "rescued in the Delhi bust"),
    ("2.9%", "Tokyo core inflation"),
    ("248", "files in the USAID dump"),
]

# Regions with at least one story, largest first.
REGION_BAR = [("AMERICAS", 10), ("ASIA", 10), ("EUROPE", 9),
              ("MIDDLE EAST", 3), ("OCEANIA", 3), ("GLOBAL", 1)]
REGION_COLOURS = [(64, 128, 120), (70, 90, 140), (96, 108, 128),
                  (150, 90, 60), (120, 130, 80), (110, 110, 110)]

DATE_CHECK = (
    "NOT FRIDAY — Thu 26 Nov: drones kill two Italians at a Kuwait "
    "air base, Iran denies it; UK net migration falls to 77,000; "
    "Spain's Pablo Hernández de Cos is picked to lead the ECB; a "
    "diesel tanker capsizes off Ibiza, one dead; Trump signs Florida "
    "flood aid; Macy's 100th parade marches. Wed 25 Nov: troops free "
    "all hostages in Cartagena. NOT YET: Eisenkot's deadline (Dec 6) "
    "· Hasina's flight home (Dec 16) · Dune: Part Three opens (Dec 16)."
)

FOOTER = ("Sources: 1News · NDTV · Economic Times · Qatar Tribune · "
          "Scoop · AJP · Times of India · Dawn — every story above "
          "happened, or was first reported, on Friday 27 November 2026.")

# Pin positions for the thirteen cards: story number -> (lon, lat).
PINS = {
    1: (174.78, -41.29), 2: (-74.01, 40.71), 3: (77.21, 28.61),
    4: (56.50, 26.60), 5: (30.52, 50.45), 6: (139.69, 35.68),
    7: (-58.38, -34.60), 8: (13.40, 52.52), 9: (4.35, 50.85),
    10: (-93.27, 44.98), 11: (126.98, 37.57), 12: (172.64, -43.53),
    13: (6.14, 46.20),
}

# Display nudges (pixels) for pins closer than one pin diameter:
# Wellington/Christchurch, Kyiv/Berlin/Brussels/Geneva, Tokyo/Seoul.
# Each marker shifts in its city's true relative direction so both
# numerals stay readable.
NUDGE = {1: (7, -7), 5: (-8, 7), 6: (7, -3), 8: (10, -6), 9: (-7, 5),
         11: (-7, 3), 12: (-7, 6), 13: (4, 9)}


# ---------------------------------------------------------------- scenes
def scene_ballot(d, x, y, w, h):
    """Wellington: a ballot box, a paper going in, a 65–65 tally."""
    box(d, [x, y, x + w, y + h], fill=(226, 232, 238))
    # tally board
    tf = sans_b(15)
    d.text((x + w * 0.1, y + h * 0.08), "65 – 65", font=tf, fill=RED)
    d.text((x + w * 0.62, y + h * 0.08), "HUNG", font=tf, fill=NAVY)
    # ballot paper sliding into the slot
    px, py = x + w * 0.3, y + h * 0.28
    d.polygon([(px, py), (px + 64, py - 8), (px + 64, py + 34),
               (px, py + 42)], fill=(252, 250, 244), outline=INK, width=1)
    d.line([(px + 10, py + 10), (px + 54, py + 4)], fill=GREY, width=1)
    d.line([(px + 10, py + 20), (px + 54, py + 14)], fill=GREY, width=1)
    # the box
    bx, by = x + w * 0.2, y + h * 0.58
    box(d, [bx, by, bx + w * 0.6, by + h * 0.34], fill=NAVY)
    d.line([(bx + 8, by), (bx + w * 0.6 - 8, by)], fill=(250, 248, 240),
           width=3)
    starburst(d, x + w * 0.86, y + h * 0.78, 8, GOLD)


def scene_storm(d, x, y, w, h):
    """Thanksgiving storm: low cloud, rain, a lightning bolt."""
    box(d, [x, y, x + w, y + h], fill=(30, 38, 54))
    # cloud bank
    for cx, cy, r in [(0.3, 0.3, 26), (0.5, 0.22, 30), (0.7, 0.32, 24)]:
        d.ellipse([x + w * cx - r, y + h * cy - r * 0.7,
                   x + w * cx + r, y + h * cy + r * 0.7],
                  fill=(120, 128, 148))
    # rain streaks
    for i in range(9):
        rx = x + w * (0.08 + i * 0.1)
        d.line([(rx, y + h * 0.55), (rx - 6, y + h * 0.85)],
               fill=(150, 170, 210), width=2)
    # lightning bolt
    bx = x + w * 0.62
    d.polygon([(bx + 8, y + h * 0.34), (bx - 8, y + h * 0.58),
               (bx, y + h * 0.58), (bx - 6, y + h * 0.82),
               (bx + 12, y + h * 0.54), (bx + 3, y + h * 0.54)],
              fill=GOLD)
    # a grounded jet, nose down in the rain
    jx, jy = x + w * 0.22, y + h * 0.78
    d.ellipse([jx - 26, jy - 6, jx + 26, jy + 6], fill=(200, 204, 214))
    d.polygon([(jx + 20, jy - 4), (jx + 34, jy - 12), (jx + 30, jy + 2)],
              fill=(200, 204, 214))


def scene_cuffs(d, x, y, w, h):
    """Delhi bust: handcuffs, one link broken open."""
    box(d, [x, y, x + w, y + h], fill=(222, 228, 238))
    # two cuffs joined by a short chain
    for cx in (0.32, 0.68):
        px = x + w * cx
        d.ellipse([px - 20, y + h * 0.42, px + 20, y + h * 0.42 + 40],
                  outline=NAVY, width=4)
        d.ellipse([px - 8, y + h * 0.42 + 12, px + 8,
                   y + h * 0.42 + 28], fill=NAVY)
    d.line([(x + w * 0.32 + 18, y + h * 0.55),
            (x + w * 0.68 - 18, y + h * 0.55)], fill=NAVY, width=3)
    # the broken link, in red
    mx, my = x + w * 0.5, y + h * 0.55
    d.arc([mx - 8, my - 8, mx + 8, my + 8], 20, 300, fill=RED, width=3)
    # a freed bird above
    d.arc([x + w * 0.44, y + h * 0.16, x + w * 0.5, y + h * 0.24], 200,
          340, fill=INK, width=2)
    d.arc([x + w * 0.5, y + h * 0.16, x + w * 0.56, y + h * 0.24], 200,
          340, fill=INK, width=2)


def scene_tanker(d, x, y, w, h):
    """Strait of Hormuz: a tanker listing, smoke and flame."""
    box(d, [x, y, x + w, y + h], fill=(186, 216, 236))
    for i in range(3):
        yy = y + h * (0.68 + i * 0.1)
        d.arc([x + 6, yy, x + w - 6, yy + 12], 0, 180,
              fill=(60, 110, 160), width=2)
    # listing hull
    hx, hy = x + w * 0.5, y + h * 0.62
    d.polygon([(hx - 62, hy - 14), (hx + 58, hy - 22), (hx + 52, hy + 10),
               (hx - 56, hy + 10)], fill=(40, 44, 54))
    # deck containers, tilted with the hull
    for i, col in enumerate([(178, 32, 38), (60, 110, 160), (176, 132, 40)]):
        cx = hx - 40 + i * 34
        d.polygon([(cx, hy - 30), (cx + 28, hy - 32), (cx + 28, hy - 16),
                   (cx, hy - 14)], fill=col)
    # flame and smoke from the deck
    starburst(d, hx + 18, hy - 34, 12, (246, 160, 30))
    smoke(d, hx - 30, hy - 30, 0.7, tone=(96, 92, 88))


def scene_drone(d, x, y, w, h):
    """Kyiv: a quadcopter over night rooftops, a searchlight."""
    box(d, [x, y, x + w, y + h], fill=(14, 20, 44))
    for fx, fy in [(0.08, 0.14), (0.9, 0.1), (0.72, 0.22), (0.2, 0.3)]:
        d.ellipse([x + w * fx, y + h * fy, x + w * fx + 3, y + h * fy + 3],
                  fill=(230, 230, 220))
    base = y + h * 0.94
    for fx, fw, fh in [(0.04, 0.24, 0.42), (0.32, 0.2, 0.58),
                       (0.56, 0.22, 0.48), (0.8, 0.18, 0.36)]:
        box(d, [x + w * fx, base - h * fh, x + w * (fx + fw), base],
            fill=(30, 40, 74))
        for r in range(2):
            for c in range(2):
                if (r * 2 + c + int(fx * 12)) % 3 == 0:
                    box(d, [x + w * fx + 5 + c * 12,
                            base - h * fh + 6 + r * 12,
                            x + w * fx + 11 + c * 12,
                            base - h * fh + 13 + r * 12], fill=GOLD)
    d.polygon([(x + w * 0.12, base), (x + w * 0.3, base),
               (x + w * 0.55, y + h * 0.3)], fill=(220, 220, 190))
    qx, qy = x + w * 0.62, y + h * 0.3
    box(d, [qx - 12, qy - 5, qx + 12, qy + 5], fill=(200, 205, 215))
    for sx in (-1, 1):
        d.line([(qx + sx * 12, qy), (qx + sx * 26, qy - 6)],
               fill=(200, 205, 215), width=2)
        d.ellipse([qx + sx * 26 - 10, qy - 12, qx + sx * 26 + 10, qy - 2],
                  outline=(200, 205, 215), width=1)
    d.ellipse([qx - 3, qy - 3, qx + 3, qy + 3], fill=RED)


def scene_inflation(d, x, y, w, h):
    """Tokyo prices: a shopping basket and a climbing arrow."""
    box(d, [x, y, x + w, y + h], fill=(244, 236, 214))
    cx, base = x + w * 0.42, y + h * 0.88
    d.polygon([(cx - 46, base - 34), (cx + 46, base - 34),
               (cx + 36, base), (cx - 36, base)], fill=(176, 132, 70),
              outline=(120, 88, 40), width=2)
    d.arc([cx - 26, base - 58, cx + 26, base - 30], 180, 360,
          fill=(120, 88, 40), width=3)
    for dx, col in [(-30, (220, 60, 40)), (-10, (240, 160, 40)),
                    (10, (120, 160, 60)), (30, (220, 60, 40))]:
        d.ellipse([cx + dx - 11, base - 48, cx + dx + 11, base - 26],
                  fill=col, outline=(90, 70, 40), width=1)
    d.line([(x + w * 0.68, y + h * 0.8), (x + w * 0.92, y + h * 0.3)],
           fill=RED, width=4)
    d.polygon([(x + w * 0.92, y + h * 0.3), (x + w * 0.84, y + h * 0.32),
               (x + w * 0.92, y + h * 0.42)], fill=RED)
    d.text((x + w * 0.66, y + h * 0.12), "¥", font=sans_b(18), fill=RED)


def scene_press(d, x, y, w, h):
    """Buenos Aires: the printing press, stopped by a red ban."""
    box(d, [x, y, x + w, y + h], fill=(244, 236, 214))
    # the press: two rollers and a sheet coming out
    box(d, [x + w * 0.1, y + h * 0.2, x + w * 0.62, y + h * 0.62],
        fill=(120, 124, 132), outline=INK, width=2)
    d.ellipse([x + w * 0.2, y + h * 0.3, x + w * 0.3, y + h * 0.52],
              fill=(200, 204, 214), outline=INK, width=1)
    d.ellipse([x + w * 0.42, y + h * 0.3, x + w * 0.52, y + h * 0.52],
              fill=(200, 204, 214), outline=INK, width=1)
    sx, sy = x + w * 0.16, y + h * 0.62
    d.polygon([(sx, sy), (sx + 76, sy), (sx + 76, sy + 30),
               (sx, sy + 30)], fill=(252, 250, 244), outline=INK, width=1)
    for i in range(2):
        d.line([(sx + 8, sy + 9 + i * 9), (sx + 68, sy + 9 + i * 9)],
               fill=(150, 150, 148), width=1)
    # a banknote under the ban sign
    bx, by = x + w * 0.72, y + h * 0.62
    box(d, [bx, by, bx + 34, by + 20], fill=(140, 170, 90),
        outline=(90, 110, 50), width=1)
    d.text((bx + 11, by + 1), "$", font=sans_b(14), fill=(60, 80, 30))
    d.ellipse([bx - 4, by - 12, bx + 38, by + 30], outline=RED, width=4)
    d.line([(bx - 4, by + 30), (bx + 38, by - 12)], fill=RED, width=4)


def scene_flag(d, x, y, w, h):
    """Berlin: a skyline under a waving flag."""
    box(d, [x, y, x + w, y + h], fill=(208, 218, 234))
    base = y + h * 0.92
    for fx, fw, fh in [(0.05, 0.14, 0.42), (0.22, 0.12, 0.6),
                       (0.38, 0.16, 0.5), (0.58, 0.13, 0.66),
                       (0.74, 0.14, 0.46)]:
        box(d, [x + w * fx, base - h * fh, x + w * (fx + fw), base],
            fill=NAVY)
        for r in range(2):
            for c in range(2):
                if (r + c + int(fx * 20)) % 2:
                    box(d, [x + w * fx + 4 + c * 10,
                            base - h * fh + 6 + r * 11,
                            x + w * fx + 9 + c * 10,
                            base - h * fh + 12 + r * 11], fill=GOLD)
    fx, fw, fh = 0.58, 0.13, 0.66
    px = x + w * (fx + fw / 2)
    d.line([(px, base - h * fh), (px, base - h * fh - 16)], fill=INK,
           width=2)
    d.polygon([(px, base - h * fh - 16), (px + 18, base - h * fh - 12),
               (px, base - h * fh - 8)], fill=RED)
    starburst(d, x + w * 0.88, y + h * 0.2, 8, GOLD)


def scene_coins(d, x, y, w, h):
    """Brussels: stacked coins and a euro sign, split down the middle."""
    box(d, [x, y, x + w, y + h], fill=(240, 232, 210))
    # three coin stacks of different heights
    for sx, n in [(0.2, 4), (0.45, 6), (0.7, 3)]:
        cx = x + w * sx
        for i in range(n):
            yy = y + h * 0.88 - i * 9
            d.ellipse([cx - 18, yy - 9, cx + 18, yy], fill=GOLD,
                      outline=(140, 100, 30), width=1)
    # the euro sign, split by a crack
    d.text((x + w * 0.42, y + h * 0.06), "€", font=sans_b(30), fill=NAVY)
    d.line([(x + w * 0.55, y + h * 0.06), (x + w * 0.48, y + h * 0.34)],
           fill=RED, width=3)


def scene_seal(d, x, y, w, h):
    """Minneapolis hearing: a document, a broken seal, a magnifier."""
    box(d, [x, y, x + w, y + h], fill=(222, 230, 242))
    dx0, dy0 = x + w * 0.16, y + h * 0.12
    box(d, [dx0, dy0, dx0 + 88, dy0 + 62], fill=(252, 250, 244),
        outline=INK, width=2)
    for i in range(4):
        d.line([(dx0 + 10, dy0 + 12 + i * 10),
                (dx0 + 78, dy0 + 12 + i * 10)], fill=(130, 134, 142),
               width=1)
    sx, sy = dx0 + 66, dy0 + 48
    d.pieslice([sx - 12, sy - 12, sx + 12, sy + 12], 90, 270, fill=RED)
    d.pieslice([sx + 6, sy - 12, sx + 30, sy + 12], 270, 90, fill=RED)
    mx, my = x + w * 0.8, y + h * 0.58
    d.ellipse([mx - 18, my - 18, mx + 18, my + 18], outline=NAVY, width=3)
    d.line([(mx + 13, my + 13), (mx + 28, my + 28)], fill=NAVY, width=4)


def scene_screen(d, x, y, w, h):
    """Seoul cinema: a lit screen, a projector beam, rows of seats."""
    box(d, [x, y, x + w, y + h], fill=(20, 20, 36))
    # the screen
    sx, sy = x + w * 0.22, y + h * 0.1
    box(d, [sx, sy, sx + w * 0.56, sy + h * 0.42], fill=(240, 242, 246),
        outline=(140, 144, 158), width=2)
    d.polygon([(sx + 8, sy + 8), (sx + w * 0.56 - 8, sy + 8),
               (sx + w * 0.28, sy + h * 0.42 - 8)], fill=(90, 110, 160))
    starburst(d, sx + w * 0.28, sy + h * 0.2, 7, GOLD)
    # projector beam from the back
    d.polygon([(x + w * 0.5, y + h * 0.95), (x + w * 0.46, y + h * 0.95),
               (sx + w * 0.28, sy + h * 0.42)], fill=(90, 90, 140))
    # seat rows
    for r in range(2):
        for c in range(5):
            px = x + w * (0.16 + c * 0.17)
            py = y + h * (0.68 + r * 0.14)
            d.ellipse([px - 8, py - 5, px + 8, py + 5], fill=(70, 70, 100))


def scene_cricket(d, x, y, w, h):
    """Christchurch Test: the pitch, the stumps, a red ball."""
    box(d, [x, y, x + w, y + h], fill=(120, 170, 90))
    # the pitch strip
    px = x + w * 0.42
    box(d, [px, y + h * 0.08, px + w * 0.16, y + h * 0.92],
        fill=(222, 200, 150))
    # stumps at both ends
    for sy in (0.16, 0.78):
        for i in range(3):
            d.line([(px + 6 + i * 8, y + h * sy),
                    (px + 6 + i * 8, y + h * (sy + 0.09))],
                   fill=(240, 220, 150), width=2)
    # the batsman's bat, mid-swing, and the ball
    bx, by = x + w * 0.68, y + h * 0.5
    d.polygon([(bx, by - 26), (bx + 12, by - 22), (bx + 8, by + 12),
               (bx - 2, by + 10)], fill=(200, 170, 110), outline=INK,
              width=1)
    d.ellipse([x + w * 0.2 - 8, y + h * 0.3 - 8, x + w * 0.2 + 8,
               y + h * 0.3 + 8], fill=RED, outline=(120, 20, 24), width=1)
    d.arc([x + w * 0.14, y + h * 0.24, x + w * 0.26, y + h * 0.36], 0,
          180, fill=(255, 252, 244), width=1)


def scene_tariff(d, x, y, w, h):
    """Geneva trade: a container, a red tag, a rising arrow."""
    box(d, [x, y, x + w, y + h], fill=(222, 230, 238))
    cx, cy = x + w * 0.38, y + h * 0.52
    box(d, [cx - 52, cy - 24, cx + 52, cy + 24], fill=(58, 96, 150),
        outline=NAVY, width=2)
    for i in range(6):
        d.line([(cx - 52 + i * 17, cy - 24), (cx - 52 + i * 17, cy + 24)],
               fill=(40, 74, 120), width=2)
    gx, gy = x + w * 0.8, y + h * 0.5
    d.polygon([(gx - 24, gy - 16), (gx + 14, gy - 16), (gx + 26, gy),
               (gx + 14, gy + 16), (gx - 24, gy + 16)], fill=RED)
    d.ellipse([gx - 16, gy - 4, gx - 8, gy + 4], fill=(250, 248, 240))
    d.text((gx - 2, gy - 13), "%", font=sans_b(20), fill=(255, 252, 244))
    d.line([(x + w * 0.1, y + h * 0.82), (x + w * 0.28, y + h * 0.62)],
           fill=RED, width=3)
    d.polygon([(x + w * 0.28, y + h * 0.62), (x + w * 0.2, y + h * 0.64),
               (x + w * 0.28, y + h * 0.72)], fill=RED)


SCENES = {
    "ballot": scene_ballot, "storm": scene_storm, "cuffs": scene_cuffs,
    "tanker": scene_tanker, "drone": scene_drone,
    "inflation": scene_inflation, "press": scene_press,
    "flag": scene_flag, "coins": scene_coins, "seal": scene_seal,
    "screen": scene_screen, "cricket": scene_cricket,
    "tariff": scene_tariff,
}


# ---------------------------------------------------------------- layout
def paint_header(d):
    kf = sans_b(14)
    d.text((EDGE, 20), KICKER, font=kf, fill=RED)
    right = "36 STORIES · ALL FROM THIS ONE DAY"
    d.text((SIDE - EDGE - text_w(d, right, kf), 20), right, font=kf,
           fill=NAVY)
    d.text((EDGE, 38), MASTHEAD, font=serif_b(54), fill=INK)
    d.text((EDGE, 100), STAND, font=serif_r(14.5), fill=RED)
    hline(d, EDGE, SIDE - EDGE, 124, fill=INK, w=3)


def paint_regions(d, y):
    total = sum(c for _, c in REGION_BAR)
    f = sans_b(9.8)
    # Proportional widths, but no segment may be narrower than its
    # own label: widen any short segment and take the extra from the
    # widest one, so every label stays inside the bar.
    widths = [(SIDE - 2 * EDGE) * c / total for _, c in REGION_BAR]
    for i, (name, count) in enumerate(REGION_BAR):
        need = text_w(d, "%s %d" % (name, count), f) + 10
        if widths[i] < need:
            extra = need - widths[i]
            widths[i] = need
            j = max(range(len(widths)), key=lambda k: widths[k])
            widths[j] -= extra
    x = EDGE
    for (name, count), colour, wseg in zip(REGION_BAR, REGION_COLOURS,
                                           widths):
        box(d, [x, y, x + wseg, y + 22], fill=colour)
        label = "%s %d" % (name, count)
        d.text((x + wseg / 2 - text_w(d, label, f) / 2, y + 5), label,
               font=f, fill=(250, 248, 240))
        x += wseg


def paint_numbers(d, y):
    box(d, [EDGE, y, EDGE + 96, y + 48], fill=RED)
    f = sans_b(12.5)
    centred(d, EDGE + 48, y + 7, "THE DAY IN", f, (255, 252, 244))
    centred(d, EDGE + 48, y + 25, "NUMBERS", f, (255, 252, 244))
    seg = (SIDE - EDGE - (EDGE + 96)) / 6
    big = serif_b(23)
    small = sans_r(9.3)
    for i, (num, label) in enumerate(NUMBERS):
        cx = EDGE + 96 + seg * i + seg / 2
        centred(d, cx, y, num, big, RED)
        ly = y + 30
        for ln in wrap(d, label, small, seg - 8)[:2]:
            centred(d, cx, ly, ln, small, (52, 54, 62))
            ly += 12
    hline(d, EDGE, SIDE - EDGE, y + 52, fill=INK, w=1)


def paint_card(img, d, card, x, y, w, h, hero):
    box(d, [x, y, x + w, y + h], fill=CARD, outline=INK, width=2)
    scene_h = 80 if hero else 52
    strip_h = 15 if hero else 13
    # The illustration is rendered on its own canvas so nothing a
    # scene draws can spill past the card's border.
    canvas = Image.new("RGB", (w - 4, scene_h), SCENE)
    SCENES[card["scene"]](ImageDraw.Draw(canvas), 0, 0, w - 4, scene_h)
    img.paste(canvas, (x + 2, y + 2))
    sy = y + 2 + scene_h
    box(d, [x + 2, sy, x + w - 2, sy + strip_h], fill=NAVY)
    tf = sans_b(9 if hero else 8)
    d.text((x + 7, sy + (3 if hero else 2)),
           "%s · %s" % (card["city"], card["tag"]), font=tf,
           fill=(240, 242, 248))
    # reported chip, top right of the strip
    chip = "REPORTED"
    cf = sans_b(8)
    cw = text_w(d, chip, cf) + 10
    round_box(d, [x + w - 7 - cw, sy + 1, x + w - 7, sy + 14], 3,
              fill=(84, 140, 84))
    d.text((x + w - 7 - cw + 5, sy + 3), chip, font=cf,
           fill=(250, 252, 246))
    cy = sy + strip_h + 6
    n = str(card["n"])
    nf = sans_b(11 if hero else 9.5)
    box(d, [x + 8, cy, x + 8 + 17, cy + 17], fill=RED)
    centred(d, x + 8 + 8.5, cy + 2, n, nf, (255, 252, 244))
    hf = sans_b(11.5 if hero else 9.5)
    d.text((x + 31, cy + 2), "%s · %s" % (card["city"], card["tag"]),
           font=hf, fill=NAVY)
    bf = serif_b(15 if hero else 12.5)
    yend = para(d, (x + 9, cy + 22), card["head"], bf, INK, w - 18,
                18.5 if hero else 14.5, limit=2)
    tf2 = sans_r(9.3 if hero else 8.5)
    body = BODY[card["n"]] + " — " + card["src"]
    para(d, (x + 9, yend + 1), body, tf2, (52, 54, 62), w - 18,
         11.5 if hero else 11, limit=3 if hero else 2)


def paint_map(d, x, y, w):
    tf = sans_b(12)
    d.text((x, y), "WHERE IT HAPPENED", font=tf, fill=INK)
    note = "numbers match the stories"
    d.text((x + w - text_w(d, note, serif_r(9)), y + 2), note,
           font=serif_r(9), fill=GREY)
    my, mh = y + 18, 96
    box(d, [x, my, x + w, my + mh], fill=(24, 44, 84))
    lon0, lon1, lat0, lat1 = -170, 195, -58, 82

    def proj(lon, lat):
        return (x + (lon - lon0) / (lon1 - lon0) * w,
                my + (lat1 - lat) / (lat1 - lat0) * mh)

    for _name, loop in OUTLINES:
        d.polygon([proj(lon, lat) for lon, lat in loop],
                  fill=(168, 178, 160), outline=(110, 120, 104))
    for lon, lat, r in ISLANDS:
        cx, cy = proj(lon, lat)
        rad = r / (lon1 - lon0) * w
        d.ellipse([cx - rad, cy - rad * 0.7, cx + rad, cy + rad * 0.7],
                  fill=(168, 178, 160), outline=(110, 120, 104))
    nf = sans_b(8.5)
    for n, (lon, lat) in PINS.items():
        cx, cy = proj(lon, lat)
        dx, dy = NUDGE.get(n, (0, 0))
        cx, cy = cx + dx, cy + dy
        d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=RED,
                  outline=(255, 252, 244), width=1)
        centred(d, cx, cy - 5, str(n), nf, (255, 252, 244))
    cf = sans_r(8.5)
    d.text((x, my + mh + 5), "Pins 1–13 are the card stories above.",
           font=cf, fill=GREY)
    d.text((x, my + mh + 16),
           "UTC 01:00 NZ final count · 06:30 IST Argentina bans money "
           "printing · 07:11 IST Trump backs Huang",
           font=cf, fill=GREY)


def paint_briefs(d, x, y, w):
    hf = sans_b(13)
    d.text((x, y), "ALSO ON FRIDAY", font=hf, fill=RED)
    d.text((x + text_w(d, "ALSO ON FRIDAY", hf) + 8, y),
           "— 23 MORE STORIES", font=hf, fill=INK)
    note = "place · what happened · source"
    d.text((x + w - text_w(d, note, serif_r(9.5)), y + 2), note,
           font=serif_r(9.5), fill=GREY)
    hline(d, x, x + w, y + 18, fill=INK, w=2)
    col_w = (w - 16) / 2
    nf = sans_b(9.0)
    cf = sans_b(9.0)
    bf = sans_r(9.0)
    for idx, (n, city, text, src) in enumerate(BRIEFS):
        col, row = divmod(idx, 12)
        cx = x + col * (col_w + 16)
        ly = y + 24 + row * 11.8
        d.text((cx, ly), str(n), font=nf, fill=RED)
        d.text((cx + 20, ly), city, font=cf, fill=NAVY)
        city_w = text_w(d, city, cf)
        d.text((cx + 24 + city_w, ly), " — " + text + " · " + src,
               font=bf, fill=INK)


def paint_check(d, x, y, w):
    box(d, [x, y, x + w, y + 66], fill=(250, 240, 238), outline=RED, width=2)
    tf = sans_b(12.5)
    d.text((x + 10, y + 7), "✓ DATE CHECK", font=tf, fill=RED)
    para(d, (x + 10 + text_w(d, "✓ DATE CHECK", tf) + 10, y + 8),
         "Every story on this page happened, or was first reported, "
         "on Friday 27 November 2026. " + DATE_CHECK,
         sans_r(10), (52, 44, 42),
         w - 30 - text_w(d, "✓ DATE CHECK", tf), 13.5)


def paint_footer(d):
    hline(d, EDGE, SIDE - EDGE, 970, fill=INK, w=2)
    d.text((EDGE, 976), FOOTER, font=sans_r(9.3), fill=GREY)
    tail = "Pictures and map drawn in code, not photographs"
    d.text((SIDE - EDGE - text_w(d, tail, sans_r(9.3)), 990), tail,
           font=sans_r(9.3), fill=GREY)


def build(out_path):
    img = Image.new("RGB", (SIDE, SIDE), PAPER)
    d = ImageDraw.Draw(img)
    paint_header(d)
    paint_regions(d, 132)
    paint_numbers(d, 162)
    cards = HEROES + SMALLS
    for i, card in enumerate(cards[:3]):
        paint_card(img, d, card, [EDGE, 353, 680][i], 220, 318, 200, True)
    for i, card in enumerate(cards[3:]):
        row, col = divmod(i, 5)
        paint_card(img, d, card, EDGE + col * 196, 428 + row * 150, 188,
                   146, False)
    paint_map(d, EDGE, 732, 322)
    paint_briefs(d, 364, 732, 634)
    paint_check(d, EDGE, 898, SIDE - 2 * EDGE)
    paint_footer(d)
    img.save(out_path, "PNG")
    return out_path


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "/output/entry.png"
    build(target)
    print("wrote", target)
