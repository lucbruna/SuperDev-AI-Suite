"""Usage tracker."""
from __future__ import annotations


class UsageTracker:
    def __init__(self) -> None:
        self._tracking: dict[str, dict[str, float]] = {}
    def track(self, org_id: str, metric: str, value: float) -> None:
        self._tracking.setdefault(org_id, {})
        self._tracking[org_id][metric] = self._tracking[org_id].get(metric, 0) + value
    def get(self, org_id: str, metric: str) -> float:
        return self._tracking.get(org_id, {}).get(metric, 0.0)
    def get_all(self, org_id: str) -> dict[str, float]:
        return dict(self._tracking.get(org_id, {}))
    def reset(self, org_id: str, metric: str = "") -> float:
        if metric:
            old = self._tracking.get(org_id, {}).get(metric, 0)
            self._tracking.get(org_id, {}).pop(metric, None)
            return old
        org_data = self._tracking.pop(org_id, {})
        return sum(org_data.values())
    def list_orgs(self) -> list:
        return list(self._tracking.keys())
    def top_users(self, metric: str, limit: int = 10) -> list:
        usage = [(org, data.get(metric, 0)) for org, data in self._tracking.items()]
        return sorted(usage, key=lambda x: x[1], reverse=True)[:limit]
