"""Object library — generic 3D object assets."""
from __future__ import annotations

from typing import Any


class ObjectLibrary:
    """Catalogues generic 3D objects with category tags."""

    def __init__(self) -> None:
        self._objects: dict[str, dict[str, Any]] = {}

    def register(self, name: str, *, ref: str, category: str = "prop", scale: float = 1.0) -> None:
        self._objects[name] = {"name": name, "ref": ref, "category": category, "scale": scale}

    def get(self, name: str) -> dict[str, Any] | None:
        return dict(self._objects[name]) if name in self._objects else None

    def by_category(self, category: str) -> list[str]:
        return [name for name, obj in self._objects.items() if obj["category"] == category]

    def names(self) -> list[str]:
        return list(self._objects.keys())
