"""Risk policy — blocks plans whose tasks exceed an allowed risk level.

Risk levels are ordered ``low < medium < high < critical``. Enforcement is
fail-closed: an unknown risk string ranks above every known level (so a
malformed task risk cannot slip through) and an invalid ``max_risk`` config
raises instead of silently allowing everything.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from modules.autonomous_developer.config.constants import RISK_LEVELS

if TYPE_CHECKING:
    from modules.autonomous_developer.core.models import Task

__all__ = ["enforce_task_risks", "risk_exceeds", "risk_rank"]

_UNKNOWN_RANK = len(RISK_LEVELS)


def risk_rank(risk: str) -> int:
    """Position in the risk ordering; unknown levels rank highest."""
    try:
        return RISK_LEVELS.index(risk)
    except ValueError:
        return _UNKNOWN_RANK


def risk_exceeds(risk: str, max_risk: str) -> bool:
    """True when ``risk`` ranks above ``max_risk`` (unknown risks exceed all)."""
    return risk_rank(risk) > risk_rank(max_risk)


def enforce_task_risks(tasks: list[Task], max_risk: str) -> list[str]:
    """Violations for tasks whose risk exceeds ``max_risk``.

    Raises :class:`SecurityError` when ``max_risk`` is not a known level so
    a misconfigured policy fails closed.
    """
    from modules.autonomous_developer.core.exceptions import SecurityError

    if max_risk not in RISK_LEVELS:
        raise SecurityError(
            f"Invalid max_risk_level {max_risk!r}; expected one of {list(RISK_LEVELS)}",
            context={"max_risk_level": max_risk},
        )
    violations: list[str] = []
    for task in tasks:
        if risk_exceeds(task.risk, max_risk):
            violations.append(
                f"{task.task_id} (risk={task.risk}, max={max_risk})"
            )
    return violations
