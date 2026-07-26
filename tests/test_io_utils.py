from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from codebinder.io_utils import read_text_file


class IoUtilsTests(unittest.TestCase):
    def test_strips_utf8_bom(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "README.md"
            path.write_bytes("\ufeffCodebinder\n".encode("utf-8"))
            self.assertEqual(read_text_file(path), "Codebinder\n")

    def test_rejects_nul_containing_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "binary.txt"
            path.write_bytes(b"text\x00more")
            self.assertIsNone(read_text_file(path))


if __name__ == "__main__":
    unittest.main()

