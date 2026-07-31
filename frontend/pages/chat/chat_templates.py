from __future__ import annotations

import logging
from typing import Any


class ChatTemplates:
    """Reusable prompt templates."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.chat.templates")
        self._templates: dict[str, dict[str, Any]] = {}

    def render(self) -> dict[str, Any]:
        return {"templates": self.list(), "count": len(self._templates)}

    def list(self) -> list[dict[str, Any]]:
        return [
            {"template_id": template_id, **template}
            for template_id, template in self._templates.items()
        ]

    def apply(self, template_id: str) -> str:
        template = self._templates.get(template_id)
        if template is None:
            raise KeyError(f"unknown template: {template_id}")
        return template["prompt"]

    def save(self, name: str, prompt: str) -> bool:
        template_id = name.lower().replace(" ", "-")
        self._templates[template_id] = {"name": name, "prompt": prompt}
        return True
