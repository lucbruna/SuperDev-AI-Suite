"""Scenario templates."""

from __future__ import annotations

from typing import Any


class ScenarioTemplates:
    def __init__(self) -> None:
        self._templates: dict[str, dict[str, Any]] = {
            "price_change": {
                "name": "Price Change",
                "parameters": {"price_delta": 0.0, "product": ""},
                "expected_metrics": ["revenue", "margin", "volume"],
            },
            "expansion": {
                "name": "Market Expansion",
                "parameters": {"location": "", "investment": 0},
                "expected_metrics": ["growth", "risk", "roi"],
            },
            "cost_reduction": {
                "name": "Cost Reduction",
                "parameters": {"target_area": "", "reduction_pct": 0.0},
                "expected_metrics": ["savings", "impact", "efficiency"],
            },
            "new_product": {
                "name": "New Product Launch",
                "parameters": {"product_name": "", "budget": 0},
                "expected_metrics": ["adoption", "revenue", "market_share"],
            },
        }

    def get(self, template_name: str) -> dict[str, Any]:
        return self._templates.get(template_name, {"error": "not_found"})

    def create(self, name: str, parameters: dict[str, Any], expected_metrics: list[str] = None) -> dict[str, Any]:
        template = {"name": name, "parameters": parameters, "expected_metrics": expected_metrics or []}
        self._templates[name] = template
        return template

    def list_all(self) -> list[str]:
        return list(self._templates.keys())

    def delete(self, name: str) -> bool:
        if name in self._templates:
            del self._templates[name]
            return True
        return False

    def count(self) -> int:
        return len(self._templates)
