"""File I/O helpers."""

from __future__ import annotations

from pathlib import Path


def read_text_file(path: Path) -> str | None:
    """Read a text file with common encoding fallbacks.

    Return ``None`` when the file looks binary, cannot be read, or cannot be
    decoded with the supported encodings.
    """

    try:
        raw = path.read_bytes()
    except OSError:
        return None

    if b"\x00" in raw:
        return None

    # BOM-aware UTF-8 first so a leading U+FEFF is stripped when present.
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return None


def to_posix(path: Path) -> str:
    """Return a stable POSIX-style path for Sphinx documents."""

    return path.as_posix().replace("\\", "/")

