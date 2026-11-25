#!/usr/bin/env python3
"""THE WEDNESDAY WORLD - one image summing up Wednesday 25 November 2026.

Pure Python standard library. Draws a 1024x1024 newspaper front page with
a hand-written 5x7 bitmap font and a hand-written PNG encoder (zlib+struct),
and writes it to /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png).

Stories verified against Reuters, BBC, CNN, RFE/RL and The Hindu reporting
published on 25 November 2026. Every event below happened, or was first
reported, on Wednesday 25 November 2026.
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---- palette ---------------------------------------------------------------
PAPER = (246, 241, 229)   # newsprint cream
INK = (24, 24, 24)        # near-black ink
RED = (168, 35, 24)       # masthead red
NAVY = (28, 68, 102)      # deep navy
GOLD = (176, 132, 30)     # gold rule
GRAY = (105, 99, 86)      # warm grey
LIGHT = (216, 207, 186)   # light rule
SKY = (198, 224, 238)     # pale sky blue
SEA = (64, 120, 165)      # sea blue
SEA_DARK = (38, 84, 128)  # deep sea
LAND = (226, 212, 172)    # map land
WHITE = (255, 255, 255)
SMOKE = (120, 118, 110)

# ---- 5x7 bitmap font -------------------------------------------------------
# Each glyph is 7 rows of 5 cells; '#' is ink, '.' is blank.
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
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    '-': ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '*': ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    '@': ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    '[': ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    ']': ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    '<': ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    '>': ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
}

CHAR_W = 6  # 5 pixels + 1 spacing, at scale 1


def text_width(text, scale):
    """Pixel width of text at the given scale."""
    return len(text) * CHAR_W * scale - scale


# ---- canvas ----------------------------------------------------------------
class Canvas:
    """A plain RGB pixel buffer with simple vector drawing primitives."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, color)

    def hline(self, x, y, w, color):
        self.rect(x, y, w, 1, color)

    def vline(self, x, y, h, color):
        self.rect(x, y, 1, h, color)

    def line(self, x0, y0, x1, y1, color):
        """Bresenham line."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, color):
        """Filled circle."""
        for yy in range(cy - r, cy + r + 1):
            half = int((r * r - (yy - cy) ** 2) ** 0.5) if abs(yy - cy) <= r else 0
            for xx in range(cx - half, cx + half + 1):
                self.set(xx, yy, color)

    def triangle(self, x0, y0, x1, y1, x2, y2, color):
        """Filled triangle, scanline fill."""
        ys = sorted([(x0, y0), (x1, y1), (x2, y2)], key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = ys
        total_h = cy - ay
        if total_h == 0:
            return
        for y in range(ay, cy + 1):
            if y < by:
                seg_h = by - ay
                alpha = (y - ay) / seg_h if seg_h else 0
                xa = int(ax + (bx - ax) * alpha)
                xb = int(ax + (cx - ax) * ((y - ay) / total_h))
            else:
                seg_h = cy - by
                alpha = (y - by) / seg_h if seg_h else 0
                xa = int(bx + (cx - bx) * alpha)
                xb = int(ax + (cx - ax) * ((y - ay) / total_h))
            if xa > xb:
                xa, xb = xb, xa
            for x in range(xa, xb + 1):
                self.set(x, y, color)

    # -- text ----------------------------------------------------------------
    def glyph(self, x, y, ch, scale, color):
        rows = FONT.get(ch, FONT['?'])
        for r, row in enumerate(rows):
            for c, bit in enumerate(row):
                if bit == '1':
                    self.rect(x + c * scale, y + r * scale, scale, scale, color)

    def text(self, x, y, s, scale, color):
        """Draw text left-aligned at (x, y); unknown chars become '?'."""
        s = s.upper()
        for i, ch in enumerate(s):
            self.glyph(x + i * CHAR_W * scale, y, ch, scale, color)

    def text_center(self, cx, y, s, scale, color):
        self.text(cx - text_width(s, scale) // 2, y, s, scale, color)

    def text_right(self, x, y, s, scale, color):
        self.text(x - text_width(s, scale), y, s, scale, color)


def wrap(text, max_chars):
    """Greedy word wrap into lines of at most max_chars characters."""
    words = text.upper().split()
    lines, cur = [], ""
    for word in words:
        if not cur:
            cur = word
        elif len(cur) + 1 + len(word) <= max_chars:
            cur += " " + word
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---- PNG encoder -----------------------------------------------------------
def png_bytes(canvas):
    """Encode the canvas as a truecolour RGB PNG (deterministic bytes)."""
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)  # filter type 0 (None) on every row
        raw += canvas.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


# ---- lead illustration: sea battle + world map ------------------------------
def draw_sea_scene(cv, x, y, w, h):
    """A stylised sea scene: sky, sun, a cargo ship, a burning warship
    listing to one side, and a small drone above. All vector-drawn."""
    # sky and sea
    cv.rect(x, y, w, h * 2 // 5, SKY)
    cv.rect(x, y + h * 2 // 5, w, h * 3 // 5, SEA)
    cv.rect(x, y + h * 2 // 5, w, 3, SEA_DARK)
    # sun
    cv.circle(x + w - 70, y + 34, 22, GOLD)
    cv.circle(x + w - 70, y + 34, 16, (232, 196, 90))
    # distant clouds
    for cx, cy, r in ((x + 90, y + 26, 14), (x + 112, y + 30, 18),
                      (x + 138, y + 26, 12), (x + 300, y + 18, 12),
                      (x + 320, y + 22, 15)):
        cv.circle(cx, cy, r, WHITE)
    # drone (small quad-copter) upper left of centre
    dx, dy = x + w // 2 - 30, y + 26
    cv.rect(dx - 14, dy, 28, 6, INK)
    cv.rect(dx - 3, dy + 6, 6, 8, INK)
    cv.line(dx - 18, dy - 2, dx - 8, dy - 2, INK)
    cv.line(dx + 8, dy - 2, dx + 18, dy - 2, INK)
    cv.line(dx - 18, dy + 2, dx - 8, dy + 2, INK)
    cv.line(dx + 8, dy + 2, dx + 18, dy + 2, INK)
    # dotted flight path from drone down to the burning ship
    for i in range(0, 46, 6):
        cv.set(dx + 4 + i, dy + 16 + i // 2, INK)
    # cargo ship, upright, left
    sx, sy = x + 36, y + h - 78
    cv.rect(sx, sy - 26, 150, 26, (52, 52, 52))          # hull
    cv.rect(sx + 8, sy - 46, 60, 20, (120, 30, 22))      # containers
    cv.rect(sx + 76, sy - 46, 60, 20, (28, 68, 102))     # containers
    cv.rect(sx + 142, sy - 58, 8, 58, INK)               # mast
    cv.rect(sx + 142, sy - 58, 22, 6, RED)               # flag
    # reflection
    for i in range(0, 150, 12):
        cv.hline(sx + i, sy + 6 + (i % 24) // 6, 8, SEA_DARK)
    # burning warship, listing right, centre-right
    bx, by = x + 300, y + h - 72
    cv.triangle(bx, by - 18, bx + 170, by - 52, bx + 176, by - 6, (52, 52, 52))
    cv.rect(bx + 96, by - 74, 10, 26, INK)               # funnel, tilted
    cv.line(bx + 96, by - 74, bx + 108, by - 74, INK)
    # flames on the deck
    for fx, fy, fr in ((bx + 60, by - 62, 12), (bx + 84, by - 70, 15),
                       (bx + 108, by - 60, 10)):
        cv.triangle(fx - fr, fy, fx, fy - fr * 2, fx + fr, fy, RED)
        cv.triangle(fx - fr // 2, fy, fx, fy - fr, fx + fr // 2, fy, GOLD)
    # smoke plumes (kept inside the scene, below the deck text)
    for sx2, sy2, sr in ((bx + 66, by - 88, 12), (bx + 88, by - 102, 14),
                         (bx + 108, by - 116, 11), (bx + 126, by - 128, 8)):
        cv.circle(sx2, sy2, sr, SMOKE)
    # waves
    for wx in range(x + 8, x + w - 8, 34):
        cv.line(wx, y + h - 26, wx + 16, y + h - 26, WHITE)
        cv.line(wx + 6, y + h - 16, wx + 22, y + h - 16, WHITE)


# Simplified continent shapes as rectangles inside the map box.
# (x, y, w, h) in map-local coordinates, map box 300 x 150.
CONTINENTS = [
    # North America
    (14, 18, 62, 26), (26, 8, 44, 16), (16, 40, 30, 22),
    # South America
    (58, 66, 26, 44), (64, 106, 12, 16),
    # Europe
    (138, 16, 34, 22), (150, 6, 18, 12),
    # Africa
    (140, 44, 34, 52), (146, 92, 22, 16),
    # Asia
    (176, 8, 92, 40), (196, 44, 52, 30), (238, 74, 22, 22),
    # Oceania
    (252, 104, 30, 16), (258, 122, 14, 8),
]
# Story dots: (story number, map x, map y)
DOTS = [
    (1, 152, 14),   # Gulf of Finland / Benghazi (Europe-Med)
    (2, 52, 40),    # United States (Huawei trial, New York)
    (3, 48, 36),    # Washington (CIA cyberattack)
    (4, 186, 56),   # Riyadh
    (5, 152, 76),   # DR Congo
    (6, 40, 44),    # Nvidia / Washington
    (7, 142, 26),   # Paris (Sarkozy)
    (8, 148, 66),   # Senegal
    (9, 46, 42),    # Washington (Thanksgiving pardons)
    (10, 214, 66),  # India (Sooryavanshi) / England T20
]


def draw_map(cv, x, y, w, h):
    """A small numbered world map: land blocks, sea, story dots."""
    cv.rect(x, y, w, h, (214, 232, 240))
    cv.rect(x, y, w, h, NAVY)  # border drawn as outline below
    cv.rect(x + 2, y + 2, w - 4, h - 4, (214, 232, 240))
    sx = (w - 4) / 300.0
    sy = (h - 4) / 150.0
    for (mx, my, mw, mh) in CONTINENTS:
        cv.rect(x + 2 + int(mx * sx), y + 2 + int(my * sy),
                max(2, int(mw * sx)), max(2, int(mh * sy)), LAND)
    cv.text(x + 8, y + 6, "THE WORLD TODAY", 1, NAVY)
    for num, mx, my in DOTS:
        px = x + 2 + int(mx * sx)
        py = y + 2 + int(my * sy)
        cv.circle(px, py, 7, RED)
        cv.text(px - text_width(str(num), 1) // 2, py - 3, str(num), 1, WHITE)


# ---- stories ---------------------------------------------------------------
# (number, kicker, headline, one-line summary)
STORIES = [
    (2, "TECH / US COURTS", "HUAWEI GUILTY IN US TRIAL",
     "CONVICTS ON 10 OF 12"),
    (3, "CYBER / WASHINGTON", "CIA AND ODNI HIT BY CYBERATTACK",
     "CLASSIFIED SYSTEMS HIT"),
    (4, "MIDDLE EAST", "HOUTHIS HIT RIYADH'S TALLEST TOWER",
     "11 WOUNDED IN RIYADH"),
    (5, "HEALTH / AFRICA", "WHO FLEES CONGO HOSPITAL AMID FIGHTING",
     "STAFF EVACUATED IN EBOLA"),
    (6, "MARKETS", "NVIDIA SLIDES AS TRUMP ROLE QUESTIONED",
     "SHARES FALL 7% ON PROBE"),
    (7, "EUROPE / PARIS", "SARKOZY AND BRUNI ORDERED TO TRIAL",
     "TRIAL SET FOR APRIL 2027"),
    (8, "SPORT / AFRICA", "SENEGAL AFCON WINNERS AGAIN",
     "COURT REINSTATES SENEGAL"),
    (9, "WHITE HOUSE", "TRUMP PARDONS THANKSGIVING TURKEYS",
     "TWO TURKEYS SPARED"),
    (10, "SPORT / CRICKET", "ENGLAND LEVEL T20 SERIES",
     "ENGLAND WIN BY 8 WICKETS"),
]

NUMBERS_LINES = [
    "700,000+ RUSSIAN SOLDIERS KILLED IN UKRAINE  -  10/12 HUAWEI COUNTS GUILTY",
    "11 WOUNDED IN RIYADH TOWER STRIKE  -  5,775 EBOLA DEAD OF 11,762 CASES",
]


def draw_story_cell(cv, x, y, w, h, num, kicker, headline, summary):
    """One story cell: number badge, kicker, headline, summary line."""
    cv.rect(x, y, w, h, PAPER)
    cv.rect(x, y, w, 2, NAVY)
    # number badge
    cv.circle(x + 16, y + 16, 11, RED)
    cv.text(x + 16 - text_width(str(num), 1) // 2, y + 13, str(num), 1, WHITE)
    cv.text(x + 34, y + 9, kicker, 1, RED)
    # headline, wrapped at scale 2
    max_chars = (w - 16) // (CHAR_W * 2)
    lines = wrap(headline, max_chars)[:2]
    yy = y + 30
    for line in lines:
        cv.text(x + 8, yy, line, 2, INK)
        yy += 16
    # summary, wrapped at scale 1... use scale 2 for legibility, one line
    max_sum = (w - 16) // (CHAR_W * 2)
    for line in wrap(summary, max_sum)[:1]:
        cv.text(x + 8, y + h - 20, line, 2, GRAY)


def build():
    cv = Canvas(W, H, PAPER)
    # page frame
    cv.rect(10, 10, W - 20, H - 20, INK)
    cv.rect(12, 12, W - 24, H - 24, PAPER)
    cv.rect(18, 18, W - 36, H - 36, INK)
    cv.rect(19, 19, W - 38, H - 38, PAPER)

    # dateline bar
    cv.text(28, 30, "WEDNESDAY 25 NOVEMBER 2026", 2, INK)
    cv.text_center(W // 2, 30, "THE WORLD IN ONE PAGE", 2, GRAY)
    cv.text_right(W - 28, 30, "NO. 329", 2, INK)
    cv.hline(28, 52, W - 56, LIGHT)
    cv.hline(28, 54, W - 56, LIGHT)

    # masthead
    cv.text_center(W // 2, 66, "THE WEDNESDAY WORLD", 7, INK)
    cv.hline(28, 132, W - 56, RED)
    cv.rect(28, 136, W - 56, 3, RED)
    cv.text_center(W // 2, 148, "WORLD NEWS  -  WEDNESDAY 25 NOVEMBER 2026", 2, RED)

    # lead headline
    cv.text_center(W // 2, 178, "UKRAINE HITS RUSSIAN SHIPS", 4, INK)
    cv.text_center(W // 2, 210, "IN FINNISH GULF AND OFF LIBYA", 4, INK)
    deck = ("Zelenskiy confirms a drone strike on a Russian cargo ship in the "
            "Gulf of Finland as Ukrainian forces sink a Russian warship in "
            "Benghazi harbour.")
    for i, line in enumerate(wrap(deck, 74)):
        cv.text_center(W // 2, 248 + i * 16, line, 2, NAVY)

    # illustration row: sea scene + world map
    draw_sea_scene(cv, 28, 306, 620, 196)
    cv.text(28, 508, "A RUSSIAN WARSHIP BURNS OFF BENGHAZI AFTER UKRAINE'S STRIKE.",
            1, GRAY)
    draw_map(cv, 664, 306, 332, 196)
    cv.text(664, 508, "WHERE THE DAY HAPPENED: 1-10 MARK THE STORIES BELOW.", 1, GRAY)

    # story grid: 3 columns x 3 rows
    gx, gy = 28, 536
    cw, ch, gap = 312, 104, 16
    for i, (num, kicker, headline, summary) in enumerate(STORIES):
        col, row = i % 3, i // 3
        draw_story_cell(cv, gx + col * (cw + gap), gy + row * (ch + 10),
                        cw, ch, num, kicker, headline, summary)

    # numbers strip
    ny = 536 + 3 * (ch + 10) + 8
    cv.rect(28, ny, W - 56, 2, GOLD)
    cv.text(28, ny + 8, "THE DAY IN NUMBERS", 2, RED)
    for i, line in enumerate(NUMBERS_LINES):
        cv.text(28, ny + 30 + i * 16, line, 2, INK)
    cv.rect(28, ny + 68, W - 56, 2, GOLD)

    # footer
    cv.text_center(W // 2, ny + 78,
                   "SOURCES: REUTERS - BBC - CNN - RFE/RL - THE HINDU", 2, GRAY)
    cv.text_center(W // 2, ny + 96,
                   "ALL EVENTS HAPPENED OR WERE FIRST REPORTED ON 25 NOVEMBER 2026",
                   1, GRAY)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = png_bytes(build())
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes)" % (path, len(data)))


if __name__ == "__main__":
    main()
