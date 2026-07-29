from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..physical_config import PhysicalConfig
from ..physical_context import PhysicalContext
from ..physical_events import PhysicalEventBus
from ..physical_models import DeviceProtocol

logger = logging.getLogger(__name__)


class IndustrialProtocols:
    def __init__(self, config: PhysicalConfig, context: PhysicalContext, event_bus: PhysicalEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self._supported = {
            DeviceProtocol.MODBUS: {"port": 502, "version": "RTU"},
            DeviceProtocol.OPC_UA: {"port": 4840, "version": "1.04"},
            DeviceProtocol.MQTT: {"port": 1883, "version": "5.0"},
            DeviceProtocol.PROFINET: {"port": 0, "version": "2.4"},
            DeviceProtocol.ETHERNET_IP: {"port": 44818, "version": "2.0"},
        }

    def is_supported(self, protocol: DeviceProtocol) -> bool:
        return protocol in self._supported

    def get_config(self, protocol: DeviceProtocol) -> Optional[Dict[str, Any]]:
        return self._supported.get(protocol)

    def list_supported(self) -> List[str]:
        return [p.value for p in self._supported.keys()]

    def detect_protocol(self, device_info: Dict[str, Any]) -> Optional[DeviceProtocol]:
        port = device_info.get("port")
        for protocol, config in self._supported.items():
            if config["port"] == port:
                return protocol
        return None
