import ast
import os
import re
import struct
import sys
import tempfile
import unittest
import zlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import main  # noqa: E402


def ihdr(data):
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    assert data[12:16] == b"IHDR"
    return struct.unpack(">IIBBBBB", data[16:29])


class TestEntry(unittest.TestCase):
    def setUp(self):
        self.cv = main.compose()
        self.png = main.encode_png(self.cv)

    def test_png_is_1024_square_rgb8(self):
        w, h, depth, ctype = ihdr(self.png)[:4]
        self.assertEqual((w, h, depth, ctype), (1024, 1024, 8, 2))

    def test_under_one_mib(self):
        self.assertLess(len(self.png), 1024 * 1024)

    def test_png_crcs_valid(self):
        i = 8
        seen = []
        while i < len(self.png):
            n = struct.unpack(">I", self.png[i:i + 4])[0]
            tag = self.png[i + 4:i + 8]
            body = self.png[i + 8:i + 8 + n]
            crc = struct.unpack(">I", self.png[i + 8 + n:i + 12 + n])[0]
            self.assertEqual(crc, zlib.crc32(tag + body) & 0xFFFFFFFF)
            seen.append(tag)
            i += 12 + n
        self.assertEqual(seen, [b"IHDR", b"IDAT", b"IEND"])

    def test_two_runs_byte_identical(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = main.build(os.path.join(tmp, "a.png"))
            b = main.build(os.path.join(tmp, "b.png"))
        self.assertEqual(a, b)
        self.assertEqual(len(a), len(b))

    def test_no_layout_warnings(self):
        main.compose()
        self.assertEqual(main.LAYOUT_WARNINGS, [])

    def test_imports_are_stdlib_only(self):
        with open(os.path.join(ROOT, "main.py"), encoding="utf-8") as fh:
            tree = ast.parse(fh.read())
        mods = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                mods.update(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                mods.add(node.module.split(".")[0])
        self.assertLessEqual(mods, {"os", "struct", "sys", "zlib"})

    def test_no_network_or_clock_calls(self):
        with open(os.path.join(ROOT, "main.py"), encoding="utf-8") as fh:
            src = fh.read()
        src = re.sub(r'\A\s*(#[^\n]*\n)*"""..*?"""', "", src, flags=re.S)
        self.assertNotIn('"""', src, "docstring strip failed, scan would be blind")
        for bad in ("import socket", "urllib", "requests.", "time.time",
                    "import datetime", "import random", "import uuid",
                    "import PIL", "from PIL", "ImageFont", "subprocess"):
            self.assertNotIn(bad, src)

    def test_headline_readable_at_300px(self):
        cap_px = 7 * main.HEADLINE_SCALE
        scaled = cap_px * 300.0 / main.W
        self.assertGreaterEqual(scaled, 11.5)

    def test_every_story_dated_25_nov(self):
        self.assertEqual(len(main.STORIES), 6)
        for st in main.STORIES:
            self.assertIn("25 NOV", st["wire"])

    def test_headline_and_deck_do_not_repeat(self):
        stop = {"the", "a", "an", "of", "in", "to", "and", "by", "at", "on"}
        for st in main.STORIES:
            h = {w.lower().strip(".,%'") for w in st["headline"].split()} - stop
            d = {w.lower().strip(".,%'") for w in st["deck"].split()} - stop
            self.assertEqual(h - d, h, "deck echoes headline: " + st["headline"])

    def test_every_headline_fits_its_column(self):
        main.compose()
        band = (main.W - main.MARGIN - 22) - (main.MARGIN + 106)
        for st in main.STORIES:
            self.assertLessEqual(
                main.text_width(st["headline"], main.HEADLINE_SCALE), band, st["headline"])


if __name__ == "__main__":
    unittest.main()
