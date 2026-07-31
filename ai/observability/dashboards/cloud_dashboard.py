"""Cloud dashboard."""
from __future__ import annotations
from typing import Any, Dict, List

class CloudDashboard:
    def __init__(self) -> None:
        self._resources: Dict[str, Dict[str, Any]] = {}
        self._costs: Dict[str, float] = {}
    def update_resource(self, resource_id: str, data: Dict[str, Any]) -> None:
        self._resources[resource_id] = data
    def update_cost(self, service: str, cost: float) -> None:
        self._costs[service] = cost
    def get_resources(self) -> List[Dict[str, Any]]:
        return [{"id": k, **v} for k, v in self._resources.items()]
    def get_total_cost(self) -> float:
        return sum(self._costs.values())
    def get_cost_breakdown(self) -> Dict[str, float]:
        return dict(self._costs)
    def get_summary(self) -> Dict[str, Any]:
        return {"resources": len(self._resources), "total_cost": self.get_total_cost()}
