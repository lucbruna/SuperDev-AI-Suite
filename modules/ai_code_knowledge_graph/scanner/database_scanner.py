"""Database scanner: parses SQL and schema files with the Database parser.

Covers ``.sql`` files and named schemas such as ``schema.prisma`` so tables,
columns and relationships surface in the knowledge graph as database
entities.
"""
from __future__ import annotations

from typing import Any

from modules.ai_code_knowledge_graph.scanner._stub import stub_scan


def scan(text: str, rel_path: str = "") -> dict[str, Any]:
    """Scan SQL/schema text. Returns the parsed structure + language."""
    try:
        from modules.ai_code_knowledge_graph.parsers import database_parser
    except ImportError:
        return stub_scan(text, rel_path, "database")
    parsed = database_parser.parse(text, rel_path)
    parsed["language"] = "database"
    parsed["rel_path"] = rel_path
    return parsed
