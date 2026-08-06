"""Dependency analytics: hygiene, duplication and outdated signals."""
from __future__ import annotations

from modules.ai_evolution_engine.core.evolution_context import EvolutionContext
from modules.ai_evolution_engine.analytics.analytics_engine import Analytic


def analyze(ctx: EvolutionContext) -> list[Analytic]:
    total = int(ctx.get_artifact("dependency_count", 0) or 0)
    outdated = int(ctx.get_artifact("outdated_dependencies", 0) or 0)
    duplicates = int(ctx.get_artifact("duplicate_dependencies", 0) or 0)
    ratio = (outdated / total) if total else 0.0
    return [
        Analytic("dependency_count", float(total), unit="count"),
        Analytic("outdated_dependencies", float(outdated), unit="count"),
        Analytic("duplicate_dependencies", float(duplicates), unit="count"),
        Analytic("outdated_ratio", round(ratio, 4), unit="ratio"),
    ]
