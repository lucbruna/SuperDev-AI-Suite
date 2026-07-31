from __future__ import annotations

import json
import os
import time
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Any

import httpx

from ..base_provider import (
    BaseProvider,
    ChatResponse,
    Choice,
    HealthStatus,
    ModelInfo,
    PricingInfo,
    ProviderLimits,
    StreamChunk,
    Usage,
)


class OllamaProvider(BaseProvider):
    def __init__(self, config: Any):
        super().__init__(config)
        self._client: httpx.AsyncClient | None = None

    def _get_base_url(self) -> str:
        return self.config.base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self._get_base_url(),
                timeout=self.config.timeout or 60,
            )
        return self._client

    async def authenticate(self) -> str:
        try:
            client = self._get_client()
            resp = await client.get("/api/tags")
            if resp.status_code == 200:
                return "authenticated"
            raise RuntimeError(f"Ollama returned status {resp.status_code}")
        except Exception as e:
            raise RuntimeError(f"Ollama authentication failed: {e}")

    async def list_models(self) -> list[ModelInfo]:
        try:
            client = self._get_client()
            resp = await client.get("/api/tags")
            if resp.status_code == 200:
                data = resp.json()
                models = []
                for model in data.get("models", []):
                    name = model.get("name", "unknown")
                    models.append(
                        ModelInfo(
                            id=name,
                            name=name,
                            provider="ollama",
                            capabilities=["chat"],
                            context_window=8192,
                            max_tokens=4096,
                        )
                    )
                return models
        except Exception:
            pass
        return [
            ModelInfo(
                id="llama3",
                name="Llama 3",
                provider="ollama",
                capabilities=["chat"],
                context_window=8192,
                max_tokens=4096,
            ),
            ModelInfo(
                id="llama3.1",
                name="Llama 3.1",
                provider="ollama",
                capabilities=["chat"],
                context_window=131072,
                max_tokens=8192,
            ),
            ModelInfo(
                id="mistral",
                name="Mistral",
                provider="ollama",
                capabilities=["chat"],
                context_window=8192,
                max_tokens=4096,
            ),
            ModelInfo(
                id="codestral",
                name="Codestral",
                provider="ollama",
                capabilities=["chat"],
                context_window=32768,
                max_tokens=8192,
            ),
            ModelInfo(
                id="deepseek-coder",
                name="DeepSeek Coder",
                provider="ollama",
                capabilities=["chat"],
                context_window=16384,
                max_tokens=4096,
            ),
            ModelInfo(
                id="mixtral",
                name="Mixtral",
                provider="ollama",
                capabilities=["chat"],
                context_window=32768,
                max_tokens=4096,
            ),
            ModelInfo(
                id="phi3",
                name="Phi-3",
                provider="ollama",
                capabilities=["chat"],
                context_window=128000,
                max_tokens=4096,
            ),
            ModelInfo(
                id="gemma2",
                name="Gemma 2",
                provider="ollama",
                capabilities=["chat"],
                context_window=8192,
                max_tokens=4096,
            ),
            ModelInfo(
                id="qwen2",
                name="Qwen 2",
                provider="ollama",
                capabilities=["chat"],
                context_window=32768,
                max_tokens=8192,
            ),
        ]

    async def chat(self, messages: list[dict], config: dict[str, Any]) -> ChatResponse:
        client = self._get_client()
        model = config.get("model") or self.config.default_model or "llama3"
        try:
            payload = {
                "model": model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": config.get("temperature", 0.7),
                    "num_predict": config.get("max_tokens", 2048),
                },
            }
            resp = await client.post("/api/chat", json=payload)
            if resp.status_code != 200:
                raise RuntimeError(f"Ollama returned {resp.status_code}: {resp.text}")
            data = resp.json()
            content = data.get("message", {}).get("content", "")
            usage = Usage(
                prompt_tokens=data.get("prompt_eval_count", 0) or 0,
                completion_tokens=data.get("eval_count", 0) or 0,
                total_tokens=(data.get("prompt_eval_count", 0) or 0) + (data.get("eval_count", 0) or 0),
            )
            return ChatResponse(
                id=f"ollama-{int(time.time())}",
                model=model,
                choices=[Choice(index=0, message={"role": "assistant", "content": content}, finish_reason="stop")],
                usage=usage,
                provider="ollama",
            )
        except Exception as e:
            return ChatResponse(
                id="fallback",
                model=model,
                choices=[Choice(index=0, message={"role": "assistant", "content": f"[Ollama error: {e}]"})],
                provider="ollama",
            )

    async def stream(self, messages: list[dict], config: dict[str, Any]) -> AsyncIterator[StreamChunk]:
        client = self._get_client()
        model = config.get("model") or self.config.default_model or "llama3"
        try:
            payload = {
                "model": model,
                "messages": messages,
                "stream": True,
                "options": {
                    "temperature": config.get("temperature", 0.7),
                    "num_predict": config.get("max_tokens", 2048),
                },
            }
            async with client.stream("POST", "/api/chat", json=payload) as response:
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        if data.get("done"):
                            yield StreamChunk(delta="", finish_reason="stop", model=model)
                        else:
                            content = data.get("message", {}).get("content", "")
                            if content:
                                yield StreamChunk(delta=content, model=model)
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            yield StreamChunk(delta=f"[Stream error: {e}]", finish_reason="error")

    async def embeddings(self, texts: list[str]) -> list[list[float]]:
        client = self._get_client()
        results = []
        for text in texts:
            try:
                payload = {
                    "model": self.config.default_model or "llama3",
                    "prompt": text,
                }
                resp = await client.post("/api/embeddings", json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    results.append(data.get("embedding", [0.0] * 4096))
                else:
                    results.append([0.0] * 4096)
            except Exception:
                results.append([0.0] * 4096)
        return results

    async def health(self) -> HealthStatus:
        start = time.monotonic()
        try:
            client = self._get_client()
            resp = await client.get("/api/tags")
            elapsed = (time.monotonic() - start) * 1000
            if resp.status_code == 200:
                return HealthStatus(status="healthy", latency_ms=elapsed, last_check=datetime.now(UTC))
            return HealthStatus(
                status="degraded", latency_ms=elapsed, last_check=datetime.now(UTC), error=f"Status {resp.status_code}"
            )
        except Exception as e:
            elapsed = (time.monotonic() - start) * 1000
            return HealthStatus(status="unhealthy", latency_ms=elapsed, last_check=datetime.now(UTC), error=str(e))

    async def limits(self) -> ProviderLimits:
        return ProviderLimits(max_requests_per_minute=0, max_tokens_per_minute=0, max_concurrent_requests=0)

    async def pricing(self) -> PricingInfo:
        return PricingInfo(input_per_1k=0.0, output_per_1k=0.0, currency="USD")
