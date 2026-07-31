"""Dashboards subsystem."""
from .dashboard_engine import DashboardEngine
from .system_dashboard import SystemDashboard
from .ai_dashboard import AIDashboard
from .security_dashboard import SecurityDashboard
from .project_dashboard import ProjectDashboard
from .cloud_dashboard import CloudDashboard
from .custom_dashboard import CustomDashboard

__all__ = [
    "DashboardEngine", "SystemDashboard", "AIDashboard", "SecurityDashboard",
    "ProjectDashboard", "CloudDashboard", "CustomDashboard"
]
