"""Self-Healing — builds remediation plans for detected issues."""
from __future__ import annotations

from typing import Any

_REMEDIATIONS: dict[str, str] = {
    "high_cpu": "restart the render worker or lower the preset",
    "render_failed": "retry the job with a lower resolution",
    "disk_full": "run the cache cleaner and purge old exports",
    "tts_unavailable": "fall back to the offline voice engine",
}


class SelfHealing:
    """Maps issues to concrete remediation actions."""

    def remediate(self, issue: str) -> dict[str, Any]:
        action = _REMEDIATIONS.get(issue, "inspect logs and escalate to an operator")
        return {"issue": issue, "action": action, "automatic": issue in _REMEDIATIONS}


_self_healing: SelfHealing | None = None


def get_self_healing() -> SelfHealing:
    global _self_healing
    if _self_healing is None:
        _self_healing = SelfHealing()
    return _self_healing
