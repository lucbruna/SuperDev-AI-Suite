from __future__ import annotations

from typing import Any, Dict, List


class Protocol:
    """Communication protocol definition."""

    def __init__(self, name: str, version: str = "1.0") -> None:
        self._name = name
        self._version = version
        self._rules: Dict[str, Any] = {}

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> str:
        return self._version

    def add_rule(self, key: str, value: Any) -> None:
        self._rules[key] = value

    def get_rule(self, key: str) -> Any:
        return self._rules.get(key)

    def validate(self, message: Dict[str, Any]) -> bool:
        return "sender" in message and "content" in message

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self._name, "version": self._version, "rules": dict(self._rules)}
