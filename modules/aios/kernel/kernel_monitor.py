"""Kernel monitor — tracks registered components and their runtime status."""
from __future__ import annotations
from datetime import UTC, datetime
from typing import Any, Callable

StatusProbe = Callable[[], dict[str, Any]]


class KernelMonitor:
    """Registers component status probes and takes periodic snapshots."""

    def __init__(self) -> None:
        self._probes: dict[str, StatusProbe] = {}
        self._last: dict[str, dict[str, Any]] = {}

    def register(self, name: str, probe: StatusProbe) -> None:
        self._probes[name] = probe

    def tick(self) -> dict[str, Any]:
        now = datetime.now(UTC).isoformat()
        for name, probe in self._probes.items():
            try:
                self._last[name] = {
                    "ok": True,
                    "checked_at": now,
                    "details": probe(),
                }
            except Exception as e:  # noqa: BLE001
                self._last[name] = {"ok": False, "checked_at": now, "error": str(e)}
        return self.snapshot()

    def snapshot(self) -> dict[str, Any]:
        return {
            "components": dict(self._last),
            "ok_count": sum(1 for s in self._last.values() if s.get("ok")),
            "total": len(self._last),
        }


_kernel_monitor: KernelMonitor | None = None


def get_kernel_monitor() -> KernelMonitor:
    global _kernel_monitor
    if _kernel_monitor is None:
        _kernel_monitor = KernelMonitor()
    return _kernel_monitor
