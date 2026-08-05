"""JSON file scanner: extracts keys and declared dependencies."""
from __future__ import annotations

from typing import Any

from modules.architecture_graph.parsers import json_parser


def scan(text: str, rel_path: str = "") -> dict[str, Any]:
    parsed = json_parser.parse(text, rel_path)
    parsed["language"] = "json"
    parsed["rel_path"] = rel_path
    return parsed
