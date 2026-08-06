"""Git parser — repository metadata from .git* files."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from modules.ai_code_knowledge_graph.ast.entities import config_entity, file_entity
from modules.ai_code_knowledge_graph.parsers.base_parser import parse_result

_SECTION_RE = re.compile(r"\[\s*submodule\s+[\"']([^\"']+)[\"']\s*\]")


def parse(text: str, rel_path: str = "") -> dict[str, Any]:
    """Parse git metadata text into config entities."""
    name = Path(rel_path).name.lower()
    lines = text.splitlines()
    entities: list[dict[str, Any]] = [file_entity(rel_path or "<string>", len(lines))]

    section: str | None = None
    for index, raw in enumerate(lines, 1):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        submodule = _SECTION_RE.match(stripped)
        if submodule:
            section = submodule.group(1)
            entities.append(config_entity(section, value="submodule", line=index, section="gitmodules"))
            continue
        if "=" in stripped:
            key, _, value = stripped.partition("=")
            entities.append(config_entity(key.strip(), value=value.strip(), line=index, section=section or name))
            continue
        entities.append(config_entity(stripped, value=None, line=index, section=name))

    return parse_result("git", rel_path, entities)
