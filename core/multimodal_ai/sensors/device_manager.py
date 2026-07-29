from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

SAMPLE_DEVICES: list[dict[str, Any]] = [
    {
        "device_id": "sensor-temp-001",
        "name": "Temperature Sensor A1",
        "type": "temperature",
        "location": "Server Room",
        "status": "online",
        "firmware": "v2.1.0",
        "last_seen": datetime.utcnow().isoformat(),
    },
    {
        "device_id": "sensor-hum-001",
        "name": "Humidity Sensor B2",
        "type": "humidity",
        "location": "Warehouse",
        "status": "online",
        "firmware": "v1.8.3",
        "last_seen": datetime.utcnow().isoformat(),
    },
    {
        "device_id": "sensor-pres-001",
        "name": "Pressure Sensor C3",
        "type": "pressure",
        "location": "Pipeline A",
        "status": "offline",
        "firmware": "v3.0.1",
        "last_seen": datetime.utcnow().isoformat(),
    },
]


class DeviceManager:
    def __init__(self) -> None:
        self._devices: dict[str, dict[str, Any]] = {}
        self._telemetry_store: dict[str, list[dict[str, Any]]] = {}
        for d in SAMPLE_DEVICES:
            self._devices[d["device_id"]] = dict(d)

    async def register_device(self, device: dict[str, Any]) -> dict[str, Any]:
        device_id = device.get("device_id", uuid.uuid4().hex[:12])
        record = dict(device)
        record["device_id"] = device_id
        record["registered_at"] = datetime.utcnow().isoformat()
        record["status"] = record.get("status", "offline")
        self._devices[device_id] = record
        return record

    async def unregister_device(self, device_id: str) -> bool:
        return self._devices.pop(device_id, None) is not None

    async def get_device(self, device_id: str) -> Optional[dict[str, Any]]:
        return self._devices.get(device_id)

    async def list_devices(self, status: Optional[str] = None) -> list[dict[str, Any]]:
        if status:
            return [d for d in self._devices.values() if d.get("status") == status]
        return list(self._devices.values())

    async def update_device_status(self, device_id: str, status: str) -> Optional[dict[str, Any]]:
        device = self._devices.get(device_id)
        if device is None:
            return None
        device["status"] = status
        device["last_seen"] = datetime.utcnow().isoformat()
        return device

    async def get_device_telemetry(self, device_id: str, limit: int = 10) -> list[dict[str, Any]]:
        if device_id not in self._telemetry_store:
            self._telemetry_store[device_id] = self._generate_sample_telemetry(device_id)
        return self._telemetry_store[device_id][-limit:]

    def _generate_sample_telemetry(self, device_id: str, count: int = 20) -> list[dict[str, Any]]:
        base_temp = 22.0
        return [
            {
                "device_id": device_id,
                "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
                "value": base_temp + (i * 0.5),
                "unit": "celsius",
            }
            for i in range(count)
        ]
