"""Cost optimizer for model selection."""
from __future__ import annotations
from typing import Any, Dict, List

class CostOptimizer:
    def __init__(self, budget_limit: float = 1000.0) -> None:
        self._budget = budget_limit
        self._spent: Dict[str, float] = {}
        self._models: Dict[str, float] = {}
    def set_budget(self, limit: float) -> None:
        self._budget = limit
    def set_model_cost(self, model_id: str, cost_per_1k: float) -> None:
        self._models[model_id] = cost_per_1k
    def record_cost(self, model_id: str, amount: float) -> None:
        self._spent[model_id] = self._spent.get(model_id, 0) + amount
    def total_spent(self) -> float:
        return sum(self._spent.values())
    def remaining_budget(self) -> float:
        return max(0, self._budget - self.total_spent())
    def is_within_budget(self) -> bool:
        return self.total_spent() < self._budget
    def recommend_model(self, task_type: str, token_estimate: int = 1000) -> str:
        remaining = self.remaining_budget()
        affordable = []
        for model_id, cost in self._models.items():
            estimated_cost = cost * (token_estimate / 1000)
            if estimated_cost <= remaining:
                affordable.append((model_id, estimated_cost))
        if not affordable:
            return min(self._models.keys(), key=lambda m: self._models[m]) if self._models else ""
        return min(affordable, key=lambda x: x[1])[0]
    def get_spend_by_model(self) -> Dict[str, float]:
        return dict(self._spent)
    def get_budget_status(self) -> Dict[str, Any]:
        return {"budget": self._budget, "spent": self.total_spent(), "remaining": self.remaining_budget(), "percent_used": (self.total_spent() / self._budget * 100) if self._budget > 0 else 0}
    def list_models(self) -> Dict[str, float]:
        return dict(self._models)
