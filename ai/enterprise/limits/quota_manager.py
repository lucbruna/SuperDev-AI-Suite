"""Quota manager."""

from __future__ import annotations


class QuotaManager:
    def __init__(self) -> None:
        self._quotas: dict[str, dict[str, float]] = {}
        self._current: dict[str, dict[str, float]] = {}

    def set_quota(self, org_id: str, metric: str, limit: float) -> None:
        self._quotas.setdefault(org_id, {})[metric] = limit

    def get_quota(self, org_id: str, metric: str) -> float:
        return self._quotas.get(org_id, {}).get(metric, 0.0)

    def consume(self, org_id: str, metric: str, amount: float) -> float:
        self._current.setdefault(org_id, {})
        self._current[org_id][metric] = self._current[org_id].get(metric, 0) + amount
        return self._current[org_id][metric]

    def get_consumed(self, org_id: str, metric: str) -> float:
        return self._current.get(org_id, {}).get(metric, 0.0)

    def available(self, org_id: str, metric: str) -> float:
        return max(0, self.get_quota(org_id, metric) - self.get_consumed(org_id, metric))

    def is_exceeded(self, org_id: str, metric: str) -> bool:
        return self.get_consumed(org_id, metric) >= self.get_quota(org_id, metric)

    def percent_used(self, org_id: str, metric: str) -> float:
        quota = self.get_quota(org_id, metric)
        if quota == 0:
            return 0.0
        return (self.get_consumed(org_id, metric) / quota) * 100

    def reset(self, org_id: str, metric: str = "") -> float:
        if metric:
            old = self._current.get(org_id, {}).get(metric, 0)
            self._current.get(org_id, {}).pop(metric, None)
            return old
        return sum(self._current.pop(org_id, {}).values())

    def list_quotas(self, org_id: str) -> dict[str, dict[str, float]]:
        return {"limits": dict(self._quotas.get(org_id, {})), "usage": dict(self._current.get(org_id, {}))}
