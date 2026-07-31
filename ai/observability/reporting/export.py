"""Report export."""
from __future__ import annotations

import json
from typing import Any


class ReportExporter:
    def __init__(self) -> None:
        self._exports: list = []
    def export_json(self, data: dict[str, Any]) -> str:
        result = json.dumps(data, indent=2)
        self._exports.append({"format": "json", "size": len(result)})
        return result
    def export_csv(self, data: dict[str, Any]) -> str:
        lines = ["key,value"]
        for k, v in data.items():
            if isinstance(v, dict):
                for sk, sv in v.items():
                    lines.append(f"{k}.{sk},{sv}")
            else:
                lines.append(f"{k},{v}")
        result = "\n".join(lines)
        self._exports.append({"format": "csv", "size": len(result)})
        return result
    def export_markdown(self, data: dict[str, Any], title: str = "Report") -> str:
        lines = [f"# {title}", ""]
        for k, v in data.items():
            lines.append(f"## {k}")
            if isinstance(v, dict):
                for sk, sv in v.items():
                    lines.append(f"- **{sk}**: {sv}")
            else:
                lines.append(f"- {v}")
            lines.append("")
        result = "\n".join(lines)
        self._exports.append({"format": "markdown", "size": len(result)})
        return result
    def get_export_history(self) -> list:
        return list(self._exports)
