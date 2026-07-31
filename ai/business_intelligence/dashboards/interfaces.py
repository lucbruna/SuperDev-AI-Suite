"""Dashboard interfaces."""
from abc import ABC, abstractmethod

from .models import Dashboard, Widget, WidgetData


class DashboardBuilderInterface(ABC):
    @abstractmethod
    async def create_dashboard(self, dashboard: Dashboard) -> Dashboard:
        pass

    @abstractmethod
    async def update_dashboard(self, dashboard_id: str, updates: dict) -> Dashboard:
        pass

    @abstractmethod
    async def delete_dashboard(self, dashboard_id: str) -> bool:
        pass

    @abstractmethod
    async def get_dashboard(self, dashboard_id: str) -> Dashboard | None:
        pass

    @abstractmethod
    async def list_dashboards(self, tags: list[str] | None = None) -> list[Dashboard]:
        pass


class WidgetRendererInterface(ABC):
    @abstractmethod
    async def render_widget(self, widget: Widget, filters: dict | None = None) -> WidgetData:
        pass

    @abstractmethod
    async def refresh_widget(self, widget_id: str) -> WidgetData:
        pass


class DashboardShareInterface(ABC):
    @abstractmethod
    async def share(self, dashboard_id: str, user_id: str, permissions: list[str]) -> bool:
        pass

    @abstractmethod
    async def unshare(self, dashboard_id: str, user_id: str) -> bool:
        pass

    @abstractmethod
    async def get_permissions(self, dashboard_id: str) -> dict[str, list[str]]:
        pass
