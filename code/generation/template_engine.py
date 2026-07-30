from __future__ import annotations

import logging
from typing import Any


class TemplateEngine:
    """Renders code templates with variable substitution."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.generation.template")

    def render(self, template: str, variables: dict[str, Any]) -> str:
        return template.format(**variables)
