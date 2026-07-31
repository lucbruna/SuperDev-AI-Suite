from __future__ import annotations

import logging
from typing import Any


class ProjectWizard:
    """Multi-step project creation wizard."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.project.wizard")
        self._steps = ["basics", "agents", "workflows", "review"]

    def render(self) -> dict[str, Any]:
        return {"steps": self._steps, "count": len(self._steps)}

    def validate(self, step: int, data: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        if step == 0 and not data.get("name"):
            errors.append("project name is required")
        return errors

    def complete(self, data: dict[str, Any]) -> str:
        errors = self.validate(0, data)
        if errors:
            raise ValueError("; ".join(errors))
        return f"project-{data.get('name', 'new').lower().replace(' ', '-')}"
