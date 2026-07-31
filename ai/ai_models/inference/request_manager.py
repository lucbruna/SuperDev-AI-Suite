"""Request manager."""

from __future__ import annotations

import time
import uuid
from typing import Any


class RequestManager:
    def __init__(self) -> None:
        self._requests: dict[str, dict[str, Any]] = {}
        self._queue: list[str] = []

    def create_request(
        self, prompt: str, model_id: str = "", max_tokens: int = 1024, temperature: float = 0.7
    ) -> dict[str, Any]:
        req_id = str(uuid.uuid4())[:8]
        request = {
            "id": req_id,
            "prompt": prompt,
            "model_id": model_id,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "status": "pending",
            "created_at": time.time(),
        }
        self._requests[req_id] = request
        self._queue.append(req_id)
        return request

    def get_request(self, req_id: str) -> dict[str, Any]:
        return self._requests.get(req_id, {})

    def complete_request(self, req_id: str, response: dict[str, Any]) -> bool:
        req = self._requests.get(req_id)
        if req:
            req["status"] = "completed"
            req["response"] = response
            req["completed_at"] = time.time()
            if req_id in self._queue:
                self._queue.remove(req_id)
            return True
        return False

    def cancel_request(self, req_id: str) -> bool:
        req = self._requests.get(req_id)
        if req:
            req["status"] = "cancelled"
            if req_id in self._queue:
                self._queue.remove(req_id)
            return True
        return False

    def get_queue(self) -> list[str]:
        return list(self._queue)

    def queue_size(self) -> int:
        return len(self._queue)

    def list_requests(self, status: str = "", limit: int = 50) -> list[dict[str, Any]]:
        results = list(self._requests.values())
        if status:
            results = [r for r in results if r["status"] == status]
        return results[-limit:]

    def count(self) -> int:
        return len(self._requests)
