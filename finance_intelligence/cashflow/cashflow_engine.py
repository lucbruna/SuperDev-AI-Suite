"""Cashflow subsystem facade (Volume 35).

Aggregates inflow/outflow management, cash projection and liquidity
analysis.
"""

from __future__ import annotations

from typing import Any

from finance_intelligence.cashflow.cash_projection import CashProjection
from finance_intelligence.cashflow.inflow_manager import InflowManager
from finance_intelligence.cashflow.liquidity_analysis import (
    LiquidityAnalysis)
from finance_intelligence.cashflow.outflow_manager import OutflowManager
from finance_intelligence.finance_events import FinanceEvents
from finance_intelligence.finance_metrics import FinanceMetrics
from finance_intelligence.finance_registry import FinanceRegistry


class CashflowEngine:
    """Aggregate facade over the cashflow subsystems."""

    def __init__(self, registry: FinanceRegistry | None = None,
                 events: FinanceEvents | None = None,
                 metrics: FinanceMetrics | None = None) -> None:
        self.registry = registry or FinanceRegistry()
        self.events = events or FinanceEvents()
        self.metrics = metrics or FinanceMetrics()
        self.inflows = InflowManager(self.registry, self.events, self.metrics)
        self.outflows = OutflowManager(self.registry, self.events,
                                       self.metrics)
        self.projection = CashProjection(self.registry, self.events,
                                         self.metrics)
        self.liquidity = LiquidityAnalysis(self.registry, self.events)

    # -- conveniences --------------------------------------------------------
    def register_inflow(self, description: str, amount: float,
                        source: str = "", scheduled_for: float = 0.0):
        return self.inflows.register(description, amount, source,
                                     scheduled_for)

    def register_outflow(self, description: str, amount: float,
                         payee: str = "", scheduled_for: float = 0.0):
        return self.outflows.register(description, amount, payee,
                                      scheduled_for)

    def project(self, opening_balance: float, horizon_days: int = 30):
        return self.projection.project(opening_balance, horizon_days)

    def analyze(self, opening_balance: float):
        return self.liquidity.analyze(
            opening_balance, self.inflows.list_inflows(),
            self.outflows.list_outflows())

    def stats(self) -> dict[str, Any]:
        return {
            "inflows": self.inflows.total(),
            "outflows": self.outflows.total(),
            "net": round(
                self.inflows.total() - self.outflows.total(), 2),
        }
