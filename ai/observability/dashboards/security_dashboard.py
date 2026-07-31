"""Security dashboard."""

from __future__ import annotations

from typing import Any


class SecurityDashboard:
    def __init__(self) -> None:
        self._threats: list[dict[str, Any]] = []
        self._compliance: dict[str, str] = {}

    def record_threat(self, threat: dict[str, Any]) -> None:
        self._threats.append(threat)

    def update_compliance(self, framework: str, status: str) -> None:
        self._compliance[framework] = status

    def get_threats(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._threats[-limit:]

    def get_compliance(self) -> dict[str, str]:
        return dict(self._compliance)

    def get_threat_count(self) -> int:
        return len(self._threats)

    def get_failed_logins(self) -> int:
        return sum(1 for t in self._threats if t.get("type") == "failed_login")

    def get_summary(self) -> dict[str, Any]:
        return {"threats": self.get_threat_count(), "compliance": len(self._compliance)}
