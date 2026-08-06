"""XML parser — element tree walk emitting config entities."""
from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Any

from modules.ai_code_knowledge_graph.ast.entities import config_entity, file_entity
from modules.ai_code_knowledge_graph.parsers.base_parser import error_result, line_count, parse_result

_MAX_DEPTH = 8


def _local(tag: str) -> str:
    return tag.split("}")[-1]


def _walk_element(element: ET.Element, path: str, entities: list[dict[str, Any]], depth: int) -> None:
    name = f"{path}/{_local(element.tag)}" if path else _local(element.tag)
    attrs = {_local(key): value for key, value in element.attrib.items()}
    children = list(element)
    if children and depth < _MAX_DEPTH:
        entities.append(config_entity(name, value="element", attrs=attrs))
        for child in children:
            _walk_element(child, name, entities, depth + 1)
    elif children:
        entities.append(config_entity(name, value="element", attrs=attrs, child_count=len(children)))
    else:
        entities.append(config_entity(name, value=(element.text or "").strip() or None, attrs=attrs))


def parse(text: str, rel_path: str = "") -> dict[str, Any]:
    """Parse an XML document into file + config entities."""
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        return error_result("xml", rel_path, f"invalid xml: {exc}", line=exc.position[0])

    entities = [file_entity(rel_path or "<string>", line_count(text))]
    _walk_element(root, "", entities, 0)
    return parse_result("xml", rel_path, entities)
