from __future__ import annotations
import os
import time
from typing import Any, AsyncIterator, Optional
from datetime import datetime, timezone

import httpx

from ..base_provider import (
    BaseProvider, ModelInfo, ChatResponse, Choice, Usage,
    StreamChunk, HealthStatus, ProviderLimits, PricingInfo,
)


class OpenRouterProvider(BaseProvider):
    def __init__(self, config: Any):
        super().__init__(config)
        self._client: Optional[httpx.AsyncClient] = None

    def _get_api_key(self) -> str:
        return self.config.api_key or os.getenv("OPENROUTER_API_KEY") or ""

    def _get_base_url(self) -> str:
        return self.config.base_url or "https://openrouter.ai/api/v1"

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self._get_base_url(),
                headers={
                    "Authorization": f"Bearer {self._get_api_key()}",
                    "HTTP-Referer": "https://superdev.ai",
                    "X-Title": "SuperDev AI Suite",
                },
                timeout=self.config.timeout or 60,
            )
        return self._client

    async def authenticate(self) -> str:
        try:
            client = self._get_client()
            resp = await client.get("/models")
            if resp.status_code == 200:
                return "authenticated"
            raise RuntimeError(f"OpenRouter returned status {resp.status_code}")
        except Exception as e:
            raise RuntimeError(f"OpenRouter authentication failed: {e}")

    async def list_models(self) -> list[ModelInfo]:
        try:
            client = self._get_client()
            resp = await client.get("/models")
            if resp.status_code == 200:
                data = resp.json()
                models = []
                for model in data.get("data", []):
                    name = model.get("id", "unknown")
                    models.append(ModelInfo(
                        id=name,
                        name=name,
                        provider="openrouter",
                        capabilities=["chat"],
                        context_window=model.get("context_length", 8192),
                        max_tokens=model.get("max_tokens", 4096),
                    ))
                return models
        except Exception:
            pass
        return [
            ModelInfo(id="openai/gpt-4o", name="GPT-4o (OpenRouter)", provider="openrouter", capabilities=["chat"], context_window=128000, max_tokens=16384),
            ModelInfo(id="anthropic/claude-3.5-sonnet", name="Claude 3.5 Sonnet (OpenRouter)", provider="openrouter", capabilities=["chat"], context_window=200000, max_tokens=8192),
            ModelInfo(id="google/gemini-pro-1.5", name="Gemini Pro 1.5 (OpenRouter)", provider="openrouter", capabilities=["chat"], context_window=1000000, max_tokens=8192),
            ModelInfo(id="meta-llama/llama-3.1-405b", name="Llama 3.1 405B (OpenRouter)", provider="openrouter", capabilities=["chat"], context_window=131072, max_tokens=8192),
            ModelInfo(id="mistral/mistral-large", name="Mistral Large (OpenRouter)", provider="openrouter", capabilities=["chat"], context_window=32768, max_tokens=8192),
            ModelInfo(id="deepseek/deepseek-coder", name="DeepSeek Coder (OpenRouter)", provider="openrouter", capabilities=["chat"], context_window=16384, max_tokens=4096),
        ]

    async def chat(self, messages: list[dict], config: dict[str, Any]) -> ChatResponse:
        client = self._get_client()
        model = config.get("model") or self.config.default_model or "openai/gpt-4o"
        try:
            payload = {
                "model": model,
                "messages": messages,
                "temperature": config.get("temperature", 0.7),
                "max_tokens": config.get("max_tokens", 2048),
            }
            resp = await client.post("/chat/completions", json=payload)
            if resp.status_code != 200:
                raise RuntimeError(f"OpenRouter returned {resp.status_code}: {resp.text}")
            data = resp.json()
            choice = data["choices"][0]
            content = choice["message"]["content"]
            usage = Usage(
                prompt_tokens=data.get("usage", {}).get("prompt_tokens", 0),
                completion_tokens=data.get("usage", {}).get("completion_tokens", 0),
                total_tokens=data.get("usage", {}).get("total_tokens", 0),
            )
            return ChatResponse(
                id=data.get("id", f"openrouter-{int(time.time())}"),
                model=data.get("model", model),
                choices=[Choice(index=0, message={"role": "assistant", "content": content}, finish_reason=choice.get("finish_reason", "stop"))],
                usage=usage,
                provider="openrouter",
            )
        except Exception as e:
            return ChatResponse(
                id="fallback",
                model=model,
                choices=[Choice(index=0, message={"role": "assistant", "content": f"[OpenRouter error: {e}]"})],
                provider="openrouter",
            )

    async def stream(self, messages: list[dict], config: dict[str, Any]) -> AsyncIterator[StreamChunk]:
        client = self._get_client()
        model = config.get("model") or self.config.default_model or "openai/gpt-4o"
        try:
            payload = {
                "model": model,
                "messages": messages,
                "temperature": config.get("temperature", 0.7),
                "max_tokens": config.get("max_tokens", 2048),
                "stream": True,
            }
            async with client.stream("POST", "/chat/completions", json=payload) as response:
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    if line.startswith("data: "):
                        line = line[6:]
                        if line.strip() == "[DONE]":
                            yield StreamChunk(delta="", finish_reason="stop", model=model)
                            continue
                        try:
                            import json
                            data = json.loads(line)
                            delta = data["choices"][0]["delta"].get("content", "")
                            finish_reason = data["choices"][0].get("finish_reason")
                            if delta:
                                yield StreamChunk(delta=delta, finish_reason=finish_reason, model=model)
                        except Exception:
                            continue
        except Exception as e:
            yield StreamChunk(delta=f"[Stream error: {e}]", finish_reason="error")

    async def embeddings(self, texts: list[str]) -> list[list[float]]:
        return [[0.0] * 1536 for _ in texts]

    async def health(self) -> HealthStatus:
        start = time.monotonic()
        try:
            client = self._get_client()
            resp = await client.get("/models")
            elapsed = (time.monotonic() - start) * 1000
            if resp.status_code == 200:
                return HealthStatus(status="healthy", latency_ms=elapsed, last_check=datetime.now(timezone.utc))
            return HealthStatus(status="degraded", latency_ms=elapsed, last_check=datetime.now(timezone.utc), error=f"Status {resp.status_code}")
        except Exception as e:
            elapsed = (time.monotonic() - start) * 1000
            return HealthStatus(status="unhealthy", latency_ms=elapsed, last_check=datetime.now(timezone.utc), error=str(e))

    async def limits(self) -> ProviderLimits:
        return ProviderLimits(max_requests_per_minute=1000, max_tokens_per_minute=200000, max_concurrent_requests=50)

    async def pricing(self) -> PricingInfo:
        return PricingInfo(input_per_1k=0.0, output_per_1k=0.0, currency="USD")