"""Chart builders for common visualizations."""

from __future__ import annotations

from typing import Any

from data_intelligence.visualization.base import (ChartBuilder,
                                                  VisualizationError, Widget)


class BarChartBuilder(ChartBuilder):
    """Bar chart: category -> value pairs."""

    def build(self, widget: Widget, data: Any) -> dict[str, Any]:
        pairs = self._pairs(data, widget)
        return {"type": "bar", "title": widget.title,
                "labels": [str(k) for k, _ in pairs],
                "values": [v for _, v in pairs],
                "config": widget.config}

    @staticmethod
    def _pairs(data: Any, widget: Widget) -> list[tuple[str, float]]:
        if isinstance(data, dict):
            return [(str(k), float(v)) for k, v in data.items()]
        if isinstance(data, list):
            label_field = widget.config.get("label", "label")
            value_field = widget.config.get("value", "value")
            pairs = []
            for item in data:
                if isinstance(item, dict):
                    pairs.append((str(item.get(label_field, "?")),
                                  float(item.get(value_field, 0))))
                else:
                    pairs.append((str(item), float(item)))
            return pairs
        raise VisualizationError("bar chart needs dict or list data")


class LineChartBuilder(ChartBuilder):
    """Line chart: series over time/categories."""

    def build(self, widget: Widget, data: Any) -> dict[str, Any]:
        if not isinstance(data, dict):
            raise VisualizationError("line chart needs dict data")
        return {"type": "line", "title": widget.title,
                "categories": [str(k) for k in data],
                "values": [float(v) for v in data.values()],
                "config": widget.config}


class PieChartBuilder(ChartBuilder):
    """Pie chart: shares of a total."""

    def build(self, widget: Widget, data: Any) -> dict[str, Any]:
        pairs = BarChartBuilder._pairs(data, widget)
        total = sum(v for _, v in pairs)
        slices = [{"label": k, "value": v,
                   "percent": round(v / total * 100, 2) if total else 0.0}
                  for k, v in pairs]
        return {"type": "pie", "title": widget.title, "slices": slices,
                "config": widget.config}


class KpiCardBuilder(ChartBuilder):
    """KPI card: single headline number."""

    def build(self, widget: Widget, data: Any) -> dict[str, Any]:
        if isinstance(data, dict):
            value = next(iter(data.values()), 0)
        elif isinstance(data, (int, float)):
            value = data
        else:
            raise VisualizationError("kpi needs a number or dict")
        return {"type": "kpi", "title": widget.title, "value": float(value),
                "config": widget.config}


class TableBuilder(ChartBuilder):
    """Table: list of records rendered as rows."""

    def build(self, widget: Widget, data: Any) -> dict[str, Any]:
        if not isinstance(data, list):
            raise VisualizationError("table needs list data")
        columns = widget.config.get("columns")
        if columns is None:
            columns = list(data[0].keys()) if data else []
        rows = [[item.get(col) for col in columns] for item in data]
        return {"type": "table", "title": widget.title,
                "columns": columns, "rows": rows, "config": widget.config}


CHART_BUILDERS: dict[str, ChartBuilder] = {
    "bar": BarChartBuilder(),
    "line": LineChartBuilder(),
    "pie": PieChartBuilder(),
    "kpi": KpiCardBuilder(),
    "table": TableBuilder(),
}
