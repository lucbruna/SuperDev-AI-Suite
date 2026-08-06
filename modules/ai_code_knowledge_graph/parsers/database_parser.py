"""Database parser — SQL DDL and Prisma schemas into table/index/view entities."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from modules.ai_code_knowledge_graph.ast.entities import (
    file_entity,
    make_entity,
)
from modules.ai_code_knowledge_graph.ast.entities import KIND_ENUM, KIND_INDEX, KIND_TABLE, KIND_VIEW
from modules.ai_code_knowledge_graph.parsers.base_parser import line_count, parse_result

_CREATE_TABLE_RE = re.compile(
    r"\bCREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([`\"\w.]+)", re.IGNORECASE
)
_CREATE_INDEX_RE = re.compile(
    r"\bCREATE\s+(?:UNIQUE\s+)?INDEX\s+(?:IF\s+NOT\s+EXISTS\s+)?([`\"\w.]+)", re.IGNORECASE
)
_CREATE_VIEW_RE = re.compile(
    r"\bCREATE\s+(?:OR\s+REPLACE\s+)?VIEW\s+([`\"\w.]+)", re.IGNORECASE
)
_COLUMN_RE = re.compile(r"^\s*([`\"\w]+)\s+([a-z][\w\s()]*?)(?:,|$)", re.IGNORECASE)

_SKIP_COLUMN_KEYWORDS = frozenset(
    {"PRIMARY", "FOREIGN", "CONSTRAINT", "UNIQUE", "CHECK", "KEY", "INDEX", "REFERENCES"}
)

_MODEL_RE = re.compile(r"^\s*model\s+(\w+)\s*\{")
_ENUM_RE = re.compile(r"^\s*enum\s+(\w+)\s*\{")


def _clean(name: str) -> str:
    return name.strip().strip("`\"'")


def _line_of(text: str, position: int) -> int:
    return text.count("\n", 0, position) + 1


def _parse_sql(text: str, entities: list[dict[str, Any]]) -> None:
    lines = text.splitlines()
    current_table: str | None = None
    columns: list[str] = []
    for index, raw in enumerate(lines, 1):
        stripped = raw.strip().rstrip(";").strip()
        if not stripped or stripped.startswith(("--", "//")):
            continue
        table_match = _CREATE_TABLE_RE.search(stripped)
        if table_match:
            current_table = _clean(table_match.group(1))
            columns = []
            entities.append(make_entity(KIND_TABLE, current_table, index, index, columns=columns))
            continue
        if current_table is not None and stripped.endswith(")"):
            current_table = None
            continue
        if current_table is not None:
            column_match = _COLUMN_RE.match(stripped)
            if column_match and column_match.group(1).strip().upper() not in _SKIP_COLUMN_KEYWORDS:
                columns.append(column_match.group(1).strip("`\" '"))

    for pattern, kind in ((_CREATE_INDEX_RE, KIND_INDEX), (_CREATE_VIEW_RE, KIND_VIEW)):
        for match in pattern.finditer(text):
            entities.append(make_entity(kind, _clean(match.group(1)), _line_of(text, match.start()), _line_of(text, match.start())))


def _parse_prisma(text: str, entities: list[dict[str, Any]]) -> None:
    current: str | None = None
    kind: str | None = None
    fields: list[str] = []
    for index, raw in enumerate(text.splitlines(), 1):
        model_match = _MODEL_RE.match(raw)
        if model_match:
            current, kind, fields = model_match.group(1), KIND_TABLE, []
            entities.append(make_entity(KIND_TABLE, current, index, index, columns=fields))
            continue
        enum_match = _ENUM_RE.match(raw)
        if enum_match:
            current, kind, fields = enum_match.group(1), KIND_ENUM, []
            entities.append(make_entity(KIND_ENUM, current, index, index, values=fields))
            continue
        if current is not None and raw.strip() == "}":
            current = None
            continue
        stripped = raw.strip()
        if current is not None and stripped and not stripped.startswith("//"):
            fields.append(stripped.split()[0] if stripped.split() else stripped)


def parse(text: str, rel_path: str = "") -> dict[str, Any]:
    """Parse SQL DDL or a Prisma schema into database entities."""
    entities: list[dict[str, Any]] = [file_entity(rel_path or "<string>", line_count(text))]
    if Path(rel_path).suffix.lower() == ".prisma":
        _parse_prisma(text, entities)
    else:
        _parse_sql(text, entities)
    return parse_result("database", rel_path, entities)
