"""Technical debt analytics: estimated remediation effort."""
from __future__ import annotations

from modules.ai_evolution_engine.core.evolution_context import EvolutionContext
from modules.ai_evolution_engine.analytics.analytics_engine import Analytic


def analyze(ctx: EvolutionContext) -> list[Analytic]:
    large = int(ctx.get_artifact("large_files", 0) or 0)
    complex_units = int(ctx.get_artifact("high_complexity", 0) or 0)
    outdated = int(ctx.get_artifact("outdated_dependencies", 0) or 0)
    # Deterministic estimation: each unit maps to abstract effort points.
    effort = large * 5 + complex_units * 3 + outdated * 2
    return [
        Analytic("debt_effort_points", float(effort), unit="points"),
        Analytic("large_files", float(large), unit="count"),
        Analytic("high_complexity_units", float(complex_units), unit="count"),
    ]
