"""Cache optimization."""

from __future__ import annotations

import time
from typing import Any


class CacheOptimizer:
    def __init__(self) -> None:
        self._metrics: list[dict[str, Any]] = []

    def analyze(self, cache_stats: dict[str, Any]) -> dict[str, Any]:
        hit_rate = cache_stats.get("hit_rate", 0)
        size = cache_stats.get("size", 0)
        max_size = cache_stats.get("max_size", 1000)
        recommendations = []
        if hit_rate < 50:
            recommendations.append("Consider increasing TTL for better hit rate")
        if size > max_size * 0.9:
            recommendations.append("Cache near capacity, consider increasing max_size")
        if hit_rate > 90:
            recommendations.append("Excellent cache performance")
        result = {
            "hit_rate": hit_rate,
            "utilization": (size / max_size * 100) if max_size > 0 else 0,
            "recommendations": recommendations,
            "analyzed_at": time.time(),
        }
        self._metrics.append(result)
        return result

    def suggest_ttl(self, access_pattern: list[float], current_ttl: int) -> int:
        if not access_pattern:
            return current_ttl
        avg_interval = sum(access_pattern) / len(access_pattern)
        suggested = int(avg_interval * 1.5)
        return max(60, min(suggested, 3600))

    def evict_candidates(self, entries: list[dict[str, Any]], target_count: int) -> list[str]:
        scored = [(e.get("key", ""), e.get("access_count", 0), e.get("last_accessed", 0)) for e in entries]
        scored.sort(key=lambda x: (x[1], x[2]))
        return [s[0] for s in scored[:target_count]]

    def get_metrics(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._metrics[-limit:]

    def count(self) -> int:
        return len(self._metrics)

    def clear(self) -> int:
        n = len(self._metrics)
        self._metrics.clear()
        return n
