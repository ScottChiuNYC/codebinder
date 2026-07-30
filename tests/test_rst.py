from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from codebinder.rst import generate_indexes


class RstTests(unittest.TestCase):
    def test_generates_root_nested_indexes_and_single_structure_page(self) -> None:
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

            # The root page must remain a structural toctree page. Embedding a
            # section before the toctree nests the entire PDF under that section.
            self.assertIn(".. toctree::", root_index)
            self.assertIn("   :titlesonly:", root_index)
            self.assertIn("project_structure", root_index)
            self.assertNotIn("Project Folder Structure", root_index)
            self.assertNotIn(".. code-block:: text", root_index)
            self.assertNotIn(":maxdepth:", root_index)

            # Every folder index is structural too: it lists child document
            # titles without asking Sphinx to surface headings from inside them.
            self.assertIn("   :titlesonly:", pkg_index)

            # The tree is rendered exactly once, in its dedicated notebook.
            self.assertIn("Project Folder Structure", "".join(structure["cells"][0]["source"]))
            structure_source = "".join(structure["cells"][1]["source"])
            self.assertIn("pkg/", structure_source)
            self.assertIn("header.h", structure_source)


if __name__ == "__main__":
    unittest.main()
