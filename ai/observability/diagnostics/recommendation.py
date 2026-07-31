"""Recommendation engine."""
from __future__ import annotations
from typing import Any, Dict, List

class RecommendationEngine:
    def __init__(self) -> None:
        self._templates: Dict[str, List[str]] = {}
    def add_template(self, category: str, recommendations: List[str]) -> None:
        self._templates[category] = recommendations
    def get_recommendations(self, category: str, context: Dict[str, Any]) -> List[str]:
        base = self._templates.get(category, [])
        context_recs = []
        if "error_type" in context:
            context_recs.append(f"Address {context['error_type']} error specifically")
        if "component" in context:
            context_recs.append(f"Focus on {context['component']} component")
        return base + context_recs
    def list_categories(self) -> List[str]:
        return list(self._templates.keys())
    def remove_template(self, category: str) -> bool:
        if category in self._templates:
            del self._templates[category]
            return True
        return False
