from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from .physical_config import PhysicalConfig
from .physical_context import PhysicalContext
from .physical_events import PhysicalEventBus, PhysicalEvent, EventType
from .physical_models import (
    AlertLevel, Device, PhysicalAlert, Robot, RobotStatus, RobotTask,
    SensorReading, SimulationResult,
)
from .physical_security import PhysicalSecurityManager

logger = logging.getLogger(__name__)


class EngineState(Enum):
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"
    EMERGENCY = "emergency"


@dataclass
class EngineConfig:
    config: PhysicalConfig
    event_bus: PhysicalEventBus
    context: PhysicalContext
    security: PhysicalSecurityManager
    enable_autonomous: bool = False
    decision_interval_seconds: int = 60
    enable_safety_monitor: bool = True


@dataclass
class EngineMetrics:
    state: EngineState = EngineState.INITIALIZING
    start_time: Optional[datetime] = None
    robots_controlled: int = 0
    tasks_completed: int = 0
    devices_managed: int = 0
    sensors_read: int = 0
    inspections_done: int = 0
    simulations_run: int = 0
    maintenance_actions: int = 0
    errors: int = 0
    alerts_triggered: int = 0
    emergency_stops: int = 0
    last_action_time: Optional[datetime] = None
    subsystem_status: Dict[str, str] = field(default_factory=dict)


class PhysicalEngine:
    def __init__(self, config: EngineConfig):
        self.config = config
        self.metrics = EngineMetrics()
        self._subsystems: Dict[str, Any] = {}
        self._running = False
        self._main_task: Optional[asyncio.Task] = None
        self._monitor_task: Optional[asyncio.Task] = None

    async def initialize(self) -> None:
        logger.info("Initializing Physical AI Engine...")
        self.metrics.state = EngineState.INITIALIZING
        self.metrics.start_time = datetime.utcnow()
        await self._initialize_subsystems()
        await self._register_event_handlers()
        self.metrics.state = EngineState.RUNNING
        logger.info("Physical AI Engine initialized")

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        if self.config.enable_safety_monitor:
            self._monitor_task = asyncio.create_task(self._safety_monitor_loop())
        logger.info("Physical AI Engine started")

    async def stop(self) -> None:
        logger.info("Stopping Physical AI Engine...")
        self._running = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        await self._shutdown_subsystems()
        self.metrics.state = EngineState.STOPPED
        logger.info("Physical AI Engine stopped")

    async def emergency_stop(self, source: str, reason: str) -> None:
        self.metrics.state = EngineState.EMERGENCY
        self.metrics.emergency_stops += 1
        await self.config.security.emergency.trigger(source, reason)
        logger.critical(f"EMERGENCY: {source} - {reason}")

    async def reset_emergency(self) -> None:
        self.config.security.emergency.reset()
        self.metrics.state = EngineState.RUNNING

    async def _initialize_subsystems(self) -> None:
        from .robotics.robotics_engine import RoboticsEngine
        from .automation.automation_engine import AutomationEngine
        from .iot.iot_engine import IoTEngine
        from .sensors.sensor_engine import SensorEngine
        from .vision_control.vision_engine import VisionEngine
        from .motion.motion_engine import MotionEngine
        from .simulation.simulation_engine import SimulationEngine
        from .digital_twin.twin_engine import TwinEngine
        from .maintenance.maintenance_engine import MaintenanceEngine

        self._subsystems = {
            "robotics": RoboticsEngine(self.config.config, self.config.context, self.config.event_bus, self.config.security),
            "automation": AutomationEngine(self.config.config, self.config.context, self.config.event_bus, self.config.security),
            "iot": IoTEngine(self.config.config, self.config.context, self.config.event_bus, self.config.security),
            "sensors": SensorEngine(self.config.config, self.config.context, self.config.event_bus, self.config.security),
            "vision": VisionEngine(self.config.config, self.config.context, self.config.event_bus, self.config.security),
            "motion": MotionEngine(self.config.config, self.config.context, self.config.event_bus, self.config.security),
            "simulation": SimulationEngine(self.config.config, self.config.context, self.config.event_bus, self.config.security),
            "digital_twin": TwinEngine(self.config.config, self.config.context, self.config.event_bus, self.config.security),
            "maintenance": MaintenanceEngine(self.config.config, self.config.context, self.config.event_bus, self.config.security),
        }
        for name, sub in self._subsystems.items():
            await sub.initialize()
            self.metrics.subsystem_status[name] = "initialized"

    async def _register_event_handlers(self) -> None:
        self.config.event_bus.subscribe(EventType.SAFETY_ALERT, self._handle_safety_alert)
        self.config.event_bus.subscribe(EventType.EMERGENCY_STOP, self._handle_emergency_stop)
        self.config.event_bus.subscribe(EventType.MACHINE_ALERT, self._handle_machine_alert)

    async def _safety_monitor_loop(self) -> None:
        while self._running:
            try:
                if self.config.security.is_emergency_active():
                    self.metrics.state = EngineState.EMERGENCY
                await asyncio.sleep(5)
            except asyncio.CancelledError:
                break

    async def _handle_safety_alert(self, event: PhysicalEvent) -> None:
        self.metrics.alerts_triggered += 1
        logger.warning(f"Safety alert: {event.payload}")

    async def _handle_emergency_stop(self, event: PhysicalEvent) -> None:
        await self.emergency_stop(event.source, str(event.payload))

    async def _handle_machine_alert(self, event: PhysicalEvent) -> None:
        self.metrics.alerts_triggered += 1

    async def get_robots(self) -> List[Robot]:
        return await self._subsystems["robotics"].get_all()

    async def get_robot(self, robot_id: str) -> Optional[Robot]:
        return await self._subsystems["robotics"].get(robot_id)

    async def send_robot_command(self, robot_id: str, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        self.metrics.robots_controlled += 1
        return await self._subsystems["robotics"].send_command(robot_id, command, params)

    async def assign_task(self, robot_id: str, task: RobotTask) -> RobotTask:
        return await self._subsystems["robotics"].assign_task(robot_id, task)

    async def get_sensor_readings(self, sensor_id: str) -> List[SensorReading]:
        self.metrics.sensors_read += 1
        return await self._subsystems["sensors"].get_readings(sensor_id)

    async def run_inspection(self, camera_id: str, product_id: str) -> Dict[str, Any]:
        self.metrics.inspections_done += 1
        return await self._subsystems["vision"].inspect(camera_id, product_id)

    async def run_simulation(self, scenario: Dict[str, Any]) -> SimulationResult:
        self.metrics.simulations_run += 1
        return await self._subsystems["simulation"].execute(scenario)

    async def get_maintenance_schedule(self) -> List[Dict[str, Any]]:
        return await self._subsystems["maintenance"].get_schedule()

    async def get_digital_twin(self, asset_id: str) -> Optional[Dict[str, Any]]:
        return await self._subsystems["digital_twin"].get(asset_id)

    async def get_alerts(self) -> List[PhysicalAlert]:
        alerts = []
        for sub in self._subsystems.values():
            if hasattr(sub, "get_alerts"):
                alerts.extend(await sub.get_alerts())
        return alerts

    async def get_metrics(self) -> EngineMetrics:
        return self.metrics

    def get_subsystem(self, name: str):
        return self._subsystems.get(name)

    async def _shutdown_subsystems(self) -> None:
        for name, sub in self._subsystems.items():
            try:
                await sub.shutdown()
                self.metrics.subsystem_status[name] = "stopped"
            except Exception as e:
                logger.error(f"Error shutting down {name}: {e}")
