"""Variable manager."""

from __future__ import annotations

from typing import Any


class VariableManager:
    def __init__(self) -> None:
        self._variables: dict[str, dict[str, Any]] = {}

    def set(self, name: str, value: Any, var_type: str = "string", secret: bool = False) -> dict[str, Any]:
        var = {"name": name, "value": value, "type": var_type, "secret": secret}
        self._variables[name] = var
        return var

    def get(self, name: str) -> Any:
        return self._variables.get(name, {}).get("value")

    def delete(self, name: str) -> bool:
        if name in self._variables:
            del self._variables[name]
            return True
        return False

    def list_all(self) -> list[dict[str, Any]]:
        return list(self._variables.values())

    def list_secrets(self) -> list[dict[str, Any]]:
        return [v for v in self._variables.values() if v.get("secret")]

    def count(self) -> int:
        return len(self._variables)
