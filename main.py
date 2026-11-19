#!/usr/bin/env python3
"""The World in One Image — 18 November 2026.

make.fun bounty news-image-20261118: sum up Wednesday 18 November 2026's
world news in one 1024x1024 image, drawn as the front page of a newspaper.

Pure Python standard library only (no Pillow / numpy). The picture is
drawn procedurally onto a bytearray canvas and encoded as PNG with zlib
+ struct. Deterministic: no clock, no randomness, no network — the same
code always writes byte-identical output.

Writes entry.png to $MAKEFUN_OUTPUT_DIR (default /output).

Four stories, all first reported on 18 November 2026:
  1. APEC OPENS IN SHENZHEN (lead) — Xi Jinping opened the APEC summit
     in Shenzhen and called for AI cooperation and free trade, denouncing
     unilateralism and protectionism. Trump, Xi and Putin meet in a
     first-ever trilateral summit on Thursday 19 November. Sources:
     FeedCast Daily Brief, SimpleLife.news, Raj Global Studies.
  2. ALASKA — Mary Peltola defeated incumbent Republican Dan Sullivan
     for the US Senate seat in Alaska, giving the Democrats 56 seats.
     Sources: FeedCast Daily Brief, OneTurn News, SimpleLife.news.
  3. KERCH BRIDGE — Ukraine struck the Kerch Bridge for a third time
     in three days on 18 November; traffic was halted again while the
     damage was assessed. The road span shown fallen in the strait
     collapsed in the 16-17 November strikes. Sources: The Guardian,
     Reuters, BBC, BusinessWorld.
  4. GULF ESCALATION — US fighter jets struck a Revolutionary Guard
     missile launch site on Qeshm Island in the Strait of Hormuz; Iran
     fired drones at the US radar site in Bahrain and at Kuwait, whose
     air defences responded; the tanker Tara Gas was struck by a
     projectile in the strait. Sources: Reuters, CBS News, Al Jazeera,
     Japan Times, WAM.
"""
import math
import os
import struct
import zlib

W = 1024
H = 1024
OUT = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")

# ---------------------------------------------------------------- palette
PAPER = (245, 240, 225)   # newsprint
INK = (20, 20, 20)        # headline ink
NAVY = (14, 27, 51)       # masthead / headline bars
NAVY_DARK = (9, 18, 36)
RED = (179, 39, 30)       # accent red
GOLD = (201, 162, 39)     # masthead rule / accents
GOLD_LT = (232, 196, 90)
CREAM = (250, 244, 226)   # light text on navy
STEEL = (26, 32, 48)      # bridge / skyline silhouette
CABLE = (96, 96, 118)

buf = bytearray(W * H * 3)


def clamp255(v):
    return 0 if v < 0 else (255 if v > 255 else int(v))


def px(x, y):
    return (int(y) * W + int(x)) * 3


def fill_rect(x0, y0, x1, y1, col):
    """Solid rectangle, [x0, x1) x [y0, y1), clipped. Row-slice fill."""
    xa = max(0, int(x0))
    xb = min(W, int(x1))
    ya = max(0, int(y0))
    yb = min(H, int(y1))
    if xa >= xb or ya >= yb:
        return
    row = bytes(col) * (xb - xa)
    for y in range(ya, yb):
        i = (y * W + xa) * 3
        buf[i:i + len(row)] = row


def rect_outline(x0, y0, x1, y1, t, col):
    fill_rect(x0, y0, x1, y0 + t, col)
    fill_rect(x0, y1 - t, x1, y1, col)
    fill_rect(x0, y0, x0 + t, y1, col)
    fill_rect(x1 - t, y0, x1, y1, col)


def blend_px(x, y, r, g, b, a=1.0):
    xi, yi = int(x), int(y)
    if xi < 0 or yi < 0 or xi >= W or yi >= H:
        return
    i = px(xi, yi)
    if a >= 1.0:
        buf[i] = clamp255(r)
        buf[i + 1] = clamp255(g)
        buf[i + 2] = clamp255(b)
    else:
        buf[i] = clamp255(buf[i] + (r - buf[i]) * a)
        buf[i + 1] = clamp255(buf[i + 1] + (g - buf[i + 1]) * a)
        buf[i + 2] = clamp255(buf[i + 2] + (b - buf[i + 2]) * a)


def lerp(a, b, t):
    return a + (b - a) * t


def lerp3(c1, c2, t):
    return (lerp(c1[0], c2[0], t), lerp(c1[1], c2[1], t), lerp(c1[2], c2[2], t))


def vgrad(x0, y0, x1, y1, top, bot):
    """Vertical gradient over a rectangle, one slice-fill per row."""
    ya = max(0, int(y0))
    yb = min(H, int(y1))
    span = max(1, yb - ya - 1)
    for y in range(ya, yb):
        c = lerp3(top, bot, (y - ya) / span)
        fill_rect(x0, y, x1, y + 1, (int(c[0]), int(c[1]), int(c[2])))


def vgrad3(x0, y0, x1, y1, c_top, c_mid, c_bot):
    """Three-stop vertical gradient."""
    mid = (int(y0) + int(y1)) // 2
    vgrad(x0, y0, x1, mid, c_top, c_mid)
    vgrad(x0, mid, x1, y1, c_mid, c_bot)


def disc(cx, cy, rad, col, a=1.0):
    r0 = int(max(0, cx - rad))
    r1 = int(min(W - 1, cx + rad))
    y0 = int(max(0, cy - rad))
    y1 = int(min(H - 1, cy + rad))
    for y in range(y0, y1 + 1):
        dy = y - cy
        for x in range(r0, r1 + 1):
            dx = x - cx
            if dx * dx + dy * dy <= rad * rad:
                blend_px(x, y, col[0], col[1], col[2], a)


def ellipse(cx, cy, rx, ry, col, a=1.0):
    r0 = int(max(0, cx - rx))
    r1 = int(min(W - 1, cx + rx))
    y0 = int(max(0, cy - ry))
    y1 = int(min(H - 1, cy + ry))
    for y in range(y0, y1 + 1):
        ny = (y - cy) / ry if ry else 0
        for x in range(r0, r1 + 1):
            nx = (x - cx) / rx if rx else 0
            if nx * nx + ny * ny <= 1.0:
                blend_px(x, y, col[0], col[1], col[2], a)


def poly(points, col, a=1.0):
    """Scanline fill of a polygon."""
    if len(points) < 3:
        return
    ys = [p[1] for p in points]
    y0 = max(0, int(math.floor(min(ys))))
    y1 = min(H - 1, int(math.ceil(max(ys))))
    n = len(points)
    for y in range(y0, y1 + 1):
        xs = []
        for i in range(n):
            x1, y1p = points[i]
            x2, y2p = points[(i + 1) % n]
            if (y1p <= y < y2p) or (y2p <= y < y1p):
                t = (y - y1p) / (y2p - y1p)
                xs.append(x1 + t * (x2 - x1))
        xs.sort()
        for k in range(0, len(xs) - 1, 2):
            xa, xb = int(math.ceil(xs[k])), int(math.floor(xs[k + 1]))
            if a >= 1.0:
                fill_rect(xa, y, xb + 1, y + 1, col)
            else:
                for x in range(max(0, xa), min(W - 1, xb) + 1):
                    blend_px(x, y, col[0], col[1], col[2], a)


def line(x1, y1, x2, y2, width, col):
    """Thick line as a chain of small squares (cheap, deterministic)."""
    dist = math.hypot(x2 - x1, y2 - y1)
    steps = max(1, int(dist * 1.5) + 1)
    hw = width / 2.0
    for i in range(steps + 1):
        t = i / steps
        cx = lerp(x1, x2, t)
        cy = lerp(y1, y2, t)
        fill_rect(cx - hw, cy - hw, cx + hw + 1, cy + hw + 1, col)


# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 cells, '#' = ink. Uppercase A-Z, digits, space
# and & . , ' - : / ( ) bullet ! ? % + =
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    # bullet (U+2022), drawn as a solid 3x3 block
    '\u2022': ("00000", "00000", "01110", "01110", "01110", "00000", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '+': ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
}


def text_width(text, scale):
    """Pixel width of text at scale (6 px advance per glyph, minus trailing gap)."""
    if not text:
        return 0
    return len(text) * 6 * scale - scale


def draw_text(x, y, text, scale, col):
    """Draw text left-aligned at (x, y); glyphs are upper-cased first."""
    cx = int(x)
    for ch in text.upper():
        glyph = FONT.get(ch, FONT[' '])
        for row in range(7):
            bits = glyph[row]
            for c in range(5):
                if bits[c] == '1':
                    fill_rect(cx + c * scale, y + row * scale,
                              cx + (c + 1) * scale, y + (row + 1) * scale, col)
        cx += 6 * scale


def draw_text_center(cx, y, text, scale, col):
    draw_text(cx - text_width(text, scale) // 2, y, text, scale, col)


def fit_scale(text, max_w, max_scale):
    """Largest scale (<= max_scale) at which text fits in max_w px."""
    s = max_scale
    while s > 1 and text_width(text, s) > max_w:
        s -= 1
    return s


def wrap_text(text, max_w, scale):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = text.split(' ')
    lines, cur = [], ''
    for w in words:
        trial = w if not cur else cur + ' ' + w
        if text_width(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def headline_block(cx, y, text, max_w, max_scale, col, line_gap=4):
    """Centred headline: try the largest scale first, wrapping to fit.

    Wrapping happens at each candidate scale, so a long headline becomes
    two lines at a large scale instead of one line shrunk to unreadable.
    Returns y just below the block.
    """
    for scale in range(max_scale, 0, -1):
        lines = wrap_text(text, max_w, scale)
        if all(text_width(ln, scale) <= max_w for ln in lines):
            break
    for ln in lines:
        draw_text_center(cx, y, ln, scale, col)
        y += 7 * scale + line_gap
    return y

# ---------------------------------------------------------------- page
# Newsprint background for the whole page.
fill_rect(0, 0, W, H, PAPER)

# --- Masthead y0-96 ---------------------------------------------------
fill_rect(0, 0, W, 96, NAVY)
draw_text_center(512, 16, "THE WORLD IN ONE IMAGE", 6, CREAM)
draw_text_center(512, 66, "WEDNESDAY, 18 NOVEMBER 2026", 3, GOLD_LT)
fill_rect(0, 90, W, 96, GOLD)

# --- Lead panel: APEC opens in Shenzhen, y104-556, x8-1016 -----------
PX0, PX1, PY0, PY1 = 8, 1016, 104, 556
BAR_Y = 468  # headline bar starts here; scene above it
# Evening sky over Shenzhen: deep teal -> warm amber at the horizon.
vgrad3(PX0, PY0, PX1, 380, (18, 42, 66), (58, 84, 110), (214, 140, 74))
# Low sun, left of centre.
disc(210, 340, 30, (255, 214, 140), 0.35)
disc(210, 340, 22, (255, 222, 150), 1.0)
disc(210, 340, 15, (255, 236, 190), 1.0)
# APEC banner across the top of the scene.
fill_rect(PX0, 112, PX1, 152, NAVY)
fill_rect(PX0, 150, PX1, 152, GOLD)
draw_text_center(512, 122, "APEC 2026 - SHENZHEN, CHINA", 3, CREAM)
# Skyline silhouettes: tall towers with lit windows, one with a spire.
for bx, bw, bh in [(30, 52, 120), (96, 40, 180), (150, 58, 140), (222, 44, 210),
                   (280, 60, 160), (356, 44, 230), (414, 58, 170), (486, 40, 200),
                   (540, 62, 150), (616, 44, 220), (674, 58, 165), (746, 42, 195),
                   (802, 56, 145), (872, 44, 205), (930, 56, 155)]:
    fill_rect(bx, BAR_Y - bh, bx + bw, BAR_Y, (20, 26, 44))
fill_rect(368, BAR_Y - 268, 372, BAR_Y - 230, (20, 26, 44))  # spire
disc(370, BAR_Y - 270, 4, (255, 90, 70))
for wx, wy in [(44, 380), (110, 330), (166, 400), (238, 300), (296, 360),
               (372, 280), (430, 380), (500, 320), (556, 400), (632, 300),
               (690, 370), (762, 320), (818, 390), (888, 300), (946, 380),
               (120, 420), (330, 420), (560, 420), (780, 420), (950, 420)]:
    fill_rect(wx, wy, wx + 6, wy + 8, GOLD_LT)
# Convention-centre roofline in front of the towers.
poly([(8, 468), (180, 420), (512, 404), (844, 420), (1016, 468),
      (1016, 468), (8, 468)], (26, 32, 48))
fill_rect(8, 452, 1016, 468, (26, 32, 48))
# Three flag poles on the roofline: China, USA, Russia.
for fx in (400, 512, 624):
    fill_rect(fx - 1, 356, fx + 2, 452, CREAM)
# China flag with gold stars.
fill_rect(402, 356, 436, 378, (179, 39, 30))
disc(410, 364, 3, GOLD_LT)
disc(420, 362, 2, GOLD_LT)
disc(420, 370, 2, GOLD_LT)
# USA flag: red/white stripes, blue canton.
for i in range(6):
    fill_rect(514, 356 + i * 4, 548, 360 + i * 4,
              (179, 39, 30) if i % 2 == 0 else CREAM)
fill_rect(514, 356, 530, 368, (20, 40, 90))
# Russia flag: white / blue / red horizontal bands.
fill_rect(626, 356, 660, 363, CREAM)
fill_rect(626, 363, 660, 370, (30, 70, 160))
fill_rect(626, 370, 660, 378, (179, 39, 30))
# Three figures at podiums under the flags: light suits so they read
# against the dark towers and roofline.
for fx, tie in ((400, RED), (512, GOLD_LT), (624, (30, 70, 160))):
    disc(fx, 398, 10, (18, 20, 32))                       # head
    poly([(fx - 16, 442), (fx + 16, 442),
          (fx + 9, 410), (fx - 9, 410)], (232, 228, 216))  # body
    fill_rect(fx - 2, 412, fx + 3, 430, tie)               # tie
rect_outline(PX0, PY0, PX1, PY1, 2, INK)
# Headline bar (dark) under the scene.
fill_rect(PX0, BAR_Y, PX1, PY1, NAVY)
fill_rect(PX0, BAR_Y, PX1, BAR_Y + 3, GOLD)
draw_text_center(512, 482, "APEC OPENS IN SHENZHEN", 6, CREAM)
draw_text_center(512, 530,
                 "XI CALLS FOR AI COOPERATION AND FREE TRADE",
                 2, GOLD_LT)

# --- Row 2: y564-828, two panels --------------------------------------
RY0, RY1 = 564, 828
RBAR_Y = 724  # headline bars start here
# Left panel: Alaska Senate race, x8-508.
LX0, LX1 = 8, 508
vgrad(LX0, RY0, LX1, 660, (10, 16, 38), (24, 40, 72))
vgrad(LX0, 660, LX1, RBAR_Y, (16, 26, 48), (10, 16, 30))
for sx, sy in [(60, 590), (120, 580), (220, 600), (300, 578), (420, 592),
               (470, 606), (90, 620), (260, 614), (380, 576)]:
    disc(sx, sy, 2, CREAM, 0.9)
# Aurora bands: layered translucent arcs across the sky.
for cy, rx, col, a in [(596, 210, (80, 220, 160), 0.35),
                       (606, 190, (120, 230, 180), 0.3),
                       (616, 170, (60, 190, 200), 0.3)]:
    for x in range(LX0, LX1):
        t = (x - LX0) / (LX1 - LX0)
        yy = cy + int(18 * math.sin(t * math.pi * 2.2))
        for dy in range(-5, 6):
            blend_px(x, yy + dy, col[0], col[1], col[2], a * (1 - abs(dy) / 6))
# Snowy mountain silhouettes.
poly([(8, 724), (120, 640), (210, 724)], (30, 38, 62))
poly([(150, 724), (300, 620), (430, 724)], (24, 32, 54))
poly([(360, 724), (470, 648), (508, 724)], (30, 38, 62))
# Snow caps.
poly([(120, 640), (96, 668), (144, 668)], CREAM)
poly([(300, 620), (272, 652), (328, 652)], CREAM)
# Spruce trees on the snowfield.
for tx, th in [(60, 34), (100, 26), (420, 30), (462, 24)]:
    poly([(tx, 724 - th), (tx - 12, 724), (tx + 12, 724)], (16, 52, 36))
    fill_rect(tx - 2, 724 - 4, tx + 2, 724, (16, 52, 36))
# Ballot box on the snow, a ballot going in, big check mark.
fill_rect(196, 664, 320, 724, (200, 60, 50))
fill_rect(196, 664, 320, 672, (160, 44, 38))
fill_rect(236, 654, 280, 664, CREAM)  # ballot slot
fill_rect(248, 640, 266, 654, CREAM)  # ballot paper
fill_rect(248, 640, 266, 644, (20, 40, 90))
line(210, 694, 236, 716, 6, CREAM)
line(236, 716, 300, 678, 6, CREAM)
rect_outline(LX0, RY0, LX1, RY1, 2, INK)
fill_rect(LX0, RBAR_Y, LX1, RY1, NAVY)
fill_rect(LX0, RBAR_Y, LX1, RBAR_Y + 3, GOLD)
headline_block(258, 734, "PELTOLA FLIPS ALASKA",
               468, 3, CREAM)
draw_text_center(258, 792, "DEMOCRATS REACH 56 SENATE SEATS", 2, GOLD_LT)

# Right panel: Kerch Bridge partly destroyed, x516-1016.
RX0, RX1 = 516, 1016
vgrad(RX0, RY0, RX1, 660, (96, 112, 142), (58, 74, 102))
fill_rect(RX0, 660, RX1, RBAR_Y, (26, 44, 66))
# Wave glints on the strait.
for wx in range(530, 1000, 48):
    fill_rect(wx, 676, wx + 22, 678, (70, 105, 140))
    fill_rect(wx + 12, 700, wx + 30, 702, (54, 88, 122))
# Distant shore haze on the left.
poly([(516, 660), (600, 628), (700, 660)], (52, 66, 92))
# Standing arch (left): steel curve over the deck.
ax0, ax1 = 540, 760
prev = None
for i in range(21):
    t = i / 20
    ax = ax0 + (ax1 - ax0) * t
    ay = 640 - 44 * 4 * t * (1 - t)
    if prev is not None:
        line(prev[0], prev[1], ax, ay, 4, (30, 34, 44))
    prev = (ax, ay)
# Hangers from the arch down to the deck.
for hx in (580, 620, 660, 700, 740):
    t = (hx - ax0) / (ax1 - ax0)
    ay = 640 - 44 * 4 * t * (1 - t)
    line(hx, ay, hx, 640, 2, (30, 34, 44))
# Bridge deck, left of the break.
fill_rect(516, 640, 800, 650, (30, 34, 44))
for rx in range(524, 800, 24):
    fill_rect(rx, 630, rx + 3, 640, (30, 34, 44))
# Broken gap: jagged deck edge + collapsed span plunging into the strait.
poly([(800, 640), (816, 650), (806, 654), (822, 650)], (30, 34, 44))
poly([(812, 646), (940, 700), (960, 694), (836, 640)], (38, 42, 52))
fill_rect(936, 690, 966, 698, (30, 34, 44))
# Debris and splash where the span went down.
for dx, dy, dr in [(920, 706, 4), (946, 712, 3), (968, 704, 4), (900, 714, 3)]:
    disc(dx, dy, dr, (120, 130, 150), 0.9)
# Smoke column rising from the break.
for sx, sw, sh in [(806, 20, 34), (826, 14, 26)]:
    ellipse(sx, 640 - sh, sw, sh, (70, 70, 80), 0.75)
# Blast glow at the break point.
disc(812, 636, 10, (255, 180, 70), 1.0)
disc(812, 636, 6, (255, 230, 150), 1.0)
# Drones above the strait.
for dx, dy in [(560, 584), (640, 576), (940, 580)]:
    disc(dx, dy, 4, (18, 18, 24), 1.0)
    fill_rect(dx - 10, dy - 2, dx + 10, dy, (18, 18, 24))
    fill_rect(dx - 2, dy - 7, dx + 2, dy - 4, (18, 18, 24))
rect_outline(RX0, RY0, RX1, RY1, 2, INK)
fill_rect(RX0, RBAR_Y, RX1, RY1, NAVY)
fill_rect(RX0, RBAR_Y, RX1, RBAR_Y + 3, GOLD)
headline_block(766, 734, "KERCH BRIDGE HIT AGAIN",
               468, 3, CREAM)
draw_text_center(766, 792, "THIRD STRIKE IN 3 DAYS - TRAFFIC HALTED", 2, GOLD_LT)

# --- Bottom strip: Gulf escalation, y836-988, x8-1016 --------------
SY0, SY1 = 836, 988
SBAR_Y = 920
# Dusk over the Gulf: dark smoke navy -> burning orange at the horizon.
vgrad3(8, SY0, 1016, SBAR_Y, (16, 24, 44), (64, 44, 60), (196, 96, 44))
# Smoke columns rising on the horizon.
for sx, sw, sh in [(120, 26, 40), (180, 18, 30), (860, 24, 44), (920, 16, 32)]:
    ellipse(sx, SBAR_Y - sh, sw, sh, (40, 40, 52), 0.8)
# Dark sea with wave glints.
fill_rect(8, 892, 1016, SBAR_Y, (10, 18, 34))
for wx in range(30, 1000, 60):
    fill_rect(wx, 902, wx + 28, 904, (40, 70, 100))
# Oil tanker crossing the strait, centre-left.
fill_rect(120, 872, 420, 892, (24, 28, 40))          # hull
poly([(420, 872), (452, 880), (420, 892)], (24, 28, 40))  # bow
fill_rect(150, 852, 190, 872, (24, 28, 40))          # bridge tower
fill_rect(160, 840, 180, 852, (24, 28, 40))
# Explosion burst above the tanker: fireball + sparks. Kept fully
# inside the strip (y 836-920): centre y 862, spark radius 16.
disc(330, 862, 14, (255, 200, 80), 1.0)
disc(330, 862, 9, (255, 240, 170), 1.0)
for ang in range(0, 360, 45):
    rad = math.radians(ang)
    line(330, 862, 330 + 16 * math.cos(rad), 862 + 16 * math.sin(rad),
         3, (255, 160, 60))
# Missile trail diving from the top right toward the burst.
for t in range(0, 13):
    tt = t / 12
    mx = 700 - 360 * tt
    my = 844 - 8 * tt + 30 * tt * tt
    disc(mx, my, 3, (255, 200, 90), 0.9)
# Drones over the Gulf: small dark quadcopters with rotor lines.
for dx, dy in [(560, 856), (640, 848), (800, 852)]:
    disc(dx, dy, 5, (16, 16, 22), 1.0)
    fill_rect(dx - 12, dy - 2, dx + 12, dy, (16, 16, 22))
    fill_rect(dx - 2, dy - 8, dx + 2, dy - 5, (16, 16, 22))
# Radar station on the right: mast with a dish bowl (Bahrain base).
fill_rect(952, 868, 956, 892, CREAM)
poly([(940, 850), (968, 850), (960, 868), (948, 868)], CREAM)
disc(954, 858, 2, NAVY)
rect_outline(8, SY0, 1016, SY1, 2, INK)
fill_rect(8, SBAR_Y, 1016, SY1, NAVY)
fill_rect(8, SBAR_Y, 1016, SBAR_Y + 3, GOLD)
draw_text_center(512, 930, "GULF ESCALATION", 3, CREAM)
draw_text_center(512, 960,
                 "U.S. JETS STRIKE QESHM - IRAN DRONES TARGET BAHRAIN, KUWAIT",
                 2, GOLD_LT)

# --- Footer ------------------------------------------------------------
draw_text_center(512, 1000,
                 "18 NOVEMBER 2026 \u2022 WORLD NEWS IN ONE IMAGE", 2, INK)

# ---------------------------------------------------------------- PNG encode
def png_bytes():
    raw = bytearray()
    for y in range(H):
        raw.append(0)  # filter: none
        raw.extend(buf[y * W * 3:(y + 1) * W * 3])
    comp = zlib.compress(bytes(raw), 9)

    def chunk(typ, data):
        c = struct.pack(">I", len(data)) + typ + data
        c += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
        return c

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp)
            + chunk(b"IEND", b""))


def main():
    os.makedirs(OUT, exist_ok=True)
    data = png_bytes()
    path = os.path.join(OUT, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print(f"wrote {path} {len(data)} bytes {W}x{H}")


if __name__ == "__main__":
    main()
