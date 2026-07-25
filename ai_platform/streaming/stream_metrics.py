from __future__ import annotations
import time
from typing import Optional
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class ProviderLatency:
    provider: str
    model: str
    latencies: list[float] = field(default_factory=list)


@dataclass
class TokenMetrics:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class StreamMetrics:
    def __init__(self):
        self._latencies: dict[str, ProviderLatency] = {}
        self._tokens: dict[str, TokenMetrics] = {}

    def _key(self, provider: str, model: str) -> str:
        return f"{provider}:{model}"

    def track_latency(self, provider: str, model: str, latency: float) -> None:
        key = self._key(provider, model)
        if key not in self._latencies:
            self._latencies[key] = ProviderLatency(provider=provider, model=model)
        self._latencies[key].latencies.append(latency)

    def track_tokens(self, provider: str, model: str, prompt_tokens: int, completion_tokens: int) -> None:
        key = self._key(provider, model)
        if key not in self._tokens:
            self._tokens[key] = TokenMetrics()
        self._tokens[key].prompt_tokens += prompt_tokens
        self._tokens[key].completion_tokens += completion_tokens
        self._tokens[key].total_tokens += prompt_tokens + completion_tokens

    def get_metrics(self) -> dict[str, dict]:
        result = {}
        for key, pl in self._latencies.items():
            lat = pl.latencies
            avg = sum(lat) / len(lat) if lat else 0.0
            sorted_lat = sorted(lat)
            n = len(sorted_lat)
            result[key] = {
                "provider": pl.provider,
                "model": pl.model,
                "avg_latency_ms": avg,
                "min_latency_ms": sorted_lat[0] if n else 0.0,
                "max_latency_ms": sorted_lat[-1] if n else 0.0,
                "p50": sorted_lat[n // 2] if n else 0.0,
                "p95": sorted_lat[int(n * 0.95)] if n else 0.0,
                "p99": sorted_lat[int(n * 0.99)] if n else 0.0,
                "total_requests": n,
            }
        for key, tm in self._tokens.items():
            if key not in result:
                result[key] = {}
            result[key].update({
                "prompt_tokens": tm.prompt_tokens,
                "completion_tokens": tm.completion_tokens,
                "total_tokens": tm.total_tokens,
            })
        return result

    def get_provider_metrics(self, provider: str) -> dict[str, dict]:
        return {k: v for k, v in self.get_metrics().items() if v.get("provider") == provider}
