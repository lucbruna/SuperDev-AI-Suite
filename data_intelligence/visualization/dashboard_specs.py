"""Prebuilt dashboard specs for each audience (Diretoria / Operação / TI).

The engine exposes ``visualization.default_dashboard(audience)`` so a
dashboard can be rendered right away, without manual widget wiring.
"""

from __future__ import annotations

from typing import Any

from data_intelligence.data_models import DashboardSpec
from data_intelligence.visualization.base import VisualizationError
from data_intelligence.visualization.dashboard import DashboardBuilder

_SPECS: dict[str, DashboardSpec] = {}


def _build() -> dict[str, DashboardSpec]:
    builder = DashboardBuilder()

    executive = builder.create("executive_overview", "Visão da Diretoria",
                               "executive")
    builder.add_widget(executive, "revenue", "kpi", "Receita total")
    builder.add_widget(executive, "growth", "kpi", "Crescimento (%)")
    builder.add_widget(executive, "sales_trend", "line",
                       "Vendas por mês")
    builder.add_widget(executive, "region_share", "pie",
                       "Participação por região")

    operations = builder.create("operations_floor", "Painel de Operação",
                                "operations")
    builder.add_widget(operations, "orders_today", "kpi", "Pedidos hoje")
    builder.add_widget(operations, "top_products", "bar",
                       "Produtos mais vendidos")
    builder.add_widget(operations, "order_queue", "table", "Fila de pedidos")

    it = builder.create("it_health", "Saúde de TI", "it")
    builder.add_widget(it, "uptime", "kpi", "Uptime (%)")
    builder.add_widget(it, "latency", "line", "Latência (ms)")

    return builder.dashboards


PREBUILT_DASHBOARDS: dict[str, DashboardSpec] = _build()

_DEFAULT_BY_AUDIENCE: dict[str, str] = {
    "executive": "executive_overview",
    "operations": "operations_floor",
    "it": "it_health",
}


def default_dashboard(audience: str) -> DashboardSpec:
    """Returns the prebuilt dashboard for the given audience."""
    dashboard_id = _DEFAULT_BY_AUDIENCE.get(audience)
    if dashboard_id is None:
        raise VisualizationError(f"unknown audience: {audience}")
    return PREBUILT_DASHBOARDS[dashboard_id]


def get_dashboard(dashboard_id: str) -> DashboardSpec:
    """Returns a prebuilt dashboard by id, if present."""
    spec = PREBUILT_DASHBOARDS.get(dashboard_id)
    if spec is None:
        raise VisualizationError(f"unknown dashboard: {dashboard_id}")
    return spec
