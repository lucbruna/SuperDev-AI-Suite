"""Custom dashboard."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class CustomDashboard:
    def __init__(self, name: str) -> None:
        self.name = name
        self._widgets: List[Dict[str, Any]] = []
        self._created_at = time.time()
    def add_widget(self, widget_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        widget = {"type": widget_type, "config": config, "added_at": time.time()}
        self._widgets.append(widget)
        return widget
    def remove_widget(self, index: int) -> bool:
        if 0 <= index < len(self._widgets):
            self._widgets.pop(index)
            return True
        return False
    def get_widgets(self) -> List[Dict[str, Any]]:
        return list(self._widgets)
    def update_widget(self, index: int, config: Dict[str, Any]) -> bool:
        if 0 <= index < len(self._widgets):
            self._widgets[index]["config"] = config
            return True
        return False
    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "widgets": self._widgets, "created_at": self._created_at}
