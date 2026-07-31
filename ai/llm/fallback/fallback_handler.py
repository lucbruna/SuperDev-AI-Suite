from __future__ import annotations

from typing import Any

from ..llm_executor import LLMExecutor


class FallbackHandler:
    """Tries providers in order until one succeeds."""

    def __init__(self) -> None:
        self._errors: dict[str, list[str]] = {}
        self._attempts = 0

    async def execute_with_fallback(
        self,
        prompt: str,
        providers: list[str],
        executor: LLMExecutor,
        **kwargs: Any,
    ) -> dict[str, Any]:
        self._attempts = 0
        for provider in providers:
            self._attempts += 1
            try:
                result = await executor.execute(provider, prompt, **kwargs)
                if result.get("success", False):
                    return result
                error = result.get("error", "Unknown error")
                self._record_error(provider, error)
            except Exception as e:
                self._record_error(provider, str(e))

        return {
            "success": False,
            "error": f"All {len(providers)} providers failed",
            "errors": dict(self._errors),
        }

    def _record_error(self, provider: str, error: str) -> None:
        if provider not in self._errors:
            self._errors[provider] = []
        self._errors[provider].append(error)

    def get_fallback_history(self) -> list[dict[str, Any]]:
        return [
            {"provider": p, "errors": errs}
            for p, errs in self._errors.items()
        ]

    @property
    def total_attempts(self) -> int:
        return self._attempts

    @property
    def success_rate(self) -> float:
        if self._attempts == 0:
            return 0.0
        successes = self._attempts - sum(len(e) for e in self._errors.values())
        return successes / self._attempts

    def reset(self) -> None:
        self._errors.clear()
        self._attempts = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_attempts": self._attempts,
            "errors_by_provider": {p: len(e) for p, e in self._errors.items()},
            "success_rate": self.success_rate,
        }
