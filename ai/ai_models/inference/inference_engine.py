"""Inference engine."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any


class InferenceEngine:
    def __init__(self) -> None:
        self._handlers: dict[str, Callable] = {}
        self._history: list[dict[str, Any]] = []
        self._started = False

    def start(self) -> None:
        self._started = True

    def register_handler(self, model_id: str, handler: Callable) -> None:
        self._handlers[model_id] = handler

    def infer(self, model_id: str, prompt: str, **kwargs: Any) -> dict[str, Any]:
        handler = self._handlers.get(model_id)
        if not handler:
            return {"error": "handler_not_found", "status": "failed"}
        start = time.time()
        try:
            result = handler(prompt, **kwargs)
            latency = (time.time() - start) * 1000
            entry = {"model_id": model_id, "prompt": prompt[:100], "latency_ms": latency, "status": "completed"}
            self._history.append(entry)
            return {"content": result, "model_id": model_id, "latency_ms": latency, "status": "completed"}
        except Exception as e:
            return {"error": str(e), "status": "failed"}

    def batch_infer(self, model_id: str, prompts: list[str], **kwargs: Any) -> list[dict[str, Any]]:
        return [self.infer(model_id, p, **kwargs) for p in prompts]

    def get_history(self, model_id: str = "", limit: int = 50) -> list[dict[str, Any]]:
        results = self._history
        if model_id:
            results = [h for h in results if h["model_id"] == model_id]
        return results[-limit:]

    def count(self) -> int:
        return len(self._history)

    def is_running(self) -> bool:
        return self._started
