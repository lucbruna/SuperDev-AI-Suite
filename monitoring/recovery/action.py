from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class ActionDefinition:
    action_type: str = ""
    name: str = ""
    description: str = ""
    handler: Callable[[], None] | None = None
    timeout: float = 30.0
    retry_on_failure: bool = True
    max_retries: int = 3


class ActionExecutor:
    """Executes recovery actions with timeout and error handling."""

    def __init__(self) -> None:
        self._results: list[dict[str, Any]] = []

    def execute(self, definition: ActionDefinition) -> dict[str, Any]:
        if not definition.handler:
            return {
                "action_id": uuid.uuid4().hex[:12],
                "name": definition.name,
                "status": "failed",
                "error": "No handler defined",
            }

        action_id = uuid.uuid4().hex[:12]
        start = time.perf_counter()
        attempts = 0
        last_error: str = ""

        while attempts <= definition.max_retries:
            attempts += 1
            try:
                definition.handler()
                elapsed = (time.perf_counter() - start) * 1000
                result = {
                    "action_id": action_id,
                    "name": definition.name,
                    "status": "succeeded",
                    "attempts": attempts,
                    "duration_ms": round(elapsed, 2),
                }
                self._results.append(result)
                return result
            except Exception as e:
                last_error = str(e)
                if not definition.retry_on_failure or attempts > definition.max_retries:
                    break
                time.sleep(min(attempts * 1.0, 5.0))

        elapsed = (time.perf_counter() - start) * 1000
        result = {
            "action_id": action_id,
            "name": definition.name,
            "status": "failed",
            "attempts": attempts - 1,
            "error": last_error,
            "duration_ms": round(elapsed, 2),
        }
        self._results.append(result)
        return result
