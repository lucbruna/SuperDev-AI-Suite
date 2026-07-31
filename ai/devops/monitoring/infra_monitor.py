"""Infrastructure monitor."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class InfraMonitor:
    def __init__(self) -> None:
        self._metrics: Dict[str, List[Dict[str, Any]]] = {}
        self._alerts: List[Dict[str, Any]] = []
    def record(self, resource: str, metric_name: str, value: float) -> Dict[str, Any]:
        entry = {"resource": resource, "metric": metric_name, "value": value, "timestamp": time.time()}
        self._metrics.setdefault(f"{resource}/{metric_name}", []).append(entry)
        return entry
    def get_metric(self, resource: str, metric_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        return self._metrics.get(f"{resource}/{metric_name}", [])[-limit:]
    def alert(self, resource: str, condition: str, severity: str = "warning") -> Dict[str, Any]:
        alert = {"resource": resource, "condition": condition, "severity": severity, "timestamp": time.time()}
        self._alerts.append(alert)
        return alert
    def get_alerts(self, severity: str = "", limit: int = 50) -> List[Dict[str, Any]]:
        alerts = self._alerts
        if severity:
            alerts = [a for a in alerts if a["severity"] == severity]
        return alerts[-limit:]
    def list_resources(self) -> List[str]:
        return list(set(k.split("/")[0] for k in self._metrics.keys()))
    def count(self) -> int:
        return sum(len(v) for v in self._metrics.values())
