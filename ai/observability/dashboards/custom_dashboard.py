"""Custom dashboard."""

from __future__ import annotations

import time
from typing import Any


class CustomDashboard:
    def __init__(self, name: str) -> None:
        self.name = name
        self._widgets: list[dict[str, Any]] = []
        self._created_at = time.time()

    def add_widget(self, widget_type: str, config: dict[str, Any]) -> dict[str, Any]:
        widget = {"type": widget_type, "config": config, "added_at": time.time()}
        self._widgets.append(widget)
        return widget

    def remove_widget(self, index: int) -> bool:
        if 0 <= index < len(self._widgets):
            self._widgets.pop(index)
            return True
        return False

    def get_widgets(self) -> list[dict[str, Any]]:
        return list(self._widgets)

    def update_widget(self, index: int, config: dict[str, Any]) -> bool:
        if 0 <= index < len(self._widgets):
            self._widgets[index]["config"] = config
            return True
        return False

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "widgets": self._widgets, "created_at": self._created_at}
