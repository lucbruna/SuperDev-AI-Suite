"""Validation rules for workflow templates."""

from __future__ import annotations

import re
from typing import Any

_PLACEHOLDER = re.compile(r"\{\{\s*([A-Za-z_]\w*)\s*\}\}")


class TemplateValidator:
    """Checks that every referenced placeholder is declared."""

    def validate(self, template: Any) -> list[str]:
        issues: list[str] = []
        if not template.template_id:
            issues.append("template_id is required")
        if not template.name:
            issues.append("name is required")
        if not template.steps:
            issues.append("template has no steps")
            return issues
        declared = {p.name for p in template.parameters}
        for step in template.steps:
            if not step.get("stage_id"):
                issues.append("every step must have a stage_id")
            if not step.get("action"):
                issues.append("every step must have an action")
        for placeholder in self._placeholders(template):
            if placeholder not in declared:
                issues.append(
                    f"parameter '{placeholder}' is used but not declared")
        return issues

    def _placeholders(self, template: Any) -> set[str]:
        found: set[str] = set()
        for step in template.steps:
            self._scan(step, found)
        return found

    def _scan(self, value: Any, found: set[str]) -> None:
        if isinstance(value, str):
            for match in _PLACEHOLDER.finditer(value):
                found.add(match.group(1))
        elif isinstance(value, dict):
            for item in value.values():
                self._scan(item, found)
        elif isinstance(value, list):
            for item in value:
                self._scan(item, found)
