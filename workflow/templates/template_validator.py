from __future__ import annotations

import re
from typing import Any

from .template_models import Template


class TemplateValidator:
    """Validates template syntax and variables."""

    def __init__(self) -> None:
        self._pattern = re.compile(r"\{\{(\w+)\}\}")

    def validate(self, template: Template) -> bool:
        variables = self._pattern.findall(template.content)
        return all(v in template.variables for v in variables)
