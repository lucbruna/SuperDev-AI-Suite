"""Usage quota."""

from __future__ import annotations


class UsageQuota:
    def __init__(self) -> None:
        self._quotas: dict[str, dict[str, float]] = {}
        self._usage: dict[str, dict[str, float]] = {}

    def set_quota(self, org_id: str, metric: str, limit: float) -> None:
        self._quotas.setdefault(org_id, {})[metric] = limit

    def get_quota(self, org_id: str, metric: str) -> float:
        return self._quotas.get(org_id, {}).get(metric, float("inf"))

    def record_usage(self, org_id: str, metric: str, amount: float) -> float:
        self._usage.setdefault(org_id, {})
        self._usage[org_id][metric] = self._usage[org_id].get(metric, 0) + amount
        return self._usage[org_id][metric]

    def get_usage(self, org_id: str, metric: str) -> float:
        return self._usage.get(org_id, {}).get(metric, 0.0)

    def remaining(self, org_id: str, metric: str) -> float:
        quota = self.get_quota(org_id, metric)
        usage = self.get_usage(org_id, metric)
        return max(0, quota - usage)

    def is_over_quota(self, org_id: str, metric: str) -> bool:
        return self.get_usage(org_id, metric) > self.get_quota(org_id, metric)

    def usage_percent(self, org_id: str, metric: str) -> float:
        quota = self.get_quota(org_id, metric)
        if quota == 0 or quota == float("inf"):
            return 0.0
        return (self.get_usage(org_id, metric) / quota) * 100

    def list_quotas(self, org_id: str) -> dict[str, float]:
        return dict(self._quotas.get(org_id, {}))

    def reset(self, org_id: str, metric: str = "") -> float:
        if metric:
            old = self._usage.get(org_id, {}).get(metric, 0)
            self._usage.get(org_id, {}).pop(metric, None)
            return old
        return sum(self._usage.pop(org_id, {}).values())
