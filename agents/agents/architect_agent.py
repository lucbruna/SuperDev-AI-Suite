from __future__ import annotations

import json
from typing import Any

from ..base.base_agent import AgentResult, BaseAgent


class ArchitectAgent(BaseAgent):
    async def initialize(self) -> None:
        self._status = "ready"

    async def execute(self, task: str, context: dict[str, Any]) -> AgentResult:
        try:
            await self._check_cancelled()
            self._status = "running"

            components = self._design_components(task)
            patterns = self._identify_patterns(task)
            decisions = self._make_decisions(task, components)

            architecture = {
                "title": f"Architecture for: {task[:50]}",
                "components": components,
                "patterns": patterns,
                "design_decisions": decisions,
                "recommendations": self._generate_recommendations(components, patterns),
            }

            return AgentResult(
                success=True,
                output=json.dumps(architecture, indent=2),
                artifacts={"architecture": architecture},
                metrics={
                    "component_count": len(components),
                    "pattern_count": len(patterns),
                    "decision_count": len(decisions),
                },
            )
        except Exception as e:
            self._error_count += 1
            return AgentResult(success=False, output="", error=str(e))
        finally:
            self._status = "idle"

    def _design_components(self, task: str) -> list[dict[str, Any]]:
        keywords = task.lower().split()
        components = []
        if any(w in keywords for w in ["api", "rest", "service", "server"]):
            components.append({"name": "APIService", "responsibility": "Handle HTTP requests/responses", "interfaces": ["REST"]})
        if any(w in keywords for w in ["db", "database", "store", "persist"]):
            components.append({"name": "DatabaseLayer", "responsibility": "Data persistence and retrieval", "interfaces": ["Repository"]})
        if any(w in keywords for w in ["auth", "login", "user", "security"]):
            components.append({"name": "AuthService", "responsibility": "Authentication and authorization", "interfaces": ["JWT", "OAuth"]})
        if any(w in keywords for w in ["ui", "web", "frontend", "app"]):
            components.append({"name": "WebUI", "responsibility": "User interface rendering", "interfaces": ["React/Angular"]})
        if not components:
            components.append({"name": "CoreModule", "responsibility": "Primary business logic", "interfaces": []})
        return components

    def _identify_patterns(self, task: str) -> list[str]:
        patterns = []
        task_lower = task.lower()
        if "microservice" in task_lower:
            patterns.append("Microservices Architecture")
        if "event" in task_lower:
            patterns.append("Event-Driven Architecture")
        if "queue" in task_lower or "message" in task_lower:
            patterns.append("Message Queue Pattern")
        if "cache" in task_lower:
            patterns.append("Caching Pattern")
        if "plugin" in task_lower:
            patterns.append("Plugin Architecture")
        patterns.append("Layered Architecture")
        return patterns

    def _make_decisions(self, task: str, components: list[dict]) -> list[dict[str, Any]]:
        return [
            {"decision": f"Use {c['name']} as a separate module", "rationale": "Separation of concerns", "status": "proposed"}
            for c in components
        ]

    def _generate_recommendations(self, components: list, patterns: list) -> list[str]:
        return [
            "Document all API interfaces before implementation",
            "Set up CI/CD pipeline early",
            "Implement logging and monitoring from day one",
        ]

    def capabilities(self) -> list[str]:
        return ["architecture_design", "component_modeling", "pattern_identification", "design_review"]
