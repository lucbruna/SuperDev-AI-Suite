"""DecisionEngine — the "who / which LLM / what tools" brain.

For every task the engine deterministically decides:
- **owner**: the Chief Agent that will execute it (via the Router);
- **llm**: the provider that should serve it (via the LLMRegistry);
- **requires**: the tools/integrations the task needs.

The decision is applied to the task and recorded on the kernel's event bus
and audit trail. The core is pure: no clock, no network, no LLM calls.
"""
from __future__ import annotations

from typing import Any

from modules.super_ai_orchestrator.agents import AgentRegistry
from modules.super_ai_orchestrator.core.task import Task
from modules.super_ai_orchestrator.events.event import DECISION_MADE
from modules.super_ai_orchestrator.kernel import OrchestrationKernel
from modules.super_ai_orchestrator.llm.registry import (
    ANALYSIS,
    CODING,
    OPERATIONS,
    PLANNING,
    REASONING,
    LLMRegistry,
)
from modules.super_ai_orchestrator.routing import Router

# Kind -> required LLM capabilities for the decision.
_KIND_LLM_CAPS: dict[str, set[str]] = {
    "develop": {CODING, REASONING},
    "repair": {CODING, REASONING},
    "analyze": {ANALYSIS},
    "review": {ANALYSIS},
    "evolve": {ANALYSIS},
    "document": {ANALYSIS},
    "plan": {PLANNING, REASONING},
    "workflow": {PLANNING},
    "monitor": {OPERATIONS},
    "recover": {OPERATIONS, REASONING},
    "deploy": {OPERATIONS},
    "coordinate": {PLANNING},
    "agent": {REASONING},
}

# Kind -> default tool requirements.
_KIND_TOOLS: dict[str, tuple[str, ...]] = {
    "develop": ("git", "llm"),
    "repair": ("git", "docker", "llm"),
    "analyze": ("knowledge_graph", "architecture_graph"),
    "review": ("git", "knowledge_graph"),
    "evolve": ("evolution_engine", "analytics"),
    "document": ("docs", "knowledge_graph"),
    "plan": ("memory",),
    "workflow": ("workflow_engine", "memory"),
    "monitor": ("monitoring", "telemetry"),
    "recover": ("checkpoint", "rollback"),
    "deploy": ("docker", "kubernetes"),
    "coordinate": ("memory",),
    "agent": ("mcp", "llm"),
}


class DecisionEngine:
    """Deterministic owner/LLM/tool selection for tasks.

    Attributes:
        router: resolves the owner for a task kind.
        llm_registry: resolves the provider for required capabilities.
        agents: agent metadata (used to validate owners and derive tools).
    """

    def __init__(
        self,
        router: Router | None = None,
        llm_registry: LLMRegistry | None = None,
        agents: AgentRegistry | None = None,
    ) -> None:
        self.router = router or Router()
        self.llm_registry = llm_registry or LLMRegistry()
        self.agents = agents or AgentRegistry()

    def decide(self, kernel: OrchestrationKernel, task: Task) -> dict[str, Any]:
        """Apply a decision to ``task`` and record it.

        Returns:
            The decision record: owner, llm, requires and the rules applied.
        """
        owner_hint = task.payload.get("owner_hint")
        owner, candidates = self.router.route(task.kind, owner_hint)
        capabilities = _KIND_LLM_CAPS.get(task.kind, {ANALYSIS})
        prefer = task.payload.get("llm_prefer")
        llm = self.llm_registry.select(capabilities, prefer=prefer)

        requires = set(_KIND_TOOLS.get(task.kind, ()))
        for marker in task.payload.get("requires", ()):
            requires.add(str(marker))
        for key in task.payload:
            if key in {"git", "rag", "memory", "docker", "mcp", "db", "api"}:
                requires.add(key)

        task.owner = owner
        task.llm = llm
        task.requires = tuple(sorted(requires))

        record = {
            "task_seq": task.seq,
            "kind": task.kind,
            "owner": owner,
            "llm": llm,
            "requires": list(task.requires),
            "candidates": candidates,
            "capabilities": sorted(capabilities),
            "llm_prefer": prefer,
        }
        kernel.event_bus.publish(DECISION_MADE, record)
        kernel.audit.record("decided", task.seq, {"owner": owner, "llm": llm})
        return record

    def decide_many(
        self, kernel: OrchestrationKernel, tasks: list[Task]
    ) -> list[dict[str, Any]]:
        return [self.decide(kernel, task) for task in tasks]
