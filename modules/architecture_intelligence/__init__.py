"""Architecture Intelligence module (volume 2).

Sits on top of the Architecture Graph module and adds a temporal/strategic
layer: metric history and trends, LLM-powered insights (with heuristic
fallbacks), forecasts, optimization recommendations, analysis agents,
diagnostics, documentation and monitoring.

Every component degrades gracefully: when no LLM provider is configured the
module falls back to deterministic heuristics, and when the underlying graph
is unavailable it reports ``{"available": False}`` instead of raising.
"""
from __future__ import annotations

from modules.architecture_intelligence.core.engine import (
    ArchitectureIntelligenceEngine,
    get_intelligence,
)

__version__ = "1.0.0"

__all__ = ["ArchitectureIntelligenceEngine", "get_intelligence", "__version__"]
