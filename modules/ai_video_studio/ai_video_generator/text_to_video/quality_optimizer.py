"""Quality optimizer — improve generation quality per output checks."""
from __future__ import annotations

from typing import Any


class QualityOptimizer:
    """Adjusts generation settings to push quality past a threshold."""

    def optimize(self, result: dict[str, Any], *, target: float = 0.85) -> dict[str, Any]:
        current = result.get("quality", 0.0)
        steps = result.get("steps", 25)
        guidance = result.get("guidance_scale", 7.0)
        suggestions: list[str] = []
        while current < target and steps < 60:
            steps += 5
            guidance = min(12.0, guidance + 0.5)
            current = min(1.0, current + 0.03)
            suggestions.append("increase steps / guidance")
        return {
            "current_quality": result.get("quality", 0.0),
            "projected_quality": round(current, 3),
            "suggested_steps": steps,
            "suggested_guidance": round(guidance, 2),
            "suggestions": suggestions,
            "achieved_target": current >= target,
        }
