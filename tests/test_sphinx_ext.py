from __future__ import annotations

import unittest
from types import SimpleNamespace

from docutils import nodes
from docutils.utils import new_document

from codebinder.sphinx_ext import suppress_content_sections_from_latex_toc


def _make_app(*, builder_format: str, docname: str, enabled: bool = True):
    return SimpleNamespace(
        builder=SimpleNamespace(format=builder_format),
        env=SimpleNamespace(docname=docname),
        config=SimpleNamespace(codebinder_structural_latex_toc=enabled),
    )


def _make_document() -> nodes.document:
    document = new_document("research/PDE.md")

    # This mirrors the nbsphinx shape produced by CodeBinder: the injected
    # filename heading is the outermost section, and source Markdown headings
    # are nested sections below it.
    file_section = nodes.section(ids=["pde-md"], names=["pde.md"])
    file_section += nodes.title("", "PDE.md")

    formulation = nodes.section(ids=["formulation"], names=["formulation"])
    formulation += nodes.title("", "PDE formulation")
    formulation += nodes.paragraph("", "Formulation body.")

    boundary = nodes.section(ids=["boundary-conditions"], names=["boundary conditions"])
    boundary += nodes.title("", "Boundary conditions")
    boundary += nodes.paragraph("", "Boundary body.")
    formulation += boundary

    file_section += formulation
    document += file_section
    return document


class SphinxExtensionTests(unittest.TestCase):
    def test_latex_source_document_preserves_file_title_and_replaces_content_sections(self) -> None:
        document = _make_document()
        app = _make_app(builder_format="latex", docname="research/PDE.md")

        suppress_content_sections_from_latex_toc(app, document)

        sections = list(document.findall(nodes.section))
        self.assertEqual(len(sections), 1)
        self.assertEqual(sections[0].astext().splitlines()[0], "PDE.md")
        self.assertEqual(sections[0]["ids"], ["pde-md"])

        rubrics = list(document.findall(nodes.rubric))
        self.assertEqual([rubric.astext() for rubric in rubrics], [
            "PDE formulation",
            "Boundary conditions",
        ])
        self.assertEqual(rubrics[0]["ids"], ["formulation"])
        self.assertEqual(rubrics[1]["ids"], ["boundary-conditions"])
        self.assertIn("codebinder-content-heading", rubrics[0]["classes"])
        self.assertIn("codebinder-content-heading-level-1", rubrics[0]["classes"])
        self.assertIn("codebinder-content-heading-level-2", rubrics[1]["classes"])
        self.assertIn("Formulation body.", document.astext())
        self.assertIn("Boundary body.", document.astext())

    def test_html_builder_keeps_normal_sections(self) -> None:
        document = _make_document()
        app = _make_app(builder_format="html", docname="research/PDE.md")

        suppress_content_sections_from_latex_toc(app, document)

        self.assertEqual(len(list(document.findall(nodes.section))), 3)
        self.assertEqual(list(document.findall(nodes.rubric)), [])

    def test_structural_index_document_is_not_rewritten(self) -> None:
        document = _make_document()
        app = _make_app(builder_format="latex", docname="research/CGC/index")

        suppress_content_sections_from_latex_toc(app, document)

        self.assertEqual(len(list(document.findall(nodes.section))), 3)
        self.assertEqual(list(document.findall(nodes.rubric)), [])


if __name__ == "__main__":
    unittest.main()
