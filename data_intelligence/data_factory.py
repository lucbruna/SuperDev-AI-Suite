"""Factory for the Data Intelligence Engine."""

from __future__ import annotations

from typing import Any

from data_intelligence.data_config import DataIntelligenceConfig
from data_intelligence.data_context import DataIntelligenceContext
from data_intelligence.data_engine import DataIntelligenceEngine
from data_intelligence.data_events import DataIntelligenceEvents
from data_intelligence.data_metrics import DataIntelligenceMetrics
from data_intelligence.data_registry import DataIntelligenceRegistry
from data_intelligence.data_runtime import DataIntelligenceRuntime
from data_intelligence.data_security import DataIntelligenceSecurity


def build_engine(
    config: DataIntelligenceConfig | None = None,
    events: DataIntelligenceEvents | None = None,
    metrics: DataIntelligenceMetrics | None = None,
    registry: DataIntelligenceRegistry | None = None,
    security: DataIntelligenceSecurity | None = None,
    context: DataIntelligenceContext | None = None,
    runtime: DataIntelligenceRuntime | None = None,
    **overrides: Any,
) -> DataIntelligenceEngine:
    """Builds a fully wired DataIntelligenceEngine.

    ``overrides`` are merged into the config, e.g.
    ``build_engine(max_batch_size=500)``.
    """
    if config is None:
        config = DataIntelligenceConfig(**(overrides or {}))
    else:
        config = config.merge(**overrides)
    return DataIntelligenceEngine(
        config=config,
        events=events or DataIntelligenceEvents(),
        metrics=metrics or DataIntelligenceMetrics(),
        registry=registry or DataIntelligenceRegistry(),
        security=security or DataIntelligenceSecurity(),
        context=context or DataIntelligenceContext(),
        runtime=runtime or DataIntelligenceRuntime(),
    )
