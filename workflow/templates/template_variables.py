from __future__ import annotations

from typing import Any


class TemplateVariables:
    """Manages template variable resolution."""

    def __init__(self, variables: dict[str, Any] | None = None) -> None:
        self._variables: dict[str, Any] = dict(variables or {})

    def set(self, name: str, value: Any) -> None:
        self._variables[name] = value

    def get(self, name: str, default: Any = None) -> Any:
        return self._variables.get(name, default)

    def resolve(self, content: str) -> str:
        for name, value in self._variables.items():
            content = content.replace("{{" + name + "}}", str(value))
        return content

    def to_dict(self) -> dict[str, Any]:
        return dict(self._variables)
