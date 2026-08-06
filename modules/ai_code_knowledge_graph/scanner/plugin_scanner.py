"""Plugin descriptor scanner: parses plugin manifests with the Plugin parser.

Recognized descriptors are ``plugin.json``, ``plugin.yaml`` and
``plugin.yml`` wherever they appear inside the scanned tree.
"""
from __future__ import annotations

from typing import Any

from modules.ai_code_knowledge_graph.scanner._stub import stub_scan


def scan(text: str, rel_path: str = "") -> dict[str, Any]:
    """Scan a plugin descriptor. Returns the parsed structure + language."""
    try:
        from modules.ai_code_knowledge_graph.parsers import plugin_parser
    except ImportError:
        return stub_scan(text, rel_path, "plugin")
    parsed = plugin_parser.parse(text, rel_path)
    parsed["language"] = "plugin"
    parsed["rel_path"] = rel_path
    return parsed
