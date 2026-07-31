"""Recommendation engine."""

from __future__ import annotations

from typing import Any


class RecommendationEngine:
    def __init__(self) -> None:
        self._templates: dict[str, list[str]] = {}

    def add_template(self, category: str, recommendations: list[str]) -> None:
        self._templates[category] = recommendations

    def get_recommendations(self, category: str, context: dict[str, Any]) -> list[str]:
        base = self._templates.get(category, [])
        context_recs = []
        if "error_type" in context:
            context_recs.append(f"Address {context['error_type']} error specifically")
        if "component" in context:
            context_recs.append(f"Focus on {context['component']} component")
        return base + context_recs

    def list_categories(self) -> list[str]:
        return list(self._templates.keys())

    def remove_template(self, category: str) -> bool:
        if category in self._templates:
            del self._templates[category]
            return True
        return False
