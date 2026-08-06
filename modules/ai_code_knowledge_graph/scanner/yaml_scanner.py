"""YAML file scanner: parses a YAML source file with the YAML parser."""
from __future__ import annotations

from typing import Any

from modules.ai_code_knowledge_graph.scanner._stub import stub_scan


def scan(text: str, rel_path: str = "") -> dict[str, Any]:
    """Scan YAML source text. Returns the parsed structure + language."""
    try:
        from modules.ai_code_knowledge_graph.parsers import yaml_parser
    except ImportError:
        return stub_scan(text, rel_path, "yaml")
    parsed = yaml_parser.parse(text, rel_path)
    parsed["language"] = "yaml"
    parsed["rel_path"] = rel_path
    return parsed
