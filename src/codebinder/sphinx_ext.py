"""Sphinx helpers for keeping CodeBinder PDF tables of contents structural."""

from __future__ import annotations

from pathlib import PurePosixPath
from typing import TYPE_CHECKING

from docutils import nodes

from .discovery import INCLUDED_EXTENSIONS

if TYPE_CHECKING:
    from sphinx.application import Sphinx


def _is_generated_source_document(docname: str) -> bool:
    """Return whether *docname* represents a source file mirrored by CodeBinder."""
    return PurePosixPath(docname).suffix.lower() in INCLUDED_EXTENSIONS


def _section_depth(section: nodes.section) -> int:
    depth = 1
    parent = section.parent
    while parent is not None:
        if isinstance(parent, nodes.section):
            depth += 1
        parent = parent.parent
    return depth


def _replace_section_with_rubric(section: nodes.section) -> None:
    """Replace one content section with an anchored, non-TOC rubric heading."""
    title = next(
        (child for child in section.children if isinstance(child, nodes.title)),
        None,
    )
    if title is None:
        return

    # The outermost section is the CodeBinder-inserted source-file title. A
    # content heading one level below it is therefore content level 1.
    content_depth = max(_section_depth(section) - 1, 1)
    rubric = nodes.rubric(
        title.rawsource,
        "",
        *(child.deepcopy() for child in title.children),
    )
    for attribute in ("ids", "names", "dupnames"):
        rubric[attribute] = list(section.get(attribute, []))
    rubric["classes"] = [
        *section.get("classes", []),
        "codebinder-content-heading",
        f"codebinder-content-heading-level-{min(content_depth, 6)}",
    ]

    remaining_children = [child for child in section.children if child is not title]
    section.children = []
    for child in remaining_children:
        child.parent = None
    section.replace_self([rubric, *remaining_children])


def suppress_content_sections_from_latex_toc(app: Sphinx, doctree: nodes.document) -> None:
    """Keep Markdown content headings visible without adding them to the PDF TOC."""
    if app.builder.format != "latex":
        return
    if not app.config.codebinder_structural_latex_toc:
        return

    docname = app.env.docname
    if not _is_generated_source_document(docname):
        return

    # nbsphinx represents the CodeBinder-inserted filename heading as the
    # outermost section. Preserve that section so the file remains a numbered
    # structural entry in the PDF hierarchy. Headings from the source Markdown
    # are descendant sections; replace only those, deepest-first, so their body
    # hierarchy and anchors survive without generating LaTeX section commands.
    sections = [
        section
        for section in doctree.findall(nodes.section)
        if _section_depth(section) > 1
    ]
    for section in reversed(sections):
        _replace_section_with_rubric(section)


def setup(app: Sphinx) -> dict[str, object]:
    """Register the CodeBinder structural-LaTeX-TOC transform."""
    app.add_config_value("codebinder_structural_latex_toc", True, "env")
    app.connect("doctree-read", suppress_content_sections_from_latex_toc)
    return {
        "version": "0.2",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
