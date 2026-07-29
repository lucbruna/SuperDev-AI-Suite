"""
Scenario Simulator - Digital Twin scenario simulation for what-if analysis.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict

from ..supply_context import SupplyChainContext
from ..supply_events import SupplyChainEvent, SupplyChainEventBus, EventType
from ..supply_models import ScenarioSimulation
from ..supply_config import SupplyChainConfig

logger = logging.getLogger(__name__)


class ScenarioSimulator:
    def __init__(self, config: SupplyChainConfig, context: SupplyChainContext, event_bus: SupplyChainEventBus):
        self.config = config
        self.event_bus = event_bus

    async def run(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        scenario_name = scenario.get("name", "unknown")
        logger.info(f"Running scenario simulation: {scenario_name}")

        if "demand_increase" in scenario:
            increase = scenario["demand_increase"]
            result = {
                "scenario": scenario_name,
                "impact_analysis": {
                    "inventory_impact": f"Estoque precisará aumentar {increase * 0.5}%",
                    "transport_impact": f"Frota precisa aumentar {increase * 0.3}%",
                    "staff_impact": f"Equipe precisa aumentar {increase * 0.2}%",
                    "cost_impact": f"Custos aumentarão {increase * 0.4}%",
                    "supplier_impact": "Fornecedores precisarão aumentar capacidade",
                },
                "recommendations": [
                    "Aumentar estoque de segurança em 30 dias",
                    "Contratar transportadora adicional",
                    "Negociar volumes com fornecedores",
                ],
            }
        elif "new_supplier" in scenario:
            result = {"impact": "Positivo", "cost_savings": 0.08, "risk_change": -0.05}
        else:
            result = {"impact": "Analisado", "recommendations": []}

        sim = ScenarioSimulation(
            scenario_id=f"SIM-{hash(scenario_name) % 10000}",
            scenario_name=scenario_name,
            parameters=scenario, results=result,
            execution_time_ms=1250,
        )

        await self.event_bus.publish(SupplyChainEvent(
            event_type=EventType.DIGITAL_TWIN_SCENARIO,
            payload={"scenario_id": sim.scenario_id, "results": result},
        ))

        return {"simulation": sim, "results": result}

    async def run_what_if(self, question: str) -> Dict[str, Any]:
        return await self.run({"name": "what_if", "question": question})

    async def compare_scenarios(self, scenarios: list) -> Dict[str, Any]:
        results = {}
        for scenario in scenarios:
            results[scenario.get("name", "unknown")] = await self.run(scenario)
        return {"comparison": results, "recommended": min(results, key=lambda k: results[k].get("results", {}).get("cost_impact", 0))}