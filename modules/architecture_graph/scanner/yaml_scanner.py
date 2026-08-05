"""YAML file scanner: extracts services, keys and service dependencies."""
from __future__ import annotations

from typing import Any

from modules.architecture_graph.parsers import yaml_parser


def scan(text: str, rel_path: str = "") -> dict[str, Any]:
    parsed = yaml_parser.parse(text, rel_path)
    parsed["language"] = "yaml"
    parsed["rel_path"] = rel_path
    return parsed
