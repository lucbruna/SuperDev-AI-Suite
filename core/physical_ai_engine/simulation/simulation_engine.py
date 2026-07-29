from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..physical_config import PhysicalConfig
from ..physical_context import PhysicalContext
from ..physical_events import PhysicalEventBus, PhysicalEvent, EventType
from ..physical_models import SimulationResult, SimulationStatus
from ..physical_security import PhysicalSecurityManager
from .environment_model import EnvironmentModel
from .physics_simulator import PhysicsSimulator
from .scenario_testing import ScenarioTesting

logger = logging.getLogger(__name__)


class SimulationEngine:
    def __init__(self, config: PhysicalConfig, context: PhysicalContext,
                 event_bus: PhysicalEventBus, security: PhysicalSecurityManager):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.security = security
        self.environment: Optional[EnvironmentModel] = None
        self.physics: Optional[PhysicsSimulator] = None
        self.testing: Optional[ScenarioTesting] = None

    async def initialize(self) -> None:
        self.environment = EnvironmentModel(self.config, self.context, self.event_bus)
        self.physics = PhysicsSimulator(self.config, self.context, self.event_bus)
        self.testing = ScenarioTesting(self.config, self.context, self.event_bus)
        logger.info("SimulationEngine initialized")

    async def execute(self, scenario: Dict[str, Any]) -> SimulationResult:
        await self.event_bus.publish(PhysicalEvent(
            event_type=EventType.SIMULATION_STARTED,
            payload={"scenario": scenario.get("name", "unknown")},
        ))
        issues = self.testing.run(scenario)
        metrics = self.physics.simulate(scenario)
        result = SimulationResult(
            id=f"sim-{abs(hash(str(scenario))) % 10000:04d}",
            scenario_name=scenario.get("name", "Simulation"),
            duration_seconds=scenario.get("duration", 60.0),
            cycles_completed=scenario.get("cycles", 1000),
            passed=len(issues) == 0,
            issues=issues,
            metrics=metrics,
        )
        await self.event_bus.publish(PhysicalEvent(
            event_type=EventType.SIMULATION_COMPLETED,
            payload={"result": result.id, "passed": result.passed},
        ))
        return result

    async def get_environment(self) -> Dict[str, Any]:
        return self.environment.get_state()

    async def shutdown(self) -> None:
        logger.info("SimulationEngine shutdown")
