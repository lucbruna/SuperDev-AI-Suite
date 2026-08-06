"""Docker parser — instructions and base-image dependencies."""
from __future__ import annotations

import re
from typing import Any

from modules.ai_code_knowledge_graph.ast.entities import (
    config_entity,
    file_entity,
    make_entity,
)
from modules.ai_code_knowledge_graph.ast.entities import KIND_DEPENDENCY, KIND_INSTRUCTION
from modules.ai_code_knowledge_graph.parsers.base_parser import parse_result

_INSTRUCTION_RE = re.compile(
    r"^\s*(FROM|RUN|CMD|ENTRYPOINT|COPY|ADD|EXPOSE|ENV|WORKDIR|LABEL|ARG|VOLUME|USER|SHELL|STOPSIGNAL|HEALTHCHECK|ONBUILD)\b(.*)$",
    re.IGNORECASE,
)

_INSTRUCTIONS = frozenset(
    {"FROM", "RUN", "CMD", "ENTRYPOINT", "COPY", "ADD", "EXPOSE", "ENV", "WORKDIR", "LABEL", "ARG", "VOLUME", "USER"}
)


def parse(text: str, rel_path: str = "") -> dict[str, Any]:
    """Parse a Dockerfile into instruction + dependency entities."""
    lines = text.splitlines()
    entities: list[dict[str, Any]] = [file_entity(rel_path or "<string>", len(lines))]

    index = 0
    while index < len(lines):
        raw = lines[index].strip()
        match = _INSTRUCTION_RE.match(raw)
        if not match:
            index += 1
            continue
        operation = match.group(1).upper()
        value = match.group(2).strip()
        # Join continuation lines (trailing backslash).
        while value.endswith("\\") and index + 1 < len(lines):
            index += 1
            value = value[:-1] + " " + lines[index].strip()

        if operation == "FROM":
            image = value.split()[0] if value else "base"
            entities.append(make_entity(KIND_DEPENDENCY, image, index + 1, index + 1, package=image))
            entities.append(make_entity(KIND_INSTRUCTION, operation, index + 1, index + 1, value=value))
        elif operation == "ENV" and "=" in value:
            key, _, env_value = value.partition("=")
            entities.append(config_entity(key.strip(), value=env_value.strip(), line=index + 1, section="docker"))
            entities.append(make_entity(KIND_INSTRUCTION, operation, index + 1, index + 1, value=value))
        elif operation in _INSTRUCTIONS:
            entities.append(make_entity(KIND_INSTRUCTION, operation, index + 1, index + 1, value=value))
        index += 1

    return parse_result("docker", rel_path, entities)
