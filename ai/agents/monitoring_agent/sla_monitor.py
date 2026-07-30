from __future__ import annotations

from typing import Any


class SLAMonitor:
    """Monitors Service Level Agreements."""

    def __init__(self) -> None:
        self._slos: dict[str, dict[str, Any]] = {}

    def add_slo(self, name: str, target: float, window: str) -> str:
        self._slos[name] = {"name": name, "target": target, "window": window, "violations": 0, "ok": True}
        return name

    def get_slo(self, name: str) -> dict[str, Any] | None:
        return self._slos.get(name)

    @property
    def slo_count(self) -> int:
        return len(self._slos)

    def record_violation(self, name: str) -> None:
        slo = self._slos.get(name)
        if slo:
            slo["violations"] += 1

    def check_slos(self) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for slo in self._slos.values():
            ok = slo["violations"] == 0
            slo["ok"] = ok
            results.append({
                "name": slo["name"],
                "target": slo["target"],
                "violations": slo["violations"],
                "ok": ok,
            })
        return results

    def to_dict(self) -> dict[str, Any]:
        return {
            "slos": list(self._slos.values()),
            "slo_count": self.slo_count,
        }
