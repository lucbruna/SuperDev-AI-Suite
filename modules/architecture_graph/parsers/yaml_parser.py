"""YAML parser (best-effort, with a regex fallback).

Used for docker-compose files, workflow definitions and plugin manifests.
Prefers PyYAML when installed; falls back to a shallow key extractor so
scanning never crashes on a missing optional dependency.
"""
from __future__ import annotations

import re
from typing import Any

_TOP_KEY_RE = re.compile(r"^([A-Za-z_][\w\-]*):\s*$")
_ITEM_KEY_RE = re.compile(r"^\s{2,}([A-Za-z_][\w\-]*):\s*$")
_SVC_KEY_RE = re.compile(r"^([A-Za-z_][\w\-]*):\s*$")


def _parse_with_yaml(text: str) -> dict[str, Any] | None:
    try:
        import yaml  # type: ignore[import-not-found]
    except ImportError:
        return None
    try:
        data = yaml.safe_load(text)
    except Exception:
        return None
    if not isinstance(data, dict):
        return {}
    return data


def _fallback(text: str) -> dict[str, Any]:
    top_keys: list[str] = []
    nested: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        top = _TOP_KEY_RE.match(line)
        if top and not line.startswith((" ", "\t")):
            name = top.group(1)
            if name is None:
                continue
            current = name
            top_keys.append(name)
            nested.setdefault(name, [])
            continue
        if current and line.startswith(("  ", "\t")):
            item = _ITEM_KEY_RE.match(line)
            if item:
                nested[current].append(item.group(1))
    return {"keys": top_keys, "nested_keys": nested, "fallback": True}


def parse(text: str, path: str = "") -> dict[str, Any]:
    data = _parse_with_yaml(text)
    if data is None:
        return _fallback(text)
    services = list((data.get("services") or {}).keys()) if isinstance(data.get("services"), dict) else []
    depends_on: list[str] = []
    for service in (data.get("services") or {}).values() if isinstance(data.get("services"), dict) else []:
        if isinstance(service, dict):
            dep = service.get("depends_on")
            if isinstance(dep, list):
                depends_on.extend(str(d) for d in dep)
            elif isinstance(dep, dict):
                depends_on.extend(dep.keys())
    return {
        "keys": list(data.keys()),
        "services": services,
        "depends_on": sorted(set(depends_on)),
        "image": data.get("image", "") if isinstance(data.get("image"), str) else "",
        "fallback": False,
    }
