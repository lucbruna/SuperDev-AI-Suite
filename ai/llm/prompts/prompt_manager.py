from __future__ import annotations

from typing import Any

from .prompt_template import PromptTemplate


class PromptManager:
    """Manages a collection of named prompt templates."""

    def __init__(self) -> None:
        self._templates: dict[str, PromptTemplate] = {}

    def register(self, name: str, template: str | PromptTemplate) -> None:
        if isinstance(template, str):
            template = PromptTemplate(template, name=name)
        self._templates[name] = template

    def get(self, name: str) -> PromptTemplate | None:
        return self._templates.get(name)

    def render(self, template_name: str, **kwargs: Any) -> str:
        template = self.get(template_name)
        if template is None:
            raise KeyError(f"Unknown template: {template_name}")
        return template.render(**kwargs)

    def list_templates(self) -> list[str]:
        return list(self._templates.keys())

    def remove(self, name: str) -> bool:
        if name in self._templates:
            del self._templates[name]
            return True
        return False

    def to_dict(self) -> dict[str, Any]:
        return {
            "template_count": len(self._templates),
            "templates": list(self._templates.keys()),
        }
