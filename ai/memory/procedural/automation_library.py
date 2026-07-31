from __future__ import annotations

from typing import Any


class AutomationScript:
    """A stored automation script."""

    def __init__(self, script_id: str, name: str, source: str, language: str = "python", description: str = ""):
        self._script_id = script_id
        self._name = name
        self._source = source
        self._language = language
        self._description = description

    @property
    def script_id(self) -> str:
        return self._script_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def source(self) -> str:
        return self._source

    @property
    def language(self) -> str:
        return self._language

    @property
    def description(self) -> str:
        return self._description

    def to_dict(self) -> dict[str, Any]:
        return {
            "script_id": self._script_id,
            "name": self._name,
            "language": self._language,
            "description": self._description,
        }


class AutomationLibrary:
    """Library of automation scripts."""

    def __init__(self):
        self._scripts: dict[str, AutomationScript] = {}

    @property
    def count(self) -> int:
        return len(self._scripts)

    def add(self, script: AutomationScript) -> None:
        self._scripts[script.script_id] = script

    def get(self, script_id: str) -> AutomationScript | None:
        return self._scripts.get(script_id)

    def get_by_language(self, language: str) -> list[AutomationScript]:
        return [s for s in self._scripts.values() if s.language == language]

    def search(self, query: str) -> list[AutomationScript]:
        q = query.lower()
        return [s for s in self._scripts.values() if q in s.name.lower() or q in s.description.lower()]

    def remove(self, script_id: str) -> bool:
        return self._scripts.pop(script_id, None) is not None

    def clear(self) -> None:
        self._scripts.clear()
