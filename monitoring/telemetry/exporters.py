import json
from typing import Any, Dict, Optional


class ConsoleExporter:
    def export(self, data: Any) -> None:
        print(json.dumps(data, default=str, indent=2))


class FileExporter:
    def __init__(self, path: str = "telemetry.jsonl") -> None:
        self._path = path

    def export(self, data: Any, path: Optional[str] = None) -> None:
        target = path or self._path
        line = json.dumps(data, default=str)
        with open(target, "a", encoding="utf-8") as f:
            f.write(line + "\n")


class PrometheusExporter:
    def export(self, metrics: Dict[str, Any]) -> str:
        lines: list[str] = []
        for metric_type, items in metrics.items():
            for name, value in items.items():
                if isinstance(value, (int, float)):
                    lines.append(f"# HELP {name} Telemetry metric")
                    lines.append(f"# TYPE {name} {metric_type[:-1] if metric_type.endswith('s') else metric_type}")
                    lines.append(f"{name} {value}")
                elif isinstance(value, str):
                    lines.append(f"{name}_info{{value=\"{value}\"}} 1")
        return "\n".join(lines)
