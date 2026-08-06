"""Dockerfile scanner: parses Dockerfile instructions with the Docker parser."""
from __future__ import annotations

from typing import Any

from modules.ai_code_knowledge_graph.scanner._stub import stub_scan


def scan(text: str, rel_path: str = "") -> dict[str, Any]:
    """Scan a Dockerfile. Returns the parsed structure + language."""
    try:
        from modules.ai_code_knowledge_graph.parsers import docker_parser
    except ImportError:
        return stub_scan(text, rel_path, "docker")
    parsed = docker_parser.parse(text, rel_path)
    parsed["language"] = "docker"
    parsed["rel_path"] = rel_path
    return parsed
