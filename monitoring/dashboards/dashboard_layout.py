from __future__ import annotations

from typing import Any, Literal

from ..monitoring_models import DashboardWidget

LayoutMode = Literal["grid", "flex", "freeform"]


class DashboardLayout:
    """Manages widget positioning and layout within a dashboard."""

    def __init__(self, mode: LayoutMode = "grid") -> None:
        self._mode = mode
        self._columns = 4
        self._gap = 16

    @property
    def mode(self) -> str:
        return self._mode

    @property
    def columns(self) -> int:
        return self._columns

    def arrange(self, widgets: list[DashboardWidget]) -> list[dict[str, Any]]:
        if self._mode == "grid":
            return self._arrange_grid(widgets)
        elif self._mode == "flex":
            return self._arrange_flex(widgets)
        return self._arrange_freeform(widgets)

    def _arrange_grid(self, widgets: list[DashboardWidget]) -> list[dict[str, Any]]:
        arranged: list[dict[str, Any]] = []
        for widget in widgets:
            col, row = widget.position
            w, h = widget.size
            arranged.append({
                "widget_id": widget.widget_id,
                "title": widget.title,
                "type": widget.widget_type,
                "grid_column": f"{col + 1} / span {max(w, 1)}",
                "grid_row": f"{row + 1} / span {max(h, 1)}",
            })
        return arranged

    def _arrange_flex(self, widgets: list[DashboardWidget]) -> list[dict[str, Any]]:
        arranged: list[dict[str, Any]] = []
        for widget in widgets:
            w, h = widget.size
            arranged.append({
                "widget_id": widget.widget_id,
                "title": widget.title,
                "type": widget.widget_type,
                "flex_basis": f"{max(w, 1) / self._columns * 100}%",
                "height": f"{max(h, 1) * 200}px",
            })
        return arranged

    def _arrange_freeform(self, widgets: list[DashboardWidget]) -> list[dict[str, Any]]:
        arranged: list[dict[str, Any]] = []
        for widget in widgets:
            col, row = widget.position
            w, h = widget.size
            arranged.append({
                "widget_id": widget.widget_id,
                "title": widget.title,
                "type": widget.widget_type,
                "left": f"{col * 260}px",
                "top": f"{row * 220}px",
                "width": f"{max(w, 1) * 260 - self._gap}px",
                "height": f"{max(h, 1) * 220 - self._gap}px",
            })
        return arranged
