"""Model trainer."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any


class ModelTrainer:
    def __init__(self) -> None:
        self._sessions: list[dict[str, Any]] = []

    def train(
        self, model_id: str, dataset: list[dict[str, Any]], config: dict[str, Any] = None, callback: Callable = None
    ) -> dict[str, Any]:
        config = config or {"epochs": 10, "lr": 0.001, "batch_size": 32}
        session = {
            "model_id": model_id,
            "config": config,
            "started_at": time.time(),
            "status": "running",
            "epoch": 0,
            "loss": 1.0,
            "samples": len(dataset),
        }
        for epoch in range(1, config["epochs"] + 1):
            session["epoch"] = epoch
            session["loss"] = max(0.01, 1.0 - (epoch / config["epochs"]) * 0.9)
            if callback:
                callback(session)
        session["status"] = "completed"
        session["completed_at"] = time.time()
        self._sessions.append(session)
        return session

    def get_session(self, index: int = -1) -> dict[str, Any]:
        if not self._sessions:
            return {"error": "no_sessions"}
        return self._sessions[index]

    def list_sessions(self) -> list[dict[str, Any]]:
        return self._sessions

    def count(self) -> int:
        return len(self._sessions)

    def clear(self) -> int:
        n = len(self._sessions)
        self._sessions.clear()
        return n
