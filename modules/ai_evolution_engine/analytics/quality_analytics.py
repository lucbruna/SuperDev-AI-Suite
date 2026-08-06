"""Quality analytics: codebase quality indicators."""
from __future__ import annotations

from modules.ai_evolution_engine.core.evolution_context import EvolutionContext
from modules.ai_evolution_engine.analytics.analytics_engine import Analytic


def analyze(ctx: EvolutionContext) -> list[Analytic]:
    total = int(ctx.get_artifact("total_files", 0) or 0)
    large = int(ctx.get_artifact("large_files", 0) or 0)
    complex_units = int(ctx.get_artifact("high_complexity", 0) or 0)
    quality = 100.0
    if total:
        quality -= (large / total) * 40
    quality -= min(complex_units, 10) * 2
    quality = max(0.0, min(100.0, quality))
    return [
        Analytic("quality_score", round(quality, 2), unit="score"),
        Analytic("total_files", float(total), unit="count"),
        Analytic("large_file_ratio", round(large / total, 4) if total else 0.0, unit="ratio"),
    ]
