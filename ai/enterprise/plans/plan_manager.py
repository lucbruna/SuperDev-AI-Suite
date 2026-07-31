"""Plan manager."""
from __future__ import annotations
from typing import Any, Dict, List

class PlanManager:
    def __init__(self) -> None:
        self._plans: Dict[str, Dict[str, Any]] = {}
    def add_plan(self, slug: str, name: str, features: List[str], limits: Dict[str, int]) -> Dict[str, Any]:
        plan = {"slug": slug, "name": name, "features": features, "limits": limits}
        self._plans[slug] = plan
        return plan
    def get_plan(self, slug: str) -> Dict[str, Any]:
        return self._plans.get(slug, {})
    def has_feature(self, slug: str, feature: str) -> bool:
        plan = self._plans.get(slug, {})
        return feature in plan.get("features", [])
    def get_limit(self, slug: str, resource: str) -> int:
        plan = self._plans.get(slug, {})
        return plan.get("limits", {}).get(resource, 0)
    def list_plans(self) -> List[Dict[str, Any]]:
        return list(self._plans.values())
    def compare_plans(self, slug1: str, slug2: str) -> Dict[str, Any]:
        p1 = self._plans.get(slug1, {})
        p2 = self._plans.get(slug2, {})
        return {"plan1": p1, "plan2": p2, "features_only_in_1": list(set(p1.get("features", [])) - set(p2.get("features", []))), "features_only_in_2": list(set(p2.get("features", [])) - set(p1.get("features", [])))}
    def remove_plan(self, slug: str) -> bool:
        if slug in self._plans:
            del self._plans[slug]
            return True
        return False
