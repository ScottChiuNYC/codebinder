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
- Keeps the root index structural, so top-level documents and folders become separate PDF chapters instead of being nested under the folder-structure page.

## Install

```console
python -m pip install -e .
```

## CLI

```console
python -m codebinder <source_project_path> [output_path]
```

If `output_path` is omitted, the Windows-compatible default is
`C:/Temp/<source_folder_name>_codebinder`.

For example, a source file `src/module.py` produces
`src/module.py.ipynb`, and its toctree entry is `src/module.py`.
