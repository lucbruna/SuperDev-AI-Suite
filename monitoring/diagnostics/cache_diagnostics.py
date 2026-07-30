from __future__ import annotations

from typing import Any

from .diagnostic_engine import DiagnosticResult


class CacheDiagnostics:
    """Cache system diagnostic checks."""

    @staticmethod
    def check_hit_rate(hits: int = 0, misses: int = 0) -> DiagnosticResult:
        total = hits + misses
        rate = (hits / total * 100) if total > 0 else 0.0
        status = "passed"
        message = f"Cache hit rate: {rate:.1f}% ({hits}h/{misses}m)"
        if total > 100 and rate < 50:
            status = "failed"
        elif total > 100 and rate < 75:
            status = "warning"
        return DiagnosticResult(
            check="cache_hit_rate",
            status=status,
            message=message,
            details={"hits": hits, "misses": misses, "hit_rate_pct": round(rate, 1)},
        )

    @staticmethod
    def check_memory_usage(used_mb: float, max_mb: float) -> DiagnosticResult:
        pct = (used_mb / max_mb * 100) if max_mb > 0 else 0.0
        status = "passed"
        message = f"Cache memory: {used_mb:.1f}/{max_mb:.0f}MB ({pct:.0f}%)"
        if pct > 90:
            status = "failed"
        elif pct > 75:
            status = "warning"
        return DiagnosticResult(
            check="cache_memory",
            status=status,
            message=message,
            details={"used_mb": round(used_mb, 1), "max_mb": round(max_mb, 1), "usage_pct": round(pct, 1)},
        )

    @staticmethod
    def check_eviction_rate(evicted: int = 0, total: int = 0) -> DiagnosticResult:
        rate = (evicted / total * 100) if total > 0 else 0.0
        status = "passed"
        message = f"Eviction rate: {rate:.1f}%"
        if rate > 10:
            status = "failed"
        elif rate > 5:
            status = "warning"
        return DiagnosticResult(
            check="cache_eviction",
            status=status,
            message=message,
            details={"evicted": evicted, "total": total, "eviction_rate_pct": round(rate, 1)},
        )
