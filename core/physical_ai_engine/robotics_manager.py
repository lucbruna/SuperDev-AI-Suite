from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from .physical_engine import PhysicalEngine, EngineConfig
from .physical_context import PhysicalContext
from .physical_events import PhysicalEventBus
from .physical_models import (
    Device, DigitalTwin, FailurePrediction, MaintenanceRecord, PhysicalAlert,
    Robot, RobotStatus, RobotTask, SensorReading, SimulationResult,
)
from .physical_security import PhysicalSecurityManager

logger = logging.getLogger(__name__)


@dataclass
class ManagerConfig:
    engine_config: EngineConfig
    enable_safety_override: bool = False
    enable_auto_recovery: bool = True
    max_retries_on_failure: int = 3


class RoboticsManager:
    def __init__(self, config: ManagerConfig):
        self.config = config
        self.engine = PhysicalEngine(config.engine_config)
        self.context = config.engine_config.context
        self.event_bus = config.engine_config.event_bus
        self.security = config.engine_config.security
        self._initialized = False

    async def initialize(self) -> None:
        if self._initialized:
            return
        await self.engine.initialize()
        await self.engine.start()
        self._initialized = True
        logger.info("Robotics Manager initialized")

    async def shutdown(self) -> None:
        await self.engine.stop()
        self._initialized = False
        logger.info("Robotics Manager shutdown")

    async def get_robots(self) -> List[Robot]:
        return await self.engine.get_robots()

    async def get_robot(self, robot_id: str) -> Optional[Robot]:
        return await self.engine.get_robot(robot_id)

    async def send_command(self, robot_id: str, command: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        return await self.engine.send_robot_command(robot_id, command, params or {})

    async def assign_task(self, robot_id: str, task_type: str, description: str, params: Dict[str, Any] = None) -> RobotTask:
        task = RobotTask(
            id=f"task-{abs(hash(robot_id + task_type)) % 10000:04d}",
            robot_id=robot_id,
            task_type=task_type,
            description=description,
            parameters=params or {},
        )
        return await self.engine.assign_task(robot_id, task)

    async def get_sensor_readings(self, sensor_id: str) -> List[SensorReading]:
        return await self.engine.get_sensor_readings(sensor_id)

    async def run_inspection(self, camera_id: str, product_id: str) -> Dict[str, Any]:
        return await self.engine.run_inspection(camera_id, product_id)

    async def run_simulation(self, scenario: Dict[str, Any]) -> SimulationResult:
        return await self.engine.run_simulation(scenario)

    async def get_maintenance_schedule(self) -> List[Dict[str, Any]]:
        return await self.engine.get_maintenance_schedule()

    async def get_digital_twin(self, asset_id: str) -> Optional[Dict[str, Any]]:
        return await self.engine.get_digital_twin(asset_id)

    async def get_alerts(self) -> List[PhysicalAlert]:
        return await self.engine.get_alerts()

    async def emergency_stop(self, reason: str = "Operator request") -> None:
        await self.engine.emergency_stop("manager", reason)

    async def reset_emergency(self) -> None:
        await self.engine.reset_emergency()

    async def get_physical_kpis(self) -> Dict[str, float]:
        metrics = await self.engine.get_metrics()
        robots = await self.get_robots()
        return {
            "robots_active": float(len(robots)),
            "tasks_completed": float(metrics.tasks_completed),
            "inspections_done": float(metrics.inspections_done),
            "simulations_run": float(metrics.simulations_run),
            "maintenance_actions": float(metrics.maintenance_actions),
            "errors": float(metrics.errors),
            "alerts": float(metrics.alerts_triggered),
            "uptime_hours": (datetime.utcnow() - metrics.start_time).total_seconds() / 3600 if metrics.start_time else 0,
        }

    async def get_factory_health(self) -> Dict[str, Any]:
        alerts = await self.get_alerts()
        kpis = await self.get_physical_kpis()
        errors = kpis.get("errors", 0)
        score = max(0, 100 - errors * 5 - len(alerts) * 2)
        return {
            "health_score": score,
            "status": "good" if score > 80 else "attention" if score > 50 else "critical",
            "active_robots": kpis.get("robots_active", 0),
            "active_alerts": len(alerts),
            "critical_alerts": sum(1 for a in alerts if getattr(a, "level", None) and a.level.value == "critical"),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def get_engine_status(self) -> Dict[str, Any]:
        m = self.engine.metrics
        return {
            "state": m.state.value,
            "uptime": (datetime.utcnow() - m.start_time).total_seconds() if m.start_time else 0,
            "robots": m.robots_controlled,
            "tasks": m.tasks_completed,
            "inspections": m.inspections_done,
            "simulations": m.simulations_run,
            "maintenance": m.maintenance_actions,
            "errors": m.errors,
            "alerts": m.alerts_triggered,
            "emergency_stops": m.emergency_stops,
            "subsystems": m.subsystem_status,
        }

    def is_healthy(self) -> bool:
        return self.engine.metrics.state.value == "running"

    def check_access(self, user_id: str, resource: str, action: str) -> bool:
        return self.security.check_access(user_id, resource, action)
