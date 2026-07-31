from __future__ import annotations

import uuid
from collections.abc import AsyncIterator

import httpx

from backend.providers.base_provider import (
    BaseProvider,
    CompletionResponse,
    EmbeddingResponse,
    Message,
    StreamChunk,
    TokenUsage,
)
from backend.providers.provider_registry import ProviderRegistry


class AnthropicProvider(BaseProvider):
    """Anthropic Claude API provider implementation."""

    BASE_URL = "https://api.anthropic.com/v1"

    MODELS = [
        "claude-sonnet-4-20250514",
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022",
        "claude-3-opus-20240229",
        "claude-3-haiku-20240307",
    ]

    PRICING = {
        "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},
        "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
        "claude-3-5-haiku-20241022": {"input": 0.80, "output": 4.00},
        "claude-3-opus-20240229": {"input": 15.00, "output": 75.00},
        "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
    }

    def __init__(self, api_key: str | None = None, base_url: str | None = None, **kwargs):
        super().__init__(api_key=api_key, base_url=base_url, **kwargs)
        self._client = httpx.AsyncClient(
            base_url=base_url or self.BASE_URL,
            headers={
                "x-api-key": api_key or "",
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            timeout=120.0,
        )

    @property
    def name(self) -> str:
        return "anthropic"

    @property
    def supported_models(self) -> list[str]:
        return self.MODELS

    def _estimate_cost(self, model: str, usage: TokenUsage) -> float:
        pricing = self.PRICING.get(model, {"input": 0.0, "output": 0.0})
        return (
            (usage.prompt_tokens / 1_000_000) * pricing["input"]
            + (usage.completion_tokens / 1_000_000) * pricing["output"]
        )

    def _format_messages(self, messages: list[Message]) -> tuple[str, list[dict]]:
        system = ""
        formatted = []
        for msg in messages:
            if msg.role == "system":
                system = msg.content
            else:
                formatted.append({"role": msg.role, "content": msg.content})
        return system, formatted

    async def complete(
        self,
        messages: list[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs,
    ) -> CompletionResponse:
        system, formatted_messages = self._format_messages(messages)
        payload = {
            "model": model,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens or 4096,
        }
        if system:
            payload["system"] = system

        response = await self._client.post("/messages", json=payload)
        response.raise_for_status()
        data = response.json()

        content = ""
        for block in data.get("content", []):
            if block.get("type") == "text":
                content += block.get("text", "")

        usage_data = data.get("usage", {})
        usage = TokenUsage(
            prompt_tokens=usage_data.get("input_tokens", 0),
            completion_tokens=usage_data.get("output_tokens", 0),
            total_tokens=usage_data.get("input_tokens", 0) + usage_data.get("output_tokens", 0),
        )
        usage.estimated_cost = self._estimate_cost(model, usage)

        return CompletionResponse(
            id=data.get("id", str(uuid.uuid4())),
            model=model,
            content=content,
            finish_reason=data.get("stop_reason"),
            usage=usage,
        )

    async def stream(
        self,
        messages: list[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs,
    ) -> AsyncIterator[StreamChunk]:
        system, formatted_messages = self._format_messages(messages)
        payload = {
            "model": model,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens or 4096,
            "stream": True,
        }
        if system:
            payload["system"] = system

        async with self._client.stream("POST", "/messages", json=payload) as response:
            response.raise_for_status()
            chunk_id = str(uuid.uuid4())
            async for line in response.aiter_lines():
                if not line.startswith("data: "):
                    continue
                data_str = line[6:]

                import json
                data = json.loads(data_str)
                event_type = data.get("type", "")

                if event_type == "content_block_delta":
                    delta = data.get("delta", {})
                    yield StreamChunk(
                        id=chunk_id,
                        model=model,
                        delta=delta.get("text", ""),
                    )
                elif event_type == "message_stop":
                    yield StreamChunk(
                        id=chunk_id,
                        model=model,
                        delta="",
                        finish_reason="stop",
                    )

    async def embed(
        self,
        texts: list[str],
        model: str | None = None,
    ) -> EmbeddingResponse:
        raise NotImplementedError("Anthropic does not provide an embedding API")

    async def close(self) -> None:
        await self._client.aclose()


ProviderRegistry.register("anthropic", AnthropicProvider)
