from __future__ import annotations

from typing import Any, AsyncIterator

from .base_provider import BaseLLMProvider


class AWSBedrockProvider(BaseLLMProvider):
    """AWS Bedrock provider."""

    def __init__(self, model: str = "claude-3", region: str = "us-east-1") -> None:
        super().__init__(name="aws", model=model)
        self._region = region

    async def generate(self, prompt: str, **kwargs: Any) -> dict[str, Any]:
        return {
            "content": f"AWS Bedrock ({self._model}) response to: {prompt[:50]}...",
            "success": True,
            "tokens_prompt": len(prompt) // 4,
            "tokens_completion": 192,
            "finish_reason": "stop",
            "cost_usd": 0.003,
        }

    async def generate_stream(self, prompt: str, **kwargs: Any) -> AsyncIterator[dict[str, Any]]:
        async def _gen() -> AsyncIterator[dict[str, Any]]:
            yield {"content": f"AWS ({self._model}) streaming...", "finish_reason": "stop"}
        return _gen()

    async def validate(self, params: dict[str, Any]) -> bool:
        return True

    def to_dict(self) -> dict[str, Any]:
        base = super().to_dict()
        base["region"] = self._region
        return base
