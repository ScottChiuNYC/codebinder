"""Sphinx RST index generation utilities."""

from __future__ import annotations

import copy
import json
from pathlib import Path

from .io_utils import to_posix


def _title_for_dir(directory: Path, root: Path, project_name: str) -> str:
    if directory == root:
        return f"{project_name} Study Notes"
    return f"Folder: {to_posix(directory.relative_to(root))}"


def _build_tree_lines(notebook_paths: list[Path]) -> list[str]:
    """Build a simple Unicode folder tree from generated notebook paths."""

    children: dict[Path, set[Path]] = {Path(""): set()}
    files_by_dir: dict[Path, set[str]] = {Path(""): set()}
    for notebook_path in sorted(notebook_paths):
        source_like_path = notebook_path.with_suffix("")
        parts = source_like_path.parts
        if not parts:
            continue
        current = Path("")
        for part in parts[:-1]:
            next_dir = current / part
            children.setdefault(current, set()).add(next_dir)
            children.setdefault(next_dir, set())
            files_by_dir.setdefault(next_dir, set())
            current = next_dir
        files_by_dir.setdefault(current, set()).add(parts[-1])

    def render_dir(directory: Path, prefix: str) -> list[str]:
        lines: list[str] = []
        directory_names = sorted((p.name for p in children.get(directory, set())), key=str.lower)
        file_names = sorted(files_by_dir.get(directory, set()), key=str.lower)
        items = [("dir", name) for name in directory_names] + [("file", name) for name in file_names]
        for index, (kind, name) in enumerate(items):
            is_last = index == len(items) - 1
            branch = "└── " if is_last else "├── "
            if kind == "dir":
                lines.append(f"{prefix}{branch}{name}/")
                child_prefix = f"{prefix}{'    ' if is_last else '│   '}"
                lines.extend(render_dir(directory / name, child_prefix))
            else:
                lines.append(f"{prefix}{branch}{name}")
        return lines

    return render_dir(Path(""), "")


def _load_template() -> dict:
    template_path = Path(__file__).parent / "templates" / "notebook_template.ipynb"
    return json.loads(template_path.read_text(encoding="utf-8"))


def _create_structure_notebook(tree_lines: list[str]) -> dict:
    notebook = copy.deepcopy(_load_template())
    notebook["cells"][0]["source"] = ["# Project Folder Structure"]
    source: list[str] = ["```text\n"]
    source.extend(f"{line}\n" for line in tree_lines)
    source.append("```")
    notebook["cells"][1]["source"] = source
    return notebook


def _make_index_content(title: str, entries: list[str]) -> str:
    """Create a structural index whose toctree is not nested under a section."""

    lines: list[str] = [title, "=" * len(title), ""]
    if entries:
        lines.extend([".. toctree::", ""])
        lines.extend(f"   {entry}" for entry in entries)
        lines.append("")
    else:
        lines.extend(["No generated notebooks in this folder.", ""])
    return "\n".join(lines)


def generate_indexes(
    output_root: Path,
    notebook_paths: list[Path],
    project_name: str,
    discovered_dirs: set[Path] | None = None,
) -> None:
    """Write root and per-folder indexes plus a project-structure notebook."""

    output_root = Path(output_root)
    dirs_with_notebooks = {output_root}
    for notebook in notebook_paths:
        directory = output_root / notebook.parent
        while True:
            dirs_with_notebooks.add(directory)
            if directory == output_root:
                break
            directory = directory.parent

    if discovered_dirs:
        for relative_dir in discovered_dirs:
            dirs_with_notebooks.add(output_root / relative_dir)

    root_tree_lines = _build_tree_lines(notebook_paths)
    for directory in sorted(dirs_with_notebooks, key=lambda path: path.as_posix().lower()):
        notebook_entries = sorted(
            path.stem
            for path in notebook_paths
            if (output_root / path).parent == directory
        )
        child_entries = sorted(
            f"{to_posix(child.relative_to(directory))}/index"
            for child in dirs_with_notebooks
            if child.parent == directory and child != directory
        )

        if directory == output_root:
            entries = ["project_structure"] + notebook_entries + child_entries
            structure_notebook = _create_structure_notebook(root_tree_lines)
            structure_path = output_root / "project_structure.ipynb"
            output_root.mkdir(parents=True, exist_ok=True)
            with structure_path.open("w", encoding="utf-8", newline="\n") as handle:
                json.dump(structure_notebook, handle, ensure_ascii=False, indent=2)
                handle.write("\n")
        else:
            entries = notebook_entries + child_entries

        content = _make_index_content(
            _title_for_dir(directory, output_root, project_name),
            entries,
        )
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "index.rst").write_text(content, encoding="utf-8", newline="\n")
