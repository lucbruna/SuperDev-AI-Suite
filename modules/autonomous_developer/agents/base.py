"""Agent framework: results, the base agent contract and timed dispatch."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from modules.autonomous_developer.core.context import DeveloperContext

__all__ = ["AgentResult", "BaseAgent", "timed_run"]


@dataclass(slots=True)
class AgentResult:
    """Outcome of an agent run, never raised — errors land on the result."""

    agent: str = ""
    goal: str = ""
    output: Any = None
    artifacts: dict[str, Any] = field(default_factory=dict)
    error: str = ""
    duration_seconds: float = 0.0

    @property
    def success(self) -> bool:
        return not self.error


class BaseAgent:
    """Contract every agent implements."""

    name: str = "base"
    description: str = ""

    def run(self, ctx: DeveloperContext, goal: str, **kwargs: Any) -> AgentResult:
        raise NotImplementedError


def timed_run(
    agent: BaseAgent, ctx: DeveloperContext, goal: str, **kwargs: Any
) -> AgentResult:
    """Run an agent, wrapping any exception into an error result.

    The duration is measured and attached even when the agent itself raises.
    """
    start = time.time()
    try:
        result = agent.run(ctx, goal, **kwargs)
    except Exception as exc:  # noqa: BLE001 - agents surface errors on the result
        result = AgentResult(agent=agent.name, goal=goal, error=str(exc))
    result.duration_seconds = round(time.time() - start, 4)
    return result
