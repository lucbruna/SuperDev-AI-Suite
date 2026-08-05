"""Dashboard Renderer — describes dashboards and their chart layout."""
from __future__ import annotations

from typing import Any


class DashboardRenderer:
    """Builds a JSON dashboard definition (chart layout + data refs)."""

    def render(self, *, title: str = "Executive dashboard",
               charts: list[str] | None = None) -> dict[str, Any]:
        charts = charts or ["revenue_line", "sales_bar", "margin_donut"]
        return {
            "type": "dashboard",
            "title": title,
            "charts": list(charts),
            "chart_count": len(charts),
            "layout": {c: {"x": i % 2, "y": i // 2, "w": 1, "h": 1} for i, c in enumerate(charts)},
        }


_dashboard_renderer: DashboardRenderer | None = None


def get_dashboard_renderer() -> DashboardRenderer:
    global _dashboard_renderer
    if _dashboard_renderer is None:
        _dashboard_renderer = DashboardRenderer()
    return _dashboard_renderer
