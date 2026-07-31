"""Protocol helpers shared by Collaboration subsystems."""

from __future__ import annotations

import uuid
import re
from typing import Any, Protocol


class Commentable(Protocol):
    """Anything that can receive comments."""

    def add_comment(self, comment: dict[str, Any]) -> dict[str, Any]: ...


class Reviewable(Protocol):
    """Anything that can be reviewed."""

    def add_review(self, review: dict[str, Any]) -> dict[str, Any]: ...


class Approvable(Protocol):
    """Anything that can go through an approval flow."""

    def start_approval(self, target_id: str, flow: str) -> dict[str, Any]: ...


def new_id(prefix: str) -> str:
    """Generates a prefixed unique identifier."""
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def safe_get(data: dict[str, Any], key: str, default: Any = None) -> Any:
    """Dot-path aware lookup: 'a.b.c' walks nested dicts."""
    value: Any = data
    for part in key.split("."):
        if not isinstance(value, dict) or part not in value:
            return default
        value = value[part]
    return value


def coerce_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value).strip().lower() in {"true", "1", "yes", "sim", "on"}


def coerce_number(value: Any) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    return float(str(value).replace(",", ".").strip())


def extract_mentions(text: str, prefix: str = "@") -> list[str]:
    """Extracts unique @mentions from a piece of text."""
    pattern = re.compile(rf"{re.escape(prefix)}([A-Za-z0-9_.-]+)")
    return list(dict.fromkeys(pattern.findall(text or "")))
