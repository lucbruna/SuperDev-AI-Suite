from __future__ import annotations

from typing import Any


class EventRegistry:
    """Registry of known event types."""

    _events: dict[str, str] = {}

    @classmethod
    def register(cls, event_type: str, description: str = "") -> None:
        cls._events[event_type] = description

    @classmethod
    def get(cls, event_type: str) -> str | None:
        return cls._events.get(event_type)

    @classmethod
    def list_events(cls) -> dict[str, str]:
        return dict(cls._events)


EventRegistry.register("user.created", "User account created")
EventRegistry.register("user.updated", "User account updated")
EventRegistry.register("user.deleted", "User account deleted")
EventRegistry.register("project.created", "Project created")
EventRegistry.register("project.updated", "Project updated")
EventRegistry.register("project.deleted", "Project deleted")
EventRegistry.register("agent.started", "Agent execution started")
EventRegistry.register("agent.completed", "Agent execution completed")
EventRegistry.register("agent.failed", "Agent execution failed")
EventRegistry.register("workflow.started", "Workflow execution started")
EventRegistry.register("workflow.completed", "Workflow execution completed")
EventRegistry.register("workflow.failed", "Workflow execution failed")
EventRegistry.register("plugin.installed", "Plugin installed")
EventRegistry.register("plugin.uninstalled", "Plugin uninstalled")
