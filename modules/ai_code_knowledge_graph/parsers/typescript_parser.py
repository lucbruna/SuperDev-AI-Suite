"""TypeScript parser — lightweight structural extraction (JS + TS types)."""
from __future__ import annotations

from typing import Any

from modules.ai_code_knowledge_graph.parsers._js_shared import dedupe_imports, extract_js


def parse(text: str, rel_path: str = "") -> dict[str, Any]:
    """Parse TypeScript source text into normalized entities."""
    result = extract_js(text, rel_path, typescript=True)
    result["entities"] = dedupe_imports(result["entities"])
    return result
