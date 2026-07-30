from __future__ import annotations

import logging
from typing import Any

from .template_models import Template


class TemplateLoader:
    """Loads templates from storage."""

    def __init__(self) -> None:
        self._templates: dict[str, Template] = {}
        self._log = logging.getLogger("superdev.workflow.templates.loader")

    def add(self, template: Template) -> None:
        self._templates[template.id] = template

    def get(self, template_id: str) -> Template | None:
        return self._templates.get(template_id)

    def remove(self, template_id: str) -> None:
        self._templates.pop(template_id, None)
