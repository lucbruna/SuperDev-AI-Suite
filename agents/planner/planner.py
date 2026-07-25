from __future__ import annotations

import json
import logging
import uuid
from typing import Any, Optional, Protocol

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class Step(BaseModel):
    id: str = ""
    description: str = ""
    depends_on: list[str] = Field(default_factory=list)
    assigned_agent: str = ""
    expected_output: str = ""
    status: str = "pending"
    priority: int = 0
    estimated_complexity: str = "medium"


class LLMProvider(Protocol):
    """Protocol for LLM providers used by the planner."""

    async def complete(self, messages: list[dict[str, str]], model: str = "") -> str: ...


class Planner:
    """Decomposes goals into executable steps using LLM or rule-based fallback."""

    def __init__(self, llm_provider: LLMProvider | None = None) -> None:
        self._steps: list[Step] = []
        self._llm = llm_provider

    async def plan(self, goal: str, context: Optional[dict[str, Any]] = None) -> list[Step]:
        ctx = context or {}
        if self._llm:
            self._steps = await self._decompose_with_llm(goal, ctx)
        else:
            self._steps = self._decompose_goal(goal, ctx)
        return self._steps

    async def _decompose_with_llm(self, goal: str, context: dict[str, Any]) -> list[Step]:
        """Use LLM to decompose a goal into structured steps."""
        system_prompt = """You are a software engineering project planner.
Given a goal, decompose it into a structured plan with dependent steps.

Return a JSON array of step objects. Each step must have:
- description: what to do (clear, actionable)
- depends_on: list of step indices (0-based) that must complete first
- assigned_agent: one of [planner_agent, architect_agent, executor_agent, reviewer_agent, testing_agent, documentation_agent, security_agent, deployment_agent]
- expected_output: what the step should produce
- priority: 1 (highest) to 5 (lowest)
- estimated_complexity: one of [low, medium, high]

Rules:
- Steps with no dependencies can run in parallel
- Assign the most appropriate agent for each task
- Include review and testing steps
- Order by logical dependency, not just sequence
- Return ONLY valid JSON, no other text"""

        context_str = ""
        if context:
            context_str = f"\n\nContext:\n{json.dumps(context, indent=2)}"

        user_prompt = f"Decompose this goal into a plan:\n\n{goal}{context_str}"

        try:
            response = await self._llm.complete([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ])

            steps_data = self._extract_json(response)
            if not isinstance(steps_data, list):
                raise ValueError("LLM did not return a JSON array")

            steps = []
            for i, item in enumerate(steps_data):
                step = Step(
                    id=str(uuid.uuid4()),
                    description=item.get("description", f"Step {i + 1}"),
                    depends_on=[str(steps[j].id) for j in item.get("depends_on", []) if j < len(steps)],
                    assigned_agent=item.get("assigned_agent", "executor_agent"),
                    expected_output=item.get("expected_output", ""),
                    status="pending",
                    priority=item.get("priority", 3),
                    estimated_complexity=item.get("estimated_complexity", "medium"),
                )
                steps.append(step)

            logger.info(f"LLM decomposed goal into {len(steps)} steps")
            return steps

        except Exception as e:
            logger.warning(f"LLM decomposition failed, falling back to rule-based: {e}")
            return self._decompose_goal(goal, context)

    def _extract_json(self, text: str) -> Any:
        """Extract JSON from LLM response, handling markdown code blocks."""
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            lines = [l for l in lines if not l.startswith("```")]
            text = "\n".join(lines)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start = text.find("[")
            end = text.rfind("]")
            if start != -1 and end != -1:
                return json.loads(text[start:end + 1])
            raise ValueError("No valid JSON found in response")

    def _decompose_goal(self, goal: str, context: dict[str, Any]) -> list[Step]:
        """Rule-based decomposition when no LLM is available."""
        steps: list[Step] = []

        # Phase 1: Planning & Architecture
        planning_steps = [
            ("Analyze requirements and define scope", "planner_agent", "high"),
            ("Design system architecture", "architect_agent", "high"),
            ("Define data models and API contracts", "architect_agent", "high"),
        ]

        # Phase 2: Implementation
        impl_steps = [
            ("Implement database layer", "executor_agent", "high"),
            ("Implement backend API", "executor_agent", "high"),
            ("Implement frontend UI", "executor_agent", "medium"),
            ("Implement authentication & security", "executor_agent", "high"),
        ]

        # Phase 3: Quality
        quality_steps = [
            ("Write unit tests", "testing_agent", "medium"),
            ("Perform code review", "reviewer_agent", "high"),
            ("Security audit", "security_agent", "high"),
        ]

        # Phase 4: Delivery
        delivery_steps = [
            ("Write documentation", "documentation_agent", "low"),
            ("Set up CI/CD pipeline", "deployment_agent", "medium"),
            ("Deploy to staging", "deployment_agent", "medium"),
        ]

        all_phases = [planning_steps, impl_steps, quality_steps, delivery_steps]
        phase_names = ["planning", "implementation", "quality", "delivery"]

        prev_phase_ids: list[str] = []

        for phase_idx, (phase_steps, phase_name) in enumerate(zip(all_phases, phase_names)):
            phase_ids: list[str] = []

            for desc, agent, complexity in phase_steps:
                step = Step(
                    id=str(uuid.uuid4()),
                    description=desc,
                    depends_on=list(prev_phase_ids) if phase_idx > 0 else [],
                    assigned_agent=agent,
                    expected_output=f"Completed: {desc}",
                    status="pending",
                    priority=phase_idx + 1,
                    estimated_complexity=complexity,
                )
                steps.append(step)
                phase_ids.append(step.id)

            prev_phase_ids = phase_ids

        return steps

    def get_steps(self) -> list[Step]:
        return self._steps

    def get_ready_steps(self) -> list[Step]:
        """Return steps whose dependencies are all completed."""
        completed_ids = {s.id for s in self._steps if s.status == "completed"}
        return [
            s for s in self._steps
            if s.status == "pending" and all(dep in completed_ids for dep in s.depends_on)
        ]

    def mark_completed(self, step_id: str) -> None:
        for step in self._steps:
            if step.id == step_id:
                step.status = "completed"
                return

    def mark_failed(self, step_id: str) -> None:
        for step in self._steps:
            if step.id == step_id:
                step.status = "failed"
                return

    def clear(self) -> None:
        self._steps.clear()
