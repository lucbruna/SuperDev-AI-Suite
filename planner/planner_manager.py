from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


class PlannerManager:
    """Manages plan lifecycle: creation, storage, retrieval."""

    def __init__(self):
        self._plans: dict[str, Any] = {}
        self._plan_index: dict[str, list[str]] = {}

    def register_plan(self, plan: Any) -> str:
        plan_id = getattr(plan, "id", str(len(self._plans) + 1))
        self._plans[plan_id] = plan
        category = getattr(plan, "category", "general")
        if category not in self._plan_index:
            self._plan_index[category] = []
        self._plan_index[category].append(plan_id)
        return plan_id

    def get_plan(self, plan_id: str) -> Any | None:
        return self._plans.get(plan_id)

    def update_plan(self, plan_id: str, updates: dict[str, Any]) -> Any | None:
        plan = self._plans.get(plan_id)
        if plan:
            for key, value in updates.items():
                setattr(plan, key, value)
        return plan

    def delete_plan(self, plan_id: str) -> None:
        self._plans.pop(plan_id, None)
        for category, ids in self._plan_index.items():
            if plan_id in ids:
                ids.remove(plan_id)

    def list_plans(self, category: str | None = None) -> list[Any]:
        if category:
            return [self._plans[pid] for pid in self._plan_index.get(category, []) if pid in self._plans]
        return list(self._plans.values())

    def count(self) -> int:
        return len(self._plans)
