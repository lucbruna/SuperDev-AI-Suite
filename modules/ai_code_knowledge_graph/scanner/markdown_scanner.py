"""Markdown file scanner: parses headings and code references."""
from __future__ import annotations

from typing import Any

from modules.ai_code_knowledge_graph.scanner._stub import stub_scan


def scan(text: str, rel_path: str = "") -> dict[str, Any]:
    """Scan Markdown source text. Returns the parsed structure + language."""
    try:
        from modules.ai_code_knowledge_graph.parsers import markdown_parser
    except ImportError:
        return stub_scan(text, rel_path, "markdown")
    parsed = markdown_parser.parse(text, rel_path)
    parsed["language"] = "markdown"
    parsed["rel_path"] = rel_path
    return parsed
