"""Core layer: engine facade, metric history and shared helpers."""
from __future__ import annotations

from modules.architecture_intelligence.core.engine import (
    ArchitectureIntelligenceEngine,
    get_intelligence,
)
from modules.architecture_intelligence.core.history import MetricHistory, get_history

__all__ = [
    "ArchitectureIntelligenceEngine",
    "get_intelligence",
    "MetricHistory",
    "get_history",
]
