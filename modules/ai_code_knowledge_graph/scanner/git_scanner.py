"""Git metadata scanner: parses git-related files with the Git parser.

Covers files such as ``.gitignore``, ``.gitattributes`` and ``.gitmodules``
so repository metadata surfaces in the knowledge graph as configuration
entities.
"""
from __future__ import annotations

from typing import Any

from modules.ai_code_knowledge_graph.scanner._stub import stub_scan


def scan(text: str, rel_path: str = "") -> dict[str, Any]:
    """Scan git metadata text. Returns the parsed structure + language."""
    try:
        from modules.ai_code_knowledge_graph.parsers import git_parser
    except ImportError:
        return stub_scan(text, rel_path, "git")
    parsed = git_parser.parse(text, rel_path)
    parsed["language"] = "git"
    parsed["rel_path"] = rel_path
    return parsed
