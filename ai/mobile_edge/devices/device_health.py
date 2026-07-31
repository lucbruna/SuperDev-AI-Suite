"""Device Health - Device health monitoring."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class HealthLevel(Enum):
    GOOD = "good"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class HealthReport:
    device_id: str
    level: HealthLevel = HealthLevel.UNKNOWN
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    battery_level: float = 100.0
    storage_usage: float = 0.0
    temperature: float = 0.0
    network_status: str = "unknown"
    issues: list[str] = field(default_factory=list)
    reported_at: datetime = field(default_factory=datetime.now)


class DeviceHealthMonitor:
    def __init__(self):
        self.reports: dict[str, list[HealthReport]] = {}
        self.thresholds: dict[str, dict[str, float]] = {}

    def report(self, device_id: str, **kwargs) -> HealthReport:
        report = HealthReport(device_id=device_id, **kwargs)
        self.reports.setdefault(device_id, []).append(report)
        return report

    def set_thresholds(self, device_id: str, **thresholds) -> None:
        self.thresholds[device_id] = thresholds

    def get_latest(self, device_id: str) -> HealthReport | None:
        reports = self.reports.get(device_id, [])
        return reports[-1] if reports else None

    def get_history(self, device_id: str, limit: int = 100) -> list[HealthReport]:
        return self.reports.get(device_id, [])[-limit:]

    def check_alerts(self, device_id: str) -> list[str]:
        latest = self.get_latest(device_id)
        if not latest:
            return []
        alerts = []
        thresholds = self.thresholds.get(device_id, {})
        if latest.cpu_usage > thresholds.get("cpu", 90):
            alerts.append(f"High CPU: {latest.cpu_usage}%")
        if latest.memory_usage > thresholds.get("memory", 85):
            alerts.append(f"High memory: {latest.memory_usage}%")
        if latest.battery_level < thresholds.get("battery", 20):
            alerts.append(f"Low battery: {latest.battery_level}%")
        return alerts

    def list_devices(self) -> list[str]:
        return list(self.reports.keys())
