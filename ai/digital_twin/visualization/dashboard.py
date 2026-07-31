"""Dashboard."""

from __future__ import annotations

from typing import Any


class Dashboard:
    def __init__(self) -> None:
        self._widgets: dict[str, dict[str, Any]] = {}
        self._layouts: dict[str, list[str]] = {}

    def add_widget(self, widget_id: str, widget_type: str, title: str, data: dict[str, Any] = None) -> dict[str, Any]:
        widget = {"widget_id": widget_id, "type": widget_type, "title": title, "data": data or {}}
        self._widgets[widget_id] = widget
        return widget

    def update_widget(self, widget_id: str, data: dict[str, Any]) -> bool:
        if widget_id not in self._widgets:
            return False
        self._widgets[widget_id]["data"] = data
        return True

    def get_widget(self, widget_id: str) -> dict[str, Any]:
        return self._widgets.get(widget_id, {"error": "not_found"})

    def create_layout(self, layout_name: str, widget_ids: list[str]) -> dict[str, Any]:
        self._layouts[layout_name] = widget_ids
        return {"layout": layout_name, "widgets": widget_ids}

    def get_layout(self, layout_name: str) -> list[dict[str, Any]]:
        widget_ids = self._layouts.get(layout_name, [])
        return [self._widgets[wid] for wid in widget_ids if wid in self._widgets]

    def list_widgets(self) -> list[dict[str, Any]]:
        return list(self._widgets.values())

    def list_layouts(self) -> list[str]:
        return list(self._layouts.keys())

    def remove_widget(self, widget_id: str) -> bool:
        if widget_id in self._widgets:
            del self._widgets[widget_id]
            return True
        return False

    def count(self) -> int:
        return len(self._widgets)
