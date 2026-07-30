# CodeBinder Architecture and Sphinx Behavior

## Purpose

This document defines the durable behavior of CodeBinder. It describes source discovery, notebook generation, asset copying, recursive folder indexes, the optional Sphinx extension, and the contract that consumers can rely on when producing HTML or LaTeX/PDF documentation.

The README is the quick-start guide. This file is the maintenance reference for changes that can affect generated document structure or downstream PDF builds.

## 1. Processing pipeline

CodeBinder applies the following pipeline:

```text
source project
    ↓ recursive discovery and .gitignore filtering
included text files + supported assets
    ↓ conversion and copying
generated notebooks + mirrored assets
    ↓ recursive RST index generation
CodeBinder documentation tree
    ↓ Sphinx and nbsphinx
HTML or LaTeX/PDF output
```

CodeBinder itself does not build HTML or PDF files. It creates an nbsphinx-compatible source tree and provides an optional Sphinx extension for structural LaTeX tables of contents.

## 2. Source discovery

`codebinder.discovery` walks the source tree recursively in deterministic relative-path order.

### 2.1 Ignore rules

Discovery:

- respects the root `.gitignore`, including negation rules when `pathspec` is installed;
- always ignores repository metadata and common generated directories such as `.git`, virtual environments, Python caches, and `node_modules`;
- applies the same ignore logic to text files and copied assets.

The root `.gitignore` is the only project ignore file interpreted by CodeBinder. Nested `.gitignore` files are not currently loaded independently.

### 2.2 Included text files

Included text files are selected by extension. The current set covers common programming languages, Markdown and documentation formats, configuration files, structured data, shell scripts, and build files.

Every included source file is converted to a notebook whose relative path is:

```text
<original relative path>.ipynb
```

For example:

```text
research/PDE.md
    → research/PDE.md.ipynb

src/model.cpp
    → src/model.cpp.ipynb
```

The original extension remains visible in the generated notebook name and document title.

### 2.3 Existing notebooks

Source `.ipynb` files are not currently included as text files or copied as assets. They are ignored by discovery.

Supporting source notebooks in the future requires an explicit design decision about whether to copy them unchanged, normalize metadata, preserve outputs, execute cells, or reject unsafe and non-reproducible states. Merely adding `.ipynb` to the ordinary text-extension set would incorrectly wrap notebook JSON in another notebook.

### 2.4 Assets

The following asset types are copied verbatim while preserving their relative paths:

```text
.png .jpg .jpeg .gif .svg .webp .bmp .pdf
```

This preserves relative image links from converted Markdown documents. For example:

```text
docs/results/convergence.md
docs/results/figures/convergence.png
```

becomes:

```text
docs/results/convergence.md.ipynb
docs/results/figures/convergence.png
```

A Markdown reference such as `![Convergence](figures/convergence.png)` therefore continues to resolve from the generated notebook.

## 3. Notebook conversion

Each generated notebook uses the packaged notebook template and contains a CodeBinder-inserted source-file title.

### 3.1 Markdown input

Markdown remains Markdown. CodeBinder shifts source headings below the inserted file title so the file title owns the outer document level.

The conceptual result is:

```text
source filename
    source Markdown heading
        source Markdown subheading
```

### 3.2 Non-Markdown input

Other supported text formats are placed in fenced code blocks with an appropriate or generic language marker. The purpose is readable source inclusion rather than execution.

### 3.3 Execution policy

CodeBinder does not execute generated notebooks. Execution behavior belongs to the consuming Sphinx configuration. A typical documentation build uses:

```python
nbsphinx_execute = "never"
```

This makes PDF production deterministic with respect to notebook execution and requires any displayed numerical figures to be present as copied assets or saved notebook outputs from a separately supported notebook workflow.

## 4. Recursive folder indexes

`codebinder.rst.generate_indexes` creates:

- one root `index.rst`;
- one `index.rst` in every discovered output folder;
- one `project_structure.ipynb` at the root.

Every folder index lists:

1. notebooks directly contained in that folder;
2. the `index` documents of directly contained child folders.

Because every child folder repeats the same rule, the generated structure is recursive without a CodeBinder-imposed maximum depth.

For example:

```text
research/
├── PDE.md
└── cgc/
    ├── derivation.md
    └── implementation/
        └── algorithm.md
```

produces structural documents equivalent to:

```text
index
└── research/index
    ├── research/PDE.md
    └── research/cgc/index
        ├── research/cgc/derivation.md
        └── research/cgc/implementation/index
            └── research/cgc/implementation/algorithm.md
```

### 4.1 Title-only toctrees

Generated indexes use:

```rst
.. toctree::
   :titlesonly:
```

They deliberately do not set `:maxdepth:`.

The consequences are:

- CodeBinder retains the entire recursive document hierarchy;
- toctrees list document titles rather than every section found inside a document;
- the consuming Sphinx builder remains responsible for deciding how many structural levels appear in navigation or a printed table of contents.

### 4.2 Project structure page

The root index references one generated `project_structure.ipynb`. The folder tree is rendered there exactly once. The root `index.rst` remains a structural toctree page and must not embed a preceding section that would nest all generated documents under one artificial chapter.

## 5. Structural LaTeX table of contents

The optional `codebinder.sphinx_ext` extension separates structural document titles from headings inside source documents.

Enable it after `nbsphinx`:

```python
extensions = [
    "nbsphinx",
    "codebinder.sphinx_ext",
]
```

The extension is enabled by default after it is loaded. It can be disabled with:

```python
codebinder_structural_latex_toc = False
```

### 5.1 Structural contract

For the LaTeX builder, the contract is:

```text
folder titles enter the global PDF hierarchy
source-file titles enter the global PDF hierarchy
headings inside source files remain in the body but do not enter the global PDF TOC
```

This distinction is the central behavioral invariant of the extension.

### 5.2 Actual nbsphinx doctree shape

For a CodeBinder-generated source notebook, nbsphinx represents the inserted filename as the outermost section. Headings originating inside the source Markdown are descendant sections.

The extension therefore:

1. runs only for the LaTeX builder;
2. runs only for generated source documents whose docname retains a supported source extension;
3. preserves the outermost source-file section;
4. replaces only descendant sections, deepest first, with `docutils.nodes.rubric` nodes;
5. copies section IDs, names, duplicate names, title children, and body children;
6. adds classes recording the original content-heading depth.

The preserved outer section keeps the file name numbered and eligible for the global TOC. The rubric nodes remain visible headings in the document body but do not generate numbered LaTeX section commands.

### 5.3 Anchors and body content

Converted content headings retain their section identifiers and names on the replacement rubric node. Existing body content remains in document order.

This is intended to preserve local anchors and readable hierarchy. Any change to the transform must include regression tests for:

- the source-file title remaining a section;
- nested source headings becoming rubrics;
- anchor IDs surviving;
- body content surviving;
- heading-depth classes remaining correct.

### 5.4 HTML behavior

The transform does nothing for HTML builders. HTML continues to receive normal section nodes for headings inside source files.

Structural folder index documents are also never rewritten by the extension.

## 6. TOC depth is a consumer decision

CodeBinder preserves recursive structure at arbitrary folder depth, but it does not choose how much of that structure a PDF prints.

A consumer may configure:

```python
latex_elements = {
    "preamble": r"""
\setcounter{tocdepth}{3}
\setcounter{secnumdepth}{3}
""",
}
```

The counters control different behavior:

- `tocdepth` controls which structural levels appear in the printed table of contents;
- `secnumdepth` controls which structural levels receive section numbers.

Because source-document content headings have already been converted to rubrics, increasing these counters exposes deeper folder and file structure without also exposing every heading inside Markdown files.

A source file deeper than the configured LaTeX depth remains part of the generated documentation and PDF body; it simply may not appear in the printed TOC or receive a full structural number.

## 7. Consumer responsibilities

A PDF-producing repository should:

1. pin CodeBinder to an immutable commit or release;
2. load `nbsphinx` and `codebinder.sphinx_ext`;
3. choose explicit `tocdepth` and `secnumdepth` values;
4. decide whether notebooks are executed;
5. provide fonts and LaTeX dependencies required by its content;
6. validate both the generated PDF and the printed TOC;
7. add repository-specific assertions for important folder and file entries;
8. inspect a rendered TOC after structural changes.

CodeBinder cannot guarantee that arbitrary Markdown, raw LaTeX, tables, equations, fonts, or cross-references compile correctly in every consumer project.

## 8. Stable invariants

Changes should preserve these invariants unless a deliberate breaking change is documented:

- discovery order is deterministic;
- ignored files and assets remain ignored consistently;
- relative source and asset paths are preserved;
- each included source file produces exactly one generated notebook;
- each discovered folder receives one structural index;
- the project tree is rendered exactly once;
- generated toctrees remain title-only and have no fixed maximum depth;
- source-file titles remain structural in LaTeX;
- source-document content headings remain visible but stay out of the global LaTeX TOC;
- HTML content-section behavior remains unchanged.

## 9. Validation and maintenance checklist

When changing discovery, conversion, RST generation, or the Sphinx extension:

1. update or add focused unit tests;
2. run `python -m unittest discover -s tests -v`;
3. verify root and nested `index.rst` output;
4. verify the project structure notebook is generated once;
5. verify file titles remain structural sections in a representative nbsphinx doctree;
6. verify nested content headings become anchored rubrics only for LaTeX;
7. verify HTML and structural index documents are unchanged;
8. build at least one real consumer PDF when TOC semantics change;
9. inspect the generated `.toc` file;
10. visually inspect the printed table of contents.

A unit test proves the transform's local contract. A real consumer build is still required because Sphinx, nbsphinx, LaTeX, document content, and project-specific post-processing interact across repository boundaries.
