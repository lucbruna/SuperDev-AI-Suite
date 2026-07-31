"""Factory for the Finance Intelligence Engine (Volume 35).

Builds a fully wired FinanceEngine. Core services are attached here;
subsystem engines are attached by build_finance_engine as they are
implemented (final wiring completes in Fase 6).
"""

from __future__ import annotations

from typing import Any

from finance_intelligence.finance_config import FinanceConfig
from finance_intelligence.finance_context import FinanceContext
from finance_intelligence.finance_engine import FinanceEngine
from finance_intelligence.finance_events import FinanceEvents
from finance_intelligence.finance_metrics import FinanceMetrics
from finance_intelligence.finance_registry import FinanceRegistry
from finance_intelligence.finance_runtime import FinanceRuntime
from finance_intelligence.finance_security import FinanceSecurity


def build_finance_engine(config: dict[str, Any] | None = None
                         ) -> FinanceEngine:
    """Builds a FinanceEngine with core services and all subsystems."""
    engine = FinanceEngine(
        config=FinanceConfig(**(config or {})),
        events=FinanceEvents(),
        metrics=FinanceMetrics(),
        registry=FinanceRegistry(),
        security=FinanceSecurity(),
        context=FinanceContext(),
        runtime=FinanceRuntime())

    # Subsystem attachments are added per phase:
    #   engine.attach_subsystem("accounting_engine", ...)
    #   engine.attach_subsystem("cashflow_engine", ...)
    #   ...
    return engine
