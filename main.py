#!/usr/bin/env python3
"""make.fun bounty entry: "Sum up 25 November's world news in one image".

Competition: news-image-20261125 — $100, deadline 2026-11-27 08:00 Beijing.
The program draws the whole infographic from code and writes it to
/output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png outside the grader).

Rules honoured (from the starter kit's RULES.txt / competition.yaml):
  * Python 3.13, standard library only (os, struct, zlib, binascii).
  * No network, no reading of any file, no imports outside this file.
  * Output is a whole PNG, 1024 x 1024 px, well under 1 MiB.
  * Fully deterministic: no time, no randomness, fixed story order, and
    zlib level 9 with fixed input, so two runs write byte-identical files.
  * The image names its day (WEDNESDAY 25 NOVEMBER 2026) and sums up six
    verified stories from that day, across regions and fields, in plain
    language with no hype and no speculation presented as fact.

The image is drawn with a small 5x7 bitmap font defined in this file
(scaled up, so every letter is crisp at any size) and a hand-rolled PNG
encoder, because the standard library has no image or font support.
"""

import os
import struct
import zlib
from binascii import crc32

WIDTH, HEIGHT = 1024, 1024

# ---------------------------------------------------------------- colours
PAPER = (250, 246, 238)      # warm paper background
INK = (17, 24, 39)           # near-black text
NAVY = (16, 35, 59)          # header / footer band
GOLD = (227, 168, 43)        # date + rules
RULE = (221, 214, 196)       # hairline between stories
MUTED = (90, 96, 110)        # (unused spare; kept for palette clarity)

# ---------------------------------------------------------------- 5x7 font
# Each glyph is 7 rows of 5 bits, '1' = ink. Uppercase + digits + the
# punctuation used in the copy below. All copy is uppercase, which suits
# a newspaper-style front page and keeps every glyph in this one set.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
}

# ---------------------------------------------------------------- stories
# Six verified stories from Wednesday 25 November 2026 (from web reporting
# checked on 25 Nov 2026). Wording stays close to what was reported; no
# story is added beyond this list, and no outcome is claimed that was not
# reported. Order is fixed: markets, Middle East, South America, Africa,
# space, climate.
STORIES = [
    {
        "tag": "MARKETS - USA / ASIA",
        "colour": (192, 57, 43),
        "headline": "NVIDIA SHARES FALL ABOUT 7%",
        "body": "AI STOCKS SLIDE AFTER HUANG'S RETURN AS CEO; LAWMAKERS QUESTION TRUMP'S ROLE.",
    },
    {
        "tag": "MIDDLE EAST",
        "colour": (14, 124, 123),
        "headline": "TANKERS HIT BY MINES IN HORMUZ",
        "body": "IRAN'S REVOLUTIONARY GUARDS SAID TWO TANKERS HIT MINES IN THE STRAIT OF HORMUZ.",
    },
    {
        "tag": "COLOMBIA",
        "colour": (211, 84, 0),
        "headline": "HOSTAGES FREED IN CARTAGENA",
        "body": "ARMED MEN HELD ABOUT 20 PEOPLE IN A SUPERMARKET. THE HOSTAGES WERE FREED.",
    },
    {
        "tag": "AFRICA - SPORT",
        "colour": (30, 132, 73),
        "headline": "SENEGAL REGAIN AFRICA CUP TITLE",
        "body": "SENEGAL REGAINED THE TITLE AFTER THE COURT OF ARBITRATION FOR SPORT RULED ON 24 NOVEMBER.",
    },
    {
        "tag": "SPACE - ASIA",
        "colour": (108, 52, 131),
        "headline": "PAKISTAN'S FIRST ASTRONAUT IN ORBIT",
        "body": "PAKISTAN'S FIRST ASTRONAUT REACHED CHINA'S SPACE STATION.",
    },
    {
        "tag": "CLIMATE",
        "colour": (36, 113, 163),
        "headline": "COP31 TALKS COLLAPSE IN ANTALYA",
        "body": "TALKS COLLAPSED AFTER OIL PRODUCERS BLOCKED ANY MENTION OF PHASING OUT FOSSIL FUELS.",
    },
]

FOOTER_MARKETS = "MARKETS: NIKKEI -2.76%   S&P 500 -0.5%   NVIDIA -7%"
FOOTER_NOTE = "ALL EVENTS REPORTED ON 25 NOVEMBER 2026"


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bytes(bg) * (w * h))

    def fill_rect(self, x, y, w, h, colour):
        row = bytes(colour) * w
        for yy in range(y, y + h):
            start = (yy * self.w + x) * 3
            self.px[start:start + w * 3] = row

    def text_width(self, text, scale):
        if not text:
            return 0
        return len(text) * 6 * scale - scale

    def draw_text(self, x, y, text, scale, colour):
        """Draw text at (x, y); top-left of the first glyph. Raises on a
        character with no glyph, so a typo can never silently vanish."""
        cx = x
        for ch in text:
            glyph = FONT.get(ch)
            if glyph is None:
                raise ValueError("no glyph for character: %r" % ch)
            for row_i, row in enumerate(glyph):
                for col_i, bit in enumerate(row):
                    if bit == "1":
                        self.fill_rect(
                            cx + col_i * scale, y + row_i * scale,
                            scale, scale, colour,
                        )
            cx += 6 * scale

    def draw_text_centred(self, cx, y, text, scale, colour):
        self.draw_text(cx - self.text_width(text, scale) // 2, y, text, scale, colour)


def wrap(text, max_width, scale, canvas):
    """Greedy word wrap to lines no wider than max_width px."""
    lines = []
    current = ""
    for word in text.split(" "):
        trial = word if not current else current + " " + word
        if canvas.text_width(trial, scale) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


# ---------------------------------------------------------------- PNG
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", crc32(kind + data) & 0xFFFFFFFF)
    return out


def png_bytes(canvas):
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)  # filter: none
        raw += canvas.px[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + _chunk(b"IEND", b"")
    )


# ---------------------------------------------------------------- layout
def build_image():
    c = Canvas(WIDTH, HEIGHT, PAPER)

    # Header band: masthead + date, then a gold rule.
    c.fill_rect(0, 0, WIDTH, 148, NAVY)
    c.draw_text_centred(WIDTH // 2, 26, "WORLD NEWS", 8, (255, 255, 255))
    c.draw_text_centred(WIDTH // 2, 102, "WEDNESDAY 25 NOVEMBER 2026", 3, GOLD)
    c.fill_rect(0, 148, WIDTH, 6, GOLD)

    # Six story rows, one column so the type stays large and readable.
    row_y, row_h = 170, 128
    text_x, text_w = 116, 880
    for i, story in enumerate(STORIES):
        y0 = row_y + i * row_h
        colour = story["colour"]
        c.fill_rect(0, y0, 10, row_h - 2, colour)
        # Number badge.
        c.fill_rect(30, y0 + 32, 64, 64, colour)
        num = str(i + 1)
        c.draw_text(
            30 + (64 - c.text_width(num, 6)) // 2, y0 + 43,
            num, 6, (255, 255, 255),
        )
        # Region tag, headline, then the body wrapped to at most 2 lines.
        c.draw_text(text_x, y0 + 8, story["tag"], 2, colour)
        c.draw_text(text_x, y0 + 32, story["headline"], 3, INK)
        lines = wrap(story["body"], text_w, 3, c)
        if len(lines) > 2:
            raise ValueError("story %d body wraps to %d lines" % (i + 1, len(lines)))
        for j, line in enumerate(lines):
            c.draw_text(text_x, y0 + 62 + j * 26, line, 3, INK)
        if i < len(STORIES) - 1:
            c.fill_rect(0, y0 + row_h - 2, WIDTH, 2, RULE)

    # Footer band: the day's market moves, and the date once more.
    fy = row_y + len(STORIES) * row_h  # 938
    c.fill_rect(0, fy, WIDTH, HEIGHT - fy, NAVY)
    c.draw_text_centred(WIDTH // 2, fy + 16, FOOTER_MARKETS, 2, (255, 255, 255))
    c.draw_text_centred(WIDTH // 2, fy + 46, FOOTER_NOTE, 2, GOLD)
    return c


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    data = png_bytes(build_image())
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
