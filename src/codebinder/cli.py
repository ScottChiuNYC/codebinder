"""Codebinder command-line interface."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from .discovery import DiscoveredFile, discover_assets, discover_files
from .io_utils import read_text_file
from .notebooks import make_notebook, write_notebook
from .rst import generate_indexes


def _default_output_dir(source_dir: Path) -> Path:
    return Path("C:/Temp") / f"{source_dir.name}_codebinder"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="codebinder",
        description="Mirror a project tree into notebooks and generate Sphinx-compatible RST indexes.",
    )
    parser.add_argument("source", type=Path, help="Source project directory")
    parser.add_argument(
        "output",
        nargs="?",
        type=Path,
        help="Output directory; defaults to C:/Temp/<source>_codebinder",
    )
    return parser


def _resolve_paths(args: argparse.Namespace) -> tuple[Path, Path]:
    source = args.source.expanduser().resolve()
    if not source.exists() or not source.is_dir():
        raise ValueError(f"Source directory not found: {source}")
    output = args.output if args.output is not None else _default_output_dir(source)
    output = output.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    return source, output


def _generate_notebooks(
    discovered: list[DiscoveredFile],
    source_root: Path,
    output_root: Path,
) -> tuple[list[Path], int]:
    del source_root  # Kept in the signature for compatibility with the scanned API.
    written_paths: list[Path] = []
    skipped = 0
    for item in discovered:
        text = read_text_file(item.source_path)
        if text is None:
            skipped += 1
            continue
        notebook = make_notebook(text, item.relative_path.suffix, item.relative_path.name)
        write_notebook(output_root / item.notebook_relative_path, notebook)
        written_paths.append(item.notebook_relative_path)
    return written_paths, skipped


def _copy_assets(source_root: Path, output_root: Path) -> int:
    copied = 0
    for source_path, relative_path in discover_assets(source_root):
        destination = output_root / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, destination)
        copied += 1
    return copied


def run(source: Path | str, output: Path | str) -> int:
    source_path = Path(source).expanduser().resolve()
    output_path = Path(output).expanduser().resolve()
    output_path.mkdir(parents=True, exist_ok=True)

    discovered = discover_files(source_path)
    notebook_paths, skipped_count = _generate_notebooks(discovered, source_path, output_path)
    asset_count = _copy_assets(source_path, output_path)

    discovered_dirs: set[Path] = set()
    for item in discovered:
        current = item.relative_path.parent
        while current != Path(""):
            discovered_dirs.add(current)
            current = current.parent

    generate_indexes(output_path, notebook_paths, source_path.name, discovered_dirs)
    print(f"Generated notebooks: {len(notebook_paths)}")
    print(f"Copied assets: {asset_count}")
    print(f"Skipped unreadable files: {skipped_count}")
    print(f"Output directory: {output_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        source, output = _resolve_paths(args)
    except ValueError as error:
        parser.error(str(error))
    return run(source, output)

