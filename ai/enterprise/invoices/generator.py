"""Invoice generator."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class InvoiceGenerator:
    def __init__(self) -> None:
        self._templates: Dict[str, Dict[str, Any]] = {}
        self._generated: List[Dict[str, Any]] = []
    def set_template(self, name: str, template: Dict[str, Any]) -> None:
        self._templates[name] = template
    def generate(self, template_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        template = self._templates.get(template_name, {})
        invoice = {**template, **data, "generated_at": time.time()}
        self._generated.append(invoice)
        return invoice
    def get_template(self, name: str) -> Dict[str, Any]:
        return self._templates.get(name, {})
    def list_templates(self) -> List[str]:
        return list(self._templates.keys())
    def list_generated(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._generated[-limit:]
    def remove_template(self, name: str) -> bool:
        if name in self._templates:
            del self._templates[name]
            return True
        return False
