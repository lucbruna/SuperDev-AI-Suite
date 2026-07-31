"""Scaling engine."""

from __future__ import annotations

from typing import Any


class ScalingEngine:
    def __init__(self) -> None:
        self._policies: dict[str, dict[str, Any]] = {}
        self._history: list[dict[str, Any]] = []
        self._started = False

    def start(self) -> None:
        self._started = True

    def create_policy(
        self, name: str, min_replicas: int = 2, max_replicas: int = 10, target_cpu: float = 70.0
    ) -> dict[str, Any]:
        policy = {
            "name": name,
            "min_replicas": min_replicas,
            "max_replicas": max_replicas,
            "target_cpu": target_cpu,
            "enabled": True,
        }
        self._policies[name] = policy
        return policy

    def evaluate(self, policy_name: str, current_replicas: int, current_cpu: float) -> dict[str, Any]:
        if policy_name not in self._policies:
            return {"error": "not_found"}
        policy = self._policies[policy_name]
        if current_cpu > policy["target_cpu"]:
            new_replicas = min(current_replicas + 1, policy["max_replicas"])
            action = "scale_up"
        elif current_cpu < policy["target_cpu"] * 0.5:
            new_replicas = max(current_replicas - 1, policy["min_replicas"])
            action = "scale_down"
        else:
            new_replicas = current_replicas
            action = "maintain"
        result = {
            "policy": policy_name,
            "action": action,
            "from": current_replicas,
            "to": new_replicas,
            "cpu": current_cpu,
        }
        self._history.append(result)
        return result

    def get_policy(self, name: str) -> dict[str, Any]:
        return self._policies.get(name, {"error": "not_found"})

    def list_policies(self) -> list[dict[str, Any]]:
        return list(self._policies.values())

    def get_history(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._history[-limit:]

    def count(self) -> int:
        return len(self._policies)

    def is_running(self) -> bool:
        return self._started
