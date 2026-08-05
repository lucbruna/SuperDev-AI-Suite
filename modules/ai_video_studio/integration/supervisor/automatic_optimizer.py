"""Automatic Optimizer — suggests quality/settings by workload."""
from __future__ import annotations

from typing import Any


class AutomaticOptimizer:
    """Recommends render settings based on workload type and target."""

    def optimize(self, *, workload: str = "batch", target: str = "fast") -> dict[str, Any]:
        presets = {
            "fast": {"quality": "draft", "crf": 28, "preset": "ultrafast", "fps": 24},
            "balanced": {"quality": "high", "crf": 23, "preset": "medium", "fps": 30},
            "quality": {"quality": "final", "crf": 18, "preset": "slow", "fps": 30},
        }
        choice = presets.get(target, presets["balanced"])
        return {"workload": workload, "target": target, "settings": choice}


_automatic_optimizer: AutomaticOptimizer | None = None


def get_automatic_optimizer() -> AutomaticOptimizer:
    global _automatic_optimizer
    if _automatic_optimizer is None:
        _automatic_optimizer = AutomaticOptimizer()
    return _automatic_optimizer
