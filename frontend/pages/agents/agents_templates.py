from __future__ import annotations

import logging
from typing import Any


class AgentsTemplates:
    """Reusable agent configuration templates."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.agents.templates")
        self._templates: dict[str, dict[str, Any]] = {}

    def render(self) -> dict[str, Any]:
        return {"templates": self.list(), "count": len(self._templates)}

    def list(self) -> list[dict[str, Any]]:
        return [
            {"template_id": template_id, **template}
            for template_id, template in self._templates.items()
        ]

    def save(self, name: str, config: dict[str, Any]) -> bool:
        template_id = name.lower().replace(" ", "-")
        self._templates[template_id] = {"name": name, "config": config}
        return True

    def delete(self, template_id: str) -> bool:
        return self._templates.pop(template_id, None) is not None
