"""Markdown file scanner: parses headings and code references."""
from __future__ import annotations

from typing import Any

from modules.architecture_graph.parsers import markdown_parser


def scan(text: str, rel_path: str = "") -> dict[str, Any]:
    parsed = markdown_parser.parse(text, rel_path)
    parsed["language"] = "markdown"
    parsed["rel_path"] = rel_path
    return parsed
