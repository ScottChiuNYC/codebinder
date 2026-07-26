from __future__ import annotations

import unittest

from codebinder.notebooks import make_notebook


class NotebookTests(unittest.TestCase):
    def test_has_two_markdown_cells(self) -> None:
        notebook = make_notebook("print('ok')\n", ".py", "main.py")
        self.assertEqual(notebook["nbformat"], 4)
        self.assertEqual(len(notebook["cells"]), 2)
        self.assertEqual(notebook["cells"][0]["cell_type"], "markdown")
        self.assertEqual(notebook["cells"][1]["cell_type"], "markdown")

    def test_title_cell_content_and_literal_underscores(self) -> None:
        notebook = make_notebook("pass\n", ".py", "__init__.py")
        title_source = "".join(notebook["cells"][0]["source"])
        self.assertEqual(title_source, "# `__init__.py`")

    def test_code_cell_is_fenced_markdown(self) -> None:
        notebook = make_notebook("int main() {}\n", ".cpp", "main.cpp")
        code_source = "".join(notebook["cells"][1]["source"])
        self.assertIn("```cpp", code_source)
        self.assertIn("int main() {}", code_source)
        self.assertTrue(code_source.strip().endswith("```"))

    def test_markdown_file_stays_markdown_and_headings_are_demoted(self) -> None:
        notebook = make_notebook("# Heading\n\nSome text\n", ".md", "notes.md")
        content_source = "".join(notebook["cells"][1]["source"])
        self.assertEqual(content_source, "## Heading\n\nSome text\n")
        self.assertNotIn("```markdown", content_source)

    def test_python_ipykernel_metadata(self) -> None:
        notebook = make_notebook("pass\n", ".py", "test.py")
        kernelspec = notebook["metadata"]["kernelspec"]
        self.assertEqual(kernelspec["name"], "python3")
        self.assertEqual(kernelspec["language"], "python")

    def test_unknown_extension_uses_extension_as_language(self) -> None:
        notebook = make_notebook("data", ".xyz", "data.xyz")
        code_source = "".join(notebook["cells"][1]["source"])
        self.assertIn("```xyz", code_source)


if __name__ == "__main__":
    unittest.main()

