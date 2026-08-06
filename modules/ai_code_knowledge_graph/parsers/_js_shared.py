"""Shared lightweight structural extraction for the JS/TS family.

Dependency-free heuristic parser: imports, classes, functions, arrow
assignments and exports are extracted with line numbers. String and comment
contents are masked first (positions preserved) to reduce false positives.
"""
from __future__ import annotations

import re
from typing import Any

from modules.ai_code_knowledge_graph.ast.entities import (
    class_entity,
    file_entity,
    function_entity,
    import_entity,
)
from modules.ai_code_knowledge_graph.parsers.base_parser import line_count, parse_result

# Order matters: full-line/block constructs before inline tokens.
_MASK_RE = re.compile(
    r"//[^\n]*|/\*.*?\*/|\"(?:\\.|[^\"\\])*\"|\'(?:\\.|[^\'\\])*\'|`(?:\\.|[^`\\])*`",
    re.DOTALL,
)
# Import extraction needs quoted module sources preserved, so comments and
# template literals are blanked on a separate pass that keeps strings intact.
_COMMENT_RE = re.compile(r"//[^\n]*|/\*.*?\*/", re.DOTALL)
_TEMPLATE_RE = re.compile(r"`(?:\\.|[^`\\])*`", re.DOTALL)
_IMPORT_FROM_RE = re.compile(r"\bimport\s+(?:type\s+)?(?:\{[\s\S]*?\}|[\w*]+(?:\s*,\s*[\w*]+)*)\s*from\s+['\"]([^'\"]+)['\"]")
_IMPORT_SIDE_RE = re.compile(r"^\s*import\s+['\"]([^'\"]+)['\"]", re.MULTILINE)
_REQUIRE_RE = re.compile(r"\brequire\s*\(\s*['\"]([^'\"]+)['\"]\s*\)")
_DYNAMIC_IMPORT_RE = re.compile(r"\bimport\s*\(\s*['\"]([^'\"]+)['\"]\s*\)")
_CLASS_RE = re.compile(r"\bclass\s+([A-Za-z_$][\w$]*)(?:\s+extends\s+([A-Za-z_$][\w$.]*))?")
_FUNCTION_RE = re.compile(r"\b(?:async\s+)?function\s*\*?\s*([A-Za-z_$][\w$]*)\s*\(")
_ARROW_RE = re.compile(
    r"\b(?:export\s+)?(?:async\s+)?(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>"
)
_EXPORT_DEFAULT_FN_RE = re.compile(r"\bexport\s+default\s+(?:async\s+)?function\s*\*?\s*([A-Za-z_$][\w$]*)\s*\(")
_INTERFACE_RE = re.compile(r"\b(?:export\s+)?interface\s+([A-Za-z_$][\w$]*)")
_TYPE_ALIAS_RE = re.compile(r"\b(?:export\s+)?type\s+([A-Za-z_$][\w$]*)\s*=")
_ENUM_RE = re.compile(r"\b(?:export\s+)?(?:const\s+)?enum\s+([A-Za-z_$][\w$]*)")

_LINE_OFFSET = re.compile(r"\n")


def _blank(match: re.Match) -> str:
    """Replace the matched span with spaces, preserving line positions."""
    return re.sub(r"[^\n]", " ", match.group(0))


def _mask(code: str) -> str:
    return _MASK_RE.sub(_blank, code)


def _line_of(code: str, position: int) -> int:
    return len(_LINE_OFFSET.findall(code, 0, position)) + 1


def _exported(code: str, position: int) -> bool:
    prefix = code[max(0, position - 16) : position]
    return bool(re.search(r"\bexport\b", prefix))


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            out.append(value)
    return out


def extract_js(text: str, rel_path: str = "", *, typescript: bool = False) -> dict[str, Any]:
    """Extract normalized entities from JavaScript/TypeScript source."""
    masked = _mask(text)
    imports_code = _COMMENT_RE.sub(_blank, _TEMPLATE_RE.sub(_blank, text))
    total_lines = line_count(text)
    entities: list[dict[str, Any]] = [file_entity(rel_path or "<string>", total_lines)]

    # Imports (module bindings + side-effect + require + dynamic).
    import_sources: list[tuple[str, int, bool]] = []
    for match in _IMPORT_FROM_RE.finditer(imports_code):
        import_sources.append((match.group(1), _line_of(imports_code, match.start()), _exported(masked, match.start())))
    for match in _IMPORT_SIDE_RE.finditer(imports_code):
        import_sources.append((match.group(1), _line_of(imports_code, match.start()), False))
    for match in _REQUIRE_RE.finditer(imports_code):
        import_sources.append((match.group(1), _line_of(imports_code, match.start()), False))
    for match in _DYNAMIC_IMPORT_RE.finditer(imports_code):
        import_sources.append((match.group(1), _line_of(imports_code, match.start()), False))
    for source, line, exported in import_sources:
        entities.append(import_entity(source.split("/")[-1] or source, source=source, line=line, exported=exported))

    # Classes.
    for match in _CLASS_RE.finditer(masked):
        name = match.group(1)
        line = _line_of(masked, match.start())
        entities.append(
            class_entity(
                name,
                line,
                line,
                bases=[match.group(2)] if match.group(2) else None,
                exported=_exported(masked, match.start()),
            )
        )

    # Functions and arrow assignments.
    for match in _FUNCTION_RE.finditer(masked):
        line = _line_of(masked, match.start())
        entities.append(function_entity(match.group(1), line, line, exported=_exported(masked, match.start())))
    for match in _EXPORT_DEFAULT_FN_RE.finditer(masked):
        line = _line_of(masked, match.start())
        entities.append(function_entity(match.group(1), line, line, exported=True))
    for match in _ARROW_RE.finditer(masked):
        line = _line_of(masked, match.start())
        entities.append(function_entity(match.group(1), line, line, exported=_exported(masked, match.start())))

    # TypeScript-only declarations.
    if typescript:
        for pattern, kind in (
            (_INTERFACE_RE, "interface"),
            (_TYPE_ALIAS_RE, "type"),
            (_ENUM_RE, "enum"),
        ):
            for match in pattern.finditer(masked):
                line = _line_of(masked, match.start())
                entities.append(
                    {
                        "kind": kind,
                        "name": match.group(1),
                        "start_line": line,
                        "end_line": line,
                        "exported": _exported(masked, match.start()),
                    }
                )

    return parse_result("typescript" if typescript else "javascript", rel_path, entities)


def dedupe_imports(entities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Merge duplicate import entities by (name, source) keeping first line."""
    imports: dict[tuple[str, str | None], dict[str, Any]] = {}
    out: list[dict[str, Any]] = []
    for entity in entities:
        if entity["kind"] == "import":
            key = (entity["name"], entity.get("source"))
            if key not in imports:
                imports[key] = entity
                out.append(entity)
        else:
            out.append(entity)
    return out
