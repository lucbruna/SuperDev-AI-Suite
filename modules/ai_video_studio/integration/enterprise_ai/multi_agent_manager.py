"""Multi-Agent Manager — orchestrates a small crew of named agents."""
from __future__ import annotations

from typing import Any

AGENTS: dict[str, dict[str, Any]] = {
    "writer": {"role": "writes scripts and narration"},
    "director": {"role": "plans scenes and shots"},
    "reviewer": {"role": "validates quality and consistency"},
}


class MultiAgentManager:
    """Deterministic multi-agent orchestration (local, no LLM required)."""

    def __init__(self) -> None:
        self._runs: list[dict[str, Any]] = []

    def agents(self) -> list[dict[str, Any]]:
        return [{"name": n, **meta} for n, meta in AGENTS.items()]

    def run(self, task: str, *, agents: list[str] | None = None) -> dict[str, Any]:
        """Run *task* through the crew, logging each agent's step."""
        selected = [a for a in (agents or list(AGENTS)) if a in AGENTS] or list(AGENTS)
        steps = [
            {"agent": name, "role": AGENTS[name]["role"], "status": "completed"}
            for name in selected
        ]
        record = {"task": task, "agents": selected, "steps": steps, "completed": True}
        self._runs.append(record)
        return record

    def history(self) -> list[dict[str, Any]]:
        return [dict(r) for r in self._runs]


_multi_agent_manager: MultiAgentManager | None = None


def get_multi_agent_manager() -> MultiAgentManager:
    global _multi_agent_manager
    if _multi_agent_manager is None:
        _multi_agent_manager = MultiAgentManager()
    return _multi_agent_manager
