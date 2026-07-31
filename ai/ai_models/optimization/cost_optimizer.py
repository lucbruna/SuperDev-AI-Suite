"""Cost optimization."""
from __future__ import annotations
from typing import Any, Dict, List

class CostOptimizer:
    def __init__(self) -> None:
        self._prices: Dict[str, Dict[str, float]] = {}
        self._usage: List[Dict[str, Any]] = []
    def set_price(self, model: str, input_per_1k: float, output_per_1k: float) -> Dict[str, Any]:
        self._prices[model] = {"input_per_1k": input_per_1k, "output_per_1k": output_per_1k}
        return {"model": model, "set": True}
    def estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        prices = self._prices.get(model, {"input_per_1k": 0.01, "output_per_1k": 0.03})
        return (input_tokens / 1000 * prices["input_per_1k"]) + (output_tokens / 1000 * prices["output_per_1k"])
    def log_usage(self, model: str, input_tokens: int, output_tokens: int, task: str = "") -> Dict[str, Any]:
        cost = self.estimate_cost(model, input_tokens, output_tokens)
        entry = {"model": model, "input_tokens": input_tokens, "output_tokens": output_tokens, "cost": cost, "task": task}
        self._usage.append(entry)
        return entry
    def total_cost(self) -> float:
        return sum(u["cost"] for u in self._usage)
    def cost_by_model(self) -> Dict[str, float]:
        costs = {}
        for u in self._usage:
            costs[u["model"]] = costs.get(u["model"], 0) + u["cost"]
        return costs
    def cheapest_model(self, input_tokens: int, output_tokens: int) -> str:
        best = ""
        best_cost = float("inf")
        for model in self._prices:
            cost = self.estimate_cost(model, input_tokens, output_tokens)
            if cost < best_cost:
                best_cost = cost
                best = model
        return best
    def get_usage(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._usage[-limit:]
    def count(self) -> int:
        return len(self._usage)
