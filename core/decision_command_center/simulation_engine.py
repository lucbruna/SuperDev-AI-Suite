from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from .decision_models import Scenario, ScenarioType, SimulationResult

logger = logging.getLogger(__name__)


class SimulationEngine:
    def __init__(self):
        self._results: Dict[str, SimulationResult] = {}
        self._scenarios: Dict[str, Scenario] = {}

    async def create_scenario(self, name: str, parameters: Dict[str, Any], scenario_type: ScenarioType = ScenarioType.WHAT_IF) -> Scenario:
        scenario = Scenario(
            id=str(uuid.uuid4()),
            name=name,
            scenario_type=scenario_type,
            parameters=parameters,
        )
        self._scenarios[scenario.id] = scenario
        return scenario

    async def execute(self, scenario: Scenario) -> SimulationResult:
        projected = {}
        for key, value in scenario.parameters.items():
            if isinstance(value, (int, float)):
                projected[f"{key}_projected"] = value * (1 + (hash(key) % 20 - 10) / 100)
                projected[f"{key}_worst_case"] = value * 0.75
                projected[f"{key}_best_case"] = value * 1.25
            else:
                projected[f"{key}_analysis"] = "Simulated"

        result = SimulationResult(
            id=str(uuid.uuid4()),
            scenario_id=scenario.id,
            projected_outcomes=projected,
            risks_identified=["Risco de execução", "Incerteza de mercado", "Restrições orçamentárias"][:hash(scenario.id) % 4],
            feasibility_score=round(60 + (hash(scenario.id + "feasibility") % 35), 1),
            recommendation=self._generate_recommendation(scenario),
            confidence=round(65 + (hash(scenario.id) % 30), 1),
            details={
                "assumptions": scenario.assumptions,
                "time_horizon": "12 months",
                "scenario_type": scenario.scenario_type.value,
            },
        )
        self._results[result.id] = result
        scenario.status = "completed"
        return result

    def _generate_recommendation(self, scenario: Scenario) -> str:
        if scenario.scenario_type == ScenarioType.WHAT_IF:
            return "Cenário viável com monitoramento de riscos."
        elif scenario.scenario_type == ScenarioType.FORECAST:
            return "Projeção positiva, manter estratégia atual."
        elif scenario.scenario_type == ScenarioType.SIMULATION:
            return "Simulação concluída. Recomenda-se validação com dados reais."
        return "Analisar resultados e ajustar parâmetros."

    async def compare_scenarios(self, scenario_ids: List[str]) -> Dict[str, Any]:
        results = [self._results.get(sid) for sid in scenario_ids if self._results.get(sid)]
        if not results:
            return {"error": "No scenarios found"}

        best = max(results, key=lambda r: r.feasibility_score)
        return {
            "best_scenario": best.scenario_id,
            "best_score": best.feasibility_score,
            "comparison": {
                r.scenario_id: {"feasibility": r.feasibility_score, "confidence": r.confidence}
                for r in results
            },
            "recommendation": f"Cenário {best.scenario_id} apresenta melhor viabilidade.",
        }

    async def get_scenario(self, scenario_id: str) -> Optional[Scenario]:
        return self._scenarios.get(scenario_id)

    async def get_result(self, result_id: str) -> Optional[SimulationResult]:
        return self._results.get(result_id)

    async def list_scenarios(self) -> List[Scenario]:
        return list(self._scenarios.values())

    async def list_results(self) -> List[SimulationResult]:
        return list(self._results.values())
