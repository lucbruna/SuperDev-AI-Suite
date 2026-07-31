from __future__ import annotations

from .components_engine import ComponentsEngine
from .components_library import (
    AgentCard,
    Charts,
    ChatBox,
    Editor,
    Header,
    Menu,
    MetricsPanel,
    Modal,
    ProjectCard,
    Sidebar,
    Table,
    Terminal,
    WorkflowViewer,
)


def create_engine() -> ComponentsEngine:
    """Create a ComponentsEngine pre-registered with the standard library."""
    engine = ComponentsEngine()
    engine.register("header", Header())
    engine.register("sidebar", Sidebar())
    engine.register("menu", Menu())
    engine.register("modal", Modal())
    engine.register("table", Table())
    engine.register("charts", Charts())
    engine.register("editor", Editor())
    engine.register("terminal", Terminal())
    engine.register("chat_box", ChatBox())
    engine.register("agent_card", AgentCard())
    engine.register("project_card", ProjectCard())
    engine.register("workflow_viewer", WorkflowViewer())
    engine.register("metrics_panel", MetricsPanel())
    return engine


__all__ = ["ComponentsEngine", "create_engine"]
