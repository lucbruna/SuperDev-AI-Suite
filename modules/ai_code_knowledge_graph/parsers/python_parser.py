"""Python parser — normalized entities via the stdlib AST extractor."""
from __future__ import annotations

from typing import Any

from modules.ai_code_knowledge_graph.ast.python_ast import extract


def parse(text: str, rel_path: str = "") -> dict[str, Any]:
    """Parse Python source text into normalized entities."""
    return extract(text, rel_path)
