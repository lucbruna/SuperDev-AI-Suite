from __future__ import annotations

import logging
from typing import Any

from ...frontend_context import FrontendContext


class AgentsBuilder:
    """Guides building a new agent from templates."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.agents.builder")
        self._templates: list[dict[str, Any]] = [
            {"template_id": "coder", "name": "Code Agent", "type": "coder"},
            {"template_id": "reviewer", "name": "Code Reviewer", "type": "reviewer"},
            {"template_id": "researcher", "name": "Researcher", "type": "researcher"},
            {"template_id": "tester", "name": "Test Runner", "type": "tester"},
        ]

    def render(self) -> dict[str, Any]:
        return {"templates": self.templates(), "count": len(self._templates)}

    def templates(self) -> list[dict[str, Any]]:
        return list(self._templates)

    def validate(self, config: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        if not config.get("name"):
            errors.append("name is required")
        if not config.get("type"):
            errors.append("type is required")
        return errors

    def create(self, config: dict[str, Any]) -> str:
        errors = self.validate(config)
        if errors:
            raise ValueError("; ".join(errors))
        return f"agent-{config['name'].lower().replace(' ', '-')}"
