from __future__ import annotations

from typing import Any


class ArchitectureDocs:
    """Generates architecture documentation."""

    def __init__(self) -> None:
        self._components: dict[str, str] = {}
        self._context: dict[str, str] = {}

    def add_component(self, name: str, description: str) -> str:
        self._components[name] = description
        return name

    def get_component(self, name: str) -> str | None:
        return self._components.get(name)

    def remove_component(self, name: str) -> bool:
        if name in self._components:
            del self._components[name]
            return True
        return False

    @property
    def component_count(self) -> int:
        return len(self._components)

    def add_context(self, key: str, value: str) -> str:
        self._context[key] = value
        return key

    def generate(self) -> str:
        lines: list[str] = ["# Architecture Documentation", ""]
        if self._context:
            lines.append("## Context")
            for k, v in self._context.items():
                lines.append(f"- **{k}**: {v}")
            lines.append("")
        if self._components:
            lines.append("## Components")
            for name, desc in self._components.items():
                lines.append(f"### {name}")
                lines.append(desc)
                lines.append("")
        return "\n".join(lines).strip()

    def to_dict(self) -> dict[str, Any]:
        return {
            "components": {k: v for k, v in self._components.items()},
            "context": {k: v for k, v in self._context.items()},
            "component_count": self.component_count,
        }
