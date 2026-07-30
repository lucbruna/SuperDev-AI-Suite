from __future__ import annotations

from typing import Any


class RetryEngine:
    """Retries failed operations with configurable strategies."""

    def __init__(self, max_retries: int = 3):
        self._max_retries = max_retries
        self._strategies: dict[str, Any] = {}

    def add_strategy(self, name: str, strategy: Any) -> None:
        self._strategies[name] = strategy

    async def retry(self, context: dict[str, Any]) -> dict[str, Any]:
        attempts = 0
        last_error: str | None = None
        while attempts < self._max_retries:
            try:
                strategy = self._strategies.get(context.get("strategy", "default"))
                if strategy:
                    result = await strategy(context)
                    return {"success": True, "result": result, "attempts": attempts + 1}
                return {"success": False, "error": "No strategy found", "attempts": attempts + 1}
            except Exception as e:
                last_error = str(e)
                attempts += 1
        return {"success": False, "error": last_error, "attempts": attempts}
