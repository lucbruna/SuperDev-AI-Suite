"""TypeScript / TSX source parser.

TypeScript imports are a superset of JavaScript imports; the extraction
logic is shared with the JS parser (type-only imports included).
"""
from __future__ import annotations

from typing import Any

from modules.architecture_graph.parsers.js_parser import parse as _parse_js


def parse(text: str, path: str = "") -> dict[str, Any]:
    result = _parse_js(text, path)
    result["language"] = "typescript"
    return result
