"""AI Router - intelligent model selection."""
from __future__ import annotations

import time
from typing import Any


class AIRouter:
    def __init__(self) -> None:
        self._models: dict[str, dict[str, Any]] = {}
        self._routing_rules: dict[str, str] = {}
        self._history: list[dict[str, Any]] = []
        self._started = False
    def start(self) -> None:
        self._started = True
    def stop(self) -> None:
        self._started = False
    def register_model(self, model_id: str, capabilities: list[str], cost_tier: str = "medium") -> None:
        self._models[model_id] = {"capabilities": capabilities, "cost_tier": cost_tier, "status": "active"}
    def add_routing_rule(self, task_type: str, preferred_model: str) -> None:
        self._routing_rules[task_type] = preferred_model
    def route(self, task_type: str, requirements: dict[str, Any] = None) -> str:
        if task_type in self._routing_rules:
            model = self._routing_rules[task_type]
            self._history.append({"task_type": task_type, "model": model, "timestamp": time.time()})
            return model
        for model_id, info in self._models.items():
            if task_type in info["capabilities"] and info["status"] == "active":
                self._history.append({"task_type": task_type, "model": model_id, "timestamp": time.time()})
                return model_id
        return list(self._models.keys())[0] if self._models else ""
    def get_history(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._history[-limit:]
    def list_models(self) -> list[str]:
        return list(self._models.keys())
    def is_running(self) -> bool:
        return self._started
