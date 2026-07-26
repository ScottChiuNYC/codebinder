"""Notebook construction helpers."""

from __future__ import annotations

import copy
import json
from pathlib import Path


LANGUAGE_BY_EXT: dict[str, str] = {
    ".py": "python", ".pyi": "python", ".cpp": "cpp", ".cc": "cpp", ".cxx": "cpp",
    ".c": "c", ".h": "c", ".hpp": "cpp", ".hxx": "cpp", ".java": "java",
    ".go": "go", ".rs": "rust", ".cs": "csharp", ".js": "javascript",
    ".ts": "typescript", ".html": "html", ".css": "css", ".scss": "scss",
    ".sh": "bash", ".bash": "bash", ".zsh": "bash", ".fish": "fish",
    ".ps1": "powershell", ".bat": "batch", ".cmd": "batch", ".json": "json",
    ".yaml": "yaml", ".yml": "yaml", ".toml": "toml", ".xml": "xml",
    ".rst": "rst", ".tex": "latex", ".sql": "sql", ".rb": "ruby",
    ".php": "php", ".lua": "lua", ".pl": "perl", ".r": "r",
}


def _load_template() -> dict:
    template_path = Path(__file__).parent / "templates" / "notebook_template.ipynb"
    return json.loads(template_path.read_text(encoding="utf-8"))


def _demote_markdown_headings(text: str) -> str:
    """Demote ATX Markdown headings by one level."""

    demoted_lines: list[str] = []
    for line in text.splitlines(keepends=True):
        stripped = line.lstrip()
        if stripped.startswith("#") and (len(stripped) == 1 or stripped[1] in "# "):
            indentation = line[: len(line) - len(stripped)]
            demoted_lines.append(indentation + "#" + stripped)
        else:
            demoted_lines.append(line)
    return "".join(demoted_lines)


def _make_markdown_source(text: str) -> list[str]:
    return _demote_markdown_headings(text).splitlines(keepends=True)


def _make_code_fence_source(text: str, language: str) -> list[str]:
    source: list[str] = [f"```{language}\n"]
    source.extend(f"{line}\n" for line in text.splitlines())
    source.append("```")
    return source


def make_notebook(text: str, extension: str, title: str) -> dict:
    """Build a two-cell Markdown notebook from the shared template."""

    notebook = copy.deepcopy(_load_template())
    notebook["cells"][0]["source"] = [f"# `{title}`"]
    if extension.lower() in {".md", ".markdown"}:
        notebook["cells"][1]["source"] = _make_markdown_source(text)
    else:
        language = LANGUAGE_BY_EXT.get(extension.lower(), extension.lstrip(".") or "text")
        notebook["cells"][1]["source"] = _make_code_fence_source(text, language)
    return notebook


def write_notebook(path: Path, notebook: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(notebook, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

