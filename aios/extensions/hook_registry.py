"""HookRegistry: ordered storage and firing of hook handlers."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from aios.extensions.extension import HOOK_POINTS, HookFunc


@dataclass
class HookEntry:
    extension: str
    hook_point: str
    handler: HookFunc


@dataclass
class FireResult:
    hook_point: str
    results: list[tuple[str, Any]] = field(default_factory=list)
    errors: list[tuple[str, str]] = field(default_factory=list)


class HookRegistry:
    """Deterministic handler storage; fires in registration order."""

    def __init__(self) -> None:
        self._entries: list[HookEntry] = []
        self._index: dict[str, list[int]] = {point: [] for point in HOOK_POINTS}

    def register(self, extension: str, hook_point: str, handler: HookFunc) -> bool:
        if hook_point not in HOOK_POINTS:
            raise ValueError(f"unknown hook point {hook_point!r}; expected one of {HOOK_POINTS}")
        entry = HookEntry(extension=extension, hook_point=hook_point, handler=handler)
        self._entries.append(entry)
        self._index[hook_point].append(len(self._entries) - 1)
        return True

    def handlers(self, hook_point: str) -> list[HookEntry]:
        if hook_point not in HOOK_POINTS:
            return []
        return [self._entries[index] for index in self._index[hook_point]]

    def remove_extension(self, extension: str) -> int:
        kept = [entry for entry in self._entries if entry.extension != extension]
        removed = len(self._entries) - len(kept)
        self._entries = kept
        self._index = {point: [] for point in HOOK_POINTS}
        for index, entry in enumerate(self._entries):
            self._index[entry.hook_point].append(index)
        return removed

    def fire(
        self,
        hook_point: str,
        enabled: Callable[[str], bool],
        *args: Any,
        **kwargs: Any,
    ) -> FireResult:
        """Fire a hook point; handlers from enabled extensions run in order."""
        result = FireResult(hook_point=hook_point)
        for entry in self.handlers(hook_point):
            if not enabled(entry.extension):
                continue
            try:
                outcome = entry.handler(*args, **kwargs)
                result.results.append((entry.extension, outcome))
            except Exception as exc:  # noqa: BLE001 - isolate handler failures
                result.errors.append((entry.extension, str(exc)))
        return result

    def snapshot(self) -> dict[str, Any]:
        return {
            "total_handlers": len(self._entries),
            "by_hook_point": {
                point: len(self._index[point]) for point in HOOK_POINTS
            },
            "extensions": sorted({entry.extension for entry in self._entries}),
        }
