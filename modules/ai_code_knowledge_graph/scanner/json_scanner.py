"""JSON file scanner: parses a JSON document with the JSON parser."""
from __future__ import annotations

from typing import Any

from modules.ai_code_knowledge_graph.scanner._stub import stub_scan


def scan(text: str, rel_path: str = "") -> dict[str, Any]:
    """Scan JSON source text. Returns the parsed structure + language."""
    try:
        from modules.ai_code_knowledge_graph.parsers import json_parser
    except ImportError:
        return stub_scan(text, rel_path, "json")
    parsed = json_parser.parse(text, rel_path)
    parsed["language"] = "json"
    parsed["rel_path"] = rel_path
    return parsed
