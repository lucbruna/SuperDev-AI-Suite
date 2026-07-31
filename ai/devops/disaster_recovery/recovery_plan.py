"""Recovery plan."""
from __future__ import annotations
from typing import Any, Dict, List

class RecoveryPlanManager:
    def __init__(self) -> None:
        self._plans: Dict[str, Dict[str, Any]] = {}
    def create(self, name: str, components: List[str], rto_minutes: int = 60, rpo_minutes: int = 15) -> Dict[str, Any]:
        plan = {"name": name, "components": components, "rto_minutes": rto_minutes, "rpo_minutes": rpo_minutes, "status": "active"}
        self._plans[name] = plan
        return plan
    def get(self, name: str) -> Dict[str, Any]:
        return self._plans.get(name, {"error": "not_found"})
    def update(self, name: str, **kwargs: Any) -> bool:
        if name in self._plans:
            self._plans[name].update(kwargs)
            return True
        return False
    def list_all(self) -> List[Dict[str, Any]]:
        return list(self._plans.values())
    def count(self) -> int:
        return len(self._plans)
