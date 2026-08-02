"""Ultra Harness Orchestrator - the brain of the SuperDev agent system."""

from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any

from .agent_profiles import AgentProfile, AgentDomain, DomainProfileRegistry
from .config import HarnessConfig
from .skills_registry import SkillsRegistry, SkillMapping

logger = logging.getLogger("harness.orchestrator")


@dataclass
class TaskRequest:
    """A task submitted to the harness."""

    task_id: str
    description: str
    domain: AgentDomain | None = None  # Auto-detect if None
    required_capabilities: list[str] = field(default_factory=list)
    priority: int = 5
    timeout_seconds: int = 600
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskResult:
    """Result of a harness task execution."""

    task_id: str
    success: bool
    output: str
    agent_used: str | None = None
    skills_used: list[str] = field(default_factory=list)
    domain: str | None = None
    duration_ms: float = 0.0
    metrics: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


class UltraHarness:
    """The SuperDev Ultra Harness - orchestrates specialized agents across all domains.

    Usage:
        harness = UltraHarness()
        await harness.initialize()

        result = await harness.execute_task(TaskRequest(
            task_id="task-1",
            description="Design a microservices architecture for an e-commerce platform",
            required_capabilities=["microservices", "api-gateway"],
        ))
    """

    def __init__(self, config: HarnessConfig | None = None) -> None:
        self._config = config or HarnessConfig()
        self._profile_registry = DomainProfileRegistry()
        self._skills_registry = SkillsRegistry()
        self._active_tasks: dict[str, TaskRequest] = {}
        self._task_history: list[TaskResult] = []
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the harness and validate all skills are available."""
        if self._initialized:
            return

        logger.info("Initializing Ultra Harness v%s", self._config.version)
        logger.info("Domains: %s", list(self._config.domains.keys()))
        logger.info("Agent profiles: %d", self._profile_registry.count())
        logger.info("Skills registered: %d", self._skills_registry.count())

        # Check which skills are actually installed
        installed = 0
        for skill in self._skills_registry.list_all():
            from pathlib import Path
            if Path(skill.skill_path).exists():
                installed += 1
            else:
                logger.warning("Skill not installed: %s (expected at %s)", skill.skill_id, skill.skill_path)

        logger.info("Skills installed: %d/%d", installed, self._skills_registry.count())
        self._initialized = True

    async def execute_task(self, request: TaskRequest) -> TaskResult:
        """Execute a task using the best matching agent and skills."""
        start_time = time.time()

        # 1. Detect domain if not specified
        domain = request.domain or self._detect_domain(request)

        # 2. Find best matching agent
        agent = self._profile_registry.find_best_match(
            request.required_capabilities, domain
        )
        if not agent:
            return TaskResult(
                task_id=request.task_id,
                success=False,
                output="",
                error=f"No matching agent found for capabilities: {request.required_capabilities}",
                duration_ms=(time.time() - start_time) * 1000,
            )

        # 3. Find matching skills
        skills = self._find_matching_skills(request.required_capabilities, domain)

        # 4. Build enhanced prompt with skill context
        skill_context = self._build_skill_context(skills)

        # 5. Execute (delegate to the backend ReActAgent)
        result: TaskResult | None = None
        try:
            self._active_tasks[request.task_id] = request
            output = await self._delegate_execution(agent, request, skill_context)

            result = TaskResult(
                task_id=request.task_id,
                success=True,
                output=output,
                agent_used=agent.agent_id,
                skills_used=[s.skill_id for s in skills],
                domain=agent.domain.value,
                duration_ms=(time.time() - start_time) * 1000,
                metrics={
                    "agent_name": agent.name,
                    "capabilities_matched": request.required_capabilities,
                    "skill_count": len(skills),
                },
            )
        except Exception as e:
            result = TaskResult(
                task_id=request.task_id,
                success=False,
                output="",
                agent_used=agent.agent_id,
                skills_used=[s.skill_id for s in skills],
                domain=agent.domain.value,
                duration_ms=(time.time() - start_time) * 1000,
                error=str(e),
            )
        finally:
            self._active_tasks.pop(request.task_id, None)
            if result is not None:
                self._task_history.append(result)

        if result is not None:
            return result

        return TaskResult(
            task_id=request.task_id,
            success=False,
            output="",
            error="Task execution failed unexpectedly",
            duration_ms=(time.time() - start_time) * 1000,
        )

    def _detect_domain(self, request: TaskRequest) -> AgentDomain | None:
        """Auto-detect the domain from task description and capabilities."""
        text = (request.description + " " + " ".join(request.required_capabilities)).lower()

        domain_keywords = {
            AgentDomain.ENVIRONMENT: ["docker", "kubernetes", "k8s", "ci/cd", "pipeline", "deploy", "container", "helm", "terraform", "ansible"],
            AgentDomain.MOBILE: ["android", "ios", "flutter", "react-native", "apk", "mobile", "app-store", "play-store"],
            AgentDomain.ARCHITECTURE: ["architecture", "microservices", "design", "pattern", "system-design", "distributed", "event-driven", "cqrs"],
            AgentDomain.AUTONOMOUS: ["autonomous", "self-healing", "afk", "incident", "sre", "chaos", "runbook", "remediation"],
            AgentDomain.EXPERIENCE: ["ux", "ui", "accessibility", "a11y", "design-system", "performance", "core-vitals", "lighthouse"],
        }

        scores = {}
        for domain, keywords in domain_keywords.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                scores[domain] = score

        if scores:
            return max(scores.keys(), key=lambda k: scores[k])
        return None

    def _find_matching_skills(
        self,
        capabilities: list[str],
        domain: AgentDomain | None = None,
    ) -> list[SkillMapping]:
        """Find skills that match the required capabilities."""
        candidates = self._skills_registry.list_by_domain(domain) if domain else self._skills_registry.list_all()
        if not candidates:
            return []

        matched = []
        cap_set = set(capabilities)
        for skill in candidates:
            tag_match = cap_set.intersection(skill.tags)
            if tag_match:
                matched.append(skill)
            elif domain and skill.domain == domain:
                matched.append(skill)

        return matched[:5]  # Limit to top 5

    def _build_skill_context(self, skills: list[SkillMapping]) -> str:
        """Build context string from skill contents."""
        if not skills:
            return ""

        parts = ["=== INSTALLED SKILLS ==="]
        for skill in skills:
            content = self._skills_registry.get_skill_content(skill.skill_id)
            if content:
                # Take first 2000 chars of each skill to avoid context overflow
                truncated = content[:2000]
                if len(content) > 2000:
                    truncated += "\n... (truncated)"
                parts.append(f"\n--- {skill.name} ---\n{truncated}")

        return "\n".join(parts)

    async def _delegate_execution(
        self,
        agent: AgentProfile,
        request: TaskRequest,
        skill_context: str,
    ) -> str:
        """Delegate task execution to the backend ReActAgent system."""
        # Build the enhanced task prompt
        prompt = f"""[ULTRA HARNESS - {agent.domain.value.upper()} DOMAIN]
Agent: {agent.name} ({agent.agent_id})
Role: {agent.role}

Task: {request.description}

{skill_context}

Execute this task using the available tools. Apply the skill knowledge above.
Respond with your analysis and any code changes needed."""

        # For now, return the structured prompt that the backend will process
        # In production, this would call the ReActAgent API
        return json.dumps({
            "status": "delegated",
            "agent": agent.agent_id,
            "domain": agent.domain.value,
            "prompt": prompt,
            "tools_available": agent.tools_allowed,
            "message": "Task delegated to specialized agent. Use the /chat/agent endpoint to execute.",
        }, indent=2)

    # === Query methods ===

    def get_config(self) -> HarnessConfig:
        return self._config

    def get_profiles(self) -> DomainProfileRegistry:
        return self._profile_registry

    def get_skills(self) -> SkillsRegistry:
        return self._skills_registry

    def get_status(self) -> dict[str, Any]:
        return {
            "initialized": self._initialized,
            "config_version": self._config.version,
            "active_tasks": len(self._active_tasks),
            "total_tasks_executed": len(self._task_history),
            "domains": self._config.to_dict()["domains"],
            "profiles": self._profile_registry.to_dict(),
            "skills": self._skills_registry.to_dict(),
        }

    def get_task_history(self) -> list[dict[str, Any]]:
        return [
            {
                "task_id": r.task_id,
                "success": r.success,
                "agent_used": r.agent_used,
                "domain": r.domain,
                "duration_ms": r.duration_ms,
                "error": r.error,
            }
            for r in self._task_history
        ]
