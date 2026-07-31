"""Agent template management system."""

from __future__ import annotations

import copy
import time
from typing import Any

BUILTIN_TEMPLATES: dict[str, dict[str, Any]] = {
    "supervisor": {
        "name": "Supervisor Agent",
        "agent_type": "supervisor",
        "tier": 0,
        "description": "Top-level orchestrator that coordinates all domain managers",
        "model": {"provider": "openai", "model": "gpt-4o", "temperature": 0.3},
        "capabilities": ["planning", "reasoning", "memory", "tools"],
        "max_iterations": 20,
        "instructions": (
            "You are the Super Orchestrator. Break complex requests into "
            "sub-tasks and delegate to the appropriate domain manager."
        ),
    },
    "planner": {
        "name": "Planner Agent",
        "agent_type": "planner",
        "tier": 1,
        "description": "Domain manager for planning and strategy",
        "model": {"provider": "openai", "model": "gpt-4o", "temperature": 0.4},
        "capabilities": ["planning", "reasoning", "memory"],
        "max_iterations": 15,
        "instructions": (
            "You are a planning specialist. Decompose goals into actionable "
            "task graphs with dependencies, priorities, and estimated effort."
        ),
    },
    "coder": {
        "name": "Coder Agent",
        "agent_type": "coder",
        "tier": 2,
        "description": "Specialist for writing and refactoring code",
        "model": {"provider": "openai", "model": "gpt-4o", "temperature": 0.2},
        "capabilities": ["chat", "tools", "code_execution"],
        "max_iterations": 10,
        "instructions": (
            "You are a senior software engineer. Write clean, well-tested, "
            "production-quality code following best practices."
        ),
    },
    "security": {
        "name": "Security Agent",
        "agent_type": "security",
        "tier": 2,
        "description": "Specialist for security analysis and hardening",
        "model": {"provider": "openai", "model": "gpt-4o", "temperature": 0.1},
        "capabilities": ["reasoning", "tools"],
        "max_iterations": 10,
        "instructions": (
            "You are a security expert. Analyze code for vulnerabilities, "
            "OWASP top 10 issues, and recommend security hardening."
        ),
    },
    "qa": {
        "name": "QA Agent",
        "agent_type": "qa",
        "tier": 2,
        "description": "Specialist for quality assurance and testing",
        "model": {"provider": "openai", "model": "gpt-4o", "temperature": 0.2},
        "capabilities": ["chat", "tools", "code_execution"],
        "max_iterations": 12,
        "instructions": (
            "You are a QA engineer. Write comprehensive tests, analyze coverage, detect bugs, and ensure code quality."
        ),
    },
    "devops": {
        "name": "DevOps Agent",
        "agent_type": "devops",
        "tier": 2,
        "description": "Specialist for deployment and infrastructure",
        "model": {"provider": "openai", "model": "gpt-4o", "temperature": 0.2},
        "capabilities": ["chat", "tools"],
        "max_iterations": 10,
        "instructions": (
            "You are a DevOps engineer. Manage CI/CD pipelines, Docker, Kubernetes, and cloud infrastructure."
        ),
    },
    "architect": {
        "name": "Architect Agent",
        "agent_type": "architect",
        "tier": 1,
        "description": "Domain manager for software architecture",
        "model": {"provider": "openai", "model": "gpt-4o", "temperature": 0.5},
        "capabilities": ["planning", "reasoning", "memory"],
        "max_iterations": 15,
        "instructions": (
            "You are a software architect. Design scalable system architectures, "
            "select appropriate patterns, and make technology decisions."
        ),
    },
}


class TemplateManager:
    """Manages agent templates for rapid creation."""

    def __init__(self) -> None:
        self._templates: dict[str, dict[str, Any]] = {}
        self._load_builtins()

    def _load_builtins(self) -> None:
        for name, template in BUILTIN_TEMPLATES.items():
            self._templates[name] = copy.deepcopy(template)

    def register_template(self, name: str, template: dict[str, Any]) -> None:
        self._templates[name] = copy.deepcopy(template)

    def get_template(self, name: str) -> dict[str, Any] | None:
        tpl = self._templates.get(name)
        return copy.deepcopy(tpl) if tpl else None

    def list_templates(self) -> list[str]:
        return list(self._templates.keys())

    def create_from_template(
        self,
        name: str,
        overrides: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        tpl = self.get_template(name)
        if tpl is None:
            return None
        if overrides:
            tpl.update(overrides)
        tpl.setdefault("created_at", time.time())
        return tpl

    def delete_template(self, name: str) -> bool:
        return self._templates.pop(name, None) is not None

    def template_exists(self, name: str) -> bool:
        return name in self._templates

    def count(self) -> int:
        return len(self._templates)

    def snapshot(self) -> dict[str, Any]:
        return {
            "templates": list(self._templates.keys()),
            "count": len(self._templates),
        }
