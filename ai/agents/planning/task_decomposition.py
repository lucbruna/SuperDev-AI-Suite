"""Task decomposition engine for breaking goals into actionable tasks."""

from __future__ import annotations

import uuid
from typing import Any


class TaskDecomposer:
    """Decomposes high-level goals into ordered, actionable tasks."""

    def __init__(self) -> None:
        self._decomposition_count: int = 0

    def decompose(self, goal: str, context: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        self._decomposition_count += 1
        tasks: list[dict[str, Any]] = []
        keywords = goal.lower().split()
        task_templates = self._infer_tasks(keywords, context)
        for i, template in enumerate(task_templates):
            task = {
                "task_id": f"task_{uuid.uuid4().hex[:8]}",
                "title": template["title"],
                "description": template.get("description", ""),
                "type": template.get("type", "general"),
                "priority": template.get("priority", 5),
                "estimated_effort": template.get("effort", "medium"),
                "dependencies": template.get("dependencies", []),
                "status": "pending",
                "order": i,
                "required_skills": template.get("skills", []),
            }
            tasks.append(task)
        return tasks

    def _infer_tasks(self, keywords: list[str], context: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        templates: list[dict[str, Any]] = []
        templates.append(
            {
                "title": "Analyze requirements",
                "description": "Understand and document all requirements",
                "type": "analysis",
                "priority": 10,
                "effort": "medium",
                "skills": ["planning", "reasoning"],
            }
        )
        tech_keywords = {"api", "database", "frontend", "backend", "ui", "test"}
        found = [k for k in keywords if k in tech_keywords]
        if found or any(w in keywords for w in ["create", "build", "implement", "desenvolver"]):
            templates.append(
                {
                    "title": "Design architecture",
                    "description": "Design system architecture and component interactions",
                    "type": "design",
                    "priority": 9,
                    "effort": "high",
                    "dependencies": ["Analyze requirements"],
                    "skills": ["planning", "architecture"],
                }
            )
            templates.append(
                {
                    "title": "Implement solution",
                    "description": "Write code and implement the solution",
                    "type": "implementation",
                    "priority": 8,
                    "effort": "high",
                    "dependencies": ["Design architecture"],
                    "skills": ["coding"],
                }
            )
            templates.append(
                {
                    "title": "Test and validate",
                    "description": "Run tests and validate the implementation",
                    "type": "testing",
                    "priority": 7,
                    "effort": "medium",
                    "dependencies": ["Implement solution"],
                    "skills": ["testing", "qa"],
                }
            )
            templates.append(
                {
                    "title": "Review and refine",
                    "description": "Code review and quality improvements",
                    "type": "review",
                    "priority": 6,
                    "effort": "medium",
                    "dependencies": ["Test and validate"],
                    "skills": ["review"],
                }
            )
        return templates

    def flatten(self, tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        flat: list[dict[str, Any]] = []
        for task in tasks:
            flat.append(task)
        return sorted(flat, key=lambda t: t.get("order", 0))

    def count(self) -> int:
        return self._decomposition_count

    def snapshot(self) -> dict[str, Any]:
        return {"total_decompositions": self._decomposition_count}
