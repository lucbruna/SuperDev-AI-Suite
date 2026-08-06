"""JavaScript file scanner: parses a JS source file with the JS parser."""
from __future__ import annotations

from typing import Any

from modules.ai_code_knowledge_graph.scanner._stub import stub_scan


def scan(text: str, rel_path: str = "") -> dict[str, Any]:
    """Scan JavaScript source text. Returns the parsed structure + language."""
    try:
        from modules.ai_code_knowledge_graph.parsers import javascript_parser
    except ImportError:
        return stub_scan(text, rel_path, "javascript")
    parsed = javascript_parser.parse(text, rel_path)
    parsed["language"] = "javascript"
    parsed["rel_path"] = rel_path
    return parsed
