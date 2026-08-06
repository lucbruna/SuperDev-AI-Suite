"""TypeScript file scanner: parses a TS source file with the TS parser."""
from __future__ import annotations

from typing import Any

from modules.ai_code_knowledge_graph.scanner._stub import stub_scan


def scan(text: str, rel_path: str = "") -> dict[str, Any]:
    """Scan TypeScript source text. Returns the parsed structure + language."""
    try:
        from modules.ai_code_knowledge_graph.parsers import typescript_parser
    except ImportError:
        return stub_scan(text, rel_path, "typescript")
    parsed = typescript_parser.parse(text, rel_path)
    parsed["language"] = "typescript"
    parsed["rel_path"] = rel_path
    return parsed
