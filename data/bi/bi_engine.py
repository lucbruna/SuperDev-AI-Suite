from __future__ import annotations

import statistics
from typing import Any

from ..data_models import KPI, DashboardConfig, DataRecord, MetricDefinition


class BIEngine:
    """Business Intelligence — dashboards, KPIs, metrics, report builder, filters, permissions."""

    def __init__(self, engine: Any) -> None:
        self.engine = engine
        self.config = engine.config.bi
        self._kpis: dict[str, KPI] = {}
        self._metrics: dict[str, MetricDefinition] = {}
        self._dashboards: dict[str, DashboardConfig] = {}
        self._roles: dict[str, set[str]] = {}
        self._initialized = False

    async def initialize(self) -> None:
        self._initialized = True

    async def shutdown(self) -> None:
        self._initialized = False

    # -- KPIs ----------------------------------------------------------------

    def create_kpi(self, name: str, metric: str, target: float = 0.0, unit: str = "") -> KPI:
        kpi = KPI(name=name, metric=metric, target=target, unit=unit)
        self._kpis[kpi.kpi_id] = kpi
        self.engine.registry.register_kpi(kpi)
        return kpi

    def list_kpis(self) -> list[KPI]:
        return list(self._kpis.values())

    def remove_kpi(self, kpi_id: str) -> bool:
        """Remove a KPI and its registry entry. Returns True if removed."""
        if kpi_id not in self._kpis:
            return False
        del self._kpis[kpi_id]
        registry = getattr(self.engine, "registry", None)
        if registry is not None and hasattr(registry, "_kpis"):
            registry._kpis.pop(kpi_id, None)  # noqa: SLF001
        return True

    def update_kpi(self, kpi_id: str, current: float) -> bool:
        kpi = self._kpis.get(kpi_id)
        if not kpi:
            return False
        kpi.current = current
        return True

    def kpi_status(self, kpi: KPI) -> dict[str, Any]:
        if kpi.target <= 0:
            return {"kpi": kpi.name, "current": kpi.current, "status": "no_target"}
        pct = (kpi.current / kpi.target) * 100
        status = "on_track" if pct >= 100 else ("warning" if pct >= 75 else "behind")
        return {"kpi": kpi.name, "current": kpi.current, "target": kpi.target, "pct": round(pct, 1), "status": status}

    # -- metrics -------------------------------------------------------------

    def define_metric(self, name: str, expression: str, unit: str = "") -> MetricDefinition:
        metric = MetricDefinition(name=name, expression=expression, unit=unit)
        self._metrics[metric.metric_id] = metric
        return metric

    def compute_metric(self, metric: MetricDefinition, records: list[DataRecord]) -> float:
        values = [
            r.data.get(metric.expression)
            for r in records
            if isinstance(r.data.get(metric.expression), (int, float))
        ]
        if not values:
            return 0.0
        return sum(values) / len(values)

    # -- dashboards ----------------------------------------------------------

    def create_dashboard(self, name: str, owner: str = "") -> DashboardConfig:
        dashboard = DashboardConfig(name=name, owner=owner)
        self._dashboards[dashboard.dashboard_id] = dashboard
        self.engine.registry.register_dashboard(dashboard)
        return dashboard

    def add_widget(
        self,
        dashboard_id: str,
        title: str,
        widget_type: str = "chart",
        metric: str = "",
    ) -> bool:
        dashboard = self._dashboards.get(dashboard_id)
        if not dashboard:
            return False
        dashboard.widgets.append({
            "title": title,
            "widget_type": widget_type,
            "metric": metric,
        })
        return True

    def get_dashboard(self, dashboard_id: str) -> DashboardConfig | None:
        return self._dashboards.get(dashboard_id)

    def list_dashboards(self) -> list[DashboardConfig]:
        return list(self._dashboards.values())

    # -- permissions ---------------------------------------------------------

    def grant(self, role: str, dashboard_id: str) -> None:
        self._roles.setdefault(role, set()).add(dashboard_id)

    def can_view(self, role: str, dashboard_id: str) -> bool:
        return dashboard_id in self._roles.get(role, set())

    # -- stats ---------------------------------------------------------------

    def average(self, records: list[DataRecord], field: str) -> float:
        values = [r.data[field] for r in records if isinstance(r.data.get(field), (int, float))]
        return statistics.mean(values) if values else 0.0

    def status(self) -> dict[str, Any]:
        return {
            "initialized": self._initialized,
            "kpis": len(self._kpis),
            "metrics": len(self._metrics),
            "dashboards": len(self._dashboards),
        }


__all__ = ["BIEngine"]
