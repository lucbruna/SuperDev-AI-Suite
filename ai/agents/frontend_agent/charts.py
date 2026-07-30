from __future__ import annotations

from typing import Any


CHART_TYPES = {"bar", "line", "pie", "area", "scatter"}


class Charts:
    """Manages chart definitions and generates chart components."""

    def __init__(self) -> None:
        self._charts: dict[str, dict[str, Any]] = {}

    def add_chart(self, name: str, chart_type: str, data_fields: list[str]) -> str:
        ctype = chart_type.lower()
        if ctype not in CHART_TYPES:
            ctype = "bar"
        self._charts[name] = {
            "name": name,
            "type": ctype,
            "data_fields": data_fields,
        }
        return name

    def get_chart(self, name: str) -> dict[str, Any] | None:
        return self._charts.get(name)

    def remove_chart(self, name: str) -> bool:
        if name in self._charts:
            del self._charts[name]
            return True
        return False

    def list_charts(self) -> list[dict[str, Any]]:
        return list(self._charts.values())

    @property
    def chart_count(self) -> int:
        return len(self._charts)

    def generate_chart_code(self, name: str) -> str:
        chart = self._charts.get(name)
        if chart is None:
            return f"// Chart '{name}' not found"
        fields = ", ".join(chart["data_fields"])
        return (
            f"import React from 'react';\n"
            f"import {{ {chart['type'].title()} }} from 'react-chartjs-2';\n\n"
            f"const {name}: React.FC = () => {{\n"
            f"  const data = {{\n"
            f"    labels: ['Label'],\n"
            f"    datasets: [{{\n"
            f"      label: '{name}',\n"
            f"      data: [0],\n"
            f"    }}],\n"
            f"  }};\n\n"
            f"  return <{chart['type'].title()} data={{data}} />;\n"
            f"}};\n\n"
            f"export default {name};\n"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "charts": list(self._charts.values()),
            "chart_count": self.chart_count,
        }
