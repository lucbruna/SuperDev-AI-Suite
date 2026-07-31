"""
Frontend Experience & User Interface Engine
Volume 25 — SuperDev AI Suite v5

Enterprise frontend platform with:
- React/TypeScript architecture
- Intelligent code editor (IDE-like)
- AI chat interface
- Dashboard engine
- Real-time communication
- Multi-tenant support
- Accessibility (WCAG 2.1)
- Responsive design
"""

from .app.app_core import App, create_app
from .app.router import Router, Route
from .app.providers import AppProvider, ThemeProvider
from .app.config import FrontendConfig
from .app.permissions import PermissionManager
from .app.initialization import AppInitializer

__all__ = [
    "App", "create_app",
    "Router", "Route",
    "AppProvider", "ThemeProvider",
    "FrontendConfig",
    "PermissionManager",
    "AppInitializer",
]
