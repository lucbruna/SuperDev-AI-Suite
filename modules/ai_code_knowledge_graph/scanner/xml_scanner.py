"""XML file scanner: parses an XML source file with the XML parser."""
from __future__ import annotations

from typing import Any

from modules.ai_code_knowledge_graph.scanner._stub import stub_scan


def scan(text: str, rel_path: str = "") -> dict[str, Any]:
    """Scan XML source text. Returns the parsed structure + language."""
    try:
        from modules.ai_code_knowledge_graph.parsers import xml_parser
    except ImportError:
        return stub_scan(text, rel_path, "xml")
    parsed = xml_parser.parse(text, rel_path)
    parsed["language"] = "xml"
    parsed["rel_path"] = rel_path
    return parsed
