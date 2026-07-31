"""Plan comparison."""
from __future__ import annotations

from typing import Any


class PlanComparison:
    def __init__(self) -> None:
        self._plans: dict[str, dict[str, Any]] = {}
    def add_plan(self, plan_id: str, name: str, price: float, features: list[str], limits: dict[str, int]) -> None:
        self._plans[plan_id] = {"name": name, "price": price, "features": features, "limits": limits}
    def compare(self, plan_ids: list[str]) -> dict[str, Any]:
        plans = {pid: self._plans.get(pid, {}) for pid in plan_ids if pid in self._plans}
        return {"plans": plans, "feature_matrix": {pid: p.get("features", []) for pid, p in plans.items()}, "price_comparison": {pid: p.get("price", 0) for pid, p in plans.items()}}
    def recommend(self, features_needed: list[str]) -> str:
        best_plan = ""
        best_score = -1
        for pid, plan in self._plans.items():
            plan_features = set(plan.get("features", []))
            score = len(set(features_needed) & plan_features)
            if score > best_score:
                best_score = score
                best_plan = pid
        return best_plan
    def list_plans(self) -> list[dict[str, Any]]:
        return [{"id": k, **v} for k, v in self._plans.items()]
    def remove_plan(self, plan_id: str) -> bool:
        if plan_id in self._plans:
            del self._plans[plan_id]
            return True
        return False
