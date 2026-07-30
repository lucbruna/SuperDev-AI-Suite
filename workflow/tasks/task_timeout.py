from __future__ import annotations

import signal
from typing import Any, Callable


class TaskTimeout:
    """Enforces time limits on task execution."""

    def __init__(self, default_timeout: float = 300.0) -> None:
        self._default_timeout = default_timeout

    def execute(self, fn: Callable[..., Any], timeout: float | None = None, *args: Any, **kwargs: Any) -> Any:
        timeout = timeout or self._default_timeout
        import threading
        result: list[Any] = []
        error: list[Exception] = []

        def runner() -> None:
            try:
                result.append(fn(*args, **kwargs))
            except Exception as e:
                error.append(e)

        thread = threading.Thread(target=runner, daemon=True)
        thread.start()
        thread.join(timeout=timeout)
        if thread.is_alive():
            raise TimeoutError(f"Task timed out after {timeout}s")
        if error:
            raise error[0]
        return result[0] if result else None
