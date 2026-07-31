"""Widget renderer."""

from datetime import datetime
from typing import Any

from .interfaces import WidgetRendererInterface
from .models import Widget, WidgetData


class WidgetRenderer(WidgetRendererInterface):
    def __init__(self, data_sources: dict[str, Any] | None = None):
        self._data_sources = data_sources or {}
        self._cache: dict[str, WidgetData] = {}

    async def render_widget(self, widget: Widget, filters: dict | None = None) -> WidgetData:
        source = self._data_sources.get(widget.data_source)
        data = None
        if source and callable(source):
            try:
                data = await source(filters) if filters else await source()
            except Exception as e:
                return WidgetData(
                    widget_id=widget.widget_id,
                    error=str(e),
                    timestamp=datetime.now(),
                )
        wd = WidgetData(
            widget_id=widget.widget_id,
            data=data,
            timestamp=datetime.now(),
            metadata={"widget_type": widget.widget_type.value, "title": widget.title},
        )
        self._cache[widget.widget_id] = wd
        return wd

    async def refresh_widget(self, widget_id: str) -> WidgetData:
        cached = self._cache.get(widget_id)
        if cached:
            cached.timestamp = datetime.now()
            return cached
        return WidgetData(widget_id=widget_id, error="Widget not found", timestamp=datetime.now())

    def register_source(self, name: str, callable_obj) -> None:
        self._data_sources[name] = callable_obj
