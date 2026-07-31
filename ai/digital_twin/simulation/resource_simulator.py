"""Resource simulator."""
from __future__ import annotations
from typing import Any, Dict, List

class ResourceSimulator:
    def __init__(self) -> None:
        self._resources: Dict[str, Dict[str, Any]] = {}
        self._history: List[Dict[str, Any]] = []
    def add(self, name: str, capacity: float, unit: str = "units") -> Dict[str, Any]:
        res = {"name": name, "capacity": capacity, "available": capacity, "unit": unit, "allocated": 0}
        self._resources[name] = res
        return res
    def allocate(self, name: str, amount: float) -> Dict[str, Any]:
        if name not in self._resources:
            return {"error": "not_found"}
        res = self._resources[name]
        if amount > res["available"]:
            return {"error": "insufficient", "available": res["available"]}
        res["available"] -= amount
        res["allocated"] += amount
        self._history.append({"resource": name, "action": "allocate", "amount": amount, "available": res["available"]})
        return {"name": name, "allocated": amount, "remaining": res["available"]}
    def release(self, name: str, amount: float) -> Dict[str, Any]:
        if name not in self._resources:
            return {"error": "not_found"}
        res = self._resources[name]
        release_amount = min(amount, res["allocated"])
        res["available"] += release_amount
        res["allocated"] -= release_amount
        self._history.append({"resource": name, "action": "release", "amount": release_amount, "available": res["available"]})
        return {"name": name, "released": release_amount, "available": res["available"]}
    def get_status(self, name: str) -> Dict[str, Any]:
        return self._resources.get(name, {"error": "not_found"})
    def utilization(self, name: str) -> float:
        res = self._resources.get(name, {})
        if not res or res["capacity"] == 0:
            return 0.0
        return res["allocated"] / res["capacity"]
    def list_all(self) -> List[Dict[str, Any]]:
        return list(self._resources.values())
    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._history[-limit:]
    def count(self) -> int:
        return len(self._resources)
