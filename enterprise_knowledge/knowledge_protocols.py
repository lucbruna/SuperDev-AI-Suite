"""Shared protocols and helpers for the Enterprise Knowledge Engine."""

from __future__ import annotations

import re
import uuid
from typing import Any

_ID_PREFIXES = {
    "node": "node",
    "relationship": "rel",
    "memory": "mem",
    "document": "doc",
    "index": "idx",
    "entity": "ent",
    "hypothesis": "hyp",
    "audit": "aud",
    "policy": "pol",
    "channel": "ekc",
    "embedding": "emb",
}

_WORD_RE = re.compile(r"[a-z0-9\u00e0-\u00fc]+")


def new_id(prefix: str = "ek") -> str:
    """Generates a short unique id with an optional prefix."""
    base = _ID_PREFIXES.get(prefix, prefix)
    return f"{base}-{uuid.uuid4().hex[:8]}"


def tokenize(text: str) -> list[str]:
    """Lowercases and splits text into word tokens."""
    return _WORD_RE.findall((text or "").lower())


def normalize(text: str) -> str:
    """Normalizes whitespace for comparisons."""
    return re.sub(r"\s+", " ", (text or "").strip())


def safe_get(data: Any, path: str, default: Any = None) -> Any:
    """Dot-path getter (``a.b.c``) that never raises."""
    current = data
    for part in path.split("."):
        if isinstance(current, dict):
            current = current.get(part)
        elif isinstance(current, (list, tuple)):
            try:
                current = current[int(part)]
            except (ValueError, IndexError):
                return default
        else:
            return default
        if current is None:
            return default
    return current


def coerce_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on", "sim"}
    return default


def coerce_number(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def top_n(items: list[Any], key, limit: int = 10) -> list[Any]:
    """Sorts ``items`` by ``key`` descending and returns the top ``limit``."""
    return sorted(items, key=key, reverse=True)[:max(0, limit)]
