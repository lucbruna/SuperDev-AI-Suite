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


class OllamaProvider(BaseProvider):
    """Ollama local LLM provider implementation."""

    DEFAULT_BASE_URL = "http://localhost:11434"

    MODELS = [
        "llama3.2",
        "llama3.1",
        "qwen2.5",
        "mistral-nemo",
        "mistral",
        "codellama",
        "deepseek-coder",
        "qwen2.5-coder",
        "phi3",
        "gemma2",
    ]

    EMBEDDING_MODELS = [
        "nomic-embed-text",
        "all-minilm",
        "snowflake-arctic-embed",
    ]

    def __init__(self, api_key: str | None = None, base_url: str | None = None, **kwargs):
        super().__init__(api_key=api_key, base_url=base_url, **kwargs)
        self._client = httpx.AsyncClient(
            base_url=base_url or self.DEFAULT_BASE_URL,
            timeout=300.0,
        )

    @property
    def name(self) -> str:
        return "ollama"

    @property
    def supported_models(self) -> list[str]:
        return self.MODELS

    async def _list_local_models(self) -> list[str]:
        response = await self._client.get("/api/tags")
        response.raise_for_status()
        data = response.json()
        return [m["name"] for m in data.get("models", [])]

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
            "stream": False,
            "temperature": temperature,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        # Ollama exposes an OpenAI-compatible API at /v1/chat/completions.
        response = await self._client.post("/v1/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()

        choice = (data.get("choices") or [{}])[0]
        message = choice.get("message", {})
        usage = data.get("usage", {}) or {}

        return CompletionResponse(
            id=data.get("id", str(uuid.uuid4())),
            model=model,
            content=message.get("content", ""),
            finish_reason=choice.get("finish_reason"),
            usage=TokenUsage(
                prompt_tokens=usage.get("prompt_tokens", 0),
                completion_tokens=usage.get("completion_tokens", 0),
                total_tokens=usage.get("total_tokens", 0),
            ),
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
            "stream": True,
            "temperature": temperature,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        # SSE format: lines like "data: {...}", terminated by "data: [DONE]".
        async with self._client.stream("POST", "/v1/chat/completions", json=payload) as response:
            response.raise_for_status()
            chunk_id = str(uuid.uuid4())

            import json

            async for line in response.aiter_lines():
                if not line.strip() or not line.startswith("data:"):
                    continue
                data_str = line[len("data:"):].strip()
                if data_str == "[DONE]":
                    break

                data = json.loads(data_str)
                choice = (data.get("choices") or [{}])[0]
                delta = choice.get("delta", {})
                content = delta.get("content", "")
                finish_reason = choice.get("finish_reason")

                if content or finish_reason:
                    yield StreamChunk(
                        id=chunk_id,
                        model=model,
                        delta=content,
                        finish_reason=finish_reason,
                    )

    async def embed(
        self,
        texts: list[str],
        model: str | None = None,
    ) -> EmbeddingResponse:
        model = model or self.EMBEDDING_MODELS[0]
        embeddings = []
        for text in texts:
            payload = {
                "model": model,
                "prompt": text,
            }
            response = await self._client.post("/api/embeddings", json=payload)
            response.raise_for_status()
            data = response.json()
            embeddings.append(data.get("embedding", []))

        return EmbeddingResponse(
            embeddings=embeddings,
            model=model,
            usage=TokenUsage(
                prompt_tokens=sum(len(t.split()) for t in texts),
                completion_tokens=0,
            ),
        )

    async def health_check(self) -> bool:
        try:
            response = await self._client.get("/api/tags")
            return response.status_code == 200
        except Exception:
            return False

    async def close(self) -> None:
        await self._client.aclose()


ProviderRegistry.register("ollama", OllamaProvider)
