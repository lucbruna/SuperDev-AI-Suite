"""Plan availability."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class PlanAvailability:
    def __init__(self) -> None:
        self._availability: Dict[str, Dict[str, Any]] = {}
    def set_availability(self, plan_id: str, available: bool = True, regions: List[str] = None) -> Dict[str, Any]:
        avail = {"plan_id": plan_id, "available": available, "regions": regions or ["global"], "updated_at": time.time()}
        self._availability[plan_id] = avail
        return avail
    def is_available(self, plan_id: str, region: str = "global") -> bool:
        avail = self._availability.get(plan_id)
        if not avail:
            return True
        return avail["available"] and (region in avail["regions"] or "global" in avail["regions"])
    def get_availability(self, plan_id: str) -> Dict[str, Any]:
        return self._availability.get(plan_id, {"available": True, "regions": ["global"]})
    def list_available(self, region: str = "global") -> List[str]:
        return [pid for pid, a in self._availability.items() if self.is_available(pid, region)]
    def remove(self, plan_id: str) -> bool:
        if plan_id in self._availability:
            del self._availability[plan_id]
            return True
        return False
