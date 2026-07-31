"""Metrics exporter."""

from __future__ import annotations

import json
import time
from typing import Any


class MetricsExporter:
    def __init__(self) -> None:
        self._exports: list[dict[str, Any]] = []

    def export_prometheus(self, data: dict[str, list[dict[str, Any]]]) -> str:
        lines = []
        for name, points in data.items():
            lines.append(f"# HELP {name} {name} metric")
            lines.append(f"# TYPE {name} gauge")
            for p in points[-1:]:
                labels = ",".join(f'{k}="{v}"' for k, v in p.get("labels", {}).items())
                label_str = f"{{{labels}}}" if labels else ""
                lines.append(f"{name}{label_str} {p['value']}")
        self._exports.append({"format": "prometheus", "timestamp": time.time(), "size": len(lines)})
        return "\n".join(lines)

    def export_json(self, data: dict[str, list[dict[str, Any]]]) -> str:
        self._exports.append({"format": "json", "timestamp": time.time(), "size": len(data)})
        return json.dumps(data, indent=2)

    def export_csv(self, data: dict[str, list[dict[str, Any]]]) -> str:
        lines = ["name,value,timestamp"]
        for name, points in data.items():
            for p in points:
                lines.append(f"{name},{p['value']},{p.get('timestamp', '')}")
        self._exports.append({"format": "csv", "timestamp": time.time(), "size": len(lines)})
        return "\n".join(lines)

    def get_export_history(self) -> list[dict[str, Any]]:
        return list(self._exports)
