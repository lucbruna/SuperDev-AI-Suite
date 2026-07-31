"""Response handler."""
from __future__ import annotations

from typing import Any


class ResponseHandler:
    def __init__(self) -> None:
        self._responses: list[dict[str, Any]] = []
    def handle(self, response: dict[str, Any]) -> dict[str, Any]:
        processed = {"content": response.get("content", ""), "model": response.get("model_id", ""), "tokens": response.get("tokens", 0), "status": "processed"}
        self._responses.append(processed)
        return processed
    def extract_content(self, response: dict[str, Any]) -> str:
        return response.get("content", "")
    def extract_tokens(self, response: dict[str, Any]) -> int:
        return response.get("tokens", 0)
    def format_response(self, response: dict[str, Any], format: str = "text") -> str:
        content = self.extract_content(response)
        if format == "json":
            import json
            return json.dumps({"content": content, "model": response.get("model_id", "")})
        return content
    def get_history(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._responses[-limit:]
    def count(self) -> int:
        return len(self._responses)
    def clear(self) -> int:
        n = len(self._responses)
        self._responses.clear()
        return n
