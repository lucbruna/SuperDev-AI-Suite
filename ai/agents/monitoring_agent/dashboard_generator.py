from __future__ import annotations

from typing import Any


class DashboardGenerator:
    """Generates monitoring dashboard configurations."""

    def __init__(self) -> None:
        self._panels: list[dict[str, Any]] = []

    def add_panel(self, name: str, metric: str, panel_type: str = "graph") -> str:
        self._panels.append({"name": name, "metric": metric, "type": panel_type})
        return name

    def get_panel(self, name: str) -> dict[str, Any] | None:
        for p in self._panels:
            if p["name"] == name:
                return p
        return None

    def remove_panel(self, name: str) -> bool:
        for i, p in enumerate(self._panels):
            if p["name"] == name:
                self._panels.pop(i)
                return True
        return False

    @property
    def panel_count(self) -> int:
        return len(self._panels)

    def generate(self) -> str:
        lines: list[str] = ["# Monitoring Dashboard", ""]
        for panel in self._panels:
            lines.append(f"## Panel: {panel['name']}")
            lines.append(f"- Metric: {panel['metric']}")
            lines.append(f"- Type: {panel['type']}")
            lines.append("")
        return "\n".join(lines).strip()

    def to_dict(self) -> dict[str, Any]:
        return {
            "panels": self._panels,
            "panel_count": self.panel_count,
        }
