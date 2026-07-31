from __future__ import annotations

import asyncio
import random
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from ..base.base_agent import BaseAgent


@dataclass
class AgentCapability:
    name: str
    version: str = "1.0"
    description: str = ""
    score: float = 1.0


@dataclass
class RoutingResult:
    agent_id: str
    agent_name: str
    confidence: float
    reason: str = ""
    fallback_used: bool = False


class RoutingEngine:
    """Smart routing engine that matches tasks to the best agent."""

    def __init__(self) -> None:
        self._capabilities: dict[str, list[AgentCapability]] = {}
        self._load_counts: dict[str, int] = {}
        self._lock = asyncio.Lock()
        self._route_history: list[dict[str, Any]] = []

    def register_agent(self, agent_id: str, agent: BaseAgent) -> None:
        caps = agent.capabilities()
        self._capabilities[agent_id] = [AgentCapability(name=c) if isinstance(c, str) else c for c in caps]
        self._load_counts[agent_id] = 0

    def unregister_agent(self, agent_id: str) -> None:
        self._capabilities.pop(agent_id, None)
        self._load_counts.pop(agent_id, None)

    async def route(
        self,
        task: str,
        task_type: str = "",
        context: dict[str, Any] | None = None,
        preferred_agent: str | None = None,
        require_fallback: bool = True,
    ) -> RoutingResult:
        """Find the best agent for a given task using capability matching."""
        async with self._lock:
            task_lower = task.lower()
            candidates: list[tuple[str, float, str]] = []

            for agent_id, caps in self._capabilities.items():
                score = 0.0
                best_match = ""

                for cap in caps:
                    cap_lower = cap.name.lower()
                    if task_type and task_type.lower() in cap_lower:
                        score += 3.0 * cap.score
                        best_match = cap.name
                    keywords = cap_lower.split("_")
                    for kw in keywords:
                        if kw and kw in task_lower:
                            score += 1.0 * cap.score
                            best_match = cap.name
                    agent_name = agent_id.lower()
                    if agent_name in task_lower or agent_name.replace("-", "_") in task_lower:
                        score += 2.0 * cap.score
                        best_match = cap.name

                load = self._load_counts.get(agent_id, 0)
                score -= load * 0.5

                if score > 0:
                    candidates.append((agent_id, score, best_match))
                elif preferred_agent and agent_id == preferred_agent:
                    candidates.append((agent_id, 0.5, "preferred"))

            candidates.sort(key=lambda x: -x[1])

            if preferred_agent:
                for idx, (aid, _, _) in enumerate(candidates):
                    if aid == preferred_agent:
                        candidate = candidates.pop(idx)
                        candidates.insert(0, candidate)
                        break

            if candidates:
                best = candidates[0]
                agent_id, confidence, reason = best
                result = RoutingResult(
                    agent_id=agent_id,
                    agent_name=agent_id,
                    confidence=min(confidence / 5.0, 1.0),
                    reason=reason or "capability match",
                    fallback_used=False,
                )
            elif require_fallback:
                if self._capabilities:
                    agent_id = min(self._load_counts, key=self._load_counts.get)  # type: ignore
                    result = RoutingResult(
                        agent_id=agent_id,
                        agent_name=agent_id,
                        confidence=0.3,
                        reason="fallback (no direct match)",
                        fallback_used=True,
                    )
                else:
                    available = list(self._capabilities.keys())
                    if available:
                        result = RoutingResult(
                            agent_id=random.choice(available),
                            agent_name=random.choice(available),
                            confidence=0.2,
                            reason="random fallback",
                            fallback_used=True,
                        )
                    else:
                        raise RuntimeError("No agents available for routing")
            else:
                raise RuntimeError(f"No suitable agent found for task: {task}")

            self._load_counts[result.agent_id] = self._load_counts.get(result.agent_id, 0) + 1

            self._route_history.append(
                {
                    "task": task[:100],
                    "task_type": task_type,
                    "routed_to": result.agent_id,
                    "confidence": result.confidence,
                    "fallback": result.fallback_used,
                    "timestamp": datetime.now(UTC).isoformat(),
                }
            )
            if len(self._route_history) > 1000:
                self._route_history = self._route_history[-500:]

            return result

    async def complete_task(self, agent_id: str) -> None:
        """Decrement load for an agent after task completion."""
        async with self._lock:
            current = self._load_counts.get(agent_id, 0)
            if current > 0:
                self._load_counts[agent_id] = current - 1

    def get_agent_load(self, agent_id: str) -> int:
        return self._load_counts.get(agent_id, 0)

    def get_all_loads(self) -> dict[str, int]:
        return dict(self._load_counts)

    def get_route_history(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._route_history[-limit:]

    def get_statistics(self) -> dict[str, Any]:
        total = len(self._route_history)
        fallbacks = sum(1 for r in self._route_history if r.get("fallback"))
        return {
            "total_routes": total,
            "fallback_count": fallbacks,
            "fallback_rate": round(fallbacks / total, 3) if total > 0 else 0,
            "agents_available": len(self._capabilities),
            "agent_loads": dict(self._load_counts),
        }
