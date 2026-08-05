"""JSON parser: extracts top-level keys and declared dependencies."""
from __future__ import annotations

import json
from typing import Any


def _collect_dependencies(data: Any) -> list[str]:
    deps: list[str] = []
    if isinstance(data, dict):
        for key in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
            section = data.get(key)
            if isinstance(section, dict):
                deps.extend(str(k) for k in section.keys())
            elif isinstance(section, list):
                deps.extend(str(d) for d in section)
    return deps


def parse(text: str, path: str = "") -> dict[str, Any]:
    try:
        data = json.loads(text)
    except ValueError as exc:
        return {"error": f"JSONDecodeError: {exc}", "keys": [], "dependencies": []}
    keys: list[str] = []
    if isinstance(data, dict):
        keys = list(data.keys())
    return {
        "keys": keys,
        "dependencies": _collect_dependencies(data),
        "error": None,
        "kind_hint": "package.json" if "scripts" in keys else "",
    }
