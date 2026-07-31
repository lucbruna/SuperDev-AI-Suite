"""Security dashboard."""
from __future__ import annotations
from typing import Any, Dict, List

class SecurityDashboard:
    def __init__(self) -> None:
        self._threats: List[Dict[str, Any]] = []
        self._compliance: Dict[str, str] = {}
    def record_threat(self, threat: Dict[str, Any]) -> None:
        self._threats.append(threat)
    def update_compliance(self, framework: str, status: str) -> None:
        self._compliance[framework] = status
    def get_threats(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._threats[-limit:]
    def get_compliance(self) -> Dict[str, str]:
        return dict(self._compliance)
    def get_threat_count(self) -> int:
        return len(self._threats)
    def get_failed_logins(self) -> int:
        return sum(1 for t in self._threats if t.get("type") == "failed_login")
    def get_summary(self) -> Dict[str, Any]:
        return {"threats": self.get_threat_count(), "compliance": len(self._compliance)}
