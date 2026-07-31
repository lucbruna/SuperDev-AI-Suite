"""Adaptation engine for dynamic behavior adjustment."""
from __future__ import annotations

import time
from typing import Any, Dict, List


class AdaptationEngine:
    """Adapts agent behavior based on feedback and environmental signals."""

    def __init__(self) -> None:
        self._adaptations: List[Dict[str, Any]] = []
        self._strategies: Dict[str, str] = {
            "performance_drop": "reduce_complexity",
            "error_increase": "add_validation",
            "slow_response": "optimize_pipeline",
            "low_quality": "increase_review",
        }

    def adapt(self, experience: Dict[str, Any]) -> Dict[str, Any]:
        issue = experience.get("issue", "unknown")
        strategy = self._strategies.get(issue, "general_review")
        adaptation = {
            "timestamp": time.time(),
            "trigger": issue,
            "strategy": strategy,
            "changes_applied": self._apply_strategy(strategy, experience),
        }
        self._adaptations.append(adaptation)
        return adaptation

    def _apply_strategy(self, strategy: str, context: Dict[str, Any]) -> List[str]:
        changes: List[str] = []
        if strategy == "reduce_complexity":
            changes.append("Switched to simpler reasoning path")
        elif strategy == "add_validation":
            changes.append("Enabled additional output validation")
        elif strategy == "optimize_pipeline":
            changes.append("Parallelized independent steps")
        elif strategy == "increase_review":
            changes.append("Added quality review step")
        else:
            changes.append(f"Applied default strategy: {strategy}")
        return changes

    def get_adaptations(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._adaptations[-limit:]

    def snapshot(self) -> Dict[str, Any]:
        return {"total_adaptations": len(self._adaptations)}
