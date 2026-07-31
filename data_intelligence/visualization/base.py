"""Base classes for visualization."""

from __future__ import annotations

from typing import Any


class VisualizationError(Exception):
    """Raised when a visualization cannot be built."""


class Widget:
    """A single dashboard widget definition."""

    def __init__(self, widget_id: str, widget_type: str,
                 title: str, **config: Any) -> None:
        self.widget_id = widget_id
        self.widget_type = widget_type
        self.title = title
        self.config = config

    def to_dict(self) -> dict[str, Any]:
        return {"widget_id": self.widget_id, "type": self.widget_type,
                "title": self.title, "config": self.config}


class ChartBuilder:
    """Turns data into chart payloads."""

    def build(self, widget: Widget,
              data: Any) -> dict[str, Any]:
        """Builds the chart payload for the widget type."""
        raise NotImplementedError
