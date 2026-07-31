"""Pipeline builder."""
from __future__ import annotations
from typing import Any, Dict, List

class PipelineBuilder:
    def __init__(self) -> None:
        self._templates: Dict[str, Dict[str, Any]] = {}
    def create_template(self, name: str, stages: List[Dict[str, Any]]) -> Dict[str, Any]:
        template = {"name": name, "stages": stages}
        self._templates[name] = template
        return template
    def build(self, template_name: str, overrides: Dict[str, Any] = None) -> Dict[str, Any]:
        template = self._templates.get(template_name, {})
        config = {**template, **(overrides or {})}
        return config
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
