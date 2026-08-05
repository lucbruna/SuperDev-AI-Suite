"""Cloud Optimizer — cost and performance optimization (Volume 7)."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class CloudOptimizer:
    """Suggest cloud cost and performance improvements."""

    def analyze(self, *, storage_gb: float = 0.0, egress_gb: float = 0.0, unused_objects: int = 0) -> dict:
        """Return an optimization report."""
        suggestions = []
        if storage_gb > 100:
            suggestions.append("Move cold data to archive storage to cut cost.")
        if egress_gb > 50:
            suggestions.append("Enable a CDN to reduce egress transfer costs.")
        if unused_objects > 100:
            suggestions.append("Enable lifecycle rules to expire unused objects.")
        if not suggestions:
            suggestions.append("Storage usage looks well balanced.")
        score = max(0.0, 100.0 - storage_gb * 0.1 - egress_gb * 0.2 - unused_objects * 0.05)
        return {
            "score": round(min(100.0, score), 1),
            "suggestions": suggestions,
            "count": len(suggestions),
        }

    def stats(self) -> dict[str, int]:
        return {"criteria": 3}


_OPTIMIZER: CloudOptimizer | None = None


def get_cloud_optimizer() -> CloudOptimizer:
    """Get the module-level singleton cloud optimizer."""
    global _OPTIMIZER
    if _OPTIMIZER is None:
        _OPTIMIZER = CloudOptimizer()
    return _OPTIMIZER
