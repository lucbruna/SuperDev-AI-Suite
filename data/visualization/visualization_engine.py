from __future__ import annotations

from typing import Any

from ..data_models import ChartType, DashboardConfig


class VisualizationEngine:
    """Data visualization — charts, graphs, dashboards, maps, realtime, interactive."""

    def __init__(self, engine: Any) -> None:
        self.engine = engine
        self.config = engine.config.visualization
        self._dashboards: dict[str, DashboardConfig] = {}
        self._rendered: dict[str, dict[str, Any]] = {}
        self._initialized = False

    async def initialize(self) -> None:
        self._initialized = True

    async def shutdown(self) -> None:
        self._initialized = False

    def render_chart(
        self,
        chart_type: str | ChartType,
        data: dict[str, Any],
        title: str = "",
    ) -> dict[str, Any]:
        """Produce a serializable chart spec (consumable by the frontend)."""
        chart_type = ChartType(chart_type) if isinstance(chart_type, str) else chart_type
        spec: dict[str, Any] = {
            "type": chart_type.value,
            "title": title,
            "data": data,
        }
        if chart_type == ChartType.BAR:
            spec["x"] = list(data.keys())
            spec["y"] = [v for v in data.values() if isinstance(v, (int, float))]
        elif chart_type == ChartType.LINE:
            spec["points"] = [
                {"x": i, "y": v} for i, v in enumerate(data.values())
                if isinstance(v, (int, float))
            ]
        elif chart_type == ChartType.PIE:
            spec["slices"] = [
                {"label": k, "value": v} for k, v in data.items()
                if isinstance(v, (int, float))
            ]
        elif chart_type == ChartType.GAUGE:
            numeric = [v for v in data.values() if isinstance(v, (int, float))]
            spec["value"] = numeric[0] if numeric else 0.0
            spec["max"] = data.get("max", 100.0)
        elif chart_type == ChartType.FUNNEL:
            numeric = [v for v in data.values() if isinstance(v, (int, float))]
            spec["stages"] = [
                {"label": k, "value": v} for k, v in data.items()
                if isinstance(v, (int, float))
            ]
            spec["total"] = numeric[0] if numeric else 0.0
        self._rendered[f"{chart_type.value}-{len(self._rendered)}"] = spec
        self.engine.metrics.increment("visualization.charts")
        return spec

    def render_table(self, rows: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "type": "table",
            "columns": list(rows[0].keys()) if rows else [],
            "rows": rows,
        }

    def render_map(self, points: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "type": "map",
            "points": [
                {"lat": p.get("lat"), "lng": p.get("lng"), "label": p.get("label", "")}
                for p in points
            ],
        }

    def create_dashboard(self, name: str, owner: str = "") -> DashboardConfig:
        dashboard = DashboardConfig(name=name, owner=owner)
        self._dashboards[dashboard.dashboard_id] = dashboard
        self.engine.registry.register_dashboard(dashboard)
        return dashboard

    def add_chart(self, dashboard_id: str, spec: dict[str, Any]) -> bool:
        dashboard = self._dashboards.get(dashboard_id)
        if not dashboard:
            return False
        dashboard.widgets.append(spec)
        return True

    def list_dashboards(self) -> list[DashboardConfig]:
        return list(self._dashboards.values())

    def realtime_snapshot(self, stream: str, events: int = 0) -> dict[str, Any]:
        return {
            "stream": stream,
            "events_processed": events,
            "generated_at": self.engine.runtime.uptime,
        }

    def status(self) -> dict[str, Any]:
        return {
            "initialized": self._initialized,
            "dashboards": len(self._dashboards),
            "charts_rendered": len(self._rendered),
        }


__all__ = ["VisualizationEngine"]
