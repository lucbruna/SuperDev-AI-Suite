"""Decision-making style configuration."""
from __future__ import annotations

from typing import Any, Dict, List


class DecisionStyle:
    """Configures how an agent approaches decisions."""

    def __init__(self, risk_tolerance: float = 0.5, analysis_depth: str = "balanced") -> None:
        self._risk_tolerance = min(max(risk_tolerance, 0.0), 1.0)
        self._analysis_depth = analysis_depth
        self._valid_depths = ["shallow", "balanced", "deep"]

    def set_risk_tolerance(self, tolerance: float) -> None:
        self._risk_tolerance = min(max(float(tolerance), 0.0), 1.0)

    def set_analysis_depth(self, depth: str) -> None:
        if depth in self._valid_depths:
            self._analysis_depth = depth

    def get_profile(self) -> Dict[str, Any]:
        return {
            "risk_tolerance": self._risk_tolerance,
            "analysis_depth": self._analysis_depth,
            "conservative": self._risk_tolerance < 0.3,
            "thorough": self._analysis_depth in ("balanced", "deep"),
        }

    def evaluate_options(self, options: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        scored = []
        for opt in options:
            risk = opt.get("risk", 0.5)
            reward = opt.get("reward", 0.5)
            if self._risk_tolerance < 0.3:
                score = reward * (1 - risk)
            elif self._risk_tolerance > 0.7:
                score = reward * risk + reward * 0.3
            else:
                score = (reward + (1 - risk)) / 2
            scored.append({**opt, "score": round(score, 3)})
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored
