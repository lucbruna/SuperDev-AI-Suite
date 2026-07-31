"""Pipeline builder."""

from __future__ import annotations

from typing import Any


class PipelineBuilder:
    def __init__(self) -> None:
        self._templates: dict[str, dict[str, Any]] = {}

    def create_template(self, name: str, stages: list[dict[str, Any]]) -> dict[str, Any]:
        template = {"name": name, "stages": stages}
        self._templates[name] = template
        return template

    def build(self, template_name: str, overrides: dict[str, Any] = None) -> dict[str, Any]:
        template = self._templates.get(template_name, {})
        config = {**template, **(overrides or {})}
        return config

    def list_templates(self) -> list[str]:
        return list(self._templates.keys())

    def get_template(self, name: str) -> dict[str, Any]:
        return self._templates.get(name, {"error": "not_found"})

    def remove_template(self, name: str) -> bool:
        if name in self._templates:
            del self._templates[name]
            return True
        return False

    def count(self) -> int:
        return len(self._templates)
