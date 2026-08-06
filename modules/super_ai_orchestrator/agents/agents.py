"""ChiefAgent — the 12 specialised agents the orchestrator can delegate to.

Each agent declares the task kinds it can handle, its capabilities and the
tools it typically needs. This metadata drives routing (who) and the
Decision Engine (which tools). Agents are pure metadata in the core; actual
execution happens through registered handlers/integrations.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ChiefAgent:
    """A specialised orchestrator agent.

    Attributes:
        name: agent id used by routing (e.g. ``developer``).
        title: human label.
        mission: one-line mandate.
        capabilities: what the agent is good at.
        kinds: task kinds this agent can execute.
        tools: tools the agent typically requires.
    """

    name: str
    title: str
    mission: str
    capabilities: frozenset[str]
    kinds: frozenset[str]
    tools: frozenset[str]

    def handles(self, kind: str) -> bool:
        return kind in self.kinds

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["capabilities"] = sorted(self.capabilities)
        data["kinds"] = sorted(self.kinds)
        data["tools"] = sorted(self.tools)
        return data


def _agent(
    name: str,
    title: str,
    mission: str,
    capabilities: set[str],
    kinds: set[str],
    tools: set[str],
) -> ChiefAgent:
    return ChiefAgent(
        name=name,
        title=title,
        mission=mission,
        capabilities=frozenset(capabilities),
        kinds=frozenset(kinds),
        tools=frozenset(tools),
    )


CHIEF_AGENTS: tuple[ChiefAgent, ...] = (
    _agent(
        "architect",
        "Chief Architect",
        "Guards architecture integrity: structure, coupling and design coherence.",
        {"analysis", "design", "review"},
        {"analyze", "plan", "review"},
        {"architecture_graph", "knowledge_graph", "architecture_intelligence"},
    ),
    _agent(
        "planner",
        "Chief Planner",
        "Breaks work into deterministic, ordered step plans.",
        {"planning", "analysis"},
        {"plan"},
        {"memory", "knowledge_graph"},
    ),
    _agent(
        "developer",
        "Chief Developer",
        "Implements changes in the project codebase.",
        {"coding", "reasoning"},
        {"develop", "repair"},
        {"git", "docker", "llm", "api"},
    ),
    _agent(
        "reviewer",
        "Chief Reviewer",
        "Reviews diffs for standards, safety and quality.",
        {"analysis", "review"},
        {"review"},
        {"git", "knowledge_graph"},
    ),
    _agent(
        "security",
        "Chief Security",
        "Assesses security posture and flags exploitable issues.",
        {"analysis", "security"},
        {"analyze", "review"},
        {"security_scan", "knowledge_graph"},
    ),
    _agent(
        "infrastructure",
        "Chief Infrastructure",
        "Builds, stages and releases; runs the platform.",
        {"operations", "coding"},
        {"deploy", "repair", "recover"},
        {"docker", "kubernetes", "api"},
    ),
    _agent(
        "evolution",
        "Chief Evolution",
        "Drives the AI Evolution Engine: measures, recommends, evolves.",
        {"analysis", "evolution"},
        {"evolve"},
        {"evolution_engine", "analytics", "ai_evolution_engine"},
    ),
    _agent(
        "monitoring",
        "Chief Monitoring",
        "Watches orchestrator and system health.",
        {"monitoring", "analysis"},
        {"monitor"},
        {"monitoring", "telemetry", "digital_twin"},
    ),
    _agent(
        "recovery",
        "Chief Recovery",
        "Restores failed work: checkpoints, rollback, self-healing.",
        {"operations", "recovery"},
        {"recover", "repair"},
        {"checkpoint", "rollback", "self_healing_engine"},
    ),
    _agent(
        "documentation",
        "Chief Documentation",
        "Produces and maintains project documentation.",
        {"writing", "analysis"},
        {"document"},
        {"docs", "knowledge_graph"},
    ),
    _agent(
        "workflow",
        "Chief Workflow",
        "Runs defined workflows and multi-step processes.",
        {"orchestration", "planning"},
        {"workflow"},
        {"workflow_engine", "memory"},
    ),
    _agent(
        "coordinator",
        "Chief Coordinator",
        "Coordinates sub-tasks and acts as the routing fallback.",
        {"orchestration"},
        {"coordinate", "agent"},
        {"memory", "mcp", "event_bus"},
    ),
)
