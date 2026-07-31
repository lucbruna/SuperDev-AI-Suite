"""Scenario builder."""
from __future__ import annotations
from typing import Any, Dict, List

class ScenarioBuilder:
    def __init__(self) -> None:
        self._templates: Dict[str, Dict[str, Any]] = {}
    def create_template(self, name: str, base_parameters: Dict[str, Any], variations: Dict[str, Any] = None) -> Dict[str, Any]:
        template = {"name": name, "base": base_parameters, "variations": variations or {}}
        self._templates[name] = template
        return template
    def build(self, template_name: str, overrides: Dict[str, Any] = None) -> Dict[str, Any]:
        template = self._templates.get(template_name, {})
        params = {**template.get("base", {}), **(overrides or {})}
        return {"template": template_name, "parameters": params}
    def build_variations(self, template_name: str, variation_name: str) -> Dict[str, Any]:
        template = self._templates.get(template_name, {})
        variation = template.get("variations", {}).get(variation_name, {})
        params = {**template.get("base", {}), **variation}
        return {"template": template_name, "variation": variation_name, "parameters": params}
    def list_templates(self) -> List[str]:
        return list(self._templates.keys())
    def get_template(self, name: str) -> Dict[str, Any]:
        return self._templates.get(name, {"error": "not_found"})
    def remove_template(self, name: str) -> bool:
        if name in self._templates:
            del self._templates[name]
            return True
        return False
    def count(self) -> int:
        return len(self._templates)
