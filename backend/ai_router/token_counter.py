from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from backend.providers.base_provider import TokenUsage


@dataclass
class UsageRecord:
    provider: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: str | None = None
    request_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class TokenCounter:
    """Tracks token usage and costs across providers."""

    def __init__(self):
        self._records: list[UsageRecord] = []
        self._total_cost: float = 0.0
        self._total_tokens: int = 0
        self._by_provider: dict[str, dict[str, Any]] = {}
        self._by_model: dict[str, dict[str, Any]] = {}

    def record(
        self,
        provider: str,
        model: str,
        usage: TokenUsage,
        user_id: str | None = None,
        request_id: str | None = None,
        **metadata,
    ) -> UsageRecord:
        record = UsageRecord(
            provider=provider,
            model=model,
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens,
            estimated_cost=usage.estimated_cost,
            user_id=user_id,
            request_id=request_id,
            metadata=metadata,
        )
        self._records.append(record)
        self._total_cost += usage.estimated_cost
        self._total_tokens += usage.total_tokens

        if provider not in self._by_provider:
            self._by_provider[provider] = {"tokens": 0, "cost": 0.0, "requests": 0}
        self._by_provider[provider]["tokens"] += usage.total_tokens
        self._by_provider[provider]["cost"] += usage.estimated_cost
        self._by_provider[provider]["requests"] += 1

        if model not in self._by_model:
            self._by_model[model] = {"tokens": 0, "cost": 0.0, "requests": 0}
        self._by_model[model]["tokens"] += usage.total_tokens
        self._by_model[model]["cost"] += usage.estimated_cost
        self._by_model[model]["requests"] += 1

        return record

    def get_summary(self) -> dict[str, Any]:
        return {
            "total_cost": self._total_cost,
            "total_tokens": self._total_tokens,
            "total_requests": len(self._records),
            "by_provider": self._by_provider,
            "by_model": self._by_model,
        }

    def get_user_summary(self, user_id: str) -> dict[str, Any]:
        user_records = [r for r in self._records if r.user_id == user_id]
        total_cost = sum(r.estimated_cost for r in user_records)
        total_tokens = sum(r.total_tokens for r in user_records)
        return {
            "user_id": user_id,
            "total_cost": total_cost,
            "total_tokens": total_tokens,
            "total_requests": len(user_records),
        }

    def get_records(
        self,
        provider: str | None = None,
        model: str | None = None,
        user_id: str | None = None,
        limit: int = 100,
    ) -> list[UsageRecord]:
        records = self._records
        if provider:
            records = [r for r in records if r.provider == provider]
        if model:
            records = [r for r in records if r.model == model]
        if user_id:
            records = [r for r in records if r.user_id == user_id]
        return records[-limit:]

    def clear(self) -> None:
        self._records.clear()
        self._total_cost = 0.0
        self._total_tokens = 0
        self._by_provider.clear()
        self._by_model.clear()


token_counter = TokenCounter()
