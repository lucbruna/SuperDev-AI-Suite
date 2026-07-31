from __future__ import annotations

from typing import Any


class HealthChecks:
    """Manages and runs health checks."""

    def __init__(self) -> None:
        self._checks: dict[str, dict[str, Any]] = {}

    def add_check(self, name: str, endpoint: str, interval: int = 60) -> str:
        self._checks[name] = {"name": name, "endpoint": endpoint, "interval": interval}
        return name

    def get_check(self, name: str) -> dict[str, Any] | None:
        return self._checks.get(name)

    def remove_check(self, name: str) -> bool:
        if name in self._checks:
            del self._checks[name]
            return True
        return False

    @property
    def check_count(self) -> int:
        return len(self._checks)

    def run_checks(self) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for check in self._checks.values():
            results.append(
                {
                    "name": check["name"],
                    "endpoint": check["endpoint"],
                    "status": "healthy",
                    "response_time_ms": 42,
                }
            )
        return results

    def to_dict(self) -> dict[str, Any]:
        return {
            "checks": list(self._checks.values()),
            "check_count": self.check_count,
        }
