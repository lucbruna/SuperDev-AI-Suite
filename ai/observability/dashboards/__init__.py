"""Dashboards subsystem."""
from .ai_dashboard import AIDashboard
from .cloud_dashboard import CloudDashboard
from .custom_dashboard import CustomDashboard
from .dashboard_engine import DashboardEngine
from .project_dashboard import ProjectDashboard
from .security_dashboard import SecurityDashboard
from .system_dashboard import SystemDashboard

__all__ = [
    "DashboardEngine", "SystemDashboard", "AIDashboard", "SecurityDashboard",
    "ProjectDashboard", "CloudDashboard", "CustomDashboard"
]
