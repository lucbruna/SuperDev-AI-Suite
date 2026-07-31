"""
Dashboard Page
"""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class DashboardWidget:
    id: str
    widget_type: str
    title: str
    size: str = "medium"
    config: dict[str, Any] = field(default_factory=dict)


class DashboardPage:
    def __init__(self):
        self.widgets: list[DashboardWidget] = []
        self.layout: str = "grid"
        self.refresh_interval: int = 5000

    def add_widget(self, widget: DashboardWidget) -> None:
        self.widgets.append(widget)

    def remove_widget(self, widget_id: str) -> None:
        self.widgets = [w for w in self.widgets if w.id != widget_id]

    def reorder_widgets(self, widget_ids: list[str]) -> None:
        widget_map = {w.id: w for w in self.widgets}
        self.widgets = [widget_map[wid] for wid in widget_ids if wid in widget_map]

    def render(self) -> dict[str, Any]:
        return {"widgets": [{"id": w.id, "type": w.widget_type, "title": w.title} for w in self.widgets], "layout": self.layout}
