from __future__ import annotations

from pathlib import Path
from typing import Any


class TemplateLoader:
    """Loads templates from filesystem, strings, or other sources."""

    def __init__(self, directories: list[str] | None = None) -> None:
        self._directories = directories or []

    def load(self, name: str) -> str:
        for d in self._directories:
            p = Path(d) / name
            if p.is_file():
                return p.read_text(encoding="utf-8")
        raise FileNotFoundError(f"Template '{name}' not found")

    def add_directory(self, directory: str) -> None:
        self._directories.append(directory)
