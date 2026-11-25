"""Smoke test for the infographic's command-line entry point."""

import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest


class EntryPointTest(unittest.TestCase):
    def test_generates_deterministic_png(self):
        script = Path(__file__).with_name("main.py")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "out"
            env = dict(os.environ, MAKEFUN_OUTPUT_DIR=str(output))
            command = [sys.executable, str(script)]

            subprocess.run(command, check=True, env=env)
            entry = output / "entry.png"
            first_run = entry.read_bytes()
            entry.unlink()

            subprocess.run(command, check=True, env=env)
            self.assertEqual(first_run, entry.read_bytes())

        self.assertEqual(first_run[:8], b"\x89PNG\r\n\x1a\n")
        self.assertEqual(first_run[12:16], b"IHDR")
        self.assertEqual(struct.unpack(">II", first_run[16:24]), (1024, 1024))
        self.assertLess(len(first_run), 1024 * 1024)
