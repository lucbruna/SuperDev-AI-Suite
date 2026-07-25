from __future__ import annotations

import uuid
from typing import AsyncIterator

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


class OpenAIProvider(BaseProvider):
    """OpenAI API provider implementation."""

    BASE_URL = "https://api.openai.com/v1"

    MODELS = [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo",
        "o1-preview",
        "o1-mini",
    ]

    EMBEDDING_MODELS = [
        "text-embedding-3-small",
        "text-embedding-3-large",
        "text-embedding-ada-002",
    ]

    PRICING = {
        "gpt-4o": {"input": 2.50, "output": 10.00},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "gpt-4-turbo": {"input": 10.00, "output": 30.00},
        "gpt-4": {"input": 30.00, "output": 60.00},
        "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
        "o1-preview": {"input": 15.00, "output": 60.00},
        "o1-mini": {"input": 3.00, "output": 12.00},
    }

    def __init__(self, api_key: str | None = None, base_url: str | None = None, **kwargs):
        super().__init__(api_key=api_key, base_url=base_url, **kwargs)
        self._client = httpx.AsyncClient(
            base_url=base_url or self.BASE_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=120.0,
        )

    @property
    def name(self) -> str:
        return "openai"

    @property
    def supported_models(self) -> list[str]:
        return self.MODELS

    def _estimate_cost(self, model: str, usage: TokenUsage) -> float:
        pricing = self.PRICING.get(model, {"input": 0.0, "output": 0.0})
        return (
            (usage.prompt_tokens / 1_000_000) * pricing["input"]
            + (usage.completion_tokens / 1_000_000) * pricing["output"]
        )

    async def complete(
        self,
        messages: list[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs,
    ) -> CompletionResponse:
        payload = {
            "model": model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        response = await self._client.post("/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()

        choice = data["choices"][0]
        usage_data = data.get("usage", {})
        usage = TokenUsage(
            prompt_tokens=usage_data.get("prompt_tokens", 0),
            completion_tokens=usage_data.get("completion_tokens", 0),
            total_tokens=usage_data.get("total_tokens", 0),
        )
        usage.estimated_cost = self._estimate_cost(model, usage)

        return CompletionResponse(
            id=data.get("id", str(uuid.uuid4())),
            model=model,
            content=choice["message"]["content"],
            finish_reason=choice.get("finish_reason"),
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
        payload = {
            "model": model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
            "stream": True,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        async with self._client.stream("POST", "/chat/completions", json=payload) as response:
            response.raise_for_status()
            chunk_id = str(uuid.uuid4())
            async for line in response.aiter_lines():
                if not line.startswith("data: "):
                    continue
                data_str = line[6:]
                if data_str.strip() == "[DONE]":
                    break

                import json
                data = json.loads(data_str)
                choice = data["choices"][0]
                delta = choice.get("delta", {})

                yield StreamChunk(
                    id=data.get("id", chunk_id),
                    model=model,
                    delta=delta.get("content", ""),
                    finish_reason=choice.get("finish_reason"),
                )

    async def embed(
        self,
        texts: list[str],
        model: str | None = None,
    ) -> EmbeddingResponse:
        model = model or self.EMBEDDING_MODELS[0]
        payload = {
            "model": model,
            "input": texts,
        }

        response = await self._client.post("/embeddings", json=payload)
        response.raise_for_status()
        data = response.json()

        embeddings = [item["embedding"] for item in data["data"]]
        usage_data = data.get("usage", {})
        usage = TokenUsage(
            prompt_tokens=usage_data.get("prompt_tokens", 0),
            completion_tokens=usage_data.get("completion_tokens", 0),
            total_tokens=usage_data.get("total_tokens", 0),
        )

        return EmbeddingResponse(
            embeddings=embeddings,
            model=model,
            usage=usage,
        )

    async def close(self) -> None:
        await self._client.aclose()


ProviderRegistry.register("openai", OpenAIProvider)
