"""
Deviation Analysis - Budget deviation detection and analysis.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from ..finance_context import FinanceContext
from ..financial_events import FinancialEventBus
from ..financial_config import FinancialConfig

logger = logging.getLogger(__name__)


class DeviationAnalysis:
    def __init__(self, config: FinancialConfig, context: FinanceContext, event_bus: FinancialEventBus):
        self.config = config
        self.context = context

    async def analyze(self, category: str, planned: float, actual: float) -> Dict[str, Any]:
        variance = actual - planned
        variance_pct = (variance / planned * 100) if planned else 0
        return {
            "category": category, "planned": planned, "actual": actual,
            "variance": variance, "variance_percent": round(variance_pct, 2),
            "severity": "critical" if abs(variance_pct) > 20 else "warning" if abs(variance_pct) > 10 else "normal",
            "root_causes": self._identify_causes(category, variance_pct),
            "recommendations": self._recommend_actions(category, variance_pct),
        }

    async def batch_analyze(self, budgets: List[Dict[str, float]]) -> List[Dict[str, Any]]:
        return [await self.analyze(b["category"], b["planned"], b["actual"]) for b in budgets]

    def _identify_causes(self, category: str, variance: float) -> List[str]:
        if variance > 0:
            return ["Gasto acima do planejado", "Possível falta de controle"]
        return ["Economia em custos", "Processo mais eficiente"]

    def _recommend_actions(self, category: str, variance: float) -> List[str]:
        if abs(variance) > 20:
            return ["Revisar orçamento", "Identificar responsáveis", "Criar plano de ação"]
        return ["Monitorar próximo período"]