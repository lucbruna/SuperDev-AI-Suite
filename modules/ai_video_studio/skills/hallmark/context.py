"""Hallmark context — assemble and summarize context for a run."""
from __future__ import annotations
from typing import Any


class ContextBuilder:
    """Collect context parts into one bundle with a summary."""

    def __init__(self) -> None:
        pass

    def build(self, **parts: Any) -> dict[str, Any]:
        """Bundle arbitrary context parts plus size and a compact summary."""
        rendered = {key: value for key, value in parts.items() if value is not None}
        return {
            "parts": rendered,
            "size": len(rendered),
            "summary": " | ".join(f"{key}: {value}" for key, value in rendered.items()),
        }
