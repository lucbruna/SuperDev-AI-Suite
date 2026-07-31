"""Fallback manager."""
from __future__ import annotations


class FallbackManager:
    def __init__(self) -> None:
        self._chains: dict[str, list[str]] = {}
        self._failures: dict[str, int] = {}
    def set_fallback_chain(self, primary_model: str, fallbacks: list[str]) -> None:
        self._chains[primary_model] = fallbacks
    def get_next(self, failed_model: str) -> str:
        for primary, fallbacks in self._chains.items():
            if failed_model == primary:
                self._failures[failed_model] = self._failures.get(failed_model, 0) + 1
                for fb in fallbacks:
                    if self._failures.get(fb, 0) < 3:
                        return fb
        return ""
    def record_failure(self, model_id: str) -> None:
        self._failures[model_id] = self._failures.get(model_id, 0) + 1
    def record_success(self, model_id: str) -> None:
        self._failures[model_id] = 0
    def is_healthy(self, model_id: str) -> bool:
        return self._failures.get(model_id, 0) < 3
    def get_chain(self, primary_model: str) -> list[str]:
        return [primary_model] + self._chains.get(primary_model, [])
    def list_chains(self) -> dict[str, list[str]]:
        return dict(self._chains)
    def get_failure_counts(self) -> dict[str, int]:
        return dict(self._failures)
    def reset_failures(self, model_id: str = "") -> None:
        if model_id:
            self._failures[model_id] = 0
        else:
            self._failures.clear()
    def remove_chain(self, primary_model: str) -> bool:
        if primary_model in self._chains:
            del self._chains[primary_model]
            return True
        return False
