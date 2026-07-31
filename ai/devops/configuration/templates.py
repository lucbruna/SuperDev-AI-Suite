"""Config templates."""
from __future__ import annotations
from typing import Any, Dict, List

class ConfigTemplates:
    def __init__(self) -> None:
        self._templates: Dict[str, Dict[str, Any]] = {}
    def create(self, name: str, config: Dict[str, Any], description: str = "") -> Dict[str, Any]:
        template = {"name": name, "config": config, "description": description}
        self._templates[name] = template
        return template
    def get(self, name: str) -> Dict[str, Any]:
        return self._templates.get(name, {"error": "not_found"})
    def apply(self, template_name: str, overrides: Dict[str, Any] = None) -> Dict[str, Any]:
        template = self._templates.get(template_name, {})
        config = {**template.get("config", {}), **(overrides or {})}
        return config
    def list_all(self) -> List[Dict[str, Any]]:
        return list(self._templates.values())
    def delete(self, name: str) -> bool:
        if name in self._templates:
            del self._templates[name]
            return True
        return False
    def count(self) -> int:
        return len(self._templates)
