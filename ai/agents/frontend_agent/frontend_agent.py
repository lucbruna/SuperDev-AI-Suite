from __future__ import annotations

from typing import Any

from .accessibility import Accessibility
from .charts import Charts
from .component_generator import ComponentGenerator
from .forms import Forms
from .page_generator import PageGenerator
from .responsive import Responsive
from .router_generator import RouterGenerator
from .state_manager import StateManager
from .theme_manager import ThemeManager
from .validation import Validation


class FrontendAgent:
    """Central orchestrator for frontend code generation."""

    def __init__(self) -> None:
        self._components = ComponentGenerator()
        self._pages = PageGenerator()
        self._routers = RouterGenerator()
        self._state = StateManager()
        self._theme = ThemeManager()
        self._forms = Forms()
        self._validation = Validation()
        self._accessibility = Accessibility()
        self._responsive = Responsive()
        self._charts = Charts()

    @property
    def components(self) -> ComponentGenerator:
        return self._components

    @property
    def pages(self) -> PageGenerator:
        return self._pages

    @property
    def routers(self) -> RouterGenerator:
        return self._routers

    @property
    def state(self) -> StateManager:
        return self._state

    @property
    def theme(self) -> ThemeManager:
        return self._theme

    @property
    def forms(self) -> Forms:
        return self._forms

    @property
    def validation(self) -> Validation:
        return self._validation

    @property
    def accessibility(self) -> Accessibility:
        return self._accessibility

    @property
    def responsive(self) -> Responsive:
        return self._responsive

    @property
    def charts(self) -> Charts:
        return self._charts

    def generate_frontend(self, spec: dict[str, Any]) -> dict[str, Any]:
        pages = spec.get("pages", [])
        for p in pages:
            self._pages.add_page(p.get("path", "/"), p.get("component", "Page"))
        return {
            "status": "generated",
            "pages": self._pages.page_count,
            "components": self._components.component_count,
        }

    def get_status(self) -> dict[str, Any]:
        return {
            "components": self._components.component_count,
            "pages": self._pages.page_count,
            "routes": self._routers.route_count,
            "stores": self._state.store_count,
            "fields": self._forms.field_count,
        }

    def to_dict(self) -> dict[str, Any]:
        return {"agent": "frontend_agent", "status": self.get_status()}
