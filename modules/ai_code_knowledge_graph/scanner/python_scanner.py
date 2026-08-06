"""Python file scanner: parses a source file with the AST parser."""
from __future__ import annotations

from typing import Any

from modules.ai_code_knowledge_graph.scanner._stub import stub_scan


def scan(text: str, rel_path: str = "") -> dict[str, Any]:
    """Scan Python source text. Returns the parsed structure + language."""
    try:
        from modules.ai_code_knowledge_graph.parsers import python_parser
    except ImportError:
        return stub_scan(text, rel_path, "python")
    parsed = python_parser.parse(text, rel_path)
    parsed["language"] = "python"
    parsed["rel_path"] = rel_path
    return parsed
