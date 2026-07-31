"""Model selector."""
from __future__ import annotations
from typing import Any, Dict, List

class ModelSelector:
    def __init__(self) -> None:
        self._models: Dict[str, Dict[str, Any]] = {}
    def add_model(self, model_id: str, capabilities: List[str], cost_per_1k: float = 0.01, quality_score: float = 0.8, latency_ms: float = 1000) -> None:
        self._models[model_id] = {"capabilities": capabilities, "cost": cost_per_1k, "quality": quality_score, "latency": latency_ms}
    def select(self, task_type: str, priority: str = "quality") -> str:
        candidates = [mid for mid, info in self._models.items() if task_type in info["capabilities"]]
        if not candidates:
            return list(self._models.keys())[0] if self._models else ""
        if priority == "cost":
            return min(candidates, key=lambda m: self._models[m]["cost"])
        if priority == "latency":
            return min(candidates, key=lambda m: self._models[m]["latency"])
        return max(candidates, key=lambda m: self._models[m]["quality"])
    def score_models(self, task_type: str) -> List[Dict[str, Any]]:
        scored = []
        for mid, info in self._models.items():
            if task_type in info["capabilities"]:
                score = info["quality"] * 0.5 + (1 - min(info["cost"], 1)) * 0.3 + (1 - min(info["latency"] / 5000, 1)) * 0.2
                scored.append({"model_id": mid, "score": score, **info})
        return sorted(scored, key=lambda x: x["score"], reverse=True)
    def list_models(self) -> List[Dict[str, Any]]:
        return [{"id": k, **v} for k, v in self._models.items()]
    def remove_model(self, model_id: str) -> bool:
        if model_id in self._models:
            del self._models[model_id]
            return True
        return False
