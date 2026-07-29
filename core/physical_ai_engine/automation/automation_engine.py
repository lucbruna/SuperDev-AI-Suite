from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..physical_config import PhysicalConfig
from ..physical_context import PhysicalContext
from ..physical_events import PhysicalEventBus
from ..physical_models import MachineState, ProductionOrder
from ..physical_security import PhysicalSecurityManager
from .process_controller import ProcessController
from .machine_interface import MachineInterface
from .plc_connector import PLCConnector
from .industrial_protocols import IndustrialProtocols

logger = logging.getLogger(__name__)


class AutomationEngine:
    def __init__(self, config: PhysicalConfig, context: PhysicalContext,
                 event_bus: PhysicalEventBus, security: PhysicalSecurityManager):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.security = security
        self.process: Optional[ProcessController] = None
        self.machines: Optional[MachineInterface] = None
        self.plc: Optional[PLCConnector] = None
        self.protocols: Optional[IndustrialProtocols] = None

    async def initialize(self) -> None:
        self.process = ProcessController(self.config, self.context, self.event_bus)
        self.machines = MachineInterface(self.config, self.context, self.event_bus)
        self.plc = PLCConnector(self.config, self.context, self.event_bus)
        self.protocols = IndustrialProtocols(self.config, self.context, self.event_bus)
        logger.info("AutomationEngine initialized")

    async def get_machine_state(self, machine_id: str) -> Optional[MachineState]:
        return self.machines.get_state(machine_id)

    async def start_production(self, order: ProductionOrder) -> ProductionOrder:
        return await self.process.start(order)

    async def stop_production(self, order_id: str) -> bool:
        return await self.process.stop(order_id)

    async def get_all_machines(self) -> List[MachineState]:
        return self.machines.get_all()

    async def read_plc(self, tag: str) -> Any:
        return self.plc.read(tag)

    async def write_plc(self, tag: str, value: Any) -> bool:
        return self.plc.write(tag, value)

    async def shutdown(self) -> None:
        logger.info("AutomationEngine shutdown")
