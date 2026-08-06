"""Plugin parser — plugin descriptors (plugin.json / plugin.yaml / plugin.yml)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from modules.ai_code_knowledge_graph.ast.entities import file_entity, make_entity
from modules.ai_code_knowledge_graph.ast.entities import KIND_PLUGIN
from modules.ai_code_knowledge_graph.parsers.base_parser import (
    error_result,
    line_count,
    load_yaml,
    parse_result,
    walk_mapping,
)


def _dependencies(data: dict[str, Any]) -> list[Any]:
    deps = data.get("dependencies") or data.get("requires") or []
    if isinstance(deps, dict):
        return list(deps)
    if isinstance(deps, str):
        return [deps]
    return deps if isinstance(deps, list) else []


def parse(text: str, rel_path: str = "") -> dict[str, Any]:
    """Parse a plugin descriptor into a plugin entity + config entities."""
    lower = rel_path.lower()
    data: Any = None
    if lower.endswith(".json"):
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            return error_result("plugin", rel_path, f"invalid plugin json: {exc.msg}", line=exc.lineno)
    else:
        data = load_yaml(text)

    entities: list[dict[str, Any]] = [file_entity(rel_path or "<string>", line_count(text))]

    if isinstance(data, dict):
        name = data.get("name") or Path(rel_path).stem
        entities.append(
            make_entity(
                KIND_PLUGIN,
                str(name),
                1,
                max(line_count(text), 1),
                version=data.get("version"),
                entry=data.get("entry") or data.get("main") or data.get("entrypoint"),
                dependencies=_dependencies(data),
            )
        )
        walk_mapping("", data, entities)
    else:
        entities.append(make_entity(KIND_PLUGIN, Path(rel_path).stem, 1, max(line_count(text), 1)))

    return parse_result("plugin", rel_path, entities)
