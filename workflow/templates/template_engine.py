from __future__ import annotations

import logging
from typing import Any

from .template_models import Template
from .template_loader import TemplateLoader
from .template_renderer import TemplateRenderer
from .template_cache import TemplateCache
from .template_validator import TemplateValidator


class TemplateEngine:
    """Central engine for template management."""

    def __init__(self) -> None:
        self._loader = TemplateLoader()
        self._renderer = TemplateRenderer()
        self._cache = TemplateCache()
        self._validator = TemplateValidator()
        self._log = logging.getLogger("superdev.workflow.templates")

    def render(self, template: Template, variables: dict[str, Any]) -> str:
        if not self._validator.validate(template):
            raise ValueError(f"Template {template.id} validation failed")
        cached = self._cache.get(template.id, variables)
        if cached is not None:
            return cached
        result = self._renderer.render(template.content, variables)
        self._cache.set(template.id, variables, result)
        return result
