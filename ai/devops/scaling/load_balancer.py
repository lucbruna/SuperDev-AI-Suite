"""Load balancer."""

from __future__ import annotations

from typing import Any


class LoadBalancer:
    def __init__(self) -> None:
        self._targets: dict[str, list[dict[str, Any]]] = {}
        self._connections: dict[str, int] = {}

    def add_target(self, pool: str, target: str, weight: int = 1) -> bool:
        self._targets.setdefault(pool, []).append({"target": target, "weight": weight, "healthy": True})
        return True

    def remove_target(self, pool: str, target: str) -> bool:
        if pool in self._targets:
            self._targets[pool] = [t for t in self._targets[pool] if t["target"] != target]
            return True
        return False

    def route(self, pool: str) -> dict[str, Any]:
        targets = self._targets.get(pool, [])
        healthy = [t for t in targets if t["healthy"]]
        if not healthy:
            return {"error": "no_healthy_targets"}
        target = min(healthy, key=lambda t: self._connections.get(t["target"], 0))
        self._connections[target["target"]] = self._connections.get(target["target"], 0) + 1
        return {"target": target["target"], "pool": pool}

    def health_check(self, pool: str, target: str, healthy: bool) -> bool:
        if pool in self._targets:
            for t in self._targets[pool]:
                if t["target"] == target:
                    t["healthy"] = healthy
                    return True
        return False

    def list_pools(self) -> list[str]:
        return list(self._targets.keys())

    def list_targets(self, pool: str) -> list[dict[str, Any]]:
        return self._targets.get(pool, [])

    def count(self) -> int:
        return sum(len(v) for v in self._targets.values())
