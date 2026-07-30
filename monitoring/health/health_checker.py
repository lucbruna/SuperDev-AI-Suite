from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable

from ..monitoring_models import HealthCheckResult, HealthStatus


@dataclass
class HealthCheckerConfig:
    timeout: float = 5.0
    interval: float = 30.0
    failure_threshold: int = 3
    recovery_threshold: int = 2


class HealthChecker:
    """Runs health checks on registered components."""

    def __init__(self, config: HealthCheckerConfig | None = None) -> None:
        self._config = config or HealthCheckerConfig()
        self._checks: dict[str, Callable[[], HealthCheckResult]] = {}
        self._results: dict[str, HealthCheckResult] = {}
        self._consecutive_failures: dict[str, int] = {}
        self._consecutive_successes: dict[str, int] = {}
        self._callbacks: list[Callable[[str, HealthStatus], None]] = []

    def register(self, name: str, check: Callable[[], HealthCheckResult]) -> None:
        self._checks[name] = check

    def unregister(self, name: str) -> None:
        self._checks.pop(name, None)
        self._results.pop(name, None)
        self._consecutive_failures.pop(name, None)
        self._consecutive_successes.pop(name, None)

    def check(self, name: str) -> HealthCheckResult | None:
        check_fn = self._checks.get(name)
        if not check_fn:
            return None
        return self._run_check(name, check_fn)

    def check_all(self) -> list[HealthCheckResult]:
        results: list[HealthCheckResult] = []
        for name, check_fn in self._checks.items():
            result = self._run_check(name, check_fn)
            results.append(result)
        return results

    def _run_check(self, name: str, check_fn: Callable[[], HealthCheckResult]) -> HealthCheckResult:
        start = time.perf_counter()
        try:
            result = check_fn()
        except Exception as e:
            result = HealthCheckResult(
                component=name,
                status=HealthStatus.UNHEALTHY,
                message=str(e),
            )
        result.latency_ms = (time.perf_counter() - start) * 1000

        prev_status = self._results.get(name)
        prev = prev_status.status if prev_status else None

        if result.status == HealthStatus.HEALTHY:
            self._consecutive_successes[name] = self._consecutive_successes.get(name, 0) + 1
            self._consecutive_failures[name] = 0
            if self._consecutive_successes[name] >= self._config.recovery_threshold:
                result.status = HealthStatus.HEALTHY
        else:
            self._consecutive_failures[name] = self._consecutive_failures.get(name, 0) + 1
            self._consecutive_successes[name] = 0
            if self._consecutive_failures[name] >= self._config.failure_threshold:
                result.status = HealthStatus.UNHEALTHY
            else:
                result.status = HealthStatus.DEGRADED

        self._results[name] = result

        if prev is not None and prev != result.status:
            self._notify(name, result.status)

        return result

    def get_result(self, name: str) -> HealthCheckResult | None:
        return self._results.get(name)

    def get_all_results(self) -> dict[str, HealthCheckResult]:
        return dict(self._results)

    def on_status_change(self, callback: Callable[[str, HealthStatus], None]) -> None:
        self._callbacks.append(callback)

    def _notify(self, name: str, status: HealthStatus) -> None:
        for cb in self._callbacks:
            try:
                cb(name, status)
            except Exception:
                pass

    def summary(self) -> dict[str, Any]:
        results = self.get_all_results()
        healthy = sum(1 for r in results.values() if r.status == HealthStatus.HEALTHY)
        degraded = sum(1 for r in results.values() if r.status == HealthStatus.DEGRADED)
        unhealthy = sum(1 for r in results.values() if r.status == HealthStatus.UNHEALTHY)
        return {
            "total": len(results),
            "healthy": healthy,
            "degraded": degraded,
            "unhealthy": unhealthy,
            "uptime_pct": round(healthy / max(len(results), 1) * 100, 1),
        }
