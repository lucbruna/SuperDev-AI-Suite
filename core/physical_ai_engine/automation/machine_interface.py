from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..physical_config import PhysicalConfig
from ..physical_context import PhysicalContext
from ..physical_events import PhysicalEventBus
from ..physical_models import MachineState

logger = logging.getLogger(__name__)


class MachineInterface:
    def __init__(self, config: PhysicalConfig, context: PhysicalContext, event_bus: PhysicalEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self._machines: Dict[str, MachineState] = {}
        self._init_machines()

    def _init_machines(self) -> None:
        for i in range(1, 11):
            self._machines[f"M-{i:03d}"] = MachineState(
                machine_id=f"M-{i:03d}",
                state="idle",
                speed=0.0,
                temperature=25.0 + i * 2,
                pressure=100.0 + i * 5,
                power_consumption=10.0 + i * 3,
                cycle_count=i * 1000,
                uptime_hours=i * 150.0,
            )

    def get_state(self, machine_id: str) -> Optional[MachineState]:
        return self._machines.get(machine_id)

    def get_all(self) -> List[MachineState]:
        return list(self._machines.values())

    def update_state(self, machine_id: str, updates: Dict[str, Any]) -> Optional[MachineState]:
        machine = self._machines.get(machine_id)
        if not machine:
            return None
        for key, value in updates.items():
            if hasattr(machine, key):
                setattr(machine, key, value)
        return machine

    def get_running(self) -> List[MachineState]:
        return [m for m in self._machines.values() if m.state == "running"]

    def get_alerts(self) -> List[Dict[str, Any]]:
        alerts = []
        for m in self._machines.values():
            if m.temperature > 80:
                alerts.append({"machine": m.machine_id, "alert": "high_temperature", "value": m.temperature})
            if m.pressure > 200:
                alerts.append({"machine": m.machine_id, "alert": "high_pressure", "value": m.pressure})
        return alerts
