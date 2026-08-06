"""Architecture analytics: coupling, cohesion and modularity metrics."""
from __future__ import annotations

from modules.ai_evolution_engine.core.evolution_context import EvolutionContext
from modules.ai_evolution_engine.analytics.analytics_engine import Analytic


def analyze(ctx: EvolutionContext) -> list[Analytic]:
    coupling = float(ctx.get_artifact("coupling_ratio", 0.0) or 0.0)
    circular = int(ctx.get_artifact("circular_dependencies", 0) or 0)
    modules = int(ctx.get_artifact("module_count", 0) or 0)
    cohesion = max(0.0, 1.0 - coupling)
    return [
        Analytic("coupling_ratio", round(coupling, 4), unit="ratio"),
        Analytic("cohesion_ratio", round(cohesion, 4), unit="ratio"),
        Analytic("circular_dependencies", float(circular), unit="count"),
        Analytic("module_count", float(modules), unit="count"),
    ]
