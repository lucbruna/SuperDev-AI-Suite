"""Invoice generator."""
from __future__ import annotations

import time
from typing import Any


class InvoiceGenerator:
    def __init__(self) -> None:
        self._templates: dict[str, dict[str, Any]] = {}
        self._generated: list[dict[str, Any]] = []
    def set_template(self, name: str, template: dict[str, Any]) -> None:
        self._templates[name] = template
    def generate(self, template_name: str, data: dict[str, Any]) -> dict[str, Any]:
        template = self._templates.get(template_name, {})
        invoice = {**template, **data, "generated_at": time.time()}
        self._generated.append(invoice)
        return invoice
    def get_template(self, name: str) -> dict[str, Any]:
        return self._templates.get(name, {})
    def list_templates(self) -> list[str]:
        return list(self._templates.keys())
    def list_generated(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._generated[-limit:]
    def remove_template(self, name: str) -> bool:
        if name in self._templates:
            del self._templates[name]
            return True
        return False
