"""Markdown parser — headings, code fences, links and frontmatter."""
from __future__ import annotations

import re
from typing import Any

from modules.ai_code_knowledge_graph.ast.entities import (
    config_entity,
    file_entity,
    make_entity,
)
from modules.ai_code_knowledge_graph.ast.entities import KIND_CODE_BLOCK, KIND_LINK, KIND_SECTION
from modules.ai_code_knowledge_graph.parsers.base_parser import line_count, parse_result

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$", re.MULTILINE)
_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
_FENCE_MARK = re.compile(r"^[ \t]*(```|~~~)([\w+-]*)")


def _line_of(text: str, position: int) -> int:
    return text.count("\n", 0, position) + 1


def parse(text: str, rel_path: str = "") -> dict[str, Any]:
    """Parse Markdown into file, section, code-block, link and config entities."""
    lines = text.splitlines()
    entities: list[dict[str, Any]] = [file_entity(rel_path or "<string>", len(lines))]

    # Frontmatter (--- ... ---).
    if len(lines) >= 3 and lines[0].strip() == "---":
        end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
        if end is not None:
            for index in range(1, end):
                if ":" in lines[index]:
                    key, _, value = lines[index].partition(":")
                    entities.append(
                        config_entity(key.strip(), value=value.strip(), line=index + 1, section="frontmatter")
                    )

    # Code fences.
    in_fence = False
    fence_start = 0
    fence_lang = ""
    for index, raw in enumerate(lines, 1):
        match = _FENCE_MARK.match(raw)
        if not match:
            continue
        if not in_fence:
            in_fence, fence_start, fence_lang = True, index, match.group(2) or ""
        else:
            entities.append(
                make_entity(KIND_CODE_BLOCK, rel_path, fence_start, index, language=fence_lang)
            )
            in_fence = False

    # Headings.
    for match in _HEADING_RE.finditer(text):
        line = _line_of(text, match.start())
        entities.append(
            make_entity(KIND_SECTION, match.group(2).strip(), line, line, level=len(match.group(1)))
        )

    # Links.
    for match in _LINK_RE.finditer(text):
        line = _line_of(text, match.start())
        entities.append(make_entity(KIND_LINK, match.group(1).strip(), line, line, target=match.group(2)))

    return parse_result("markdown", rel_path, entities)
