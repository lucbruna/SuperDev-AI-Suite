"""Python file scanner: parses a source file with the AST parser."""
from __future__ import annotations

from typing import Any

from modules.architecture_graph.parsers import python_parser


def scan(text: str, rel_path: str = "") -> dict[str, Any]:
    """Scan a Python source file. Returns the parsed structure + language."""
    parsed = python_parser.parse(text, rel_path)
    parsed["language"] = "python"
    parsed["rel_path"] = rel_path
    return parsed
