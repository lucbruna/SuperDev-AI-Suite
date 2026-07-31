from __future__ import annotations

from typing import Any


class Header:
    """Top navigation header component."""

    def render(self, design: Any, **props: Any) -> dict[str, Any]:
        return {
            "type": "header",
            "brand": props.get("brand", "SuperDev"),
            "height": 64,
            "background": design.colors.color("surface"),
            "border_color": design.colors.color("border"),
            "items": props.get("items", []),
            "props": props,
        }


class Sidebar:
    """Side navigation panel component."""

    def render(self, design: Any, **props: Any) -> dict[str, Any]:
        return {
            "type": "sidebar",
            "width": props.get("width", 260),
            "collapsed": props.get("collapsed", False),
            "background": design.colors.color("surface"),
            "items": props.get("items", []),
            "props": props,
        }


class Menu:
    """Menu list component."""

    def render(self, design: Any, **props: Any) -> dict[str, Any]:
        return {
            "type": "menu",
            "items": props.get("items", []),
            "orientation": props.get("orientation", "vertical"),
            "props": props,
        }


class Modal:
    """Modal dialog overlay component."""

    def render(self, design: Any, **props: Any) -> dict[str, Any]:
        return {
            "type": "modal",
            "open": props.get("open", False),
            "title": props.get("title", ""),
            "size": props.get("size", "md"),
            "overlay": True,
            "props": props,
        }


class Table:
    """Data table component."""

    def render(self, design: Any, **props: Any) -> dict[str, Any]:
        return {
            "type": "table",
            "columns": props.get("columns", []),
            "rows": props.get("rows", []),
            "sortable": props.get("sortable", True),
            "props": props,
        }


class Charts:
    """Chart rendering component."""

    KINDS = ("line", "bar", "pie", "area", "scatter")

    def render(self, design: Any, **props: Any) -> dict[str, Any]:
        kind = props.get("kind", "line")
        if kind not in self.KINDS:
            raise ValueError(f"unsupported chart kind: {kind}")
        return {
            "type": "chart",
            "kind": kind,
            "data": props.get("data", []),
            "title": props.get("title", ""),
            "props": props,
        }


class Editor:
    """Code editor component."""

    def render(self, design: Any, **props: Any) -> dict[str, Any]:
        return {
            "type": "editor",
            "language": props.get("language", "python"),
            "content": props.get("content", ""),
            "read_only": props.get("read_only", False),
            "theme": "dark" if design.mode == "dark" else "light",
            "props": props,
        }


class Terminal:
    """Embedded terminal component."""

    def render(self, design: Any, **props: Any) -> dict[str, Any]:
        return {
            "type": "terminal",
            "lines": props.get("lines", []),
            "prompt": props.get("prompt", "$"),
            "props": props,
        }


class ChatBox:
    """AI chat message list component."""

    def render(self, design: Any, **props: Any) -> dict[str, Any]:
        return {
            "type": "chat_box",
            "messages": props.get("messages", []),
            "input_placeholder": props.get("input_placeholder", "Type a message..."),
            "props": props,
        }


class AgentCard:
    """Agent summary card component."""

    def render(self, design: Any, **props: Any) -> dict[str, Any]:
        return {
            "type": "agent_card",
            "agent": props.get("agent", {}),
            "status": props.get("status", "idle"),
            "model": props.get("model", ""),
            "props": props,
        }


class ProjectCard:
    """Project summary card component."""

    def render(self, design: Any, **props: Any) -> dict[str, Any]:
        return {
            "type": "project_card",
            "project": props.get("project", {}),
            "status": props.get("status", "active"),
            "props": props,
        }


class WorkflowViewer:
    """Workflow graph viewer component."""

    def render(self, design: Any, **props: Any) -> dict[str, Any]:
        return {
            "type": "workflow_viewer",
            "nodes": props.get("nodes", []),
            "edges": props.get("edges", []),
            "layout": props.get("layout", "dagre"),
            "props": props,
        }


class MetricsPanel:
    """Metrics panel component."""

    def render(self, design: Any, **props: Any) -> dict[str, Any]:
        return {
            "type": "metrics_panel",
            "metrics": props.get("metrics", []),
            "refresh_interval": props.get("refresh_interval", 5),
            "props": props,
        }


__all__ = [
    "Header",
    "Sidebar",
    "Menu",
    "Modal",
    "Table",
    "Charts",
    "Editor",
    "Terminal",
    "ChatBox",
    "AgentCard",
    "ProjectCard",
    "WorkflowViewer",
    "MetricsPanel",
]
