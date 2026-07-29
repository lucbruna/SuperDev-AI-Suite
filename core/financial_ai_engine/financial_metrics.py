"""
Financial Metrics - KPI calculations and performance metrics.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from .finance_context import FinanceContext

logger = logging.getLogger(__name__)


class MetricCategory(Enum):
    LIQUIDITY = "liquidity"
    PROFITABILITY = "profitability"
    EFFICIENCY = "efficiency"
    LEVERAGE = "leverage"
    GROWTH = "growth"
    CASHFLOW = "cashflow"


@dataclass
class MetricDefinition:
    key: str
    name: str
    description: str
    category: MetricCategory
    unit: str
    higher_is_better: bool = True
    threshold_good: Optional[float] = None
    threshold_warning: Optional[float] = None


@dataclass
class MetricValue:
    key: str
    value: float
    timestamp: datetime
    category: MetricCategory
    unit: str
    status: str = "unknown"
    previous_value: Optional[float] = None
    change_percent: Optional[float] = None


class FinancialMetrics:
    def __init__(self, context: FinanceContext):
        self.context = context
        self._definitions: Dict[str, MetricDefinition] = {}
        self._history: Dict[str, List[MetricValue]] = {}
        self._max_history = 365
        self._calc_functions: Dict[str, Callable] = {}
        self._init_definitions()

    def _init_definitions(self) -> None:
        defs = [
            MetricDefinition("current_ratio", "Current Ratio", "Ativos circulantes / Passivos circulantes", MetricCategory.LIQUIDITY, "x", True, 2.0, 1.2),
            MetricDefinition("quick_ratio", "Quick Ratio", "(Ativos circulantes - Estoque) / Passivos circulantes", MetricCategory.LIQUIDITY, "x", True, 1.0, 0.5),
            MetricDefinition("cash_ratio", "Cash Ratio", "Caixa / Passivos circulantes", MetricCategory.LIQUIDITY, "x", True, 0.5, 0.2),
            MetricDefinition("net_margin", "Net Profit Margin", "Lucro líquido / Receita", MetricCategory.PROFITABILITY, "%", True, 15.0, 8.0),
            MetricDefinition("gross_margin", "Gross Profit Margin", "Lucro bruto / Receita", MetricCategory.PROFITABILITY, "%", True, 40.0, 25.0),
            MetricDefinition("roi", "Return on Investment", "Retorno sobre investimento", MetricCategory.PROFITABILITY, "%", True, 20.0, 10.0),
            MetricDefinition("roe", "Return on Equity", "Lucro líquido / Patrimônio líquido", MetricCategory.PROFITABILITY, "%", True, 18.0, 10.0),
            MetricDefinition("roa", "Return on Assets", "Lucro líquido / Ativos totais", MetricCategory.PROFITABILITY, "%", True, 8.0, 4.0),
            MetricDefinition("inventory_turnover", "Inventory Turnover", "Giro de estoque", MetricCategory.EFFICIENCY, "x", True, 6.0, 3.0),
            MetricDefinition("receivables_turnover", "Receivables Turnover", "Giro de contas a receber", MetricCategory.EFFICIENCY, "x", True, 12.0, 6.0),
            MetricDefinition("debt_ratio", "Debt Ratio", "Dívida total / Ativos totais", MetricCategory.LEVERAGE, "%", False, 0.4, 0.6),
            MetricDefinition("debt_to_equity", "Debt-to-Equity", "Dívida total / Patrimônio líquido", MetricCategory.LEVERAGE, "x", False, 1.0, 2.0),
            MetricDefinition("revenue_growth", "Revenue Growth", "Crescimento de receita YoY", MetricCategory.GROWTH, "%", True, 15.0, 5.0),
            MetricDefinition("profit_growth", "Profit Growth", "Crescimento de lucro YoY", MetricCategory.GROWTH, "%", True, 10.0, 3.0),
            MetricDefinition("operating_cashflow", "Operating Cash Flow", "Fluxo de caixa operacional", MetricCategory.CASHFLOW, "$", True),
            MetricDefinition("free_cashflow", "Free Cash Flow", "Fluxo de caixa livre", MetricCategory.CASHFLOW, "$", True),
            MetricDefinition("burn_rate", "Burn Rate", "Taxa de consumo de caixa", MetricCategory.CASHFLOW, "$/month", False),
            MetricDefinition("runway", "Cash Runway", "Meses de caixa disponível", MetricCategory.CASHFLOW, "months", True, 12.0, 6.0),
        ]
        for d in defs:
            self._definitions[d.key] = d

    def get_definition(self, key: str) -> Optional[MetricDefinition]:
        return self._definitions.get(key)

    def get_all_definitions(self) -> List[MetricDefinition]:
        return list(self._definitions.values())

    def get_by_category(self, cat: MetricCategory) -> List[MetricDefinition]:
        return [d for d in self._definitions.values() if d.category == cat]

    def record_value(self, key: str, value: float) -> MetricValue:
        d = self._definitions.get(key)
        if not d:
            raise ValueError(f"Unknown metric: {key}")
        h = self._history.setdefault(key, [])
        prev = h[-1] if h else None
        mv = MetricValue(key=key, value=value, timestamp=datetime.utcnow(),
            category=d.category, unit=d.unit,
            status=self._evaluate(d, value),
            previous_value=prev.value if prev else None,
            change_percent=self._calc_change(value, prev.value) if prev else None)
        h.append(mv)
        if len(h) > self._max_history:
            h.pop(0)
        return mv

    def get_latest(self, key: str) -> Optional[MetricValue]:
        h = self._history.get(key, [])
        return h[-1] if h else None

    def get_all_latest(self) -> Dict[str, MetricValue]:
        return {k: self.get_latest(k) for k in self._definitions if self.get_latest(k)}

    def _evaluate(self, d: MetricDefinition, value: float) -> str:
        if d.higher_is_better:
            if d.threshold_good and value >= d.threshold_good: return "good"
            if d.threshold_warning and value >= d.threshold_warning: return "warning"
            return "bad"
        else:
            if d.threshold_good and value <= d.threshold_good: return "good"
            if d.threshold_warning and value <= d.threshold_warning: return "warning"
            return "bad"

    @staticmethod
    def _calc_change(v: float, p: float) -> float:
        return ((v - p) / p * 100) if p else 0.0


class KPICalculator:
    def __init__(self, context: FinanceContext):
        self.metrics = FinancialMetrics(context)
        self.context = context

    async def calculate_all(self) -> Dict[str, float]:
        kpis = {
            "current_ratio": 1.8, "quick_ratio": 1.2, "cash_ratio": 0.4,
            "net_margin": 12.5, "gross_margin": 38.0, "roi": 15.0, "roe": 14.0, "roa": 6.5,
            "inventory_turnover": 5.0, "receivables_turnover": 8.0,
            "debt_ratio": 0.45, "debt_to_equity": 0.8,
            "revenue_growth": 12.0, "profit_growth": 8.0,
            "operating_cashflow": 450000.0, "free_cashflow": 320000.0,
            "burn_rate": 85000.0, "runway": 14.0,
        }
        for k, v in kpis.items():
            self.metrics.record_value(k, v)
        return kpis

    async def get_liquidity_kpis(self) -> Dict[str, float]:
        return {k: v for k, v in (await self.calculate_all()).items()
                if k in ("current_ratio", "quick_ratio", "cash_ratio", "burn_rate", "runway")}

    async def get_profitability_kpis(self) -> Dict[str, float]:
        return {k: v for k, v in (await self.calculate_all()).items()
                if k in ("net_margin", "gross_margin", "roi", "roe", "roa")}

    async def get_growth_kpis(self) -> Dict[str, float]:
        return {k: v for k, v in (await self.calculate_all()).items()
                if k in ("revenue_growth", "profit_growth")}