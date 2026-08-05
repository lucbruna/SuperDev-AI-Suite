"""Dependency mapping: converts a parsed file into concrete graph edges.

Given a parsed file (output of the scanner layer) and the set of known
project files, produces a list of edges with either a resolved project
target or an explicit ``external`` marker.
"""
from __future__ import annotations

from typing import Any

from modules.architecture_graph.dependency.import_mapper import (
    js_module_to_path,
    python_module_to_path,
)


def map_file_dependencies(
    parsed: dict[str, Any],
    *,
    rel_path: str,
    known_files: set[str],
) -> list[dict[str, Any]]:
    """Return dependency records for a parsed file.

    Each record: ``{"target": str | None, "module": str, "kind": str}``.
    ``target`` None means the import is external (stdlib / third-party).
    """
    language = parsed.get("language", "")
    records: list[dict[str, Any]] = []
    seen: set[str] = set()

    if language == "python":
        for imp in parsed.get("imports", []):
            module = imp.get("module") or ""
            if not module:
                continue
            target = python_module_to_path(module, known_files=known_files)
            key = f"py:{module}"
            if key in seen:
                continue
            seen.add(key)
            records.append(
                {
                    "target": target,
                    "module": module,
                    "kind": "imports",
                    "external": target is None,
                }
            )
    elif language in {"javascript", "typescript"}:
        for imp in parsed.get("imports", []):
            spec = imp.get("module") or ""
            if not spec:
                continue
            target = js_module_to_path(spec, current_rel=rel_path, known_files=known_files)
            key = f"js:{spec}"
            if key in seen:
                continue
            seen.add(key)
            records.append(
                {
                    "target": target,
                    "module": spec,
                    "kind": "imports",
                    "external": target is None and not spec.startswith((".", "@/")),
                }
            )
    return records
