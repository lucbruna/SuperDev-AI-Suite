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


class OllamaProvider(BaseProvider):
    """Ollama local LLM provider implementation."""

    DEFAULT_BASE_URL = "http://localhost:11434"

    MODELS = [
        "llama3.1",
        "llama3.2",
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
            "options": {
                "temperature": temperature,
            },
        }
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens

        response = await self._client.post("/api/chat", json=payload)
        response.raise_for_status()
        data = response.json()

        message = data.get("message", {})
        eval_count = data.get("eval_count", 0)
        prompt_eval_count = data.get("prompt_eval_count", 0)

        usage = TokenUsage(
            prompt_tokens=prompt_eval_count,
            completion_tokens=eval_count,
            total_tokens=prompt_eval_count + eval_count,
        )

        return CompletionResponse(
            id=str(uuid.uuid4()),
            model=model,
            content=message.get("content", ""),
            finish_reason="stop" if data.get("done") else None,
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
            "stream": True,
            "options": {
                "temperature": temperature,
            },
        }
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens

        async with self._client.stream("POST", "/api/chat", json=payload) as response:
            response.raise_for_status()
            chunk_id = str(uuid.uuid4())
            async for line in response.aiter_lines():
                if not line.strip():
                    continue

                import json
                data = json.loads(line)
                message = data.get("message", {})

                yield StreamChunk(
                    id=chunk_id,
                    model=model,
                    delta=message.get("content", ""),
                    finish_reason="stop" if data.get("done") else None,
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
