from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..decision_config import DecisionConfig
from ..decision_models import BusinessArea, KPI, KpiGroup
from ..decision_security import DecisionSecurityManager
from .kpi_manager import KPIManager
from .metric_calculator import MetricCalculator
from .benchmark import Benchmark

logger = logging.getLogger(__name__)


class IndicatorEngine:
    def __init__(self, config: DecisionConfig, security: DecisionSecurityManager):
        self.config = config
        self.security = security
        self.kpis: Optional[KPIManager] = None
        self.calculator: Optional[MetricCalculator] = None
        self.benchmark: Optional[Benchmark] = None

    async def initialize(self) -> None:
        self.kpis = KPIManager(self.config)
        self.calculator = MetricCalculator(self.config)
        self.benchmark = Benchmark(self.config)
        logger.info("IndicatorEngine initialized")

    async def get_all_kpis(self) -> List[KPI]:
        return self.kpis.get_all()

    async def get_all_values(self) -> Dict[str, float]:
        return self.kpis.get_all_values()

    async def get_kpi(self, kpi_id: str) -> Optional[KPI]:
        return self.kpis.get(kpi_id)

    async def calculate_metric(self, metric_name: str, value: float) -> KPI:
        return self.calculator.calculate(metric_name, value)

    async def get_benchmarks(self) -> Dict[str, Any]:
        return self.benchmark.get_all()

    async def get_groups(self) -> List[KpiGroup]:
        return self.kpis.get_groups()

    async def shutdown(self) -> None:
        logger.info("IndicatorEngine shutdown")
