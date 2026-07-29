from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..decision_config import DecisionConfig
from ..decision_models import BenchmarkData, BusinessArea

logger = logging.getLogger(__name__)

INDUSTRY_BENCHMARKS = {
    "margem_operacional": {"industry_avg": 15.0, "best_in_class": 28.0},
    "nps": {"industry_avg": 55.0, "best_in_class": 85.0},
    "churn": {"industry_avg": 5.0, "best_in_class": 1.5},
    "produtividade": {"industry_avg": 75.0, "best_in_class": 95.0},
    "sla_compliance": {"industry_avg": 85.0, "best_in_class": 99.0},
}


class Benchmark:
    def __init__(self, config: DecisionConfig):
        self._config = config
        self._data: Dict[str, BenchmarkData] = {}
        self._init_data()

    def _init_data(self) -> None:
        for metric, values in INDUSTRY_BENCHMARKS.items():
            self._data[metric] = BenchmarkData(
                id=str(uuid.uuid4()),
                metric=metric,
                company_value=values["industry_avg"] * 1.15,
                industry_average=values["industry_avg"],
                best_in_class=values["best_in_class"],
                percentile=round(65 + (hash(metric) % 25), 1),
                gap=round(values["best_in_class"] - values["industry_avg"] * 1.15, 1),
                period="2026-Q2",
            )

    def get(self, metric: str) -> Optional[BenchmarkData]:
        return self._data.get(metric)

    def get_all(self) -> Dict[str, BenchmarkData]:
        return dict(self._data)

    def compare(self, metric: str, company_value: float) -> BenchmarkData:
        bench = self._data.get(metric)
        if not bench:
            raise ValueError(f"Unknown metric: {metric}")
        bench.company_value = company_value
        bench.gap = round(bench.best_in_class - company_value, 1)
        return bench
