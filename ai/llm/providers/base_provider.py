from __future__ import annotations

import asyncio
import logging
import random
import time
from collections.abc import AsyncIterator
from dataclasses import dataclass
from enum import Enum
from typing import Any

from ..llm_interfaces import ILLMProvider

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Error classification
# ---------------------------------------------------------------------------

class ProviderErrorCode(Enum):
    AUTH = "auth_error"
    RATE_LIMIT = "rate_limit"
    TIMEOUT = "timeout"
    SERVER_ERROR = "server_error"
    INVALID_REQUEST = "invalid_request"
    CONTEXT_LENGTH = "context_length"
    CONTENT_FILTER = "content_filter"
    API_ERROR = "api_error"
    EMBEDDINGS = "embeddings_not_supported"
    VISION = "vision_not_supported"
    TOOLS = "tools_not_supported"
    UNKNOWN = "unknown"


@dataclass
class ProviderError(Exception):
    code: ProviderErrorCode = ProviderErrorCode.UNKNOWN
    message: str = ""
    status_code: int = 0
    retry_after: float | None = None
    provider: str = ""
    raw: Any = None

    def __post_init__(self) -> None:
        super().__init__(self.message)

    @classmethod
    def from_exception(cls, exc: Exception, provider: str = "") -> ProviderError:
        msg = str(exc).lower()

        if "authentication" in msg or "unauthorized" in msg or "401" in msg or "api key" in msg:
            return cls(ProviderErrorCode.AUTH, str(exc), 401, provider=provider, raw=exc)
        if "rate limit" in msg or "429" in msg or "too many" in msg:
            return cls(ProviderErrorCode.RATE_LIMIT, str(exc), 429, provider=provider, raw=exc)
        if "timeout" in msg or "timed out" in msg or "408" in msg:
            return cls(ProviderErrorCode.TIMEOUT, str(exc), 408, provider=provider, raw=exc)
        if "context" in msg and ("length" in msg or "exceed" in msg):
            return cls(ProviderErrorCode.CONTEXT_LENGTH, str(exc), 400, provider=provider, raw=exc)
        if "content_filter" in msg or "content_policy" in msg or "safety" in msg:
            return cls(ProviderErrorCode.CONTENT_FILTER, str(exc), 400, provider=provider, raw=exc)
        if "500" in msg or "502" in msg or "503" in msg or "server" in msg:
            return cls(ProviderErrorCode.SERVER_ERROR, str(exc), int(getattr(exc, 'status_code', 503)), provider=provider, raw=exc)
        return cls(ProviderErrorCode.API_ERROR, str(exc), getattr(exc, 'status_code', 0), provider=provider, raw=exc)


# ---------------------------------------------------------------------------
# Streaming types
# ---------------------------------------------------------------------------

@dataclass
class StreamDelta:
    content: str = ""
    role: str = "assistant"
    tool_calls: list[dict[str, Any]] | None = None
    finish_reason: str | None = None
    usage: dict[str, int] | None = None


# ---------------------------------------------------------------------------
# Rate Limiter (token bucket)
# ---------------------------------------------------------------------------

class TokenBucket:
    """Simple token bucket rate limiter."""

    def __init__(self, rate: float, capacity: float) -> None:
        self._rate = rate
        self._capacity = capacity
        self._tokens = capacity
        self._last = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self) -> float:
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self._last
            self._tokens = min(self._capacity, self._tokens + elapsed * self._rate)
            self._last = now

            if self._tokens >= 1.0:
                self._tokens -= 1.0
                return 0.0

            wait = (1.0 - self._tokens) / self._rate if self._rate > 0 else 1.0
            self._tokens = 0.0
            return wait


# ---------------------------------------------------------------------------
# Retry helper
# ---------------------------------------------------------------------------

DEFAULT_RETRY_CODES = {429, 500, 502, 503, 504}
MAX_RETRIES = 3
BASE_DELAY = 1.0
MAX_DELAY = 60.0


def _exponential_backoff(attempt: int, base_delay: float = BASE_DELAY, max_delay: float = MAX_DELAY) -> float:
    delay = base_delay * (2 ** attempt)
    jitter = random.uniform(0, delay * 0.1)
    return min(delay + jitter, max_delay)


def _is_retryable(error: ProviderError, retry_codes: set[int] | None = None) -> bool:
    codes = retry_codes or DEFAULT_RETRY_CODES
    return error.status_code in codes or error.code in (ProviderErrorCode.RATE_LIMIT, ProviderErrorCode.TIMEOUT, ProviderErrorCode.SERVER_ERROR)


# ---------------------------------------------------------------------------
# Cost helpers (per-provider overrides)
# ---------------------------------------------------------------------------

@dataclass
class PricingRow:
    input_per_1k: float = 0.0
    output_per_1k: float = 0.0
    currency: str = "USD"


OPENAI_PRICING: dict[str, PricingRow] = {
    "gpt-4o": PricingRow(0.0025, 0.01),
    "gpt-4o-mini": PricingRow(0.00015, 0.0006),
    "gpt-4-turbo": PricingRow(0.01, 0.03),
    "gpt-4": PricingRow(0.03, 0.06),
    "gpt-3.5-turbo": PricingRow(0.0005, 0.0015),
}

ANTHROPIC_PRICING: dict[str, PricingRow] = {
    "claude-3-5-sonnet-20241022": PricingRow(0.003, 0.015),
    "claude-3-opus-20240229": PricingRow(0.015, 0.075),
    "claude-3-haiku-20240307": PricingRow(0.00025, 0.00125),
    "claude-2.1": PricingRow(0.008, 0.024),
}

GEMINI_PRICING: dict[str, PricingRow] = {
    "gemini-2.0-flash": PricingRow(0.0001, 0.0004),
    "gemini-2.0-flash-lite": PricingRow(0.000075, 0.0003),
    "gemini-1.5-pro": PricingRow(0.00125, 0.005),
    "gemini-1.5-flash": PricingRow(0.000075, 0.0003),
    "gemini-pro": PricingRow(0.000125, 0.0005),
}


def estimate_cost(provider_name: str, model: str, prompt_tokens: int, completion_tokens: int) -> float:
    table: dict[str, dict[str, PricingRow]] = {
        "openai": OPENAI_PRICING,
        "anthropic": ANTHROPIC_PRICING,
        "google": GEMINI_PRICING,
    }
    pricing_map = table.get(provider_name, {})
    row = pricing_map.get(model) or PricingRow()
    return (row.input_per_1k * prompt_tokens / 1000) + (row.output_per_1k * completion_tokens / 1000)


# ---------------------------------------------------------------------------
# Message format helpers
# ---------------------------------------------------------------------------

def convert_messages(messages: list[dict[str, Any]]) -> tuple[str | None, list[dict[str, Any]]]:
    """Extract system message and return (system_prompt, chat_messages)."""
    system = None
    chat = messages
    if messages and messages[0].get("role") == "system":
        system = messages[0]["content"]
        chat = messages[1:]
    return system, chat


def count_tokens(text: str, model: str = "") -> int:
    """Rough token estimation (4 chars per token)."""
    return len(text) // 4


# ---------------------------------------------------------------------------
# BaseLLMProvider
# ---------------------------------------------------------------------------

class BaseLLMProvider(ILLMProvider):
    """Base class for all LLM provider implementations.

    Features:
    - Automatic retry with exponential backoff
    - Token bucket rate limiting
    - Error classification
    - Cost estimation
    - Streaming base patterns
    """

    def __init__(self, name: str = "", model: str = "") -> None:
        self._name = name
        self._model = model
        self._rate_limiter: TokenBucket | None = None
        self._max_retries = MAX_RETRIES
        self._retry_codes: set[int] | None = None
        self._pricing: dict[str, PricingRow] = {}
        self._default_pricing = PricingRow()
        self._call_count = 0
        self._total_prompt_tokens = 0
        self._total_completion_tokens = 0
        self._total_cost = 0.0

    # ── ILLMProvider ────────────────────────────────────────────────

    def name(self) -> str:
        return self._name

    def model(self) -> str:
        return self._model

    async def generate(self, prompt: str, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError

    async def generate_stream(self, prompt: str, **kwargs: Any) -> AsyncIterator[dict[str, Any]]:
        async def _empty() -> AsyncIterator[dict[str, Any]]:
            yield {"content": "", "finish_reason": "stop"}
        return _empty()

    async def validate(self, params: dict[str, Any]) -> bool:
        return True

    async def rollback(self) -> None:
        self._model = getattr(self, "_original_model", self._model)

    async def cleanup(self) -> None:
        pass

    # ── Rate limiting ───────────────────────────────────────────────

    def set_rate_limit(self, requests_per_minute: float = 60, burst: float = 10) -> None:
        rate = requests_per_minute / 60.0
        self._rate_limiter = TokenBucket(rate, burst)

    async def _throttle(self) -> None:
        if self._rate_limiter:
            wait = await self._rate_limiter.acquire()
            if wait > 0:
                logger.debug("Rate limited, waiting %.2fs", wait)
                await asyncio.sleep(wait)

    # ── Retry ───────────────────────────────────────────────────────

    async def _execute_with_retry(
        self,
        fn,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        last_error: ProviderError | None = None
        for attempt in range(self._max_retries + 1):
            try:
                await self._throttle()
                return await fn(*args, **kwargs)
            except ProviderError as e:
                last_error = e
                if attempt < self._max_retries and _is_retryable(e, self._retry_codes):
                    retry_after = e.retry_after or _exponential_backoff(attempt)
                    logger.warning("Provider %s: retry %d/%d after %.1fs: %s", self._name, attempt + 1, self._max_retries, retry_after, e.message)
                    await asyncio.sleep(retry_after)
                else:
                    raise
            except Exception as e:
                pe = ProviderError.from_exception(e, self._name)
                last_error = pe
                if attempt < self._max_retries and _is_retryable(pe, self._retry_codes):
                    retry_after = _exponential_backoff(attempt)
                    await asyncio.sleep(retry_after)
                else:
                    raise pe from e

        if last_error:
            raise last_error

    # ── Cost tracking ───────────────────────────────────────────────

    def _track_usage(self, prompt_tokens: int, completion_tokens: int) -> dict[str, Any]:
        cost = self._estimate_cost(prompt_tokens, completion_tokens)
        self._call_count += 1
        self._total_prompt_tokens += prompt_tokens
        self._total_completion_tokens += completion_tokens
        self._total_cost += cost
        return {
            "tokens_prompt": prompt_tokens,
            "tokens_completion": completion_tokens,
            "cost_usd": round(cost, 6),
            "call_count": self._call_count,
        }

    def _estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        row = self._pricing.get(self._model) or self._default_pricing
        return (row.input_per_1k * prompt_tokens / 1000) + (row.output_per_1k * completion_tokens / 1000)

    # ── Determinism helper ──────────────────────────────────────────

    def _ensure_deterministic(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        kwargs["temperature"] = 0.0
        kwargs["top_p"] = 1.0
        return kwargs

    # ── Stats ───────────────────────────────────────────────────────

    def stats(self) -> dict[str, Any]:
        return {
            "name": self._name,
            "model": self._model,
            "call_count": self._call_count,
            "total_prompt_tokens": self._total_prompt_tokens,
            "total_completion_tokens": self._total_completion_tokens,
            "total_cost_usd": round(self._total_cost, 6),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            **self.stats(),
            "rate_limiter": self._rate_limiter is not None,
            "max_retries": self._max_retries,
        }
