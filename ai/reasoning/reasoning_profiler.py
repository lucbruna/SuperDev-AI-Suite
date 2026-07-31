from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


class ReasoningProfiler:
    """Profiles reasoning operations for performance analysis."""

    def __init__(self):
        self._marks: dict[str, float] = {}

    def start(self, label: str = "root") -> None:
        self._marks[label] = datetime.now(UTC).timestamp()

    def stop(self, label: str = "root") -> float:
        start = self._marks.pop(label, 0.0)
        if start == 0:
            return 0.0
        return (datetime.now(UTC).timestamp() - start) * 1000

    def profile(self, label: str, func: Any, *args: Any, **kwargs: Any) -> tuple[Any, float]:
        self.start(label)
        try:
            result = func(*args, **kwargs)
            return result, self.stop(label)
        except Exception:
            self.stop(label)
            raise

    def report(self) -> dict[str, Any]:
        return {"active_marks": list(self._marks.keys())}
