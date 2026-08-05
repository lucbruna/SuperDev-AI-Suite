"""TypeScript file scanner: parses imports and API path references."""
from __future__ import annotations

from typing import Any

from modules.architecture_graph.parsers import ts_parser


def scan(text: str, rel_path: str = "") -> dict[str, Any]:
    parsed = ts_parser.parse(text, rel_path)
    parsed["language"] = "typescript"
    parsed["rel_path"] = rel_path
    return parsed
