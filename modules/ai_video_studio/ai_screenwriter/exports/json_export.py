"""JSON export — serializes a script to JSON."""
from __future__ import annotations

import json
from typing import Any


class JsonExport:
    """Exports a script dict as JSON."""

    def export(self, script: dict[str, Any], indent: int = 2) -> str:
        return json.dumps(script, ensure_ascii=False, indent=indent)

    def to_file(self, script: dict[str, Any], path: str) -> None:
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(self.export(script))


_json_export: JsonExport | None = None


def get_json_export() -> JsonExport:
    global _json_export
    if _json_export is None:
        _json_export = JsonExport()
    return _json_export
