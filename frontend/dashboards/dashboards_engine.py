from __future__ import annotations

import logging
from typing import Any, Callable


class DashboardWidget:
    """A single widget on a dashboard."""

    def __init__(self, widget_id: str, kind: str, title: str = "", **config: Any) -> None:
        self.widget_id = widget_id
        self.kind = kind
        self.title = title
        self.config = config
        self._renderer: Callable[..., dict[str, Any]] | None = None

    def set_renderer(self, renderer: Callable[..., dict[str, Any]]) -> None:
        self._renderer = renderer

    def render(self, **props: Any) -> dict[str, Any]:
        if self._renderer is not None:
            return self._renderer(**props)
        return {"widget_id": self.widget_id, "kind": self.kind, "title": self.title, **self.config}


class DashboardsEngine:
    """Manages dashboards and their widgets."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.dashboards")
        self._dashboards: dict[str, list[DashboardWidget]] = {}
        self._layout: dict[str, dict[str, Any]] = {}

    def create(self, name: str, title: str = "", layout: str = "grid") -> None:
        if name in self._dashboards:
            raise KeyError(f"dashboard already exists: {name}")
        self._dashboards[name] = []
        self._layout[name] = {"title": title or name, "layout": layout}

    def add_widget(self, dashboard: str, widget: DashboardWidget, **placement: Any) -> None:
        if dashboard not in self._dashboards:
            raise KeyError(f"unknown dashboard: {dashboard}")
        self._dashboards[dashboard].append(widget)
        self._layout[dashboard].setdefault("widgets", {})[widget.widget_id] = placement

    def remove_widget(self, dashboard: str, widget_id: str) -> bool:
        widgets = self._dashboards.get(dashboard, [])
        for index, widget in enumerate(widgets):
            if widget.widget_id == widget_id:
                widgets.pop(index)
                self._layout[dashboard].get("widgets", {}).pop(widget_id, None)
                return True
        return False

    def render(self, dashboard: str, **props: Any) -> dict[str, Any]:
        if dashboard not in self._dashboards:
            raise KeyError(f"unknown dashboard: {dashboard}")
        return {
            "name": dashboard,
            **self._layout[dashboard],
            "widgets": [widget.render(**props) for widget in self._dashboards[dashboard]],
        }

    def list(self) -> list[str]:
        return list(self._dashboards)

    def widgets(self, dashboard: str) -> list[DashboardWidget]:
        return list(self._dashboards.get(dashboard, []))

    def remove(self, dashboard: str) -> bool:
        return self._dashboards.pop(dashboard, None) is not None
