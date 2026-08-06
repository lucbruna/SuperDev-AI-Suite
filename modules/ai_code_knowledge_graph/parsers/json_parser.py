"""JSON parser — validates the document and emits config entities."""
from __future__ import annotations

import json
from typing import Any

from modules.ai_code_knowledge_graph.ast.entities import file_entity
from modules.ai_code_knowledge_graph.parsers.base_parser import (
    error_result,
    line_count,
    parse_result,
    walk_mapping,
)


def parse(text: str, rel_path: str = "") -> dict[str, Any]:
    """Parse a JSON document into file + config entities."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        return error_result("json", rel_path, f"invalid json: {exc.msg}", line=exc.lineno)

    entities = [file_entity(rel_path or "<string>", line_count(text))]
    walk_mapping("", data, entities)
    return parse_result("json", rel_path, entities)
