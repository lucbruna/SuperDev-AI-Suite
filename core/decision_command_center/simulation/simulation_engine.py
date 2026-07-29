from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..decision_config import DecisionConfig
from ..decision_security import DecisionSecurityManager
from .scenario_builder import ScenarioBuilder
from .impact_analysis import ImpactAnalysis
from .strategy_simulator import StrategySimulator

logger = logging.getLogger(__name__)


class SimulationEngine:
    def __init__(self, config: DecisionConfig, security: DecisionSecurityManager):
        self.config = config
        self.security = security
        self.builder: Optional[ScenarioBuilder] = None
        self.impact: Optional[ImpactAnalysis] = None
        self.simulator: Optional[StrategySimulator] = None

    async def initialize(self) -> None:
        self.builder = ScenarioBuilder(self.config)
        self.impact = ImpactAnalysis(self.config)
        self.simulator = StrategySimulator(self.config)
        logger.info("SimulationEngine initialized")

    async def simulate(self, scenario_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        if scenario_type == "new_branch":
            return self.simulator.simulate_new_branch(parameters)
        elif scenario_type == "price_change":
            return self.simulator.simulate_price_change(parameters)
        elif scenario_type == "hiring":
            return self.simulator.simulate_hiring(parameters)
        else:
            return self.simulator.generic_simulation(parameters)

    async def analyze_impact(self, change: str, value: float) -> Dict[str, Any]:
        return self.impact.analyze(change, value)

    async def build_scenario(self, name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        return self.builder.build(name, params)

    async def list_scenarios(self) -> List[Dict[str, Any]]:
        return self.builder.list_templates()

    async def shutdown(self) -> None:
        logger.info("SimulationEngine shutdown")
