from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..physical_config import PhysicalConfig
from ..physical_context import PhysicalContext
from ..physical_events import PhysicalEventBus
from ..physical_models import Device, TelemetryData
from ..physical_security import PhysicalSecurityManager
from .device_registry import DeviceRegistry
from .communication import Communication
from .telemetry_manager import TelemetryManager
from .protocol_adapter import ProtocolAdapter

logger = logging.getLogger(__name__)


class IoTEngine:
    def __init__(self, config: PhysicalConfig, context: PhysicalContext,
                 event_bus: PhysicalEventBus, security: PhysicalSecurityManager):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.security = security
        self.registry: Optional[DeviceRegistry] = None
        self.comms: Optional[Communication] = None
        self.telemetry: Optional[TelemetryManager] = None
        self.adapter: Optional[ProtocolAdapter] = None

    async def initialize(self) -> None:
        self.registry = DeviceRegistry(self.config, self.context, self.event_bus)
        self.comms = Communication(self.config, self.context, self.event_bus)
        self.telemetry = TelemetryManager(self.config, self.context, self.event_bus)
        self.adapter = ProtocolAdapter(self.config, self.context, self.event_bus)
        logger.info("IoTEngine initialized")

    async def register_device(self, name: str, device_type: str = "generic", protocol: str = "mqtt") -> Device:
        return self.registry.register(name, device_type, protocol)

    async def get_device(self, device_id: str) -> Optional[Device]:
        return self.registry.get(device_id)

    async def get_all_devices(self) -> List[Device]:
        return self.registry.get_all()

    async def send_telemetry(self, device_id: str, metrics: Dict[str, float]) -> Optional[TelemetryData]:
        return self.telemetry.record(device_id, metrics)

    async def get_telemetry(self, device_id: str, limit: int = 100) -> List[TelemetryData]:
        return self.telemetry.get_history(device_id, limit)

    async def ping_device(self, device_id: str) -> bool:
        return self.comms.ping(device_id)

    async def shutdown(self) -> None:
        logger.info("IoTEngine shutdown")
