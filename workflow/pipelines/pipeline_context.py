from __future__ import annotations

from typing import Any


class PipelineContext:
    """Shared context passed through pipeline stages."""

    def __init__(self, initial: dict[str, Any] | None = None) -> None:
        self.data: dict[str, Any] = dict(initial or {})
        self.error: str | None = None

    def update(self, values: dict[str, Any]) -> None:
        self.data.update(values)

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value
