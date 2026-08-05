"""HealthCheck: deterministic component health probes."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

#: probe: () -> bool
Probe = Callable[[], bool]


@dataclass
class HealthStatus:
    name: str
    ok: bool
    error: str = ""
    critical: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "ok": self.ok, "error": self.error, "critical": self.critical}


class HealthCheck:
    """Wraps a probe; exceptions are reported as failures."""

    def __init__(self, name: str, check: Probe, critical: bool = False) -> None:
        self.name = name
        self.check = check
        self.critical = critical

    def run(self) -> HealthStatus:
        try:
            ok = bool(self.check())
            return HealthStatus(name=self.name, ok=ok, critical=self.critical)
        except Exception as exc:  # noqa: BLE001 - any probe failure is a health failure
            return HealthStatus(
                name=self.name,
                ok=False,
                error=str(exc),
                critical=self.critical,
            )
