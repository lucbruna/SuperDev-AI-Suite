"""Shared helpers for the parser package."""
from __future__ import annotations

from typing import Any

from modules.ai_code_knowledge_graph.ast.entities import config_entity


def parse_result(
    language: str,
    rel_path: str,
    entities: list[dict[str, Any]],
    error: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the canonical parser output dict."""
    return {"language": language, "rel_path": rel_path, "entities": entities, "error": error}


def error_result(language: str, rel_path: str, message: str, line: int | None = None) -> dict[str, Any]:
    """Parser output for an unparseable input (no entities, error record)."""
    error: dict[str, Any] = {"message": message}
    if line is not None:
        error["line"] = line
    return parse_result(language, rel_path, [], error)


def line_count(text: str) -> int:
    return len(text.splitlines())


def load_yaml(text: str) -> Any:
    """Return parsed YAML or ``None`` when PyYAML is unavailable or unparseable."""
    try:
        import yaml  # type: ignore[import-not-found]
    except ImportError:
        return None
    try:
        return yaml.safe_load(text)
    except Exception:  # noqa: BLE001 — caller falls back to a heuristic scan
        return None


def has_yaml() -> bool:
    try:
        import yaml  # noqa: F401
    except ImportError:
        return False
    return True


def walk_mapping(prefix: str, data: Any, entities: list[dict[str, Any]]) -> None:
    """Emit config entities for a nested dict/list structure (JSON/YAML/XML)."""
    if isinstance(data, dict):
        for key, value in data.items():
            # YAML 1.1 keys can be non-strings (e.g. ``on`` → True); normalize.
            key = str(key)
            path = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                entities.append(config_entity(path, value="object"))
                walk_mapping(path, value, entities)
            elif isinstance(value, list):
                scalar = all(isinstance(item, (str, int, float, bool)) or item is None for item in value)
                if scalar and len(value) <= 50:
                    entities.append(config_entity(path, value=value))
                else:
                    entities.append(config_entity(path, value="array"))
                    walk_mapping(path, value, entities)
            else:
                entities.append(config_entity(path, value=value))
    elif isinstance(data, list):
        for index, item in enumerate(data):
            if isinstance(item, (dict, list)):
                walk_mapping(f"{prefix}[{index}]", item, entities)
            else:
                entities.append(config_entity(f"{prefix}[{index}]", value=item))
