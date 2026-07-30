from __future__ import annotations

from typing import Any


class HelmGenerator:
    """Generates Helm chart configurations."""

    def __init__(self) -> None:
        self._templates: dict[str, str] = {}
        self._values: dict[str, Any] = {}

    def add_template(self, name: str, content: str) -> str:
        self._templates[name] = content
        return name

    def get_template(self, name: str) -> str | None:
        return self._templates.get(name)

    @property
    def template_count(self) -> int:
        return len(self._templates)

    def set_value(self, key: str, value: Any) -> str:
        self._values[key] = value
        return key

    def generate(self) -> str:
        lines: list[str] = ["# Helm Chart", ""]
        lines.append("## Values")
        for k, v in self._values.items():
            lines.append(f"{k}: {v}")
        lines.append("")
        lines.append("## Templates")
        for name in self._templates:
            lines.append(f"- {name}")
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        return {
            "templates": {k: v for k, v in self._templates.items()},
            "values": {k: v for k, v in self._values.items()},
            "template_count": self.template_count,
        }
