from __future__ import annotations

from typing import Any

from .base_adapter import BaseAdapter


class OpenAIAdapter(BaseAdapter):
    """Converts between standard format and OpenAI API format."""

    async def adapt_request(self, request: Any) -> dict[str, Any]:
        if isinstance(request, dict):
            return {
                "model": request.get("model", "gpt-4"),
                "messages": [{"role": "user", "content": request.get("prompt", "")}],
                "max_tokens": request.get("max_tokens", 1024),
                "temperature": request.get("temperature", 0.7),
            }
        return {
            "model": "gpt-4",
            "messages": [{"role": "user", "content": str(request)}],
        }

    async def adapt_response(self, response: Any) -> dict[str, Any]:
        if isinstance(response, dict):
            content = ""
            choices = response.get("choices", [])
            if choices and isinstance(choices[0], dict):
                msg = choices[0].get("message", {})
                content = msg.get("content", "")

            usage = response.get("usage", {})
            return {
                "content": content,
                "success": True,
                "tokens_prompt": usage.get("prompt_tokens", 0),
                "tokens_completion": usage.get("completion_tokens", 0),
                "finish_reason": choices[0].get("finish_reason", "stop") if choices else "stop",
                "model": response.get("model", ""),
            }
        return {"content": str(response), "success": True}

    def to_dict(self) -> dict[str, Any]:
        base = super().to_dict()
        base["provider"] = "openai"
        return base
