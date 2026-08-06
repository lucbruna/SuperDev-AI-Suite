"""Shared fallback for language scanners whose parser is not yet available.

Produces a minimal parsed payload so the knowledge pipeline stays runnable
before the parser phase ships. Each scanner replaces the fallback by
importing its dedicated parser; the stub keeps the whole module import-clean
and testable at every build stage.
"""
from __future__ import annotations

from typing import Any


def stub_scan(text: str, rel_path: str, language: str) -> dict[str, Any]:
    """Return a minimal parsed payload with a single ``file`` entity."""
    line_count = len(text.splitlines())
    return {
        "language": language,
        "rel_path": rel_path,
        "entities": [
            {
                "kind": "file",
                "name": rel_path,
                "start_line": 1,
                "end_line": max(line_count, 1),
                "line_count": line_count,
            }
        ],
        "error": None,
    }
