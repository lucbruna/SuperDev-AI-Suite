"""Workflow descriptor scanner: parses workflow files with the Workflow parser.

Catches descriptors living under any ``workflows`` directory, e.g.
``.github/workflows/*.yml`` or ``modules/*/workflows/*.yaml``.
"""
from __future__ import annotations

from typing import Any

from modules.ai_code_knowledge_graph.scanner._stub import stub_scan


def scan(text: str, rel_path: str = "") -> dict[str, Any]:
    """Scan a workflow descriptor. Returns the parsed structure + language."""
    try:
        from modules.ai_code_knowledge_graph.parsers import workflow_parser
    except ImportError:
        return stub_scan(text, rel_path, "workflow")
    parsed = workflow_parser.parse(text, rel_path)
    parsed["language"] = "workflow"
    parsed["rel_path"] = rel_path
    return parsed
