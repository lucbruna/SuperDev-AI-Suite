"""Kernel health — registered checks with aggregate health status."""
from __future__ import annotations
from typing import Any, Callable

HealthCheck = Callable[[], bool]


class KernelHealth:
    """Runs registered health checks and reports aggregate status."""

    def __init__(self) -> None:
        self._checks: dict[str, HealthCheck] = {}
        self._results: dict[str, dict[str, Any]] = {}

    def register(self, name: str, check: HealthCheck) -> None:
        self._checks[name] = check

    def run(self) -> dict[str, Any]:
        self._results = {}
        for name, check in self._checks.items():
            try:
                ok = bool(check())
                self._results[name] = {"ok": ok, "error": None}
            except Exception as e:  # noqa: BLE001
                self._results[name] = {"ok": False, "error": str(e)}
        failed = [n for n, r in self._results.items() if not r["ok"]]
        return {
            "status": "ok" if not failed else ("degraded" if len(failed) < len(self._checks) else "failed"),
            "total": len(self._results),
            "passed": len(self._results) - len(failed),
            "failed": failed,
            "checks": dict(self._results),
        }


_kernel_health: KernelHealth | None = None


def get_kernel_health() -> KernelHealth:
    global _kernel_health
    if _kernel_health is None:
        _kernel_health = KernelHealth()
    return _kernel_health
