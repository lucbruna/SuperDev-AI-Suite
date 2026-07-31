from __future__ import annotations

from typing import Any

from .llm_interfaces import ILLMContext


class LLMContextBuilder(ILLMContext):
    """Builds and manages LLM request contexts."""

    def __init__(self, max_tokens: int = 8192) -> None:
        self._max_tokens = max_tokens

    def build(self, messages: list[dict[str, Any]], **kwargs: Any) -> dict[str, Any]:
        context: dict[str, Any] = {
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", self._max_tokens),
            "temperature": kwargs.get("temperature", 0.7),
            "top_p": kwargs.get("top_p", 1.0),
            "frequency_penalty": kwargs.get("frequency_penalty", 0.0),
            "presence_penalty": kwargs.get("presence_penalty", 0.0),
            "stop": kwargs.get("stop"),
        }

        if "system" in kwargs:
            context["system"] = kwargs["system"]

        return context

    def truncate(self, context: dict[str, Any], max_tokens: int) -> dict[str, Any]:
        messages = context.get("messages", [])
        total = 0
        truncated: list[dict[str, Any]] = []

        for msg in reversed(messages):
            content = msg.get("content", "")
            tokens = len(content) // 4
            if total + tokens > max_tokens:
                break
            total += tokens
            truncated.insert(0, msg)

        context["messages"] = truncated
        context["truncated"] = len(messages) - len(truncated)
        return context

    def to_dict(self) -> dict[str, Any]:
        return {"max_tokens": self._max_tokens}
