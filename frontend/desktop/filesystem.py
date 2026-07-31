from __future__ import annotations

import logging
from typing import Any


class DesktopFilesystem:
    """Virtual filesystem access for the desktop surface."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.desktop.filesystem")
        self._open_files: dict[str, dict[str, Any]] = {}
        self._favorites: list[str] = []

    def open_file(self, path: str, content: str = "") -> str:
        handle = f"f{len(self._open_files) + 1}"
        self._open_files[handle] = {"path": path, "content": content, "dirty": False}
        return handle

    def read(self, handle: str) -> str:
        entry = self._open_files.get(handle)
        if entry is None:
            raise KeyError(f"unknown file handle: {handle}")
        return entry["content"]

    def write(self, handle: str, content: str) -> bool:
        entry = self._open_files.get(handle)
        if entry is None:
            return False
        entry["content"] = content
        entry["dirty"] = True
        return True

    def save(self, handle: str) -> bool:
        entry = self._open_files.get(handle)
        if entry is None:
            return False
        entry["dirty"] = False
        return True

    def close(self, handle: str) -> bool:
        return self._open_files.pop(handle, None) is not None

    def add_favorite(self, path: str) -> None:
        if path not in self._favorites:
            self._favorites.append(path)

    def open_files(self) -> list[dict[str, Any]]:
        return [{"handle": handle, **entry} for handle, entry in self._open_files.items()]

    def favorites(self) -> list[str]:
        return list(self._favorites)

    def status(self) -> dict[str, Any]:
        return {"open_files": len(self._open_files), "favorites": len(self._favorites)}
