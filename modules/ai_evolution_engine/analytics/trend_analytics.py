"""Trend analytics: score deltas across cycles (from persisted history)."""
from __future__ import annotations

from modules.ai_evolution_engine.core.evolution_context import EvolutionContext
from modules.ai_evolution_engine.analytics.analytics_engine import Analytic


def analyze(ctx: EvolutionContext) -> list[Analytic]:
    history = list(ctx.memory.recall("score_history", []) or [])
    if len(history) >= 2:
        delta = float(history[-1]) - float(history[-2])
    else:
        delta = 0.0
    return [
        Analytic("score_delta", round(delta, 2), unit="points"),
        Analytic("history_len", float(len(history)), unit="count"),
    ]
