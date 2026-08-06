"""Deterministic filesystem helpers."""
from __future__ import annotations

import hashlib
import os
import tempfile
from pathlib import Path

__all__ = ["atomic_write", "ensure_dir", "read_text", "safe_join", "sha256_file"]


def ensure_dir(path: str | Path) -> Path:
    """Create ``path`` (and parents) and return it."""
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def atomic_write(path: str | Path, content: str, encoding: str = "utf-8") -> None:
    """Write ``content`` to ``path`` atomically via a temp file + replace."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(target.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding=encoding) as handle:
            handle.write(content)
        os.replace(tmp, target)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def read_text(path: str | Path, default: str | None = None) -> str | None:
    """Read a text file, returning ``default`` when it does not exist."""
    target = Path(path)
    if not target.exists():
        return default
    return target.read_text(encoding="utf-8")


def sha256_file(path: str | Path) -> str:
    """Hex sha256 of the file contents."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def safe_join(root: str | Path, *parts: str) -> Path:
    """Join ``parts`` under ``root``, refusing paths that escape it."""
    base = Path(root).resolve()
    target = base.joinpath(*parts)
    if not target.resolve().is_relative_to(base):
        raise ValueError(f"Path escapes root: {target}")
    return target
