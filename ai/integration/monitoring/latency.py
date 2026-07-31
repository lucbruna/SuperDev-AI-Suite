"""
Latency Monitor - Response time tracking
"""
import statistics
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class LatencyRecord:
    integration_id: str
    endpoint: str
    latency_ms: float
    timestamp: datetime = field(default_factory=datetime.now)
    success: bool = True


class LatencyMonitor:
    def __init__(self):
        self.records: dict[str, list[LatencyRecord]] = {}
        self.thresholds: dict[str, float] = {}

    def record(self, integration_id: str, endpoint: str, latency_ms: float, success: bool = True) -> LatencyRecord:
        record = LatencyRecord(integration_id=integration_id, endpoint=endpoint, latency_ms=latency_ms, success=success)
        self.records.setdefault(integration_id, []).append(record)
        return record

    def set_threshold(self, integration_id: str, threshold_ms: float) -> None:
        self.thresholds[integration_id] = threshold_ms

    def get_stats(self, integration_id: str) -> dict[str, float]:
        records = self.records.get(integration_id, [])
        if not records:
            return {"count": 0, "mean": 0, "min": 0, "max": 0, "p50": 0, "p95": 0}
        latencies = sorted([r.latency_ms for r in records])
        return {"count": len(latencies), "mean": statistics.mean(latencies), "min": min(latencies), "max": max(latencies), "p50": latencies[len(latencies) // 2], "p95": latencies[int(len(latencies) * 0.95)] if len(latencies) > 1 else latencies[0]}

    def get_slow(self, integration_id: str) -> list[LatencyRecord]:
        threshold = self.thresholds.get(integration_id, 1000)
        return [r for r in self.records.get(integration_id, []) if r.latency_ms > threshold]

    def get_records(self, integration_id: str, limit: int = 100) -> list[LatencyRecord]:
        return self.records.get(integration_id, [])[-limit:]

    def count(self) -> int:
        return sum(len(v) for v in self.records.values())
