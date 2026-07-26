from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from codebinder.cli import main


class CliSmokeTests(unittest.TestCase):
    def test_cli_generates_expected_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source = base / "project"
            output = base / "out"
            (source / "sub").mkdir(parents=True)
            (source / "main.py").write_text("print('ok')\n", encoding="utf-8")
            (source / "sub" / "readme.md").write_text("Hello\n", encoding="utf-8")
            (source / "icon.png").write_bytes(b"\x89PNG\r\n")

            result = main([str(source), str(output)])

            self.assertEqual(result, 0)
            self.assertTrue((output / "main.py.ipynb").exists())
            self.assertTrue((output / "sub" / "readme.md.ipynb").exists())
            self.assertTrue((output / "icon.png").exists())
            self.assertTrue((output / "index.rst").exists())
            self.assertTrue((output / "sub" / "index.rst").exists())
            self.assertFalse((output / "conf.py").exists())


if __name__ == "__main__":
    unittest.main()

