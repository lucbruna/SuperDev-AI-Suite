from __future__ import annotations

from ..monitoring_models import DashboardWidget

from .dashboard_manager import Dashboard


class DashboardTemplates:
    """Pre-built dashboard templates."""

    @staticmethod
    def _widget(
        title: str,
        metric: str,
        widget_type: str = "stat",
        position: tuple[int, int] = (0, 0),
        size: tuple[int, int] = (1, 1),
        **config: object,
    ) -> DashboardWidget:
        return DashboardWidget(
            title=title,
            metric=metric,
            widget_type=widget_type,
            position=position,
            size=size,
            config=config,
        )

    @staticmethod
    def system_overview() -> Dashboard:
        dash = Dashboard(title="System Overview", description="CPU, memory, disk, and network metrics")
        dash.widgets = [
            DashboardTemplates._widget("CPU Usage", "system.cpu.percent", position=(0, 0), size=(1, 1)),
            DashboardTemplates._widget("Memory Usage", "system.memory.percent", position=(1, 0), size=(1, 1)),
            DashboardTemplates._widget("Disk Usage", "system.disk.percent", position=(2, 0), size=(1, 1)),
            DashboardTemplates._widget("CPU Over Time", "system.cpu.percent", "chart", (0, 1), (2, 2)),
            DashboardTemplates._widget("Memory Over Time", "system.memory.percent", "chart", (2, 1), (2, 2)),
            DashboardTemplates._widget("Top Processes", "system.processes", "table", (0, 3), (4, 2)),
        ]
        dash.tags = ["system", "overview"]
        return dash

    @staticmethod
    def api_monitoring() -> Dashboard:
        dash = Dashboard(title="API Monitoring", description="Request rates, latencies, and error rates")
        dash.widgets = [
            DashboardTemplates._widget("Requests/min", "api.requests.rate", position=(0, 0), size=(1, 1)),
            DashboardTemplates._widget("Avg Latency", "api.latency.p50", position=(1, 0), size=(1, 1)),
            DashboardTemplates._widget("Error Rate", "api.errors.rate", position=(2, 0), size=(1, 1)),
            DashboardTemplates._widget("Request Rate", "api.requests.rate", "chart", (0, 1), (3, 2)),
            DashboardTemplates._widget("Latency (p50/p95/p99)", "api.latency", "chart", (0, 3), (3, 2)),
            DashboardTemplates._widget("Error Distribution", "api.errors", "heatmap", (3, 0), (1, 4)),
        ]
        dash.tags = ["api", "monitoring"]
        return dash

    @staticmethod
    def database_monitoring() -> Dashboard:
        dash = Dashboard(title="Database Monitoring", description="Database engine metrics")
        dash.widgets = [
            DashboardTemplates._widget("Connections", "database.connections", position=(0, 0), size=(1, 1)),
            DashboardTemplates._widget("Query Rate", "database.queries.rate", position=(1, 0), size=(1, 1)),
            DashboardTemplates._widget("Avg Query Time", "database.query.latency.avg", position=(2, 0), size=(1, 1)),
            DashboardTemplates._widget("Active Connections", "database.connections.active", "chart", (0, 1), (2, 2)),
            DashboardTemplates._widget("Query Latency", "database.query.latency", "chart", (2, 1), (2, 2)),
            DashboardTemplates._widget("Slow Queries", "database.slow_queries", "table", (0, 3), (4, 2)),
        ]
        dash.tags = ["database", "monitoring"]
        return dash

    @staticmethod
    def ai_monitoring() -> Dashboard:
        dash = Dashboard(title="AI Engine Monitoring", description="LLM calls, tokens, and agent metrics")
        dash.widgets = [
            DashboardTemplates._widget("LLM Calls/min", "ai.llm.requests.rate", position=(0, 0), size=(1, 1)),
            DashboardTemplates._widget("Total Tokens", "ai.llm.tokens.total", position=(1, 0), size=(1, 1)),
            DashboardTemplates._widget("Avg Latency", "ai.llm.latency.p50", position=(2, 0), size=(1, 1)),
            DashboardTemplates._widget("Token Usage", "ai.llm.tokens", "chart", (0, 1), (3, 2)),
            DashboardTemplates._widget("Agent Activity", "ai.agents.active", "chart", (0, 3), (3, 2)),
            DashboardTemplates._widget("Recent Events", "ai.events", "log", (3, 0), (1, 4)),
        ]
        dash.tags = ["ai", "llm", "agents"]
        return dash

    @staticmethod
    def business_kpis() -> Dashboard:
        dash = Dashboard(title="Business KPIs", description="Key business metrics and trends")
        dash.widgets = [
            DashboardTemplates._widget("Active Users", "business.users.active", position=(0, 0), size=(1, 1)),
            DashboardTemplates._widget("Revenue (MTD)", "business.revenue.mtd", position=(1, 0), size=(1, 1)),
            DashboardTemplates._widget("Conversion", "business.conversion.rate", position=(2, 0), size=(1, 1)),
            DashboardTemplates._widget("Daily Active Users", "business.users.dau", "chart", (0, 1), (2, 2)),
            DashboardTemplates._widget("Revenue Trend", "business.revenue.daily", "chart", (2, 1), (2, 2)),
            DashboardTemplates._widget("Top Customers", "business.customers.top", "table", (0, 3), (4, 2)),
        ]
        dash.tags = ["business", "kpi"]
        return dash
