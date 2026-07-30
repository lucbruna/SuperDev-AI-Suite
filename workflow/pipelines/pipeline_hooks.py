from __future__ import annotations

from typing import Any, Callable


class PipelineHooks:
    """Lifecycle hooks for pipeline execution."""

    def __init__(self) -> None:
        self._hooks: dict[str, list[Callable[..., Any]]] = {}

    def register(self, event: str, callback: Callable[..., Any]) -> None:
        self._hooks.setdefault(event, []).append(callback)

    def run(self, event: str, *args: Any, **kwargs: Any) -> None:
        for cb in self._hooks.get(event, []):
            cb(*args, **kwargs)
