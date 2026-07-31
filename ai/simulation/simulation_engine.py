from __future__ import annotations

from typing import Any

from .cost_estimator import CostEstimator
from .risk_estimator import RiskEstimator
from .scenario_builder import ScenarioBuilder
from .simulation_runner import SimulationRunner
from .timeline_estimator import TimelineEstimator


class SimulationEngine:
    """Core simulation engine for scenario analysis."""

    def __init__(
        self,
        builder: ScenarioBuilder | None = None,
        runner: SimulationRunner | None = None,
        risk: RiskEstimator | None = None,
        cost: CostEstimator | None = None,
        timeline: TimelineEstimator | None = None,
    ):
        self._builder = builder or ScenarioBuilder()
        self._runner = runner or SimulationRunner()
        self._risk = risk or RiskEstimator()
        self._cost = cost or CostEstimator()
        self._timeline = timeline or TimelineEstimator()

    async def simulate(self, context: dict[str, Any]) -> dict[str, Any]:
        scenario = await self._builder.build(context)
        result = await self._runner.run(scenario)
        risk = await self._risk.estimate(scenario, result)
        cost = await self._cost.estimate(scenario)
        timeline = await self._timeline.estimate(scenario)
        return {
            "scenario": scenario,
            "result": result,
            "risk": risk,
            "cost": cost,
            "timeline": timeline,
        }

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        return await self.simulate(context)
