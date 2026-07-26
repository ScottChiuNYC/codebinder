"""Source-tree discovery and filtering."""

from __future__ import annotations

from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path, PurePosixPath

try:  # The package dependency supplies full gitignore semantics.
    import pathspec
except ImportError:  # Keep source checkouts usable before dependencies install.
    pathspec = None  # type: ignore[assignment]


INCLUDED_EXTENSIONS = {
    # Python
    ".py", ".pyi",
    # Markdown and documentation
    ".md", ".markdown", ".txt", ".rst", ".tex",
    # Configuration and structured data
    ".toml", ".json", ".yaml", ".yml", ".ini", ".cfg", ".conf", ".env",
    ".csv", ".tsv",
    # Shell
    ".sh", ".bash", ".zsh", ".fish", ".ps1", ".bat", ".cmd",
    # Web and front-end
    ".html", ".htm", ".css", ".scss", ".sass", ".xhtml", ".xml", ".vue", ".svelte",
    # C and C++
    ".c", ".h", ".cpp", ".cc", ".cxx", ".hpp", ".hxx",
    # Compiled languages
    ".java", ".kt", ".swift", ".go", ".rs", ".cs",
    # Other scripting/build languages
    ".rb", ".php", ".lua", ".pl", ".pm", ".r", ".scala", ".clj", ".cljs",
    ".hs", ".f", ".f90", ".cmake",
}

ASSET_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp", ".pdf"}

IGNORED_DIRS = {
    ".git", ".hg", ".svn", ".venv", "venv", "__pycache__", ".mypy_cache",
    ".pytest_cache", ".ruff_cache", "node_modules",
}


@dataclass(frozen=True)
class DiscoveredFile:
    source_path: Path
    relative_path: Path
    notebook_relative_path: Path


class _SimpleGitIgnoreSpec:
    """Small fallback used only when the optional `pathspec` import is absent."""

    def __init__(self, lines: list[str]) -> None:
        self.patterns = [line.strip() for line in lines if line.strip() and not line.lstrip().startswith("#")]

    def match_file(self, value: str) -> bool:
        ignored = False
        path = value.lstrip("./")
        for raw in self.patterns:
            negated = raw.startswith("!")
            pattern = raw[1:] if negated else raw
            anchored = pattern.startswith("/")
            pattern = pattern.lstrip("/")
            directory_only = pattern.endswith("/")
            pattern = pattern.rstrip("/")
            if not pattern:
                continue

            if directory_only:
                matched = path == pattern or path.startswith(pattern + "/")
            elif "/" in pattern or anchored:
                matched = fnmatch(path, pattern) or PurePosixPath(path).match(pattern)
            else:
                matched = any(fnmatch(part, pattern) for part in PurePosixPath(path).parts)

            if matched:
                ignored = not negated
        return ignored


def should_include(path: Path) -> bool:
    return path.suffix.lower() in INCLUDED_EXTENSIONS


def is_asset(path: Path) -> bool:
    return path.suffix.lower() in ASSET_EXTENSIONS


def _load_gitignore_spec(source_root: Path):
    gitignore_path = source_root / ".gitignore"
    if not gitignore_path.exists():
        return None
    lines = gitignore_path.read_text(encoding="utf-8", errors="replace").splitlines()
    if pathspec is not None:
        return pathspec.PathSpec.from_lines("gitwildmatch", lines)
    return _SimpleGitIgnoreSpec(lines)


def _is_ignored(relative_path: Path, gitignore_spec) -> bool:
    if any(part in IGNORED_DIRS for part in relative_path.parts):
        return True
    return gitignore_spec is not None and gitignore_spec.match_file(relative_path.as_posix())


def discover_files(source_root: Path) -> list[DiscoveredFile]:
    """Return included files in deterministic relative-path order."""

    source_root = Path(source_root)
    gitignore_spec = _load_gitignore_spec(source_root)
    discovered: list[DiscoveredFile] = []

    for path in sorted(source_root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(source_root)
        if _is_ignored(relative, gitignore_spec) or not should_include(path):
            continue
        discovered.append(
            DiscoveredFile(
                source_path=path,
                relative_path=relative,
                notebook_relative_path=relative.with_name(f"{relative.name}.ipynb"),
            )
        )
    return discovered


def discover_assets(source_root: Path) -> list[tuple[Path, Path]]:
    """Return binary assets to copy verbatim beside generated notebooks."""

    source_root = Path(source_root)
    gitignore_spec = _load_gitignore_spec(source_root)
    assets: list[tuple[Path, Path]] = []
    for path in sorted(source_root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(source_root)
        if _is_ignored(relative, gitignore_spec) or not is_asset(path):
            continue
        assets.append((path, relative))
    return assets

