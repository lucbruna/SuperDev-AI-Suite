"""YAML parser — config entities via PyYAML when available, else a heuristic scan.

PyYAML is optional: without it the parser still emits top-level keys, keeping
the module dependency-free.
"""
from __future__ import annotations

from typing import Any

from modules.ai_code_knowledge_graph.ast.entities import config_entity, file_entity
from modules.ai_code_knowledge_graph.parsers.base_parser import (
    error_result,
    has_yaml,
    line_count,
    load_yaml,
    parse_result,
    walk_mapping,
)


def parse(text: str, rel_path: str = "") -> dict[str, Any]:
    """Parse a YAML document into file + config entities."""
    entities = [file_entity(rel_path or "<string>", line_count(text))]

    if has_yaml():
        data = load_yaml(text)
        if data is None:
            return error_result("yaml", rel_path, "invalid yaml")
        walk_mapping("", data, entities)
        return parse_result("yaml", rel_path, entities)

    # Fallback: top-level keys.
    for index, raw in enumerate(text.splitlines(), 1):
        stripped = raw.strip()
        if (
            stripped
            and not stripped.startswith(("#", "-", " "))
            and ":" in stripped
            and not stripped.startswith(("{", "[", "|", ">"))
        ):
            key = stripped.split(":", 1)[0].strip().strip("'\"")
            if key:
                entities.append(config_entity(key, line=index, section="top-level"))
    return parse_result("yaml", rel_path, entities)
