"""Log retention management."""
from __future__ import annotations

import time


class RetentionPolicy:
    def __init__(self, name: str, retention_days: int = 365, max_size_mb: int = 1000) -> None:
        self.name = name
        self.retention_days = retention_days
        self.max_size_mb = max_size_mb

class LogRetention:
    def __init__(self) -> None:
        self._policies: dict[str, RetentionPolicy] = {}
        self._log_sizes: dict[str, int] = {}
        self._log_dates: dict[str, float] = {}
    def add_policy(self, name: str, retention_days: int = 365, max_size_mb: int = 1000) -> RetentionPolicy:
        policy = RetentionPolicy(name, retention_days, max_size_mb)
        self._policies[name] = policy
        return policy
    def register_log(self, log_name: str, size_bytes: int, created_at: float = 0.0) -> None:
        self._log_sizes[log_name] = size_bytes
        self._log_dates[log_name] = created_at or time.time()
    def check_expiry(self, log_name: str) -> bool:
        created = self._log_dates.get(log_name, time.time())
        age_days = (time.time() - created) / 86400
        return any(age_days > policy.retention_days for policy in self._policies.values())
    def get_expired(self) -> list[str]:
        return [name for name in self._log_dates if self.check_expiry(name)]
    def cleanup_expired(self) -> list[str]:
        expired = self.get_expired()
        for name in expired:
            self._log_sizes.pop(name, None)
            self._log_dates.pop(name, None)
        return expired
    def get_total_size_mb(self) -> float:
        return sum(self._log_sizes.values()) / (1024 * 1024)
    def list_policies(self) -> list[str]:
        return list(self._policies.keys())
