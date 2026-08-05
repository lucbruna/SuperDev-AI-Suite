"""YouTube A/B Testing — thumbnail and title experiments (Volume 7)."""
from __future__ import annotations

import logging
import math
import time
import uuid

logger = logging.getLogger(__name__)


class YoutubeABTesting:
    """Manage A/B experiments and pick winners with significance heuristics."""

    def __init__(self) -> None:
        self._experiments: dict[str, dict] = {}

    def create(self, *, name: str, variants: list[dict]) -> dict:
        """Start an experiment with a list of variant descriptors."""
        if len(variants) < 2:
            return {"success": False, "error": "Need at least 2 variants"}
        exp_id = uuid.uuid4().hex[:12]
        experiment = {
            "id": exp_id,
            "name": name,
            "variants": [{"key": v, "impressions": 0, "clicks": 0} for v in variants],
            "created_at": time.time(),
            "state": "running",
        }
        self._experiments[exp_id] = experiment
        return {"success": True, "experiment": experiment}

    def record(self, exp_id: str, variant_key: str, *, impressions: int = 1, clicks: int = 0) -> dict:
        """Record impressions/clicks for a variant."""
        experiment = self._experiments.get(exp_id)
        if not experiment:
            return {"success": False, "error": "Unknown experiment"}
        for variant in experiment["variants"]:
            if variant["key"] == variant_key:
                variant["impressions"] += impressions
                variant["clicks"] += clicks
                break
        return {"success": True}

    def results(self, exp_id: str) -> dict:
        """Return variant CTRs and a winner recommendation."""
        experiment = self._experiments.get(exp_id)
        if not experiment:
            return {"success": False, "error": "Unknown experiment"}
        rows = []
        for variant in experiment["variants"]:
            impressions = variant["impressions"]
            ctr = round(variant["clicks"] / impressions * 100.0, 2) if impressions else 0.0
            rows.append({**variant, "ctr": ctr})
        winner = max(rows, key=lambda r: r["ctr"], default=None)
        return {"success": True, "variants": rows, "winner": winner}

    @staticmethod
    def significance(*, impressions_a: int, clicks_a: int, impressions_b: int, clicks_b: int) -> dict:
        """Rough two-proportion significance heuristic (z-score approximation)."""
        p_a = clicks_a / impressions_a if impressions_a else 0.0
        p_b = clicks_b / impressions_b if impressions_b else 0.0
        p_pool = (clicks_a + clicks_b) / (impressions_a + impressions_b) if (impressions_a + impressions_b) else 0.0
        if p_pool in (0.0, 1.0):
            return {"z_score": 0.0, "significant": False}
        se = math.sqrt(p_pool * (1 - p_pool) * (1 / impressions_a + 1 / impressions_b))
        z = (p_a - p_b) / se if se else 0.0
        return {"z_score": round(abs(z), 3), "significant": abs(z) >= 1.96}

    def stats(self) -> dict[str, int]:
        return {"experiments": len(self._experiments)}


_AB_TESTING: YoutubeABTesting | None = None


def get_youtube_ab_testing() -> YoutubeABTesting:
    """Get the module-level singleton A/B testing manager."""
    global _AB_TESTING
    if _AB_TESTING is None:
        _AB_TESTING = YoutubeABTesting()
    return _AB_TESTING
