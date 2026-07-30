from __future__ import annotations

import uuid
from typing import Any, Callable


class WorkerTask:
    """Represents a unit of work for a worker."""

    def __init__(self, task_id: str | None = None, action: Callable[..., Any] | None = None) -> None:
        self.id = task_id or str(uuid.uuid4())
        self._action = action
        self._result: Any = None
        self._error: str | None = None

    def execute(self) -> None:
        if self._action:
            try:
                self._result = self._action()
            except Exception as exc:
                self._error = str(exc)

    @property
    def result(self) -> Any:
        return self._result

    @property
    def error(self) -> str | None:
        return self._error

    @property
    def succeeded(self) -> bool:
        return self._error is None
