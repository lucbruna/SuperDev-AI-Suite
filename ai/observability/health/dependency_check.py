"""Dependency health checks."""

from __future__ import annotations

from typing import Any


class DependencyCheck:
    def __init__(self) -> None:
        self._dependencies: dict[str, dict[str, Any]] = {}

    def register(self, name: str, version: str = "", required: bool = True) -> None:
        self._dependencies[name] = {"version": version, "required": required}

    def check(self, name: str) -> dict[str, Any]:
        dep = self._dependencies.get(name)
        if not dep:
            return {"dependency": name, "status": "not_registered"}
        return {"dependency": name, "status": "available", "version": dep["version"], "required": dep["required"]}

    def check_all(self) -> list[dict[str, Any]]:
        return [self.check(name) for name in self._dependencies]

    def list_dependencies(self) -> list[str]:
        return list(self._dependencies.keys())

    def remove(self, name: str) -> bool:
        if name in self._dependencies:
            del self._dependencies[name]
            return True
        return False
