from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from codebinder.discovery import discover_files


class DiscoveryTests(unittest.TestCase):
    def test_discovers_allowlisted_files_and_preserves_names(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "a.py").write_text("print('hi')\n", encoding="utf-8")
            (root / "a.txt").write_text("hello\n", encoding="utf-8")
            (root / "index.py").write_text("pass\n", encoding="utf-8")
            (root / "skip.png").write_bytes(b"\x89PNG")
            (root / ".git").mkdir()
            (root / ".git" / "ignored.py").write_text("pass\n", encoding="utf-8")

            found = discover_files(root)
            relative = {item.relative_path.as_posix() for item in found}
            notebooks = {item.notebook_relative_path.as_posix() for item in found}

            self.assertEqual(relative, {"a.py", "a.txt", "index.py"})
            self.assertIn("a.py.ipynb", notebooks)
            self.assertIn("a.txt.ipynb", notebooks)
            self.assertIn("index.py.ipynb", notebooks)

    def test_respects_gitignore_patterns_and_negation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / ".gitignore").write_text("*.py\n!keep.py\nskip_dir/\n", encoding="utf-8")
            (root / "ignored.py").write_text("pass\n", encoding="utf-8")
            (root / "keep.py").write_text("pass\n", encoding="utf-8")
            (root / "skip_dir").mkdir()
            (root / "skip_dir" / "inside.txt").write_text("skip\n", encoding="utf-8")

            relative = {item.relative_path.as_posix() for item in discover_files(root)}
            self.assertIn("keep.py", relative)
            self.assertNotIn("ignored.py", relative)
            self.assertNotIn("skip_dir/inside.txt", relative)


if __name__ == "__main__":
    unittest.main()

