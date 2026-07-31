"""DevOps factory."""

from __future__ import annotations

from typing import Any


class DevOpsFactory:
    def __init__(self) -> None:
        self._templates: dict[str, dict[str, Any]] = {}

    def register_template(self, name: str, template: dict[str, Any]) -> dict[str, Any]:
        self._templates[name] = template
        return {"name": name, "registered": True}

    def create(self, template_name: str, overrides: dict[str, Any] = None) -> dict[str, Any]:
        template = self._templates.get(template_name, {})
        resource = {**template, **(overrides or {})}
        resource["template"] = template_name
        return resource

    def list_templates(self) -> List[str]:
        return list(self._templates.keys())

    def get_template(self, name: str) -> dict[str, Any] | None:
        return self._templates.get(name)

    def remove_template(self, name: str) -> bool:
        if name in self._templates:
            del self._templates[name]
            return True
        return False

    def count(self) -> int:
        return len(self._templates)
