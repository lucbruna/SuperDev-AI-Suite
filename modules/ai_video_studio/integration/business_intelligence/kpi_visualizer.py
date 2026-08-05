"""KPI Visualizer — builds sparkline series and summary briefs."""
from __future__ import annotations

import math
from typing import Any

from modules.ai_video_studio.integration._brief import build_brief


class KPIVisualizer:
    """Computes KPI sparkline data and narration."""

    def visualize(self, *, name: str = "revenue", series: list[float] | None = None,
                  voice: str = "default") -> dict[str, Any]:
        series = [float(v) for v in (series or [100, 120, 110, 150, 180, 200])]
        if len(series) < 2:
            series = [100.0, 110.0]
        growth = (series[-1] - series[0]) / series[0] if series[0] else 0.0
        peak = max(series)
        scenes = [
            f"KPI {name} across {len(series)} periods.",
            f"Started at {series[0]:g} and closed at {series[-1]:g} — {growth:+.1%}.",
            f"Peak value {peak:g} shown in the chart.",
        ]
        brief = build_brief("bi", f"{name} KPI", scenes, voice=voice, name=name).to_dict()
        brief["meta"]["sparkline"] = [round(v, 2) for v in series]
        brief["meta"]["growth"] = round(growth, 4)
        brief["meta"]["peak"] = round(peak, 2)
        return brief

    @staticmethod
    def zscore(series: list[float]) -> list[float]:
        """Standard-score a series (used by anomaly detection elsewhere)."""
        n = len(series)
        if n == 0:
            return []
        mean = sum(series) / n
        var = sum((v - mean) ** 2 for v in series) / n
        std = math.sqrt(var) or 1.0
        return [round((v - mean) / std, 3) for v in series]


_kpi_visualizer: KPIVisualizer | None = None


def get_kpi_visualizer() -> KPIVisualizer:
    global _kpi_visualizer
    if _kpi_visualizer is None:
        _kpi_visualizer = KPIVisualizer()
    return _kpi_visualizer
