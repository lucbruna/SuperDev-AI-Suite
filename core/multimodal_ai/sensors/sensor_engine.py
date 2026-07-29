from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class EngineState(Enum):
    STOPPED = "stopped"
    INITIALIZING = "initializing"
    RUNNING = "running"
    ERROR = "error"


@dataclass
class EngineConfig:
    polling_interval: float = 1.0
    batch_size: int = 50
    anomaly_threshold: float = 3.0
    max_alerts: int = 100
    enable_realtime: bool = True
    enable_telemetry_processing: bool = True
    enable_anomaly_detection: bool = True


@dataclass
class EngineMetrics:
    readings_processed: int = 0
    anomalies_detected: int = 0
    alerts_generated: int = 0
    devices_monitored: int = 0
    telemetry_batches: int = 0
    errors: int = 0
    avg_latency: float = 0.0
    start_time: Optional[datetime] = None


class SensorEngine:
    def __init__(self, config: Optional[EngineConfig] = None) -> None:
        self.config = config or EngineConfig()
        self.state = EngineState.STOPPED
        self.metrics = EngineMetrics()
        self._engine_id: str = uuid.uuid4().hex[:12]
        self._session: Optional[dict[str, Any]] = None

    async def initialize(self) -> None:
        self.state = EngineState.INITIALIZING
        await asyncio.sleep(0.05)
        self._session = {
            "engine_id": self._engine_id,
            "initialized_at": datetime.utcnow().isoformat(),
            "config_snapshot": self.config,
        }
        self.metrics.start_time = datetime.utcnow()
        self.state = EngineState.RUNNING

    async def stop(self) -> None:
        self.state = EngineState.STOPPED
        self._session = None
        self.metrics.start_time = None

    async def process_reading(self, reading: dict[str, Any]) -> dict[str, Any]:
        self.metrics.readings_processed += 1
        return {
            "reading_id": reading.get("id", uuid.uuid4().hex),
            "device_id": reading.get("device_id", "unknown"),
            "value": reading.get("value"),
            "timestamp": reading.get("timestamp", datetime.utcnow().isoformat()),
            "status": "processed",
        }

    async def analyze_telemetry(self, readings: list[dict[str, Any]]) -> dict[str, Any]:
        self.metrics.telemetry_batches += 1
        values = [r.get("value", 0) for r in readings if r.get("value") is not None]
        avg = sum(values) / max(len(values), 1)
        return {
            "batch_size": len(readings),
            "average": avg,
            "min": min(values) if values else 0,
            "max": max(values) if values else 0,
            "count": len(values),
        }

    async def detect_anomalies(self, readings: list[dict[str, Any]]) -> list[dict[str, Any]]:
        anomalies: list[dict[str, Any]] = []
        values = [r.get("value", 0) for r in readings if r.get("value") is not None]
        if not values:
            return anomalies
        avg = sum(values) / len(values)
        std = (sum((v - avg) ** 2 for v in values) / len(values)) ** 0.5 or 1
        for r in readings:
            v = r.get("value", 0)
            if abs(v - avg) > self.config.anomaly_threshold * std:
                anomalies.append({
                    "reading_id": r.get("id", uuid.uuid4().hex),
                    "device_id": r.get("device_id", "unknown"),
                    "value": v,
                    "mean": avg,
                    "std": std,
                    "z_score": (v - avg) / std,
                })
                self.metrics.anomalies_detected += 1
        return anomalies

    async def get_realtime_data(self, device_id: str) -> dict[str, Any]:
        return {
            "device_id": device_id,
            "timestamp": datetime.utcnow().isoformat(),
            "temperature": 22.5,
            "humidity": 45.0,
            "pressure": 1013.25,
            "status": "active",
        }
