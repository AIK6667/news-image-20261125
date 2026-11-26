#!/usr/bin/env python3
"""World news for 25 November 2026, summed up in one 1024x1024 PNG.

Standard library only: no Pillow, no third-party packages, no network,
no external font files. Type is drawn from a hand-built 5x7 bitmap font
scaled by whole pixels. Output is fully deterministic: no clock reads,
no randomness and no dict/set iteration, so two runs are byte-identical.

    python3 main.py [/output/entry.png]
"""
import os
import struct
import sys
import zlib

# 5x7 bitmap font, hand-drawn below; no external font files are read.
_G = {
" ": ["...", "...", "...", "...", "...", "...", "..."],
"A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
"B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
"C": [".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."],
"D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
"E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
"F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
"G": [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."],
"H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
"I": ["###", ".#.", ".#.", ".#.", ".#.", ".#.", "###"],
"J": ["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."],
"K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
"L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
"M": ["#...#", "##.##", "#.#.#", "#...#", "#...#", "#...#", "#...#"],
"N": ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
"O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
"P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
"Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
"R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
"S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
"T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
"U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
"V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
"W": ["#...#", "#...#", "#...#", "#...#", "#.#.#", "##.##", "#...#"],
"X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
"Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
"Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
"a": [".....", ".....", ".###.", "....#", ".####", "#...#", ".####"],
"b": ["#....", "#....", "####.", "#...#", "#...#", "#...#", "####."],
"c": [".....", ".....", ".###.", "#....", "#....", "#...#", ".###."],
"d": ["....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"],
"e": [".....", ".....", ".###.", "#...#", "#####", "#....", ".###."],
"f": ["..##.", ".#..#", ".#...", "###..", ".#...", ".#...", ".#..."],
"g": [".....", ".####", "#...#", "#...#", ".####", "....#", ".###."],
"h": ["#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"],
"i": ["..#..", ".....", ".##..", "..#..", "..#..", "..#..", ".###."],
"j": ["...#.", ".....", "..##.", "...#.", "...#.", "#..#.", ".##.."],
"k": ["#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."],
"l": [".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."],
"m": [".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"],
"n": [".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"],
"o": [".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."],
"p": [".....", ".....", "####.", "#...#", "#...#", "####.", "#...."],
"q": [".....", ".....", ".####", "#...#", "#...#", ".####", "....#"],
"r": [".....", ".....", ".#.##", ".#...", ".#...", ".#...", ".#..."],
"s": [".....", ".....", ".####", "#....", ".###.", "....#", "####."],
"t": [".#...", ".#...", "###..", ".#...", ".#...", ".#..#", "..##."],
"u": [".....", ".....", "#...#", "#...#", "#...#", "#...#", ".####"],
"v": [".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
"w": [".....", ".....", "#...#", "#...#", "#.#.#", "#.#.#", ".#.#."],
"x": [".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"],
"y": [".....", ".....", "#...#", "#...#", ".####", "....#", ".###."],
"z": [".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"],
"0": [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
"1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
"2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
"3": ["####.", "....#", "....#", ".###.", "....#", "....#", "####."],
"4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
"5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
"6": [".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."],
"7": ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."],
"8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
"9": [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."],
".": ["..", "..", "..", "..", "..", "..", "##"],
",": ["..", "..", "..", "..", "..", ".#", "#."],
"-": ["...", "...", "...", "###", "...", "...", "..."],
"'": ["#", "#", ".", ".", ".", ".", "."],
":": ["..", "..", "##", "..", "##", "..", ".."],
"/": ["....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."],
"%": ["#...#", "#..#.", "...#.", "..#..", ".#...", ".#..#", "#...#"],
"&": [".##..", "#..#.", ".##..", ".#...", "#.#.#", "#..#.", ".##.#"],
"(": ["..#", ".#.", "#..", "#..", "#..", ".#.", "..#"],
")": ["#..", ".#.", "..#", "..#", "..#", ".#.", "#.."],
"!": ["#", "#", "#", "#", "#", ".", "#"],
"?": [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."],
"+": [".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."],
"\u2019": ["..", ".#", "#.", "..", "..", "..", ".."],
"\u00b7": ["...", "...", "...", ".#.", "...", "...", "..."],
}


W = H = 1024
MARGIN = 40
BG = (11, 16, 26)
CARD = (18, 25, 39)
RULE = (35, 48, 74)
WHITE = (255, 255, 255)
DECK = (169, 183, 204)
WIRE = (109, 126, 153)
DATE_BAR = (255, 90, 69)

LAYOUT_WARNINGS = []


def gap(scale):
    return max(2, (scale * 7) // 10)


def glyph(ch):
    return _G.get(ch, _G["?"])


def adv(ch, scale, tracking=0):
    return len(glyph(ch)[0]) * scale + gap(scale) + tracking


def text_width(s, scale, tracking=0):
    if not s:
        return 0
    return sum(adv(c, scale, tracking) for c in s) - gap(scale) - tracking


def line_h(scale):
    return 7 * scale + max(4, scale)


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(bytes(bg) * (w * h))

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i] = c[0]
            self.buf[i + 1] = c[1]
            self.buf[i + 2] = c[2]

    def rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.buf[i:i + len(row)] = row

    def hline(self, x, y, w, c):
        self.rect(x, y, w, 1, c)

    def vline(self, x, y, h, c):
        self.rect(x, y, 1, h, c)

    def line(self, x0, y0, x1, y1, c, thick=1):
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.rect(x0, y0, thick, thick, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c):
        for y in range(-r, r + 1):
            span = int((r * r - y * y) ** 0.5)
            self.rect(cx - span, cy + y, 2 * span + 1, 1, c)

    def ring(self, cx, cy, r, c, thick=1):
        inner = (r - thick) * (r - thick)
        outer = r * r
        for y in range(-r, r + 1):
            span = int((outer - y * y) ** 0.5)
            x = -span
            while x <= span:
                if x * x + y * y >= inner:
                    self.px(cx + x, cy + y, c)
                x += 1

    def poly(self, pts, c):
        if not pts:
            return
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if y0 == y1:
                    continue
                if min(y0, y1) <= y < max(y0, y1):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.rect(int(round(xs[i])), y, int(round(xs[i + 1])) - int(round(xs[i])), 1, c)


def draw_text(cv, x, y, s, scale, color, bold=False, tracking=0):
    cx = x
    off = max(1, scale // 3) if bold else 0
    for ch in s:
        g = glyph(ch)
        gw = len(g[0])
        for ry, rowbits in enumerate(g):
            for rx, bit in enumerate(rowbits):
                if bit == "#":
                    px = cx + rx * scale
                    py = y + ry * scale
                    cv.rect(px, py, scale, scale, color)
                    if off:
                        cv.rect(px + off, py, scale, scale, color)
        cx += gw * scale + gap(scale) + tracking
    return cx


def wrap(s, scale, maxw, tracking=0):
    words = s.split(" ")
    lines = []
    cur = ""
    for wd in words:
        trial = wd if not cur else cur + " " + wd
        if text_width(trial, scale, tracking) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def icon_market(cv, x, y, c):
    for i, hgt in enumerate((22, 15, 8)):
        cv.rect(x + 3 + i * 11, y + 22 - hgt, 7, hgt, c)
    cv.line(x + 4, y + 8, x + 38, y + 18, c, 2)
    cv.poly([(x + 33, y + 12), (x + 40, y + 19), (x + 32, y + 21)], c)


def icon_tanker(cv, x, y, c):
    cv.poly([(x + 4, y + 16), (x + 40, y + 16), (x + 34, y + 26), (x + 10, y + 26)], c)
    cv.rect(x + 14, y + 10, 16, 6, c)
    for i in range(3):
        cv.hline(x + 3 + i * 2, y + 31 + i * 3, 30 - i * 4, c)
    cv.poly([(x + 30, y + 2), (x + 34, y + 9), (x + 41, y + 10), (x + 36, y + 15),
             (x + 37, y + 22), (x + 30, y + 16), (x + 23, y + 22), (x + 24, y + 15),
             (x + 19, y + 10), (x + 26, y + 9)], c)


def icon_padlock(cv, x, y, c):
    cv.ring(x + 22, y + 15, 9, c, 3)
    cv.rect(x + 22 - 9, y + 14, 18, 4, BG)
    cv.rect(x + 8, y + 17, 28, 20, c)
    cv.rect(x + 20, y + 23, 4, 8, BG)
    cv.circle(x + 22, y + 24, 3, BG)


def icon_trophy(cv, x, y, c):
    cv.poly([(x + 11, y + 4), (x + 33, y + 4), (x + 31, y + 18), (x + 25, y + 24),
             (x + 19, y + 24), (x + 13, y + 18)], c)
    cv.ring(x + 8, y + 10, 5, c, 2)
    cv.ring(x + 36, y + 10, 5, c, 2)
    cv.rect(x + 20, y + 24, 4, 9, c)
    cv.rect(x + 12, y + 33, 20, 5, c)


def icon_rocket(cv, x, y, c):
    cv.poly([(x + 22, y + 2), (x + 30, y + 14), (x + 30, y + 26), (x + 14, y + 26),
             (x + 14, y + 14)], c)
    cv.poly([(x + 14, y + 16), (x + 6, y + 28), (x + 14, y + 26)], c)
    cv.poly([(x + 30, y + 16), (x + 38, y + 28), (x + 30, y + 26)], c)
    cv.rect(x + 18, y + 10, 8, 8, BG)
    cv.poly([(x + 18, y + 28), (x + 22, y + 40), (x + 26, y + 28)], c)


def icon_tag(cv, x, y, c):
    cv.poly([(x + 6, y + 12), (x + 20, y + 2), (x + 38, y + 2), (x + 38, y + 20),
             (x + 28, y + 34), (x + 6, y + 20)], c)
    cv.circle(x + 32, y + 9, 4, BG)
    cv.line(x + 14, y + 28, x + 30, y + 36, WHITE, 2)


ICONS = (icon_market, icon_tanker, icon_padlock, icon_trophy, icon_rocket, icon_tag)

STORIES = (
    {
        "eyebrow": "MARKETS",
        "headline": "Nvidia slides 5.9%",
        "deck": "AI stocks slid as the S&P 500 fell 0.5%.",
        "wire": "REUTERS \u00b7 25 NOV",
        "accent": (255, 106, 87),
    },
    {
        "eyebrow": "MIDDLE EAST",
        "headline": "Mines hit two tankers",
        "deck": "Both vessels burned in the Strait of Hormuz, Iran's Guards said.",
        "wire": "REUTERS \u00b7 25 NOV",
        "accent": (255, 169, 77),
    },
    {
        "eyebrow": "COLOMBIA",
        "headline": "All freed in Cartagena",
        "deck": "Police ended a 17-hour supermarket siege; captives released.",
        "wire": "AL JAZEERA \u00b7 25 NOV",
        "accent": (79, 209, 165),
    },
    {
        "eyebrow": "AFRICA / SPORT",
        "headline": "Senegal title restored",
        "deck": "Sport's top court upheld the appeal over the disputed 2025 final.",
        "wire": "DAWN \u00b7 25 NOV",
        "accent": (255, 209, 102),
    },
    {
        "eyebrow": "SPACE / ASIA",
        "headline": "Pakistan reaches station",
        "deck": "The country's first astronaut is now aboard China's Tiangong.",
        "wire": "PID.GOV.PK \u00b7 25 NOV",
        "accent": (110, 193, 255),
    },
    {
        "eyebrow": "BRITAIN / RETAIL",
        "headline": "Poundland to close",
        "deck": "Administrators moved in, putting about 11,000 jobs at risk.",
        "wire": "BBC NEWS \u00b7 25 NOV",
        "accent": (199, 155, 255),
    },
)


ROW_GAP = 8
HEADLINE_SCALE = 6


def compose():
    cv = Canvas(W, H, BG)
    LAYOUT_WARNINGS.clear()

    draw_text(cv, MARGIN, 34, "THE DAY IN ONE IMAGE", 2, DATE_BAR, tracking=4)
    draw_text(cv, MARGIN, 56, "25 NOVEMBER 2026", 7, WHITE, bold=True)
    draw_text(cv, MARGIN, 116,
              "WEDNESDAY'S SIX BIGGEST STORIES, EACH WITH ITS WIRE", 2, WIRE, tracking=1)

    right = "SIX STORIES"
    draw_text(cv, W - MARGIN - text_width(right, 2, 3), 62, right, 2, WHITE, bold=True, tracking=3)
    right2 = "ALL DATED 25 NOV"
    draw_text(cv, W - MARGIN - text_width(right2, 2, 2), 82, right2, 2, WIRE, tracking=2)

    cv.rect(MARGIN, 142, W - 2 * MARGIN, 5, DATE_BAR)

    top = 164
    foot_rule = 966
    avail = foot_rule - top - 14 - ROW_GAP * (len(STORIES) - 1)
    row_h = avail // len(STORIES)

    for i, st in enumerate(STORIES):
        y = top + 14 + i * (row_h + ROW_GAP)
        cv.rect(MARGIN, y, W - 2 * MARGIN, row_h, CARD)
        cv.rect(MARGIN, y, 5, row_h, st["accent"])

        ix = MARGIN + 24
        ICONS[i](cv, ix, y + 18, st["accent"])

        tx = MARGIN + 106
        tw = (W - MARGIN - 22) - tx

        draw_text(cv, tx, y + 10, st["eyebrow"], 2, st["accent"], bold=True, tracking=3)
        wire = st["wire"]
        draw_text(cv, W - MARGIN - 20 - text_width(wire, 2, 1), y + 10, wire, 2, WIRE, tracking=1)

        hl = st["headline"]
        if text_width(hl, HEADLINE_SCALE, 0) > tw:
            LAYOUT_WARNINGS.append("headline overflows: " + hl)
        draw_text(cv, tx, y + 31, hl, HEADLINE_SCALE, WHITE, bold=True)

        lines = wrap(st["deck"], 3, tw)
        if len(lines) > 2:
            LAYOUT_WARNINGS.append("deck over 2 lines: " + st["headline"])
        for j, ln in enumerate(lines):
            if text_width(ln, 3, 0) > tw:
                LAYOUT_WARNINGS.append("deck overflows: " + ln)
            draw_text(cv, tx, y + 78 + j * 23, ln, 3, DECK)

        bottom = y + 78 + (len(lines) - 1) * 23 + 21
        if bottom > y + row_h - 2:
            LAYOUT_WARNINGS.append("row too tall: " + st["headline"])

    cv.hline(MARGIN, foot_rule, W - 2 * MARGIN, RULE)
    foot = "ALL EVENTS REPORTED ON 25 NOVEMBER 2026"
    draw_text(cv, MARGIN, foot_rule + 12, foot, 2, WIRE, tracking=1)
    return cv


def _chunk(tag, data):
    return (struct.pack(">I", len(data)) + tag + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))


def encode_png(cv):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.buf[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + _chunk(b"IEND", b""))


def build(out_path):
    data = encode_png(compose())
    parent = os.path.dirname(out_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(out_path, "wb") as fh:
        fh.write(data)
    return data


def main(argv):
    out = argv[1] if len(argv) > 1 else "/output/entry.png"
    data = build(out)
    for w in LAYOUT_WARNINGS:
        print("layout: " + w, file=sys.stderr)
    print(out, len(data), "bytes", cv_dims(), "warnings=" + str(len(LAYOUT_WARNINGS)))
    return 0


def cv_dims():
    return "%dx%d" % (W, H)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
