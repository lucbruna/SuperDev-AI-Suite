from __future__ import annotations

from .dashboards_engine import DashboardWidget, DashboardsEngine


def create_default_dashboard() -> DashboardsEngine:
    """Create a default dashboard with common widgets."""
    engine = DashboardsEngine()
    engine.create("overview", title="Overview", layout="grid")
    engine.add_widget("overview", DashboardWidget("system-status", "metric", "System Status"))
    engine.add_widget("overview", DashboardWidget("agent-activity", "chart", "Agent Activity"))
    engine.add_widget("overview", DashboardWidget("resource-usage", "chart", "Resource Usage"))
    engine.add_widget("overview", DashboardWidget("recent-alerts", "list", "Recent Alerts"))
    return engine


__all__ = ["DashboardWidget", "DashboardsEngine", "create_default_dashboard"]
