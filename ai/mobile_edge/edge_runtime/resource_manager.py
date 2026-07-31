"""Resource Manager - Edge device resource management."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ResourceSnapshot:
    device_id: str
    cpu_percent: float = 0.0
    memory_used_mb: float = 0.0
    memory_total_mb: float = 0.0
    storage_used_mb: float = 0.0
    storage_total_mb: float = 0.0
    battery_percent: float = 100.0
    gpu_percent: float = 0.0
    temperature_c: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


class EdgeResourceManager:
    def __init__(self):
        self.snapshots: dict[str, list[ResourceSnapshot]] = {}
        self.limits: dict[str, dict[str, float]] = {}

    def report(self, device_id: str, **kwargs) -> ResourceSnapshot:
        snapshot = ResourceSnapshot(device_id=device_id, **kwargs)
        self.snapshots.setdefault(device_id, []).append(snapshot)
        return snapshot

    def set_limits(self, device_id: str, **limits) -> None:
        self.limits[device_id] = limits

    def get_latest(self, device_id: str) -> ResourceSnapshot | None:
        snaps = self.snapshots.get(device_id, [])
        return snaps[-1] if snaps else None

    def is_over_limit(self, device_id: str) -> bool:
        latest = self.get_latest(device_id)
        limits = self.limits.get(device_id, {})
        if not latest:
            return False
        if "cpu_percent" in limits and latest.cpu_percent > limits["cpu_percent"]:
            return True
        if "memory_percent" in limits:
            mem_pct = (latest.memory_used_mb / latest.memory_total_mb * 100) if latest.memory_total_mb > 0 else 0
            if mem_pct > limits["memory_percent"]:
                return True
        return False

    def get_history(self, device_id: str, limit: int = 100) -> list[ResourceSnapshot]:
        return self.snapshots.get(device_id, [])[-limit:]

    def list_devices(self) -> list[str]:
        return list(self.snapshots.keys())
