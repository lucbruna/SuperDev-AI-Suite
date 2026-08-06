"""Normalized entity model for the AI Code Knowledge Graph.

Every parser emits a list of entities in this canonical shape so later
phases (graph builder, relations, semantic engine) consume a single schema::

    {"kind": str, "name": str, "start_line": int, "end_line": int, **extras}

Entity kinds cover the graph node kinds plus parser-level granularity
(methods, imports, columns, sections, instructions, ...).
"""
from __future__ import annotations

from typing import Any

KIND_FILE = "file"
KIND_MODULE = "module"
KIND_CLASS = "class"
KIND_METHOD = "method"
KIND_FUNCTION = "function"
KIND_IMPORT = "import"
KIND_INTERFACE = "interface"
KIND_TYPE = "type"
KIND_ENUM = "enum"
KIND_CONFIG = "config"
KIND_TABLE = "table"
KIND_COLUMN = "column"
KIND_INDEX = "index"
KIND_VIEW = "view"
KIND_PLUGIN = "plugin"
KIND_WORKFLOW = "workflow"
KIND_SECTION = "section"
KIND_CODE_BLOCK = "code_block"
KIND_LINK = "link"
KIND_INSTRUCTION = "instruction"
KIND_DEPENDENCY = "dependency"


def make_entity(
    kind: str,
    name: str,
    start_line: int = 1,
    end_line: int | None = None,
    **extra: Any,
) -> dict[str, Any]:
    """Build a normalized entity dict, dropping ``None`` extras."""
    entity: dict[str, Any] = {
        "kind": kind,
        "name": name,
        "start_line": int(start_line),
        "end_line": int(end_line if end_line is not None else start_line),
    }
    entity.update({key: value for key, value in extra.items() if value is not None})
    return entity


def file_entity(rel_path: str, line_count: int) -> dict[str, Any]:
    """Entity representing the whole scanned file."""
    return make_entity(KIND_FILE, rel_path, 1, max(line_count, 1), line_count=line_count)


def class_entity(
    name: str,
    start: int,
    end: int,
    *,
    bases: list[str] | None = None,
    decorators: list[str] | None = None,
    methods: list[dict[str, Any]] | None = None,
    module: str | None = None,
    exported: bool = False,
) -> dict[str, Any]:
    return make_entity(
        KIND_CLASS,
        name,
        start,
        end,
        bases=bases or [],
        decorators=decorators or [],
        methods=methods or [],
        module=module,
        exported=exported,
    )


def method_entity(
    name: str,
    start: int,
    end: int,
    *,
    params: list[str] | None = None,
    decorators: list[str] | None = None,
    static: bool = False,
    classmethod: bool = False,
    async_: bool = False,
) -> dict[str, Any]:
    return make_entity(
        KIND_METHOD,
        name,
        start,
        end,
        params=params or [],
        decorators=decorators or [],
        static=static,
        classmethod=classmethod,
        async_=async_,
    )


def function_entity(
    name: str,
    start: int,
    end: int,
    *,
    params: list[str] | None = None,
    decorators: list[str] | None = None,
    async_: bool = False,
    module: str | None = None,
    exported: bool = False,
) -> dict[str, Any]:
    return make_entity(
        KIND_FUNCTION,
        name,
        start,
        end,
        params=params or [],
        decorators=decorators or [],
        async_=async_,
        module=module,
        exported=exported,
    )


def import_entity(
    name: str,
    *,
    source: str | None = None,
    alias: str | None = None,
    line: int = 1,
    exported: bool = False,
) -> dict[str, Any]:
    return make_entity(KIND_IMPORT, name, line, line, source=source, alias=alias, exported=exported)


def config_entity(
    name: str,
    *,
    value: Any = None,
    line: int = 1,
    section: str | None = None,
    kind: str = KIND_CONFIG,
    **extra: Any,
) -> dict[str, Any]:
    return make_entity(kind, name, line, line, value=value, section=section, **extra)
