"""
Integration Monitor - Core monitoring
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import hashlib
import statistics


class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    check_id: str
    integration_id: str
    status: HealthStatus = HealthStatus.UNKNOWN
    message: str = ""
    latency_ms: float = 0.0
    checked_at: datetime = field(default_factory=datetime.now)


@dataclass
class IntegrationStatus:
    integration_id: str
    is_online: bool = True
    uptime_percent: float = 100.0
    avg_latency_ms: float = 0.0
    error_rate: float = 0.0
    last_check: Optional[datetime] = None


class IntegrationMonitor:
    def __init__(self):
        self.health_checks: Dict[str, List[HealthCheck]] = {}
        self.statuses: Dict[str, IntegrationStatus] = {}
        self.alerts: List[Dict[str, Any]] = []

    def check_health(self, integration_id: str, status: HealthStatus = HealthStatus.HEALTHY, message: str = "", latency_ms: float = 0.0) -> HealthCheck:
        check_id = hashlib.sha256(f"{integration_id}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        check = HealthCheck(check_id=check_id, integration_id=integration_id, status=status, message=message, latency_ms=latency_ms)
        self.health_checks.setdefault(integration_id, []).append(check)
        if integration_id not in self.statuses:
            self.statuses[integration_id] = IntegrationStatus(integration_id=integration_id)
        self.statuses[integration_id].last_check = datetime.now()
        self.statuses[integration_id].is_online = status == HealthStatus.HEALTHY
        return check

    def get_status(self, integration_id: str) -> Optional[IntegrationStatus]:
        return self.statuses.get(integration_id)

    def get_health_history(self, integration_id: str, limit: int = 100) -> List[HealthCheck]:
        return self.health_checks.get(integration_id, [])[-limit:]

    def alert(self, integration_id: str, message: str, severity: str = "warning") -> None:
        self.alerts.append({"integration_id": integration_id, "message": message, "severity": severity, "timestamp": datetime.now().isoformat()})

    def get_alerts(self, integration_id: str = None) -> List[Dict[str, Any]]:
        if integration_id:
            return [a for a in self.alerts if a["integration_id"] == integration_id]
        return self.alerts

    def get_uptime(self, integration_id: str) -> float:
        checks = self.health_checks.get(integration_id, [])
        if not checks:
            return 100.0
        healthy = sum(1 for c in checks if c.status == HealthStatus.HEALTHY)
        return (healthy / len(checks)) * 100

    def get_avg_latency(self, integration_id: str) -> float:
        checks = self.health_checks.get(integration_id, [])
        if not checks:
            return 0.0
        latencies = [c.latency_ms for c in checks if c.latency_ms > 0]
        return statistics.mean(latencies) if latencies else 0.0

    def count(self) -> int:
        return len(self.health_checks)
