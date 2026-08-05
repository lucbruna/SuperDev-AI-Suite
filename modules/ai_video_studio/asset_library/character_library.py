"""Character library — reusable character assets and rigs."""
from __future__ import annotations

from typing import Any


class CharacterLibrary:
    """Stores character models, rigs and motion config references."""

    def __init__(self) -> None:
        self._characters: dict[str, dict[str, Any]] = {}

    def register(
        self,
        name: str,
        *,
        model_ref: str,
        rig_ref: str | None = None,
        style: str = "stylized",
    ) -> None:
        self._characters[name] = {
            "name": name,
            "model_ref": model_ref,
            "rig_ref": rig_ref,
            "style": style,
        }

    def get(self, name: str) -> dict[str, Any] | None:
        return dict(self._characters[name]) if name in self._characters else None

    def names(self) -> list[str]:
        return list(self._characters.keys())
