"""Hypothesis generation and management for reasoning."""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional


class HypothesisManager:
    """Generates, tracks, and evaluates hypotheses."""

    def __init__(self) -> None:
        self._hypotheses: Dict[str, Dict[str, Any]] = {}
        self._generation_count: int = 0

    def generate(self, problem: str,
                 context: Optional[Dict[str, Any]] = None) -> List[str]:
        self._generation_count += 1
        hypotheses: List[str] = []
        hypotheses.append(f"The root cause is related to: {problem[:100]}")
        if context:
            for key in list(context.keys())[:3]:
                hypotheses.append(f"Factor '{key}' may be contributing")
        hypotheses.append(f"Alternative approach: Consider different angle on {problem[:60]}")
        for i, h in enumerate(hypotheses):
            hid = f"hyp_{self._generation_count}_{i}"
            self._hypotheses[hid] = {
                "text": h,
                "status": "proposed",
                "score": 0.5,
                "created_at": time.time(),
            }
        return hypotheses

    def update_status(self, hypothesis_id: str, status: str) -> bool:
        if hypothesis_id in self._hypotheses:
            self._hypotheses[hypothesis_id]["status"] = status
            return True
        return False

    def get_supported(self) -> List[Dict[str, Any]]:
        return [h for h in self._hypotheses.values() if h["status"] == "supported"]

    def get_rejected(self) -> List[Dict[str, Any]]:
        return [h for h in self._hypotheses.values() if h["status"] == "rejected"]

    def count(self) -> int:
        return len(self._hypotheses)

    def snapshot(self) -> Dict[str, Any]:
        return {
            "total_generated": self._generation_count,
            "active": len(self._hypotheses),
        }
