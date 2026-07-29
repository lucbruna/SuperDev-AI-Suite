from __future__ import annotations

import asyncio
import uuid
from collections import defaultdict
from datetime import datetime
from typing import Any, Callable, Optional

AlertCallback = Callable[[dict[str, Any]], None]


class RealtimeMonitor:
    def __init__(self) -> None:
        self._running = False
        self._readings: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self._alerts: list[dict[str, Any]] = []
        self._subscribers: list[AlertCallback] = []
        self._task: Optional[asyncio.Task[None]] = None

    async def start_monitoring(self) -> None:
        self._running = True
        self._task = asyncio.create_task(self._monitor_loop())

    async def stop_monitoring(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            self._task = None

    async def get_current_readings(self, device_id: Optional[str] = None) -> list[dict[str, Any]]:
        if device_id:
            return self._readings.get(device_id, [])[-10:]
        all_readings: list[dict[str, Any]] = []
        for readings in self._readings.values():
            all_readings.extend(readings[-5:])
        return all_readings[-20:]

    async def get_alerts(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._alerts[-limit:]

    def subscribe_to_alerts(self, callback: AlertCallback) -> None:
        self._subscribers.append(callback)

    async def check_health(self) -> dict[str, Any]:
        return {
            "status": "healthy" if self._running else "stopped",
            "active_devices": len(self._readings),
            "total_alerts": len(self._alerts),
            "subscriber_count": len(self._subscribers),
            "uptime": "N/A",
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def _monitor_loop(self) -> None:
        device_ids = [f"sensor-{t}-{i:03d}" for t in ("temp", "hum", "pres", "vib") for i in range(1, 4)]
        while self._running:
            for did in device_ids:
                reading = {
                    "device_id": did,
                    "timestamp": datetime.utcnow().isoformat(),
                    "value": 20.0 + (hash(did + datetime.utcnow().isoformat()) % 10),
                    "unit": "celsius",
                }
                self._readings[did].append(reading)
                if reading["value"] > 28.0 or reading["value"] < 15.0:
                    alert = {
                        "alert_id": uuid.uuid4().hex[:12],
                        "device_id": did,
                        "type": "threshold_breach",
                        "severity": "warning" if reading["value"] > 28.0 else "critical",
                        "message": f"Value {reading['value']} out of normal range",
                        "timestamp": reading["timestamp"],
                    }
                    self._alerts.append(alert)
                    for cb in self._subscribers:
                        cb(alert)
            await asyncio.sleep(0.5)
