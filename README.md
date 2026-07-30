# Codebinder

Codebinder mirrors a source project tree into Jupyter notebooks and generates
hierarchical RST indexes so Sphinx and nbsphinx can build browsable documentation
and PDFs.

## What it does

- Walks a project folder recursively.
- Respects a root `.gitignore`, including negation rules.
- Includes common source, documentation, configuration, and data files.
- Creates `<original_name>.ipynb` for every included text file.
- Leaves Markdown as Markdown and wraps other source in a fenced code block.
- Copies common image/PDF assets alongside the generated notebooks.
- Creates `index.rst` in the root and every discovered output folder.
- Creates one project-folder-structure notebook and references it from the root toctree.
- Keeps generated toctrees structural and title-only, without a fixed maximum depth.
- Provides an optional Sphinx extension that keeps source-file headings visible in LaTeX output without adding them to the global PDF table of contents.

## Documentation

See [`docs/architecture.md`](docs/architecture.md) for the detailed discovery,
conversion, recursive-index, Sphinx-extension, and PDF table-of-contents contract.
The architecture document also records current limitations, including the fact
that source `.ipynb` files are not yet included.

## Install

```console
python -m pip install -e .
```

For development and Sphinx-extension tests:

```console
python -m pip install -e '.[test]'
```

## CLI

```console
python -m codebinder <source_project_path> [output_path]
```

If `output_path` is omitted, the Windows-compatible default is
`C:/Temp/<source_folder_name>_codebinder`.

For example, a source file `src/module.py` produces
`src/module.py.ipynb`, and its toctree entry is `src/module.py`.

## Structural PDF table of contents

Add the extension after `nbsphinx` in the Sphinx configuration:

```python
extensions = [
    "nbsphinx",
    "codebinder.sphinx_ext",
]
```

For a repository tree such as:

```text
research/
├── PDE.md
└── CGC/
    ├── algorithm.md
    └── numerical_results.md
```

the generated folder and file titles remain structural LaTeX sections. Headings
inside `PDE.md`, `algorithm.md`, and `numerical_results.md` are converted only for
the LaTeX builder into anchored rubric headings. They remain visible in the body,
but do not enter the global PDF table of contents. HTML output is unchanged.

A consumer can therefore increase the LaTeX structural depth without exposing all
headings from inside each Markdown file:

```python
latex_elements = {
    "preamble": r"""
\setcounter{tocdepth}{3}
\setcounter{secnumdepth}{3}
""",
}
```

Set `codebinder_structural_latex_toc = False` to disable the transform.
