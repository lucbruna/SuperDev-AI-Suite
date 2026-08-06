"""LLM-backed planner with a deterministic fallback.

Asks a configured live LLM to decompose a goal into tasks (JSON), then
validates the payload through the deterministic :class:`ProjectPlanner` so
every plan keeps the module's invariants (risk levels, priorities, file
specs, topological ordering). When no live LLM is configured or the response
is unusable, planning degrades to the deterministic decomposition — the loop
never depends on the LLM being up.
"""
from __future__ import annotations

import json
import logging
from typing import Any

from modules.autonomous_developer.config.llm_config import LLMConfig
from modules.autonomous_developer.config.planner_config import PlannerConfig
from modules.autonomous_developer.core.exceptions import DeveloperError
from modules.autonomous_developer.core.models import TaskPlan
from modules.autonomous_developer.llm import providers
from modules.autonomous_developer.llm.client import LLMClient
from modules.autonomous_developer.llm.errors import LLMError
from modules.autonomous_developer.memory.lessons import format_lessons
from modules.autonomous_developer.planner.project_planner import ProjectPlanner

logger = logging.getLogger(__name__)

_PLAN_PROMPT = """You are the planning brain of an autonomous developer.

Decompose the goal below into concrete, ordered tasks. Respond with ONLY a
JSON object (no markdown fences, no prose) with this exact shape:

{{
  "goal": "<verbatim goal>",
  "tasks": [
    {{
      "title": "short task title",
      "description": "what to change and why",
      "priority": "medium",
      "risk": "low",
      "files": [
        {{"path": "relative/file.py", "content": "full file content"}}
      ]
    }}
  ]
}}

Rules:
- priority: low | medium | high | critical
- risk: low | medium | high | critical
- files may be empty; when present, each entry needs a path and content.

GOAL:
{goal}

PREVIOUS FAILURES TO AVOID:
{lessons}
"""


class LLMPlanner:
    """LLM-first planner that degrades to the deterministic ProjectPlanner.

    ``client`` is injected for tests (e.g. a mock client); otherwise one is
    resolved from the runtime config so live providers are picked up from the
    environment automatically.
    """

    def __init__(
        self,
        config: PlannerConfig | None = None,
        llm: LLMConfig | None = None,
        client: LLMClient | None = None,
    ) -> None:
        self.config = config or PlannerConfig()
        self.llm_config = llm or LLMConfig()
        self.client = client
        self._planner = ProjectPlanner(self.config)

    def _resolve_client(self, ctx=None) -> LLMClient:
        if self.client is not None:
            return self.client
        ctx_llm = getattr(getattr(ctx, "config", None), "llm", None)
        return LLMClient(config=ctx_llm or self.llm_config)

    def _llm_available(self, client: LLMClient) -> bool:
        if client.mock_response is not None:
            return True
        return client.config.enabled and providers.is_configured(client.config)

    def plan(
        self,
        goal: str,
        *,
        tasks: list[str | dict[str, Any]] | None = None,
        priority: str | None = None,
        lessons: str = "",
        ctx=None,
    ) -> TaskPlan:
        """Build a plan, using the LLM when available (explicit ``tasks`` win)."""
        return self._plan_with_usage(
            goal, tasks=tasks, priority=priority, lessons=lessons, ctx=ctx
        )[0]

    def _plan_with_usage(
        self,
        goal: str,
        *,
        tasks: list[str | dict[str, Any]] | None = None,
        priority: str | None = None,
        lessons: str = "",
        ctx=None,
    ) -> tuple[TaskPlan, dict[str, int]]:
        if tasks is not None:
            return self._planner.plan(goal, tasks=tasks, priority=priority), {}
        client = self._resolve_client(ctx)
        if not self._llm_available(client):
            return self._planner.plan(goal, priority=priority), {}
        prompt = _PLAN_PROMPT.format(goal=goal, lessons=lessons or "(none)")
        try:
            response = client.complete(prompt, max_tokens=self.llm_config.max_tokens)
            payload = self._parse_plan(response.text)
            plan = self._planner.plan(
                str(payload.get("goal") or goal),
                tasks=payload.get("tasks"),
                priority=priority,
            )
            return plan, response.usage or {}
        except (LLMError, ValueError, TypeError, DeveloperError) as exc:
            logger.warning(
                "LLM planning failed (%s); falling back to deterministic", exc
            )
            return self._planner.plan(goal, priority=priority), {}

    @staticmethod
    def _parse_plan(text: str) -> dict[str, Any]:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
        payload = json.loads(cleaned)
        if not isinstance(payload, dict):
            raise ValueError("plan payload must be a JSON object")
        return payload

    def run(self, ctx, goal: str, session_id: str | None = None, **kwargs: Any) -> TaskPlan:
        """Runtime entry point — mirrors ProjectPlanner.run's records/events."""
        lessons = ctx.lessons.for_goal(goal)
        plan, usage = self._plan_with_usage(
            goal,
            tasks=kwargs.get("tasks"),
            priority=kwargs.get("priority"),
            lessons=format_lessons(lessons),
            ctx=ctx,
        )
        if usage:
            ctx.record_usage(
                "plan",
                usage.get("prompt_tokens", 0),
                usage.get("completion_tokens", 0),
            )
        ctx.record("task_count", len(plan.tasks))
        ctx.record("lessons_used", len(lessons))
        ctx.record("knowledge_used", ctx.memory.contains("knowledge_graph"))
        ctx.publish(
            "plan.ready",
            {
                "goal": plan.goal,
                "task_count": len(plan.tasks),
                "lessons_used": len(lessons),
            },
        )
        return plan
