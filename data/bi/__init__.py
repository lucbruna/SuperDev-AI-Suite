"""Business Intelligence subsystem package."""

from __future__ import annotations

from .bi_engine import BIEngine
from .dashboard_builder import DashboardBuilder
from .executive_dashboard import (
    KPI_AGENT_PERFORMANCE,
    KPI_AVG_DEV_TIME,
    KPI_COMPLETED_PROJECTS,
    KPI_COSTS,
    KPI_ERRORS,
    KPI_KEYS,
    ExecutiveDashboard,
)

__all__ = [
    "BIEngine",
    "ExecutiveDashboard",
    "DashboardBuilder",
    "KPI_COMPLETED_PROJECTS",
    "KPI_AVG_DEV_TIME",
    "KPI_ERRORS",
    "KPI_COSTS",
    "KPI_AGENT_PERFORMANCE",
    "KPI_KEYS",
]
