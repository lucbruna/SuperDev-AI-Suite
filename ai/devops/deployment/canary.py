"""Canary deployment."""

from __future__ import annotations

from typing import Any


class CanaryDeployer:
    def __init__(self) -> None:
        self._canaries: dict[str, dict[str, Any]] = {}

    def start(self, name: str, current_version: str, canary_version: str, traffic_pct: float = 10.0) -> dict[str, Any]:
        canary = {
            "name": name,
            "current": current_version,
            "canary": canary_version,
            "traffic_pct": traffic_pct,
            "status": "active",
        }
        self._canaries[name] = canary
        return canary

    def increase_traffic(self, name: str, pct: float) -> bool:
        if name in self._canaries:
            self._canaries[name]["traffic_pct"] = min(100.0, self._canaries[name]["traffic_pct"] + pct)
            return True
        return False

    def promote(self, name: str) -> dict[str, Any]:
        if name not in self._canaries:
            return {"error": "not_found"}
        self._canaries[name]["status"] = "promoted"
        return self._canaries[name]

    def rollback(self, name: str) -> bool:
        if name in self._canaries:
            self._canaries[name]["status"] = "rolled_back"
            self._canaries[name]["traffic_pct"] = 0
            return True
        return False

    def list_all(self) -> list[dict[str, Any]]:
        return list(self._canaries.values())

    def count(self) -> int:
        return len(self._canaries)
