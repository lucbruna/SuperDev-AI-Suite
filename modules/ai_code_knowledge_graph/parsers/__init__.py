"""Parser package — per-language parsing into normalized entities.

Every parser exposes ``parse(text, rel_path="") -> dict`` returning
``{"language", "rel_path", "entities", "error"}``. Parsers are registered in
the default knowledge registry under the ``parser`` kind and can be invoked
through :func:`parse_text`.
"""
from __future__ import annotations

import importlib
from typing import Any

from modules.ai_code_knowledge_graph.core.knowledge_registry import default_registry

_PARSERS: dict[str, str] = {
    "python": "python_parser",
    "javascript": "javascript_parser",
    "typescript": "typescript_parser",
    "json": "json_parser",
    "yaml": "yaml_parser",
    "xml": "xml_parser",
    "markdown": "markdown_parser",
    "docker": "docker_parser",
    "git": "git_parser",
    "plugin": "plugin_parser",
    "workflow": "workflow_parser",
    "database": "database_parser",
}


def parse_text(language: str, text: str, rel_path: str = "") -> dict[str, Any]:
    """Parse ``text`` with the parser registered for ``language``."""
    module_name = _PARSERS.get(language)
    if module_name is None:
        return {
            "language": language,
            "rel_path": rel_path,
            "entities": [],
            "error": {"message": f"no parser registered for '{language}'"},
        }
    module = importlib.import_module(f"modules.ai_code_knowledge_graph.parsers.{module_name}")
    return module.parse(text, rel_path)


def _register_parsers() -> None:
    registry = default_registry()
    for name, module_name in _PARSERS.items():
        if registry.has("parser", name):
            continue
        module = importlib.import_module(f"modules.ai_code_knowledge_graph.parsers.{module_name}")
        registry.register("parser", name, module.parse)


_register_parsers()

__all__ = ["parse_text"]
