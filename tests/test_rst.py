from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from codebinder.rst import generate_indexes


class RstTests(unittest.TestCase):
    def test_generates_root_nested_indexes_and_structure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            notebook_paths = [
                Path("main.py.ipynb"),
                Path("pkg") / "utils.cpp.ipynb",
                Path("pkg") / "sub" / "header.h.ipynb",
            ]
            generate_indexes(root, notebook_paths, "Demo")

            root_index = (root / "index.rst").read_text(encoding="utf-8")
            pkg_index = (root / "pkg" / "index.rst").read_text(encoding="utf-8")
            structure = json.loads((root / "project_structure.ipynb").read_text(encoding="utf-8"))

            self.assertIn("main.py", root_index)
            self.assertIn("pkg/index", root_index)
            self.assertIn("utils.cpp", pkg_index)
            self.assertIn("sub/index", pkg_index)
            self.assertIn("Project Folder Structure", root_index)
            self.assertIn(".. code-block:: text", root_index)
            self.assertIn("pkg/", root_index)
            self.assertIn("header.h", root_index)
            self.assertIn("Project Folder Structure", "".join(structure["cells"][0]["source"]))


if __name__ == "__main__":
    unittest.main()

